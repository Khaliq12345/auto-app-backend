from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from fastapi import (
    FastAPI,
)
from fastapi.middleware.cors import CORSMiddleware
from supabase import (
    Client,
    create_client,
)
from supabase.lib.client_options import SyncClientOptions

from config import config
from services import autoscout24, lacentrale, leboncoin
from utilities import utils

OUT_FILE = Path(config.UPLOAD_FILE)
domains = [lacentrale.domain, autoscout24.domain, leboncoin.domain]
domain_functions = {
    "lacentrale": lacentrale.main,
    "autoscout24": autoscout24.main,
    "leboncoin": leboncoin.main,
}


def get_avg_price_based_on_domain(
    records: list[dict],
    percentage_limit: int = 95,
):
    # Get the average price based on the best matching percentage for each domain
    best_prices = []
    for domain in domains:
        for record in records:
            if (record["domain"] == domain) and (
                record["matching_percentage"] >= percentage_limit
            ):
                best_prices.append(record["price"])
    best_prices = [bp for bp in best_prices if bp]
    if best_prices:
        return sum(best_prices) / len(best_prices)
    else:
        return 0


def get_session() -> Client:
    client: Client = create_client(
        supabase_key=utils.supabase_key,
        supabase_url=utils.url,
        options=SyncClientOptions(postgrest_client_timeout=60000),
    )
    return client


def check_if_id_supabase(
    row_id: str, ignore_old: bool, site_to_scrape: list[str]
) -> list[str]:
    site_to_scrape = deepcopy(site_to_scrape)
    if not ignore_old:
        return site_to_scrape
    client = get_session()
    response = (
        client.table("Vehicles")
        .select("id", "leboncoin", "lacentrale")
        .eq("id", row_id)
        .execute()
    )
    if not response.data:
        return site_to_scrape
    record = response.data[0]
    if record.get("leboncoin"):
        site_to_scrape.remove("leboncoin") if "leboncoin" in site_to_scrape else None
    if record.get("lacentrale"):
        site_to_scrape.remove("lacentrale") if "lacentrale" in site_to_scrape else None
    return site_to_scrape


def start_services(
    mileage_plus_minus: int,
    ignore_old: bool,
    sites_to_scrape: list[str],
    dev: bool = True,
    car_id: Optional[Union[str, int]] = None,
):
    client = get_session()
    try:
        if dev:
            df = pd.read_excel(OUT_FILE, header=None).sample(1000)
        else:
            df = pd.read_excel(OUT_FILE, header=None)
            print(f"Total: {len(df)}")

        new_columns = []
        for col in df.columns.to_list():
            new_columns.append(utils.numeric_to_alphabetic_column_name(int(col)))
        df.columns = new_columns
        df.fillna(value=0, inplace=True)
        for row_id in range(len(df)):
            car_dict = utils.get_row_dict(df, row_id)
            if (car_id) and (car_dict["id"] != car_id):
                continue

            print(f"Car Info - {car_dict}")
            updated_sites_to_scrape = check_if_id_supabase(
                car_dict["id"], ignore_old=ignore_old, site_to_scrape=sites_to_scrape
            )
            print(f"ID is not scraped by - {updated_sites_to_scrape}")

            # Verifying which to scrape from and submitting the tasks to the thread pool
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = []
                if not sites_to_scrape:
                    for func in domain_functions:
                        future = executor.submit(
                            domain_functions[func],
                            car_dict,
                            mileage_plus_minus,
                        )
                        futures.append(future)
                else:
                    for site_to_scrape in updated_sites_to_scrape:
                        if site_to_scrape in domain_functions:
                            future = executor.submit(
                                domain_functions[site_to_scrape],
                                car_dict,
                                mileage_plus_minus,
                            )
                            futures.append(future)
                # get the future results
                for future in futures:
                    future.result()
            # verify status
            if (row_id + 1) == len(df):
                stats = "success"
                stopped_at = datetime.now().isoformat()
            else:
                stopped_at = None
                stats = "running"

            client.table("Status").update(
                {
                    "id": 1,
                    "status": stats,
                    "stopped_at": stopped_at,
                    "total_completed": row_id + 1,
                    "total_running": len(df),
                }
            ).eq("site", sites_to_scrape[0]).execute()

    except (KeyboardInterrupt, Exception) as e:
        print(f"Error: {str(e)}")
        client.table("Status").update(
            {
                "id": 1,
                "status": "failed",
                "stopped_at": datetime.now().isoformat(),
            }
        ).eq("site", sites_to_scrape[0]).execute()
        raise e


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ArgumentParser doit être dans ce bloc pour éviter les conflits
# quand le module est importé par FastAPI ou Celery
if __name__ == "__main__":
    from argparse import ArgumentParser

    args = ArgumentParser()
    args.add_argument("--mileage-plus-minus", type=int, default=10000)
    args.add_argument("--dev", action="store_true")
    args.add_argument("--ignore-old", action="store_true")
    args.add_argument("--sites-to-scrape", type=str, default="leboncoin:lacentrale")
    args.add_argument("--car-id", type=int, default=None)
    parsed_args = args.parse_args()
    print(parsed_args)

    start_services(
        parsed_args.mileage_plus_minus,
        dev=parsed_args.dev,
        ignore_old=parsed_args.ignore_old,
        sites_to_scrape=parsed_args.sites_to_scrape.split(":"),
        car_id=parsed_args.car_id,
    )

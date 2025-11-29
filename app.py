import os
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional, Union

import aiofiles
import pandas as pd
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from postgrest.types import CountMethod
from supabase import (
    AuthApiError,
    Client,
    create_client,
)

from config import config
from services import autoscout24, lacentrale, leboncoin
from utilities import utils

OUT_FILE = Path(config.UPLOAD_FILE)
session_deps = Depends()
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


@utils.runner
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
                if not sites_to_scrape:
                    for func in domain_functions:
                        executor.submit(
                            domain_functions[func],
                            car_dict,
                            mileage_plus_minus,
                        )
                else:
                    for site_to_scrape in updated_sites_to_scrape:
                        if site_to_scrape in domain_functions:
                            executor.submit(
                                domain_functions[site_to_scrape],
                                car_dict,
                                mileage_plus_minus,
                            )

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
            ).eq("id", 1).execute()

    except Exception as e:
        print(f"Error: {e}")
        client.table("Status").update(
            {
                "id": 1,
                "status": "failed",
                "stopped_at": datetime.now().isoformat(),
            }
        ).eq("id", 1).execute()
        raise e


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login")
def login(
    client: Annotated[Client, Depends(get_session)],
    email: str,
    password: str,
):
    try:
        response = client.auth.sign_in_with_password(
            credentials={
                "email": email,
                "password": password,
            }
        )
        return {
            "message": "Login successful",
            "details": jsonable_encoder(response),
        }
    except AuthApiError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )


@app.get("/get_all_cars")
def get_all_cars(
    # access_token: str,
    # refresh_token: str,
    client: Annotated[Client, Depends(get_session)],
    offset: int = 0,
    limit: int = 20,
    cut_off_price: int = 500,
    domain: str | None = None,
    percentage_limit: int = 95,
):
    try:
        # auth = client.auth.set_session(
        #     access_token=access_token,
        #     refresh_token=refresh_token,
        # )
        stmt = (
            client.table("Vehicles")
            .select("*, comparisons(*)", count=CountMethod.exact)
            .limit(limit)
            .offset(offset)
            .order(
                "matching_percentage",
                desc=True,
                foreign_table="comparisons",
            )
        )
        if domain:
            stmt = stmt.eq("comparisons.domain", domain)
        response = stmt.execute()
        vehicles = []
        for vehicle in response.data:
            comparison_prices = [x["price"] for x in vehicle["comparisons"]]
            comparison_prices = [0] if not comparison_prices else comparison_prices
            vehicle["lowest_price"] = min(comparison_prices)
            vehicle["average_price"] = sum(comparison_prices) / len(comparison_prices)
            avg_price = get_avg_price_based_on_domain(
                vehicle["comparisons"],
                percentage_limit,
            )
            vehicle["average_price_based_on_best_match"] = avg_price
            vehicle["price_difference_with_avg_price"] = (
                avg_price - vehicle["price_with_tax"]
            )

            if vehicle["price_with_tax"] < avg_price:
                vehicle["card_color"] = "green"
            elif abs(vehicle["price_with_tax"] - avg_price) >= cut_off_price:
                vehicle["card_color"] = "red"
            else:
                vehicle["card_color"] = "yellow"
            best_match_cars = sorted(
                vehicle["comparisons"],
                key=lambda x: x["matching_percentage"],
                reverse=True,
            )
            vehicle["best_match_percentage"] = 0
            vehicle["best_match_link"] = None
            if best_match_cars:
                best_match_car = best_match_cars[0]
                vehicle["best_match_percentage"] = best_match_car.get(
                    "matching_percentage"
                )
                vehicle["best_match_link"] = best_match_car.get("link")

            vehicles.append(vehicle)  # 2091556
        return {
            # "session": jsonable_encoder(auth),
            "details": jsonable_encoder(vehicles),
            "total": response.count,
        }
    except AuthApiError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scrape_status")
def get_status(
    # access_token: str,
    # refresh_token: str,
    client: Annotated[Client, Depends(get_session)],
):
    try:
        # auth = client.auth.set_session(
        #     access_token=access_token,
        #     refresh_token=refresh_token,
        # )
        response = client.table("Status").select("*").execute()
        return {
            # "session": jsonable_encoder(auth),
            "details": jsonable_encoder(response),
        }
    except AuthApiError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Crée le dossier si absent


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    # 1. Vérifier le type du fichier
    allowed_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ]
    print("Uploaded file content type:", file.content_type)

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed."
        )

    # 2. Lire le contenu
    try:
        content = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")

    # 3. Nom du fichier
    filename = "25630.xlsx"
    file_path = UPLOAD_DIR / filename

    # 4. Sauvegarde locale
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file locally: {e}",
        )

    return {
        "message": "File uploaded successfully",
        "filename": filename,
        "path": str(file_path),
    }


if __name__ == "__main__":
    start_services(
        10000,
        dev=False,
        ignore_old=True,
        sites_to_scrape=["lacentrale"],
        car_id=None,
    )


# Try to set up the api on the server.

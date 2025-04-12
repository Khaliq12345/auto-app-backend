import pandas as pd
from supabase import Client, create_client
from model.model import Car
from fastapi.encoders import jsonable_encoder
from datetime import datetime
import traceback
from config import config
import os
from selectolax.parser import Node

url = config.SUPABASE_URL
supabase_key = config.SUPABASE_KEY
fuel_types = {
    1: "Benzin",
    2: "Diesel",
    3: "Autogas",
    4: "Erdgas",
    6: "Elektro",
    7: "Hybrid",
    8: "Wasserstoff",
    9: "Ethanol",
    10: "Hybrid-Diesel",
    11: "Bi-Fuel",
    0: "Andere",
}


def get_text(node: Node | None):
    value = node.text(strip=True, separator=" ") if node else None
    value = "".join([x.strip() for x in value.splitlines()]) if value else None
    return value


def drop_duplicate_cars(lst):
    seen = set()
    new_lst = []
    for x in lst:
        if x["id"] not in seen:
            seen.add(x["id"])
            new_lst.append(x)
    return new_lst


def get_row_dict(df: pd.DataFrame, row_id: int):
    print(f"Getting row dict of - {row_id}")
    row_raw_dict = df.iloc[row_id].to_dict()
    row = {}
    row["id"] = row_raw_dict[1]
    row["make"] = row_raw_dict[3]
    row["model"] = row_raw_dict[4]
    row["version"] = row_raw_dict[288]
    row["color"] = row_raw_dict[397]
    row["mileage"] = row_raw_dict[9]
    row["fuel_type"] = row_raw_dict[109]
    row["price"] = row_raw_dict[10]
    return row


def save_to_db(data: dict | list[dict], table: str):
    client: Client = create_client(supabase_key=supabase_key, supabase_url=url)
    client.table(table).upsert(data).execute()
    return True


def parse_and_save(car_dict: dict, cars: list[Car]):
    car_dict["updated_at"] = datetime.now().isoformat()
    car_dict["fuel_type"] = fuel_types[car_dict["fuel_type"]]
    jsoned_cars = jsonable_encoder(cars)
    compared_car_dicts = drop_duplicate_cars(jsoned_cars)
    if compared_car_dicts:
        save_to_db(car_dict, "Vehicles")
        save_to_db(compared_car_dicts, "comparisons")


def runner(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            log_path = "/logs/error_log.txt"
            if not os.path.exists(log_path):
                with open(log_path, "w") as f:
                    pass
            with open(log_path, "a") as error_file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                error_file.write(f"Time {timestamp}:\n")
                error_file.write(f"Error type: {type(e).__name__}\n")
                error_file.write(f"Error message: {str(e)}\n")
                error_file.write("Traceback:\n")
                error_file.write(traceback.format_exc())
                error_file.write("-" * 50 + "\n")

    return wrapper

import pandas as pd
from supabase import Client, create_client
from model.model import Car
from fastapi.encoders import jsonable_encoder
from datetime import datetime
import traceback
from config import config

url = config.SUPABASE_URL
supabase_key = config.SUPABASE_KEY


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
    return row


def save_to_db(data: dict | list[dict], table: str):
    client: Client = create_client(supabase_key=supabase_key, supabase_url=url)
    client.table(table).upsert(data).execute()
    return True


def parse_and_save(car_dict: dict, cars: list[Car]):
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
            car_dict: dict = args[0]
            with open("./error_log.txt", "a") as error_file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                error_file.write(
                    f"[{timestamp}] Error processing car_dict {car_dict.get('id', 'unknown')}:\n"
                )
                error_file.write(f"Error type: {type(e).__name__}\n")
                error_file.write(f"Error message: {str(e)}\n")
                error_file.write("Traceback:\n")
                error_file.write(traceback.format_exc())
                error_file.write("-" * 50 + "\n")

    return wrapper

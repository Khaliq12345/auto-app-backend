import pandas as pd
from supabase import Client, create_client
from model.model import Car
from fastapi.encoders import jsonable_encoder
from datetime import datetime
import traceback
from config import config
import os
from selectolax.parser import Node
from dateparser import parse
import string


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


def numeric_to_alphabetic_column_name(n: int) -> str:
    if n < 0:
        raise ValueError("Column index must be non-negative")

    result = ""
    while True:
        n, remainder = divmod(n, 26)
        result = string.ascii_uppercase[remainder] + result
        if n == 0:
            break
        n -= 1  # Adjust for 0-based indexing
    return result


def map_equipment(row_raw_dict: dict, key: str) -> bool:
    try:
        return True if int(row_raw_dict.get(key, 0)) == 1 else False
    except (ValueError, TypeError):
        return None


def get_row_dict(df: pd.DataFrame, row_id: int):
    print(f"Getting row dict of - {row_id}")
    row_raw_dict = df.iloc[row_id].to_dict()
    row = {}

    # Basic fields
    row["id"] = row_raw_dict["B"]
    row["make"] = row_raw_dict["D"]
    row["model"] = row_raw_dict["E"]
    row["version"] = row_raw_dict["KC"]
    row["color"] = row_raw_dict["OH"]
    row["mileage"] = row_raw_dict["J"]
    row["fuel_type"] = row_raw_dict["DF"]
    row["price_with_no_tax"] = row_raw_dict["K"]
    row["price_with_tax"] = float(row_raw_dict["K"]) * 1.19
    row["boite_de_vitesse"] = (
        int(row_raw_dict.get("DG")) if row_raw_dict.get("DG") else None
    )

    # Parse date for year
    try:
        date = parse(row_raw_dict["I"])
        row["year_from"] = date.year
        row["year_to"] = date.year
    except (ValueError, TypeError):
        row["year_from"] = None
        row["year_to"] = None

    # Equipment fields: Set to French equipment name if value is 1, else None
    row["camera_360"] = map_equipment(row_raw_dict, "JY")
    row["attelage"] = map_equipment(row_raw_dict, "AI")
    row["bluetooth"] = map_equipment(row_raw_dict, "FS")
    row["aide_stationnement_avant"] = map_equipment(
        row_raw_dict,
        "GR",
    )
    row["radar_de_recul"] = map_equipment(row_raw_dict, "GS")
    row["camera_de_recul"] = map_equipment(row_raw_dict, "GT")
    row["kit_mains_libres"] = map_equipment(row_raw_dict, "FX")
    row["limiteur_de_vitesse"] = map_equipment(row_raw_dict, "KX")
    row["affichage_tete_haute"] = map_equipment(row_raw_dict, "FW")
    row["gps"] = map_equipment(row_raw_dict, "AL")
    row["toit_panoramique"] = map_equipment(row_raw_dict, "GD")
    row["toit_ouvrant"] = map_equipment(row_raw_dict, "AM")
    row["sieges_chauffants"] = map_equipment(row_raw_dict, "CX")
    row["assistant_changement_voie"] = map_equipment(row_raw_dict, "IV")
    row["assistant_maintien_voie"] = map_equipment(row_raw_dict, "IQ")
    cuir_value = row_raw_dict.get("FA")
    row["cuir"] = True if cuir_value == 1 else False

    four_by_four = row_raw_dict.get("AP")
    row["4x4"] = True if four_by_four == 1 else False

    row["car_url"] = (
        f"https://auto-brass.com/decouvrir-les-occasions?freier_text={row_raw_dict.get('B')}"
    )

    return row


def save_to_db(data: dict | list[dict], table: str):
    client: Client = create_client(supabase_key=supabase_key, supabase_url=url)
    client.table(table).upsert(data).execute()
    return True


def parse_and_save(car_dict: dict, cars: list[Car]):
    car_dict["updated_at"] = datetime.now().isoformat()
    if str(car_dict["fuel_type"]).isdigit():
        car_dict["fuel_type"] = fuel_types[car_dict["fuel_type"]]
    # selecting fields to save
    car_to_save_dict = {}
    fields = [
        "id",
        "make",
        "model",
        "version",
        "color",
        "mileage",
        "fuel_type",
        "price_with_tax",
        "price_with_no_tax",
        "year_from",
        "year_to",
        "car_url",
        "updated_at",
    ]
    for field in fields:
        car_to_save_dict[field] = car_dict[field]

    # send to supabase
    jsoned_cars = jsonable_encoder(cars)
    compared_car_dicts = drop_duplicate_cars(jsoned_cars)
    if compared_car_dicts:
        save_to_db(car_to_save_dict, "Vehicles")
        save_to_db(compared_car_dicts, "comparisons")


def runner(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            log_path = config.ERROR_FILE
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

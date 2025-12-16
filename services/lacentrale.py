from time import sleep
from typing import Any
from urllib.parse import ParseResult, urlencode, urlunparse

import httpx

from browser import client, get_the_listing_html, types
from config import config
from model.model import Car, Filter
from utilities import utils

domain = "https://www.lacentrale.fr/"

lacentrale_fuel_dict = {
    0: "OTHER",  # Autre (Other), including duplicate
    1: "ESSENCE",  # Essence (Gasoline)
    2: "DIESEL",  # Diesel
    3: "BIO_ESSENCE_GPL",  # GPL (Autogas), including duplicate
    6: "ELECTRIC",  # Électrique (Electric)
    7: "HYBRID",  # Hybride variations
    9: "ETHANOL",  # Éthanol (Ethanol), including duplicate
}

params = {
    "aggregations": "EXTERNAL_COLOR,MAKE_MODEL_COMMERCIAL_NAME,VERSION",
    "families": "AUTO,UTILITY",
    "makesModelsCommercialNames": "CUPRA",
}


def extract_10_cars(
    json_or_soup: Any, domain: str, parent_car_id: int, updated_at: str
) -> list[Car]:
    cars = []
    hits = json_or_soup["hits"]
    for hit in hits:
        if not hit:
            continue
        if isinstance(hit, list):
            hit = hit[0]
        item = hit.get("item")
        if not item:
            continue
        car = item.get("vehicle")
        name = car.get("detailedModel")
        price = item.get("price")
        deal_type = item.get("goodDealBadge")
        link = "https://www.lacentrale.fr/auto-occasion-annonce-69116222960.html"
        image = item.get("photoUrl")
        mileage = car.get("mileage")
        car_metadata = car.get("version")
        fuel_type = car.get("energy")
        boite_de_vitesse = car.get("gearbox")
        parent_car_id = parent_car_id
        cars.append(
            Car(
                id="",
                name=name,
                price=price,
                deal_type=deal_type,
                link=link,
                image=image,
                mileage=mileage,
                car_metadata=car_metadata,
                domain=domain,
                fuel_type=fuel_type,
                boite_de_vitesse=boite_de_vitesse,
                parent_car_id=parent_car_id,
                updated_at=updated_at,
                matching_percentage=0.0,
                matching_percentage_reason=None,
            )
        )

    return cars


def user_prompt(models, colors, versions, fuel_types, target_dict):
    return f"""
        You are an AI assistant tasked with generating a dictionary that matches a provided vehicle specification dictionary, using only values from specified lists and dictionaries. I will provide you with:
        - A list of vehicle models.
        - A list of colors.
        - A list of versions.
        - A dictionary of fuel types where numbers are keys and fuel codes are values.
        - A target dictionary to compare against.

        Your task is to:
        1. Compare each key-value pair in the target dictionary with the provided options.
        2. Create a new dictionary where:
        - The keys are the same as the target dictionary ('make', 'model', 'version', 'color', 'mileage', 'fuel_type').
        - The values are selected from the provided options (models, colors, versions, fuel types) that most closely match the target dictionary's values.
        - If no exact match exists for a key's value in the provided options, use None for that key, unless the original value is explicitly allowed (e.g., 'make' or 'mileage' when no alternatives are given).
        3. Ensure all values in the output dictionary come from the provided lists/dictionary, except where explicitly noted.

        Here are the inputs:

        - Models: {models}
        - Colors: {colors}
        - Versions: {versions}
        - Fuel types: {fuel_types}
        - Target dictionary: {target_dict}

        Rules:
        - For 'make', use the provided value ('CUPRA') if no alternative makes are listed, as it's implied to be valid.
        - For 'model', select the closest matching model name from the models list, ignoring extra details not in the list.
        - For 'version', match to a string in the versions list; if the target value (e.g., an integer) isn't present as a string, use None.
        - For 'color', match to the closest color in the colors list, translating if necessary (e.g., 'grau' to 'gris' for gray).
        - For 'mileage', use the provided value if no mileage options are given.
        - For 'fuel_type', use the string value from the fuel types dictionary that corresponds to the provided key (e.g., 6 → 'elec').

        Output the resulting dictionary in Python dictionary format. Provide a brief explanation of your choices.

        Please process this and return the matched dictionary.
        """


def get_prompt_from_make(input_dict: dict) -> str:
    print("Sending requests to get the models and versions")
    params["makesModelsCommercialNames"] = input_dict["make"]
    print(params)
    headers = utils.get_json_from_local("./uploads/Lacentrale_Headers.json")
    proxy = (
        f"http://{config.PROXY_USERNAME}:{config.PROXY_PASSWORD}@fr.decodo.com:40000"
    )
    response = httpx.get(
        "https://recherche.lacentrale.fr/v5/aggregations",
        params=params,
        headers=headers,
        proxy=proxy,
    )
    response.raise_for_status()
    print(f"Filter - {response.status_code}")
    json_data = response.json()
    all_models = []
    all_colors = []
    all_versions = []
    if json_data["total"]:
        # Get all the models based on the make
        models = response.json()["aggs"]["vehicle.makeModelCommercialName"][0]["agg"]
        for model in models:
            # for inner_model in model["agg"]:
            all_models.append(model["key"])
        # get all colors available
        colors = response.json()["aggs"]["vehicle.externalColor"]
        for color in colors:
            all_colors.append(color["key"])
        if input_dict.get("version"):
            # get all version associated to the make
            versions = response.json()["aggs"]["vehicle.version"]
            for version in versions:
                all_versions.append(version["key"])

    return user_prompt(
        all_models, all_colors, all_versions, lacentrale_fuel_dict, input_dict
    )


def get_options(car_dict: dict):
    options = []
    if car_dict.get("toit_ouvrant"):
        options.append("TOIT_OUVRANT")
    if car_dict.get("camera_de_recul"):
        options.append("CAMERA_RECUL")
    if car_dict.get("cuir"):
        options.append("CUIR")
    if car_dict.get("toit_panoramique"):
        options.append("TOIT_PANORAMIQUE")
    if car_dict.get("attelage"):
        options.append("ATTELAGE")
    if car_dict.get("gps"):
        options.append("GPS")
    if car_dict.get("radar_de_recul"):
        options.append("RADAR_RECUL")
    if car_dict.get("bluetooth"):
        options.append("BLUETOOTH")
    return options


def get_filter_url(params: dict, car_dict: dict, car_filter: Filter) -> str:
    # build the filter url
    params["makesModelsCommercialNames"] = f"{car_filter.make}:{car_filter.model}"
    params["yearMax"] = car_filter.year_to
    params["yearMin"] = car_filter.year_from
    params["energies"] = car_filter.fuel_type
    if car_dict.get("boite_de_vitesse"):
        boite_de_vitesse = car_dict.get("boite_de_vitesse")
        match boite_de_vitesse:
            case 3:
                params["gearbox"] = "AUTO"
            case 1:
                params["gearbox"] = "MANUAL"
    query_string = urlencode(params)
    filter_url = urlunparse(
        ParseResult(
            scheme="https",
            netloc="mobile-app.lacentrale.fr",
            path="/api/v1/listing",
            params="",
            query=query_string,
            fragment="",
        )
    )
    return filter_url


def get_filter_urls(car_dict: dict, mileage_plus_minus: int = 10000):
    print("CAR - ", car_dict)
    print("Generating Filter url based on row dict")
    prompt_to_use = get_prompt_from_make(car_dict)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt_to_use,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Filter,
            system_instruction="You are an Intelligent Html Parser Bot, that prioritze data intergrity.",
        ),
    )
    car_filter: Filter = response.parsed
    km_from = abs(round(car_filter.mileage - mileage_plus_minus))
    km_to = abs(round(car_filter.mileage + mileage_plus_minus))
    equipments = get_options(car_dict)

    # build the filter url
    filter_urls = []
    params = {}
    filter_urls.append(
        get_filter_url(
            params,
            car_dict,
            car_filter,
        )
    )
    params["mileageMax"] = km_to
    params["mileageMin"] = km_from
    filter_urls.append(
        get_filter_url(
            params,
            car_dict,
            car_filter,
        )
    )
    params["customerFamilyCodes"] = "PROFESSIONNEL"
    filter_urls.append(
        get_filter_url(
            params,
            car_dict,
            car_filter,
        )
    )
    if car_dict.get("4x4"):
        params["categories"] = 47
        filter_urls.append(
            get_filter_url(
                params,
                car_dict,
                car_filter,
            )
        )
    if equipments:
        for idx in range(len(equipments)):
            params["options"] = ",".join(equipments[0 : idx + 1])
            filter_urls.append(
                get_filter_url(
                    params,
                    car_dict,
                    car_filter,
                )
            )
    return filter_urls


def main(car_dict: dict, mileage_plus_minus):
    make = car_dict["make"]
    if make == "VW":
        print("MAKE ", make)
        make = "VOLKSWAGEN"
    elif make == "DS AUTOMOBILES":
        make = "DS"
    car_dict["make"] = make
    filter_urls = get_filter_urls(car_dict, mileage_plus_minus)
    filter_urls.reverse()
    cars = []
    for idx, filter_url in enumerate(filter_urls):
        print(f"Filter url - {filter_url}")
        # get the listing page
        is_basic_filter = idx == len(filter_urls) - 1
        cars = get_the_listing_html(
            car_dict,
            filter_url,
            domain,
            car_dict["id"],
            extract_10_cars,
            is_basic_filter=is_basic_filter,
        )
        print(f"Total cars - {len(cars)}")
        if cars:
            break
        sleep_secs = 3
        print(f"Sleeping for {sleep_secs} seconds")
        sleep(sleep_secs)

    utils.parse_and_save(car_dict, cars, "lacentrale")


if __name__ == "__main__":
    pass

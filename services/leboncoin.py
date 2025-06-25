from copy import deepcopy
import httpx
from browser import client, types
from model.model import Filter, Car
from utilities import utils
from browser import get_the_listing_html

domain = "https://www.leboncoin.fr/"

leboncoin_fuel_dict = {
    0: "5",  # Autre (Other), including duplicate
    1: "1",  # Essence (Gasoline)
    2: "2",  # Diesel
    3: "3",  # GPL (Autogas), including duplicate
    6: "4",  # Électrique (Electric)
    7: "6",  # Hybride variations
    8: "9",  # Hydrogen
    4: "7",  # GNV
}


cookies = {
    "FPID": "FPID2.2.fcEcGj6pHxZpLI%2BdDPLraSVSQejQxpJAPckhYlwp3m8%3D.1743343323",
    "__Secure-Install": "a7629a20-7b3e-40a6-8dfa-cbde4fa5b3c2",
    "deviceId": "ae44ef1e-73fd-45bf-977a-1d677289e73d",
    "FPAU": "1.2.1452550628.1748679201",
    "cnfdVisitorId": "936b967f-ce9f-4b07-99c8-f5fa47a4c747",
    "_gcl_au": "1.1.1937787640.1750861704",
    "lg": "13",
    "_ga": "GA1.1.218914528.1750861705",
    "_pcid": "%7B%22browserId%22%3A%22mcc1ulwcbcvggptf%22%2C%22_t%22%3A%22ms0gs7j1%7Cmcc1uq71%22%7D",
    "_pctx": "%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbCAAYA5hADsAKwDMAH34BjBQEYwAR3HSQAXyA",
    "ry_ry-l3b0nco_so_realytics": "eyJpZCI6InJ5X0FCRkY3MTRFLTE1MDItNDY1OS05MDFCLUVFQUVEMkZCQTBCQSIsImNpZCI6bnVsbCwib3JpZ2luIjp0cnVlLCJyZWYiOm51bGwsImNvbnQiOm51bGwsIm5zIjp0cnVlLCJzYyI6Im9rIiwic3AiOm51bGx9",
    "ry_ry-l3b0nco_realytics": "eyJpZCI6InJ5X0FCRkY3MTRFLTE1MDItNDY1OS05MDFCLUVFQUVEMkZCQTBCQSIsImNpZCI6bnVsbCwiZXhwIjoxNzgyMzk3NzA0NTQ3LCJjcyI6MX0%3D",
    "utag_main": "v_id:0197a77d66b9008e931ab6adddd804065002d05d00ac2$_sn:1$_ss:0$_pn:2%3Bexp-session$_st:1750863505626$ses_id:1750861702841%3Bexp-session",
    "_ga_Z707449XJ2": "GS2.1.s1750861705$o1$g1$t1750861705$j60$l0$h291290784",
    "FPLC": "5RnyhW3GT7wKRkwylz%2BC5t2hz67pj3s2v%2Fmziy%2FJ523Dd5QvnMg25W38R4B34kEhwhyuTx%2FDbzPSUeW04czXbaLF1EAnq9HmYJ2wwHy2quJ1XCAyKcPd7ZLchG7HrA%3D%3D",
    "datadome": "pJ72dDuxZnWp5CCjw2qgFUCv043jhd_LD0eR1r6TkjzShxFDjY6jvANfQzCiF1vtCb1Rp9xzWtRANVZjVDGXR7DebAGYrCMVGQu0GpSCmf1qWPBLbHaKzrRG3zsHJmBM",
}

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.6",
    "api_key": "ba0c2dad52b3ec",
    "content-type": "application/json",
    "origin": "https://www.leboncoin.fr",
    "priority": "u=1, i",
    "referer": "https://www.leboncoin.fr/",
    "sec-ch-ua": '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
}


def extract_10_cars(
    ads: list[dict], domain: str, parent_car_id: int, updated_at: str
) -> list[Car] | None:
    cars = []
    for ad in ads:
        name = ad.get("subject", "")
        prices = ad.get("price", [])
        price = prices[0] if prices else None
        deal_type = None
        link = ad.get("url", None)
        images = ad.get("images", {})
        thumbs = images.get("urls_large", [])
        image = thumbs[0] if thumbs else None
        mileage = None
        fuel_type = None
        boite_de_vitesse = None
        attributes = ad.get("attributes", [])
        sub_names = []
        if attributes:
            for attribute in attributes:
                match attribute.get("key", ""):
                    case "mileage":
                        mileage = attribute.get("value", 0)
                        mileage = float(mileage) if mileage else 0
                    case "fuel":
                        fuel_type = attribute.get("value_label", None)
                    case "gearbox":
                        boite_de_vitesse = attribute.get("value_label", None)
                    case _:
                        meta = f"{attribute.get('key_label')} - {attribute.get('value_label')}"
                        sub_names.append(meta)
        sub_name = "; ".join(sub_names)

        cars.append(
            Car(
                id="",
                name=name,
                price=price,
                deal_type=deal_type,
                link=link,
                image=image,
                mileage=mileage,
                car_metadata=sub_name,
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


def user_prompt(models, fuel_types, target_dict):
    return f""" 
        You are an AI assistant tasked with generating a dictionary that matches a provided vehicle specification dictionary,
        using only values from specified lists and dictionaries. I will provide you with:
        - A list of vehicle models.
        - A dictionary of fuel types where numbers are keys and fuel codes are values.
        - A target dictionary to compare against.

        Your task is to:
        1. Compare each key-value pair in the target dictionary with the provided options.
        2. Create a new dictionary where:
        - The keys are the same as the target dictionary ('make', 'model', 'mileage', 'fuel_type').
        - The values are selected from the provided options (models, fuel types) that most closely match the target dictionary's values.
        - If no exact match exists for a key's value in the provided options, use None for that key, unless the original value is explicitly allowed (e.g., 'make' or 'mileage' when no alternatives are given).
        3. Ensure all values in the output dictionary come from the provided lists/dictionary, except where explicitly noted.

        Here are the inputs:

        - Models: {models}
        - Fuel types: {fuel_types}
        - Target dictionary: {target_dict}

        Rules:
        - For 'make', use the provided value ('CUPRA') if no alternative makes are listed, as it's implied to be valid.
        - For 'model', select the closest matching model name from the models list, ignoring extra details not in the list.
        - For 'mileage', use the provided value if no mileage options are given.
        - For 'fuel_type', return the value and not the key of the fuel_type dict.

        Output the resulting dictionary in Python dictionary format. Provide a brief explanation of your choices.

        Please process this and return the matched dictionary.
        """


def get_prompt_from_make(input_dict: dict) -> str:
    json_data = {
        "filters": {
            "category": {
                "id": "2",
            },
            "enums": {
                "ad_type": [
                    "offer",
                ],
                "u_car_brand": [
                    input_dict["make"],
                ],
            },
        },
        "limit": 0,
        "limit_alu": 0,
        "sort_by": "relevance",
    }
    print("Sending requests to get the models")
    response = httpx.post(
        "https://api.leboncoin.fr/finder/search",
        headers=headers,
        json=json_data,
        cookies=cookies,
    )
    print(f"Filter - {response.status_code}")
    json_data = response.json()
    options = json_data.get("aggregations", {})
    if options:
        models = options.get("u_car_model", [])
        models = [model for model in models if model]

    return user_prompt(models, leboncoin_fuel_dict, input_dict)


def get_filter_url(params: dict, car_dict: dict, car_filter: Filter) -> dict:
    # build the filter url
    params = deepcopy(params)
    params["filters"]["enums"]["u_car_brand"] = [f"{car_filter.make}"]
    params["filters"]["enums"]["u_car_model"] = [f"{car_filter.model}"]
    params["filters"]["ranges"]["regdate"]["max"] = car_filter.year_to
    params["filters"]["ranges"]["regdate"]["min"] = car_filter.year_from
    params["filters"]["enums"]["fuel"] = [f"{car_filter.fuel_type}"]
    if car_dict.get("boite_de_vitesse"):
        boite_de_vitesse = car_dict.get("boite_de_vitesse")
        match boite_de_vitesse:
            case 3:
                params["filters"]["enums"]["gearbox"] = ["2"]
            case 1:
                params["filters"]["enums"]["gearbox"] = ["1"]
    return params


def get_filter_urls(car_dict: dict, mileage_plus_minus: int = 10000):
    print("Generating Filter url based on row dict")
    params = {
        "filters": {
            "category": {
                "id": "2",
            },
            "enums": {
                "ad_type": [
                    "offer",
                ],
            },
            "ranges": {
                "mileage": {},
                "regdate": {},
            },
        },
        "limit": 35,
        "limit_alu": 3,
        "sort_by": "relevance",
        "offset": 0,
        "extend": True,
        "listing_source": "direct-search",
    }
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=get_prompt_from_make(car_dict),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Filter,
            system_instruction="You are an Intelligent Html Parser Bot, that prioritze data intergrity.",
        ),
    )
    car_filter: Filter = response.parsed
    km_from = abs(round(car_filter.mileage - mileage_plus_minus))
    km_to = abs(round(car_filter.mileage + mileage_plus_minus))
    # build the filter url
    filters = []
    filters.append(
        get_filter_url(
            params,
            car_dict,
            car_filter,
        )
    )
    params["filters"]["ranges"]["mileage"]["min"] = km_from
    params["filters"]["ranges"]["mileage"]["max"] = km_to
    filters.append(
        get_filter_url(
            params,
            car_dict,
            car_filter,
        )
    )
    params["owner_type"] = "pro"
    filters.append(
        get_filter_url(
            params,
            car_dict,
            car_filter,
        )
    )
    if car_dict.get("4x4"):
        params["filters"]["enums"]["vehicle_type"] = ["4x4"]
        filters.append(
            get_filter_url(
                params,
                car_dict,
                car_filter,
            )
        )
    return filters


@utils.runner
def main(car_dict: dict, mileage_plus_minus) -> None:
    params = get_filter_urls(car_dict, mileage_plus_minus)
    params.reverse()
    cars = []
    for idx, param in enumerate(params):
        print(f"Filter url - {param}")
        # get the listing page
        is_basic_filter = idx == len(params) - 1
        response = httpx.post(
            "https://api.leboncoin.fr/finder/search",
            cookies=cookies,
            headers=headers,
            json=param,
        )
        response.raise_for_status()
        json_data = response.json()
        ads = json_data.get("ads", [])
        print(f"Total ads - {len(ads)}")
        cars = get_the_listing_html(
            car_dict,
            param,
            domain,
            car_dict["id"],
            extract_10_cars,
            is_basic_filter=is_basic_filter,
            skip_requests=True,
            ads=ads[:10],
        )
        print(f"Total cars - {len(cars)}")
        if cars:
            break
    utils.parse_and_save(car_dict, cars)

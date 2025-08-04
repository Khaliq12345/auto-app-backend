from urllib.parse import ParseResult, urlencode, urlunparse
import httpx
from selectolax.parser import HTMLParser
from browser import client, types
from model.model import Filter, Car
from utilities import utils
from browser import get_the_listing_html
from config.config import PROXY_PASSWORD, PROXY_USERNAME

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
    "__Secure-Install": "36ae2011-5d35-4273-9d08-d42eb458331f",
    "cnfdVisitorId": "6cefd47c-0d9b-4ce7-9bc9-34c913d0b90b",
    "didomi_token": "eyJ1c2VyX2lkIjoiMTk4NmE1ZmYtNjUzNi02OGEyLWJlMDEtNTBlOGQ5OWVhNjA1IiwiY3JlYXRlZCI6IjIwMjUtMDgtMDJUMTA6NDI6MTAuNjQzWiIsInVwZGF0ZWQiOiIyMDI1LTA4LTAyVDEwOjQyOjEyLjg3M1oiLCJ2ZW5kb3JzIjp7ImVuYWJsZWQiOlsiZ29vZ2xlIiwiYzpsYmNmcmFuY2UiLCJjOmdvb2dsZWFuYS00VFhuSmlnUiIsImM6cHVycG9zZWxhLTN3NFpmS0tEIiwiYzptNnB1YmxpY2ktdFhUWUROQWMiLCJjOmFmZmlsaW5ldCIsImM6c3BvbmdlY2VsbC1ueXliQUtIMiIsImM6dGlrdG9rLXJLQVlEZ2JIIiwiYzp6YW5veC1hWVl6NnpXNCIsImM6cGludGVyZXN0IiwiYzpwcmViaWRvcmctSGlqaXJZZGIiLCJjOmlnbml0aW9uby1MVkFNWmRuaiIsImM6ZGlkb21pIiwiYzpsYmNmcmFuY2UtSHkza1lNOUYiXX0sInB1cnBvc2VzIjp7ImVuYWJsZWQiOlsiZXhwZXJpZW5jZXV0aWxpc2F0ZXVyIiwibWVzdXJlYXVkaWVuY2UiLCJwZXJzb25uYWxpc2F0aW9ubWFya2V0aW5nIiwicHJpeCIsImRldmljZV9jaGFyYWN0ZXJpc3RpY3MiLCJjb21wYXJhaXNvLVkzWnkzVUV4IiwiZ2VvbG9jYXRpb25fZGF0YSJdfSwidmVuZG9yc19saSI6eyJlbmFibGVkIjpbImdvb2dsZSIsImM6cHVycG9zZWxhLTN3NFpmS0tEIl19LCJ2ZXJzaW9uIjoyLCJhYyI6IkRDS0FnQUZrQTl3Q1N3SWtnUlRBNmNDQmdFVkFKclFVR0FvUkJYT0N3WUZ0NExsZ1lSQUEuRENLQWdBRmtBOXdDU3dJa2dSVEE2Y0NCZ0VWQUpyUVVHQW9SQlhPQ3dZRnQ0TGxnWVJBQSJ9",
    "euconsent-v2": "CQVhVIAQVhVIAAHABBENB1FsAP_gAELgAAAAKENB7CfdQSFiUbJlAOtAYQxP4BAiogAABgABgwwBCBLAMIwEhGAIIADAAAACGBAAICBAAQBlCADAAAAAIAAAACAEAAAAARAAJiAAAEAAAmBICABICYAAAQAQgkiEAAEAgAIAAAogSEgAAAAAHAAAAAAAAAAAAAAAAAEAAAAAAAAAAgAAAAAACAAAAAAEAFAAAAAAAAAAAAAAAAAMAAAAAAAABBQiBeAAsAB4AFQAOAAeABAACQAFQAMoAaABqADwAIYATAAoQBcAF0AMQAfAA_ACEAEdAMoAywBogDnAHcAP2Ag4CEAEWAIxARwBHQDRAGvANoAj0BNoCj4FNAU2ArIBbAC8wGSAMnAZZA1cDWAIAgQvAjsBQgAMUABgACC2gwADAAEFtCAAGAAILaAA.f_wACFwAAAAA",
    "include_in_experiment": "true",
    "_ga": "GA1.1.1570886354.1754131333",
    "FPID": "FPID2.2.ON2v7dK1aWcr2RhsSQNJeFJAO8dDHLq0N%2BgXlbs1oWM%3D.1754131333",
    "FPAU": "1.2.1929399324.1754131334",
    "deviceId": "e7475994-8fbe-4025-8fb5-384271b1796f",
    "experiment_visitor_id": "e8b931b3-0a70-4c0b-bfda-ea44deb602e3",
    "_gcl_au": "1.1.357828164.1754131338",
    "FPLC": "dqEoY3XY3H4h3TGvRfOPJqcUc4PLfz%2F2uGPb5xo7pySiR9fP%2BctshiFoCnKMgZ1hS9C%2BYeaNhcp2DwQrIHZuyDGoWwVR8nmnkf7v%2Fp%2FK3%2Fqbx8cyaTpKRl0cz3Nzyg%3D%3D",
    "user_search_config": '{"owner_type":"pro"}',
    "_hjSessionUser_2783207": "eyJpZCI6ImE5MDM1OTM1LTVmMzAtNTNhOS05NDBhLWQ2Njk3OWQ0NTU1MCIsImNyZWF0ZWQiOjE3NTQxMzEzMzQ2NTgsImV4aXN0aW5nIjp0cnVlfQ==",
    "_pcid": "%7B%22browserId%22%3A%22mdvdqyefgoxu2yfe%22%2C%22_t%22%3A%22mtjsohqa%7Cmdvdr0ea%22%7D",
    "_pctx": "%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbfACsIlABYBHAEYAffqwBurGAAYoUkAF8gA",
    "lg": "9",
    "__gsas": "ID=663b8f9af9388491:T=1754207327:RT=1754207327:S=ALNI_MZs4JO4EEVJDS7sEm59bJIadUdcEA",
    "ry_ry-l3b0nco_realytics": "eyJpZCI6InJ5X0VGOTAzQ0U2LTFFQzktNDYzOS04MzNBLUY1NzZFNjVCQTlCRSIsImNpZCI6bnVsbCwiZXhwIjoxNzg1NjY3MzM4NDA1LCJjcyI6MX0%3D",
    "_fbp": "fb.1.1754207399461.156474195924338493",
    "_scid": "6iUW8A2nKR2Dg6U2tXAVKRs60nB4zRuY",
    "_ScCbts": "%5B%5D",
    "ivBlk": "n",
    "_sctr": "1%7C1754175600000",
    "_hjSession_2783207": "eyJpZCI6Ijk1Y2E4MWM1LTZiMDYtNGNlNi04MWZkLTc3ZmUwMWE4NzJlMCIsImMiOjE3NTQyNzQ1MzUxOTgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=",
    "ry_ry-l3b0nco_so_realytics": "eyJpZCI6InJ5X0VGOTAzQ0U2LTFFQzktNDYzOS04MzNBLUY1NzZFNjVCQTlCRSIsImNpZCI6bnVsbCwib3JpZ2luIjp0cnVlLCJyZWYiOm51bGwsImNvbnQiOm51bGwsIm5zIjp0cnVlLCJzYyI6Im9rIiwic3AiOm51bGx9",
    "_ga_Z707449XJ2": "GS2.1.s1754274534$o9$g1$t1754274535$j59$l0$h1156005454",
    "_scid_r": "5KUW8A2nKR2Dg6U2tXAVKRs60nB4zRuYcGgieA",
    "cto_bundle": "4MLeBl9FbUVLbFRBR1hoRjVkc0V1UnlqUURMUHZGa1NEUlpmJTJCTWcyVk4wZzBidTVLJTJGclg5VG5QVWxOcWVCR1FGdGRnbG91Z3lYMzh0aDhOY2ZXeGZlWHNLMjR2MHRqMUFlSmpOWkolMkZTSlBuZXh0OGo4cTkwdiUyQmhrTm00S1htZENjcDlLYmp6QVNWTVBud3lCS09sRyUyRjJkZDJMdiUyQjZ3UCUyRkMlMkJUdTM0RkJSaDdIYTFNJTNE",
    "__gads": "ID=aacc7c3b980ef105:T=1754207334:RT=1754274539:S=ALNI_MbkArq2M_cUnYFwLV1ZEZXIAP9Tfw",
    "__gpi": "UID=00001243a1aa4db2:T=1754207334:RT=1754274539:S=ALNI_MYTmGBVUQA82DutdqJJcnE5S1VGcg",
    "__eoi": "ID=6a69744913b00b24:T=1754207334:RT=1754274539:S=AA-AfjZjG2ffcw1fDjRmsFKHAx6I",
    "datadome": "fWZw_NbBZwAmF38ikc8hHClttGbYYxSwVeXqLZJOz_1bgOV7994nn6046ubik4kn9VPdKseiSzZer15xd0C_AwFglxoDTDaIY_mt~CyyuFif8XDTCWRK1KVgnORRsPtA",
}

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "api_key": "ba0c2dad52b3ec",
    "content-type": "application/json",
    "origin": "https://www.leboncoin.fr",
    "priority": "u=1, i",
    "referer": "https://www.leboncoin.fr/recherche?category=2&u_car_brand=AUDI&owner_type=pro&page=2",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "x-lbc-experiment-id": "e8b931b3-0a70-4c0b-bfda-ea44deb602e3",
    "x-lbc-visitor-id": "6cefd47c-0d9b-4ce7-9bc9-34c913d0b90b",
}


def extract_10_cars(
    soup: HTMLParser, domain: str, parent_car_id: int, updated_at: str
) -> list[Car] | None:
    cars = []
    ads = soup.css('li[class="styles_adCard__JzKik"]')
    for ad in ads[:10]:
        article = ad.css_first("article")
        if article.attributes.get("data-test-id") != "ad":
            continue
        name = article.attributes.get("aria-label")
        price = 0
        price_node = article.css_first('p[data-test-id="price"] span')
        if price_node:
            price = (
                price_node.text()
                .replace(" ", "")
                .replace("€", "")
                .replace("\u202f", "")
                .strip()
            )
            try:
                price = float(price)
            except Exception as _:
                price = 0
        deal_type = ""
        deals = article.css('span[data-spark-component="tag"]')
        for deal in deals:
            deal_type += f" {deal.text()}"
        deal_type = deal_type.strip()
        link = None
        link_node = article.css_first("a")
        if link_node:
            link = link_node.attributes.get("href")
            link = f"https://www.leboncoin.fr{link}"
        image = None
        image_node = article.css_first('picture source[type="image/jpeg"]')
        if image_node:
            image = image_node.attributes.get("srcset")
        mileage = None
        fuel_type = None
        boite_de_vitesse = None
        params_node = article.css_first('div[data-test-id="ad-params-light"]')
        if params_node:
            params = params_node.text(strip=True).split("·")
            for idx, param in enumerate(params):
                if idx == 1:
                    mileage = (
                        param.replace(" ", "")
                        .replace("km", "")
                        .replace("\u202f", "")
                        .strip()
                    )
                    try:
                        mileage = float(mileage)
                    except Exception as _:
                        mileage = None
                elif idx == 2:
                    fuel_type = param
                elif idx == 3:
                    boite_de_vitesse = param
        store_name = ""
        store_node = article.css_first('p[data-test-id="pro-store-name"]')
        if store_node:
            store_name = store_node.text()
            if "Auto Brass".lower() in store_name.lower():
                continue
        sub_name = None
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
    print(f"Models - {models}")
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
    proxy = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@fr.decodo.com:40000"
    response = httpx.post(
        "https://api.leboncoin.fr/finder/search",
        headers=headers,
        json=json_data,
        cookies=cookies,
        proxy=proxy,
    )
    print(f"Filter - {response.status_code}")
    json_data = response.json()
    options = json_data.get("aggregations", {})
    if options:
        models = options.get("u_car_model", [])
        models = [model for model in models if model]
        print("There's options")
        return user_prompt(models, leboncoin_fuel_dict, input_dict)
    print("No options")


def get_filter_url(params: dict, car_dict: dict, car_filter: Filter) -> str:
    # build the filter url
    params["category"] = "2"
    params["u_car_brand"] = car_filter.make
    params["u_car_model"] = car_filter.model
    if (car_filter.year_from) and (car_filter.year_to):
        params["regdate"] = f"{car_filter.year_from}-{car_filter.year_to}"
    params["fuel"] = car_filter.fuel_type
    if car_dict.get("boite_de_vitesse"):
        boite_de_vitesse = car_dict.get("boite_de_vitesse")
        match boite_de_vitesse:
            case 3:
                params["gearbox"] = "2"
            case 1:
                params["gearbox"] = "1"
    query_string = urlencode(params)
    filter_url = urlunparse(
        ParseResult(
            scheme="https",
            netloc="www.leboncoin.fr",
            path="/recherche",
            params="",
            query=query_string,
            fragment="",
        )
    )
    return filter_url


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
    print("Before modeling")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=get_prompt_from_make(car_dict),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Filter,
                system_instruction="You are an Intelligent Html Parser Bot, that prioritze data intergrity.",
            ),
        )
    except Exception as e:
        print(f"error - {e}")
    print("Model response")
    car_filter: Filter = response.parsed
    km_from = abs(round(car_filter.mileage - mileage_plus_minus))
    km_to = abs(round(car_filter.mileage + mileage_plus_minus))
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

    params["mileage"] = f"{km_from}-{km_to}"
    filter_urls.append(get_filter_url(params, car_dict, car_filter))

    params["owner_type"] = "pro"
    filter_urls.append(
        get_filter_url(
            params,
            car_dict,
            car_filter,
        )
    )
    if car_dict.get("4x4"):
        params["vehicle_type"] = "4x4"
        filter_urls.append(
            get_filter_url(
                params,
                car_dict,
                car_filter,
            )
        )
    return filter_urls


@utils.runner
def main(car_dict: dict, mileage_plus_minus) -> None:
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
        print(f"Total cars - {len(cars)}")
        if cars:
            break
    utils.parse_and_save(car_dict, cars)

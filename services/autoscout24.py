from browser import client, types, HEADERS
from model.model import Filter, Car
from utilities import utils
from browser import get_the_listing_html
import json
from selectolax.parser import HTMLParser
import httpx

domain = "https://www.autoscout24.fr/"


def extract_10_cars(
    soup: HTMLParser, domain: str, parent_car_id: int, updated_at: str
) -> list[Car]:
    cars = []
    for x in soup.css("main article")[:10]:
        price = x.attributes.get("data-price")
        mileage = x.attributes.get("data-mileage")
        deal_type = x.attributes.get("data-price-label")
        name = utils.get_text(x.css_first("h2"))
        sub_name = utils.get_text(x.css_first('span[class="ListItem_subtitle__VEw08"]'))
        fuel_type = utils.get_text(x.css_first('span[aria-label="Carburant"]'))
        boite_de_vitesse = utils.get_text(x.css_first('span[aria-label="Boîte"]'))
        image = x.css_first("img")
        image = image.attributes.get("src") if image else None
        link = x.css_first("a")
        link = (
            f"https://www.autoscout24.fr{link.attributes.get('href')}" if link else link
        )
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
            )
        )

    return cars


def user_prompt(models: dict, colors: dict, fuel_types: dict, target_dict: dict):
    return f""" 
        You are an AI assistant tasked with generating a dictionary that matches a provided vehicle specification dictionary, using only values from specified lists and dictionaries. I will provide you with:
        - A dictionary of models where numbers are value and model name are key.
        - A dictionary of colors where numbers are value and model name are key.
        - A dictionary of fuel types where numbers are value and model name are key.
        - A target dictionary to compare against.

        Your task is to:
        1. Compare each key-value pair in the target dictionary with the provided options.
        2. Create a new dictionary where:
        - The keys are the same as the target dictionary ('make', 'model', 'version', 'color', 'mileage', 'fuel_type').
        - The values are selected from the provided options (models, colors, versions, fuel types) that most closely match the target dictionary's values.
        - If no exact match exists for a key's value in the provided options, try to extract it from the target dictionnary (e.g., 'make', 'version' or 'mileage' when no alternatives are given).
        3. Ensure all values in the output dictionary come from the provided lists/dictionary, except where explicitly noted.

        Here are the inputs:

        - Models: {models}
        - Colors: {colors}
        - Fuel types: {fuel_types}
        - Target dictionary: {target_dict}

        Rules:
        - For 'make', use the provided value ('CUPRA') if no alternative makes are listed, as it's implied to be valid.
        - For 'model', use the dict value from the models dictionary. I want the key (name) of the dict, (e.g., 'CLE 180' → '76795').
        - For 'color', use the dict value from the colors dictionary. I want the (value) of the dict not the name (key), (e.g., 'Noir' → '11').
        - For 'mileage', use the provided value if no mileage options are given.
        - For 'version', use the provided value if no version options are given.
        - For 'fuel_type', use the string value from the fuel types dictionary. I want the (value) of the dict not the name (key), (e.g., 'Essence' → 'B').

        Output the resulting dictionary in Python dictionary format. Provide a brief explanation of your choices.

        Please process this and return the matched dictionary.
        """


def get_prompt_from_make(input_dict: dict) -> str:
    print("Sending requests to get the models and colors")
    input_url = (
        f"https://www.autoscout24.fr/lst/{input_dict['make'].replace(' ', '-').lower()}"
    )
    print(input_url)
    json_data = {
        "url": input_url,
        "geo": "France",
        "device_type": "mobile",
    }
    response = httpx.post(
        "https://scraper-api.smartproxy.com/v2/scrape",
        headers=HEADERS,
        timeout=None,
        json=json_data,
    )
    response.raise_for_status()
    json_data = response.json()
    if json_data.get("results"):
        content = json_data.get("results")[0]["content"]
    soup = HTMLParser(content)
    json_str = soup.css_first('script[id="__NEXT_DATA__"]').text()
    json_data = json.loads(json_str)
    taxonomy = json_data["props"]["pageProps"]["taxonomy"]
    makes = taxonomy["makeLabels"]
    all_models = {}
    all_colors = {}
    fuel_types = {}
    for x in makes:
        if makes[x].lower() == input_dict["make"].lower():
            models = taxonomy["models"][x]
            for model in models:
                all_models[model["label"]] = model["value"]
            colors = taxonomy["bodyColor"]
            for color in colors:
                all_colors[color["label"]] = color["value"]
            fuels = taxonomy["fuelType"]
            for fuel in fuels:
                fuel_types[fuel["label"]] = fuel["value"]
            break
    return user_prompt(all_models, all_colors, fuel_types, input_dict)


def get_filter_url(car_dict):
    print("Generating Filter url based on row dict")
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
    car_filter.model = car_filter.model.replace(" ", "-").lower()
    filter_url = f"https://www.autoscout24.fr/lst/{car_filter.make.lower()}/{car_filter.model}?bcol={car_filter.color}&fuel={car_filter.fuel_type}&version0={car_filter.version}"
    return filter_url


@utils.runner
def main(car_dict: dict):
    url = get_filter_url(car_dict)
    cars = get_the_listing_html(car_dict, url, domain, car_dict["id"], extract_10_cars)
    utils.parse_and_save(car_dict, cars)


if __name__ == "__main__":
    pass

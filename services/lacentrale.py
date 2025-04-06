from browser import client, types
from model.model import Filter, Car
import httpx
from utilities import utils
from browser import get_the_listing_html

domain = "https://www.lacentrale.fr/"

lacentrale_fuel_dict = {
    0: "alt",  # Autre (Other), including duplicate
    1: "ess",  # Essence (Gasoline)
    2: "dies",  # Diesel
    3: "gpl",  # GPL (Autogas), including duplicate
    6: "elec",  # Électrique (Electric)
    7: "hyb",  # Hybride variations
    9: "eth",  # Éthanol (Ethanol), including duplicate
}

headers = {
    "sec-ch-ua-platform": '"Linux"',
    "Referer": "https://www.lacentrale.fr/",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
    "sec-ch-ua-mobile": "?0",
    "x-api-key": "2vHD2GjDJ07RpNvbGYpJG7s6bQNwRNkI9SEkgQnR",
    "X-Client-Source": "lc:recherche:front",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

params = {
    "aggregations": "EXTERNAL_COLOR,MAKE_MODEL_COMMERCIAL_NAME,VERSION",
    "families": "AUTO,UTILITY",
    "makesModelsCommercialNames": "CUPRA",
}


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
    response = httpx.get(
        "https://recherche.lacentrale.fr/v5/aggregations",
        params=params,
        headers=headers,
    )
    json_data = response.json()
    all_models = []
    all_colors = []
    all_versions = []
    if json_data["total"]:
        # Get all the models based on the make
        models = response.json()["aggs"]["vehicle.makeModelCommercialName"][0]["agg"]
        for model in models:
            for inner_model in model["agg"]:
                all_models.append(inner_model["key"])
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
    filter_url = f"https://www.lacentrale.fr/listing?energies={car_filter.fuel_type}&externalColors={car_filter.color}&makesModelsCommercialNames={car_filter.make}:{car_filter.model}&versions={car_filter.version}"
    return filter_url


@utils.runner
def main(car_dict: dict) -> list[Car]:
    url = get_filter_url(car_dict)
    cars = get_the_listing_html(car_dict, url, domain, car_dict["id"])
    utils.parse_and_save(car_dict, cars)


if __name__ == "__main__":
    pass

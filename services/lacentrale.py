from browser import client, types
from model.model import Filter, Car
import httpx
from utilities import utils
from browser import get_the_listing_html
from selectolax.parser import HTMLParser
from urllib.parse import urlencode, urlunparse, ParseResult

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


def extract_10_cars(
    soup: HTMLParser, domain: str, parent_car_id: int, updated_at: str
) -> list[Car]:
    cars = []
    for x in soup.css("div.searchCard"):
        price = x.css_first(
            'div[class="Text_Text_text Text_Text_subtitle-large vehiclecardV2_vehiclePrice__En33S"]'
        )
        price = (
            float(utils.get_text(price).replace("€", "").replace(" ", "").strip())
            if price
            else None
        )
        characs = x.css('div[class="Text_Text_text Text_Text_body-medium"]')
        if len(characs) < 4:
            continue
        mileage = (
            float(utils.get_text(characs[2]).replace("km", "").replace(" ", "").strip())
            if characs[2]
            else None
        )
        deal_type = utils.get_text(x.css_first('span[class="Tag_Tag_label"]'))
        name = utils.get_text(x.css_first("h2"))
        sub_name = utils.get_text(x.css_first("div.vehiclecardV2_subTitle__c8h4X"))
        fuel_type = utils.get_text(characs[3])
        boite_de_vitesse = utils.get_text(characs[1])
        image = x.css_first("img")
        image = image.attributes.get("src") if image else None
        image = image.split("?")[0] if image else None
        link = x.css_first("a")
        link = (
            f"https://www.lacentrale.fr{link.attributes.get('href')}" if link else link
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
    return ",".join(options)


def get_filter_url(car_dict: dict):
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
    km_from = abs(round(car_filter.mileage - 10000))
    km_to = abs(round(car_filter.mileage + 10000))
    equipments = get_options(car_dict)

    # build the filter url
    params = {}
    params["energies"] = car_filter.fuel_type
    params["makesModelsCommercialNames"] = f"{car_filter.make}:{car_filter.model}"
    if car_filter.version:
        params["versions"] = car_filter.version
    params["yearMax"] = car_filter.year_to
    params["yearMin"] = car_filter.year_from
    params["mileageMax"] = km_to
    params["mileageMin"] = km_from
    params["customerFamilyCodes"] = "PROFESSIONNEL"
    if equipments:
        params["options"] = equipments
    if car_dict.get("4x4"):
        params["categories"] = 47
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
            netloc="www.lacentrale.fr",
            path="/listing",
            params="",
            query=query_string,
            fragment="",
        )
    )

    # filter_url = f"https://www.lacentrale.fr/listing?energies={car_filter.fuel_type}&makesModelsCommercialNames={car_filter.make}:{car_filter.model}&versions={car_filter.version if car_filter.version else ''}&yearMax={car_filter.year_to}&yearMin={car_filter.year_from}&mileageMax={km_to}&mileageMin={km_from}&customerFamilyCodes=PROFESSIONNEL&options={equipments}"
    return filter_url


@utils.runner
def main(car_dict: dict) -> list[Car]:
    url = get_filter_url(car_dict)
    cars = get_the_listing_html(car_dict, url, domain, car_dict["id"], extract_10_cars)
    utils.parse_and_save(car_dict, cars)


if __name__ == "__main__":
    pass

import json
from datetime import datetime
from time import sleep

import httpx
from google import genai
from google.genai import types
from selectolax.parser import HTMLParser
from the_retry import retry

from config import config
from model.model import Car, Match
from utilities import utils

client = genai.Client(api_key=config.GEMINI_API)

selectors = {
    "https://www.lacentrale.fr/": 'div[class="searchCardContainer"]',
    "www.leboncoin.fr": 'ul[data-test-id="listing-column"]',
    "https://www.autoscout24.fr/": 'main[class="ListPage_main___0g2X"]',
}

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Basic {config.SMART_PROXY}",
}

LACENTRALE_COOKIES = {
    "access-token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTcyNDUyNTAsInZlcnNpb24iOiIyMDE4LTA3LTE2IiwidXNlckNvcnJlbGF0aW9uSWQiOm51bGwsInVzZXJfY29ycmVsYXRpb25faWQiOm51bGwsImxvZ2dlZFVzZXIiOnsiY29ycmVsYXRpb25JZCI6bnVsbCwicmVmcmVzaFRva2VuVFRMIjoxNzYxMTI5NjUwfSwibW9kZU1hc3F1ZXJhZGUiOmZhbHNlLCJhdXRob3JpemF0aW9ucyI6eyJ2ZXJzaW9uIjoiMjAxOC0wNy0xNiIsInN0YXRlbWVudHMiOlt7InNpZCI6IioiLCJlZmZlY3QiOiJEZW55IiwiYWN0aW9ucyI6WyIqIl0sInJlc291cmNlcyI6WyIqIl19XX0sImlhdCI6MTc1NzI0MTY1MH0.tx0GGQ_wYcTcK1g5_-z2czcZd97yKBGTjgjoUPKeDLYVFIUTFOhfQZe7rTicN8hB7DewDnzQuMsvkyLlzur9iLknLiOoKzFKQSirQMAkKmTakWRmCnqxqud7JNwi9tx0tbwg1K7oYxv5aIl4DyJARbFnQkks9KWF88OCv2gaRUOd9HOITXmKB7vpwUv9xtRtyQhQejI6mB7Or5L3YkomerYBXh3QUlo3h9klTmsMeeIhxNMc_SWNvaaraJnzTSJTT-MqNWeYQGSVR7omZRa4YeWfEXS45aPzx5RjdszhVTz74YRTBYyE8IL7495BNJFXJjmCGmEXnz9M19kVl3yn7A",
    "kameleoonVisitorCode": "ghu7fueff",
    "kameleoonTrackings": "%5B%7B%22Experiments.assignVariation%22%3A%22289282%2C1068407%22%2C%22Experiments.trigger%22%3A%22289282%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22298892%2C1150713%22%2C%22Experiments.trigger%22%3A%22298892%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22302730%2C1099455%22%2C%22Experiments.trigger%22%3A%22302730%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22304495%2C1103475%22%2C%22Experiments.trigger%22%3A%22304495%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22313627%2C1127045%22%2C%22Experiments.trigger%22%3A%22313627%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22313978%2C1126422%22%2C%22Experiments.trigger%22%3A%22313978%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22315702%2C1130328%22%2C%22Experiments.trigger%22%3A%22315702%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22327940%2C1157938%22%2C%22Experiments.trigger%22%3A%22327940%2Ctrue%22%7D%5D",
    "kameleoonFeatureFlags": "%5B%22composer-classified-composer%22%2C%22copy_af64u95oqng_copy_jr16u2dmikg__dev__cas__logged_cote-seeprice%22%2C%22copy_h6f1fpu0cbg_copy_dsg7dt33qvo__dev__cas__ab_highlight_area-highlight_depot%22%2C%22lacentrale-chat-2-0-13%22%2C%22new-financing-design-activated%22%2C%22one-click-call-activated%22%2C%22one-click-call-wording-activated%22%2C%22publicity-default%22%2C%22strengths-revamp-on%22%5D",
    "visitor_id": "d79cf621-26aa-4ba5-86e7-abf6caa93543",
    "_pprv": "eyJjb25zZW50Ijp7IjAiOnsibW9kZSI6ImVzc2VudGlhbCJ9LCI3Ijp7Im1vZGUiOiJvcHQtaW4ifX0sInB1cnBvc2VzIjp7IjAiOiJBTSIsIjciOiJETCJ9LCJfdCI6Im11eHo4bDBwfG1mOWtiM29wIn0%3D",
    "atidvisitor251312": "%7B%22name%22%3A%22atidvisitor251312%22%2C%22val%22%3A%7B%22vrn%22%3A%22-251312-%22%7D%2C%22options%22%3A%7B%22path%22%3A%22%2F%22%2C%22session%22%3A15724800%2C%22end%22%3A15724800%7D%7D",
    "tCdebugLib": "1",
    "pa_vid": "%22d79cf621-26aa-4ba5-86e7-abf6caa93543%22",
    "didomi_token": "eyJ1c2VyX2lkIjoiMTk5MjNjM2ItNGIxNS02MGUzLTkwOGMtMTE0MWJjOWU4YTkzIiwiY3JlYXRlZCI6IjIwMjUtMDktMDdUMTA6NDA6NTIuNDAxWiIsInVwZGF0ZWQiOiIyMDI1LTA5LTA3VDEwOjQwOjUyLjQwMloiLCJ2ZXJzaW9uIjpudWxsfQ==",
    "atuserid": "%7B%22name%22%3A%22atuserid%22%2C%22val%22%3A%22d79cf621-26aa-4ba5-86e7-abf6caa93543%22%2C%22options%22%3A%7B%22end%22%3A%222026-03-08T10%3A47%3A05.147Z%22%2C%22path%22%3A%22%2F%22%7D%7D",
    "datadome": "_BTvZHaw9eXcTRGcc0dP4NZGdVPGRU~AvwWo1N4xKB23ru6XDutJBZAptGxN8VRMRtpPG2qIvxEE4AUbjxA9fXOglHMpTPK6ZHKpM6gmPgWJXys08mnKGd9BFVg1HPFN",
}


def prompt(car1_details: str, car2_details: str) -> str:
    return f"""
    You are an expert in automotive comparisons.
    I will provide you with details of two cars, including their make, model, version (if available), and mileage. "
    "Your task is to compare these two cars and calculate a percentage match based on the following attributes: make, model, version, and mileage. "
    "Use your car knowledge to enhance the comparison, especially for the version attribute,
    "Assign weights to each attribute as follows: make (20%), model (20%), version (20%), and mileage (40%). "
    "Also provide a short explanation on why a particular percentage is assign to the car"
    "Here are the details for the two cars: "
    "- Car 1: {car1_details} "
    "- Car 2: {car2_details} "
    "Return the percentage match as a float, don't forget to inclue the reason as well."
    """


def get_percentage_match(car1_details: str, car2_details: str):
    print("Calculating the percentage match")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt(car1_details, car2_details),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Match,
            system_instruction="You are an expert in automotive comparisons.",
        ),
    )
    percentage_percent = response.parsed
    if isinstance(percentage_percent, Match):
        return (
            percentage_percent.matching_percentage,
            percentage_percent.matching_percentage_reason,
        )
    else:
        return 0, None


@retry(attempts=2, backoff=5, exponential_backoff=True)
def get_the_listing_html(
    car_dict: dict,
    filter_url: str,
    domain: str,
    parent_car_id: str,
    extract_10_cars,
    is_basic_filter: bool = False,
    skip_requests: bool = False,
    ads: list[dict] = [],
) -> list[Car]:
    if skip_requests:
        ten_cars: list[Car] = extract_10_cars(
            ads, domain, parent_car_id, datetime.now().isoformat()
        )
    else:
        if domain == "https://www.lacentrale.fr/":
            proxy = f"http://{config.PROXY_USERNAME}:{config.PROXY_PASSWORD}@fr.decodo.com:40000"
            lacentrale_headers = utils.get_json_from_local(
                "./uploads/Lacentrale_Headers.json"
            )
            response = httpx.get(
                filter_url,
                cookies=LACENTRALE_COOKIES,
                headers=lacentrale_headers,
                # proxy=proxy,
            )
            response.raise_for_status()
            soup = response.json()
        else:
            json_data = {
                "url": filter_url,
                "geo": "France",
                "device_type": "mobile",
                "headless": "html",
            }
            response = httpx.post(
                "https://scraper-api.decodo.com/v2/scrape",
                headers=HEADERS,
                json=json_data,
                timeout=None,
            )
            content = None
            if response.status_code != 200:
                raise ValueError("Content is null")
            json_data = response.json()
            if json_data.get("results"):
                content = json_data.get("results")[0]["content"]
            else:
                print("NO OUTPUTS")

            if not content:
                raise ValueError("Content is null")
            soup = HTMLParser(content)
        ten_cars: list[Car] = extract_10_cars(
            soup, domain, parent_car_id, datetime.now().isoformat()
        )
        print(f"Found - {len(ten_cars)} cars")
    if (len(ten_cars) < 10) and (not is_basic_filter):
        return []
    for car in ten_cars:
        if not car.link:
            continue
        car.id = f"{int(datetime.now().timestamp())}_{parent_car_id}"
        car.matching_percentage, car.matching_percentage_reason = get_percentage_match(
            json.dumps(car_dict), car.model_dump_json()
        )
        print(car.matching_percentage, car.matching_percentage_reason)
        sleep(2)

    return ten_cars

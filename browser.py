from selectolax.parser import HTMLParser
from google import genai
from google.genai import types
from model.model import Car, Match
from config import config
import hashlib
from datetime import datetime
import httpx
import json

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


def prompt(car1_details: dict, car2_details: dict) -> str:
    return f"""
    You are an expert in automotive comparisons. 
    I will provide you with details of two cars, including their make, model, version (if available), and mileage. "
    "Your task is to compare these two cars and calculate a percentage match based on the following attributes: make, model, version, and mileage. "
    "Use your car knowledge to enhance the comparison, especially for the version attribute, 
    by considering factors like generation, engine specifications, trim level, and additional features. "
    "Assign weights to each attribute as follows: make (20%), model (20%), version (20%), and mileage (40%, given more weight due to its significance in condition assessment). "
    "For each attribute: "
    "- **Make**: Score 1.0 for an exact match, 0.0 otherwise. "
    "- **Model**: Score 1.0 for an exact match, 0.0 otherwise. "
    "- **Version**: Score between 0.0 and 1.0 based on similarity (e.g., generation, engine size, trim, features). Use your car expertise to estimate partial matches (e.g., same trim but different engines = partial score). "
    "- **Mileage**: Calculate a score between 0.0 and 1.0 using the formula `1 - (difference / max_range)`, where `max_range` is 200,000 km (a typical lifespan for most cars), and cap the score at 0 if the difference exceeds the range. "
    "Provide the final percentage match by summing the weighted scores (make_score * 0.20 + model_score * 0.20 + version_score * 0.20 + mileage_score * 0.40) and multiplying by 100. "
    "Here are the details for the two cars: "
    "- Car 1: {car1_details} "
    "- Car 2: {car2_details} "
    "Return the percentage match as a float"
    """


def get_percentage_match(car1_details: dict, car2_details: dict):
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
    percentage_percent: Match = response.parsed
    return percentage_percent.matching_percentage


def get_the_listing_html(
    car_dict: dict, filter_url: str, domain: str, parent_car_id: str, extract_10_cars
) -> list[Car]:
    print(f"Fetching the listing page - {filter_url}")
    json_data = {
        "url": filter_url,
        "geo": "France",
        "device_type": "mobile",
        "headless": "html",
    }
    response = httpx.post(
        "https://scraper-api.smartproxy.com/v2/scrape",
        headers=HEADERS,
        json=json_data,
        timeout=None,
    )
    response.raise_for_status()
    json_data = response.json()
    if json_data.get("results"):
        content = json_data.get("results")[0]["content"]
    soup = HTMLParser(content)
    ten_cars: list[Car] = extract_10_cars(
        soup, domain, parent_car_id, datetime.now().isoformat()
    )
    print(f"Found - {len(ten_cars)} cars")
    for car in ten_cars:
        car.id = f"{hashlib.md5(car.link.encode()).hexdigest()}_{parent_car_id}"
        car.matching_percentage = get_percentage_match(
            json.dumps(car_dict), car.model_dump_json()
        )
        print(car.matching_percentage)
    return ten_cars

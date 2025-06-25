from browserforge import headers
from selectolax.parser import HTMLParser
from google import genai
from google.genai import types
from model.model import Car, Match
from config import config
import hashlib
from datetime import datetime
import json
from the_retry import retry
import hrequests
import httpx

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

LACENTALE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "Origin": "https://www.lacentrale.fr",
    "Connection": "keep-alive",
    "Referer": "https://www.lacentrale.fr/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Priority": "u=6",
    "Cookie": "datadome=ciYGhJL4Xb2Y76J0qGPm59Z2UuGlV938ZNZIYAmUVHcf3_LJ7CKHOsWEMgbPqaeDLy6w2JzbCVkHg4xvnuyJCsiqQzuRnHlMPFfv7r9vxh57XI1wTZddgGbqn1tOssg~; Max-Age=31536000; Domain=.lacentrale.fr; Path=/; Secure; SameSite=Lax",
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


@retry(attempts=5, backoff=5, exponential_backoff=True)
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
            username = "sp4hm5m7z0"
            password = "85K6wSkwq4Zo~Rjkie"
            proxy = f"http://{username}:{password}@fr.decodo.com:40000"
            response = httpx.get(
                url=filter_url, headers=LACENTALE_HEADERS, proxy=proxy
            )
            response.raise_for_status()
            soup = HTMLParser(response.text)
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
        car.id = f"{hashlib.md5(car.link.encode()).hexdigest()}_{parent_car_id}"
        car.matching_percentage, car.matching_percentage_reason = (
            get_percentage_match(json.dumps(car_dict), car.model_dump_json())
        )
        print(car.matching_percentage, car.matching_percentage_reason)
    return ten_cars

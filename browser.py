from selectolax.parser import HTMLParser
from google import genai
from google.genai import types
from html_to_markdown import convert_to_markdown
from model.model import Car
from urllib.parse import urljoin
from config import config
import hashlib
from datetime import datetime
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


def prompt(metadata):
    return f"""
    Extract the first 10 cars info from the markdown, be sure to complete the car's link and include the metadata.
    Make sure the prices and mileage are in float.
    Use this page metadata to get the site's link to complete the car's link if needed -> {metadata}
    Remove unneccssary space from each fields.
    MAKE SURE TO INCLUDE DATA EXACTLY AS IT IS ON THE SITE. DATA INTERGRITY IS VERY IMPORTANT
    """


def extract_10_cars(soup: HTMLParser, domain: str) -> list[Car]:
    metas = "; ".join([meta.html for meta in soup.css("meta")])
    listing_page = soup.css_first(selectors[domain])
    if listing_page:
        markdown = convert_to_markdown(listing_page.html)
        metadata_of_page = convert_to_markdown(metas)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[markdown, prompt(metadata_of_page)],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[Car],
                system_instruction="You are an Intelligent Html Parser Bot, that prioritze data intergrity.",
            ),
        )
        cars: list[Car] = response.parsed
        return cars
    return []


def get_the_listing_html(filter_url: str, domain: str, parent_car_id: str) -> list[Car]:
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
    ten_cars = extract_10_cars(soup, domain)
    print(f"Found - {len(ten_cars)} cars")
    for car in ten_cars:
        car.domain = domain
        car.link = urljoin(domain, car.link)
        car.id = f"{hashlib.md5(car.link.encode()).hexdigest()}_{parent_car_id}"
        car.parent_car_id = parent_car_id
        car.updated_at = datetime.now().isoformat()
    return ten_cars

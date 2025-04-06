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


def prompt(metadata: dict, car_dict: dict) -> str:
    """
    Generate a prompt for extracting car information from a Markdown source.

    Args:
        metadata (dict): Metadata containing the site's base URL to complete car links.
        car_dict (dict): Dictionary containing car info to calculate matching percentage.

    Returns:
        str: A formatted prompt string with instructions for data extraction.
    """
    return f"""
    1. Extract the first 10 cars' information from the provided Markdown content.
    2. Ensure each car's information includes the following fields exactly as they appear on the site:
       - Make
       - Model
       - Year
       - Price (convert to float)
       - Mileage (convert to float)
       - Link (complete the URL if needed)
    3. Use the provided page metadata to complete the car's link if the link is relative:
       - Metadata: {metadata}
       - If the car's link is relative (e.g., '/cars/123'), prepend the site's base URL from the metadata (e.g., 'https://example.com') to form a full URL (e.g., 'https://example.com/cars/123').
    4. Convert the 'Price' and 'Mileage' fields to float values:
       - Remove any currency symbols, commas, or units (e.g., '$12,345' -> 12345.0, '15,000 miles' -> 15000.0).
    5. Remove unnecessary whitespace from all fields (e.g., '  Toyota  ' -> 'Toyota').
    6. Include the metadata in the output alongside the extracted car data.
    7. Calculate a matching percentage for each car based on the provided car info, giving higher weight to Mileage due to its importance in pricing:
       - Car info for matching: {car_dict}
       - Compare fields like Make, Model, Year, Price, and Mileage with the following weights:
         - Mileage: 40% (since it's critical for pricing)
         - Make: 15%
         - Model: 15%
         - Year: 15%
         - Price: 15%
       - Matching percentage should be a float (e.g., 85.5) based on how closely the car matches the provided car_dict.
       - For each field:
         - **Mileage**: Calculate the percentage match as (1 - |car_dict['Mileage'] - car['Mileage']| / max(car_dict['Mileage'], car['Mileage'])) * 100, then multiply by 0.4 (40% weight).
         - **Make, Model, Year**: If they match exactly (case-insensitive), assign 100% for that field; otherwise, 0%. Multiply by 0.15 (15% weight) for each.
         - **Price**: Calculate the percentage match as (1 - |car_dict['Price'] - car['Price']| / max(car_dict['Price'], car['Price'])) * 100, then multiply by 0.15 (15% weight).
       - Sum the weighted scores to get the final matching percentage (e.g., 40% Mileage + 15% Make + 15% Model + 15% Year + 15% Price).
       - Example: If car_dict has Make='Toyota', Model='Camry', Year=2020, Price=25000, Mileage=15000:
         - Extracted car: Toyota Camry, 2020, $24,000, 14,000 miles
         - Mileage match: (1 - |15000 - 14000| / 15000) * 100 = 93.33% → 93.33 * 0.4 = 37.33
         - Make match: 100% → 100 * 0.15 = 15
         - Model match: 100% → 100 * 0.15 = 15
         - Year match: 100% → 100 * 0.15 = 15
         - Price match: (1 - |25000 - 24000| / 25000) * 100 = 96% → 96 * 0.15 = 14.4
         - Total: 37.33 + 15 + 15 + 15 + 14.4 = 96.73%
    8. Ensure data integrity:
       - Extract data EXACTLY as it appears on the site (e.g., do not change 'Camry XLE' to 'Camry' unless that's how it's listed).
       - Do not infer or modify values; preserve the original data's formatting except for the float conversion and whitespace removal.
    """


def extract_10_cars(soup: HTMLParser, car_dict: dict, domain: str) -> list[Car]:
    metas = "; ".join([meta.html for meta in soup.css("meta")])
    listing_page = soup.css_first(selectors[domain])
    if listing_page:
        markdown = convert_to_markdown(listing_page.html)
        metadata_of_page = convert_to_markdown(metas)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[markdown, prompt(metadata_of_page, car_dict)],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[Car],
                system_instruction="You are an Intelligent Html Parser Bot, that prioritze data intergrity.",
            ),
        )
        cars: list[Car] = response.parsed
        return cars
    return []


def get_the_listing_html(
    car_dict: str, filter_url: str, domain: str, parent_car_id: str
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
    ten_cars = extract_10_cars(soup, car_dict, domain)
    print(f"Found - {len(ten_cars)} cars")
    for car in ten_cars:
        car.domain = domain
        car.link = urljoin(domain, car.link)
        car.id = f"{hashlib.md5(car.link.encode()).hexdigest()}_{parent_car_id}"
        car.parent_car_id = parent_car_id
        car.updated_at = datetime.now().isoformat()
    return ten_cars

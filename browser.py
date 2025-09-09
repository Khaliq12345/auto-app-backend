from selectolax.parser import HTMLParser
from google import genai
from google.genai import types
from model.model import Car, Match
from config import config
import hashlib
from datetime import datetime
import json
from the_retry import retry
import httpx
import hrequests

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
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "priority": "u=0, i",
    "referer": "https://www.lacentrale.fr/",
    "sec-ch-device-memory": "8",
    "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-full-version-list": '"Chromium";v="139.0.7258.138", "Not;A=Brand";v="99.0.0.0"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "cookie": 'access-token=eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTY3MzA0NDcsInZlcnNpb24iOiIyMDE4LTA3LTE2IiwidXNlckNvcnJlbGF0aW9uSWQiOm51bGwsInVzZXJfY29ycmVsYXRpb25faWQiOm51bGwsImxvZ2dlZFVzZXIiOnsiY29ycmVsYXRpb25JZCI6bnVsbCwicmVmcmVzaFRva2VuVFRMIjoxNzYwNjE0ODQ3fSwibW9kZU1hc3F1ZXJhZGUiOmZhbHNlLCJhdXRob3JpemF0aW9ucyI6eyJ2ZXJzaW9uIjoiMjAxOC0wNy0xNiIsInN0YXRlbWVudHMiOlt7InNpZCI6IioiLCJlZmZlY3QiOiJEZW55IiwiYWN0aW9ucyI6WyIqIl0sInJlc291cmNlcyI6WyIqIl19XX0sImlhdCI6MTc1NjcyNjg0N30.tgh8rPxQ87nI5lrd6U3fqE3delXh_cgIP2Ptzp3yGpZKDsCeufdzOC1joi9p-IT6y6x8TfHrfo-VRo0136ISqiddb3bZqywwUX5W-jczi5XaHInl1WJriG__Cvqc0aHs_tautqmL6qKN2h6YLW-XxpKbFpHLLPMmLu4i3RWPFs5d_YAfbwULWwjeb9FXwUK_RZH-xOAORpnndnhxUc4FPFAE8XIRGOQjL_U_ozoEDghNShrxKfBHCDuq5VHR9PPEAfhQ1NPTstvdAIfrsqp3GkmwZQnse3lvjLiWDabu7yLiJQ6TH27QWulE8YggkfB3sEzUS4sCoPQgOGW64yrQzg; visitor_id=055bb825-9631-4dc4-bfae-4b089e027697; kameleoonVisitorCode=7s92rohe90g; kameleoonTrackings=%5B%7B%22Experiments.assignVariation%22%3A%22289282%2C1068407%22%2C%22Experiments.trigger%22%3A%22289282%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22298892%2C1150713%22%2C%22Experiments.trigger%22%3A%22298892%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22302730%2C1099455%22%2C%22Experiments.trigger%22%3A%22302730%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22304495%2C1103475%22%2C%22Experiments.trigger%22%3A%22304495%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22313627%2C1127045%22%2C%22Experiments.trigger%22%3A%22313627%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22313978%2C1126421%22%2C%22Experiments.trigger%22%3A%22313978%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22315702%2C1130328%22%2C%22Experiments.trigger%22%3A%22315702%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22323253%2C1147037%22%2C%22Experiments.trigger%22%3A%22323253%2Ctrue%22%7D%2C%7B%22Experiments.assignVariation%22%3A%22327940%2C1157938%22%2C%22Experiments.trigger%22%3A%22327940%2Ctrue%22%7D%5D; kameleoonFeatureFlags=%5B%22atc-ranking-new%22%2C%22composer-classified-composer%22%2C%22copy_af64u95oqng_copy_jr16u2dmikg__dev__cas__logged_cote-seeprice%22%2C%22copy_h6f1fpu0cbg_copy_dsg7dt33qvo__dev__cas__ab_highlight_area-highlight_lre%22%2C%22lacentrale-chat-2-0-13%22%2C%22new-financing-design-activated%22%2C%22one-click-call-activated%22%2C%22one-click-call-wording-activated%22%2C%22publicity-default%22%2C%22strengths-revamp-on%22%5D; atidvisitor251312=%7B%22name%22%3A%22atidvisitor251312%22%2C%22val%22%3A%7B%22vrn%22%3A%22-251312-%22%7D%2C%22options%22%3A%7B%22path%22%3A%22%2F%22%2C%22session%22%3A15724800%2C%22end%22%3A15724800%7D%7D; _pcid=%7B%22browserId%22%3A%22mf11t6dl3bbt7pd5%22%2C%22_t%22%3A%22mupgqnpz%7Cmf11t6dz%22%7D; _cs_mk_pa=0.9120987193281638_1756726852248; tc_sampling=10; tCdebugLib=1; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbMAAcA5gEckMAB4AffgDMAjIvwA2eVJABfIA; lc_pageSize=16; persist:lc:client=%7B%22_persist%22%3A%22%7B%5C%22version%5C%22%3A-1%2C%5C%22rehydrated%5C%22%3Atrue%7D%22%7D; reduxPersistIndex=%5B%22persist%3Alc%3Aclient%22%5D; ab.storage.deviceId.c96d7fed-e0d2-4550-8d72-1036262ded5a=g%3Af8079dc5-e20b-7152-a34b-27729e51c5be%7Ce%3Aundefined%7Cc%3A1756726852887%7Cl%3A1756726852887; ab.storage.sessionId.c96d7fed-e0d2-4550-8d72-1036262ded5a=g%3A3d9f8cdb-1183-1c65-a9a5-9b0bb31eb216%7Ce%3A1756728652891%7Cc%3A1756726852885%7Cl%3A1756726852891; didomi_cookies=essential,analytics,marketing,social; _pprv=eyJjb25zZW50Ijp7IjAiOnsibW9kZSI6Im9wdC1pbiJ9LCI3Ijp7Im1vZGUiOiJvcHQtaW4ifX0sInB1cnBvc2VzIjp7IjAiOiJBTSIsIjciOiJETCJ9LCJfdCI6Im11cGdxbnBwfG1mMTF0NmRwIn0%3D; gdprValid=1; atPrivacy=optin; atuserid=%7B%22name%22%3A%22atuserid%22%2C%22val%22%3A%22mf11t6dl3bbt7pd5%22%2C%22options%22%3A%7B%22end%22%3A%222026-03-02T11%3A40%3A53.021Z%22%2C%22path%22%3A%22%2F%22%7D%7D; atauthority=%7B%22name%22%3A%22atauthority%22%2C%22val%22%3A%7B%22authority_name%22%3A%22default%22%2C%22visitor_mode%22%3A%22optin%22%7D%2C%22options%22%3A%7B%22end%22%3A%222026-10-03T11%3A40%3A53.021Z%22%2C%22path%22%3A%22%2F%22%7D%7D; tc_pianoConsent=1; _cs_ex=1743683889; _cs_c=0; _lm_id=2DX302QV324BDIGS; _uetsid=86982100872811f0b7c473cecba29549; _uetvid=86985c50872811f0979b3b18d84ec025; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22055bb825-9631-4dc4-bfae-4b089e027697%22%2C%22expiryDate%22%3A%222026-09-01T11%3A40%3A59.073Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%222c9tD3Cw0qxN3GO46mLN%22%2C%22expiryDate%22%3A%222026-09-01T11%3A40%3A59.073Z%22%7D; ry_ry-9mpyr1d3_realytics=eyJpZCI6InJ5XzBGMjQ0MTI3LTQ0MjctNDUyQS04MkYxLUI1NTc2NjhENzhDQSIsImNpZCI6bnVsbCwiZXhwIjoxNzg4MjYyODU5Mjk0LCJjcyI6bnVsbH0%3D; ry_ry-9mpyr1d3_so_realytics=eyJpZCI6InJ5XzBGMjQ0MTI3LTQ0MjctNDUyQS04MkYxLUI1NTc2NjhENzhDQSIsImNpZCI6bnVsbCwib3JpZ2luIjp0cnVlLCJyZWYiOm51bGwsImNvbnQiOm51bGwsIm5zIjpmYWxzZSwic2MiOm51bGwsInNwIjpudWxsfQ%3D%3D; _gcl_au=1.1.1300786257.1756726860; _fbp=fb.1.1756726861677.87585764724909690; datadome=J3VAqK1KDUC5ypmhI2tctYWvwiYzm1O6RcNNsWtML5GDwFvPdwUWQ6LoVCPVRyR1ButrvnO~yJPqaoO8yKWsHmSpSPw7mCijDGxZjC03CmznabhR8N8PhOcUVBPg_y~f; _hjSessionUser_1339841=eyJpZCI6IjFkYTA3MzNmLTk1OGEtNTIxYy05MTU5LTVmNWViNTk2YWZmYyIsImNyZWF0ZWQiOjE3NTY3MjY4NjM5MTYsImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_1339841=eyJpZCI6IjM2OWRhOWM0LTdmZTktNGZlYy1hZDExLWU0MTA5NGNkMGI1MCIsImMiOjE3NTY3MjY4NjM5MTcsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MX0=; _lr_geo_location_state=QC; _lr_geo_location=CA; _clck=1wm52rj%5E2%5Efyy%5E0%5E2070; _clsk=kkd2cc%5E1756726871471%5E1%5E0%5Ek.clarity.ms%2Fcollect; lc_seed=20250901114; lc_delta_event_referrer={"event_page":"home", "event_page_zone":"moteurHome"}',
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

LACENTRALE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "Connection": "Keep-Alive",
    "firebase-performance-monitoring": "enabled",
    "Host": "mobile-app.lacentrale.fr",
    "If-Modified-Since": "Sun, 07 Sep 2025 10:41:18 GMT",
    "User-Agent": "okhttp/4.9.2",
    "x-client-source": "classified:android:lcpab",
    "x-datadome-clientid": "u6xUs~Ih0pjKrnO6ue312FNPNeL7vUjyWX~Te9Zc6y~JU~PH6G7YZ~OfCEc_smYyqmKifLxk7PCInXtAbBXFESXWjc8RIVIkxMgTA56O05StI_Aho1u0qmMBjKp1pjpI",
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
            proxy = f"http://{config.PROXY_USERNAME}:{config.PROXY_PASSWORD}@fr.decodo.com:40000"
            response = httpx.get(
                filter_url,
                # cookies=LACENTRALE_COOKIES,
                headers=LACENTRALE_HEADERS,
                proxy=proxy,
            )
            soup = response.json()
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
            print(response)
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

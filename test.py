import hrequests
import httpx
import requests


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    "Content-Type": "application/json",
    "Origin": "https://www.lacentrale.fr",
    "Connection": "keep-alive",
    "Referer": "https://www.lacentrale.fr/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Priority": "u=6",
    "Cookie": "datadome=Sp8hD1_HD3kzN37w3J8nWjTNDpLlnKHWMdXBdGnHmo70lCl7pKGb_MMgHQjFYpFc0n3XpQA35xojMKqCizR4MufF4uDCsP275ozKInUl4zepc4Fb_xKdkOI_Nr_VXCzu; Max-Age=31536000; Domain=.lacentrale.fr; Path=/; Secure; SameSite=Lax",
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

#
# resp = hrequests.get("https://www.lacentrale.fr/listing?options=&page=3")
# page = resp.render()
# print(page.url)
# page.screenshot(path="screenshot.png", full_page=True)
# page.close()

username = "sp4hm5m7z0"
password = "85K6wSkwq4Zo~Rjkie"
proxy = f"http://{username}:{password}@fr.decodo.com:40000"
url = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=OPEL%3ACOMBO&yearMax=2023&yearMin=2023&energies=elec&gearbox=AUTO&mileageMax=22530&mileageMin=2530&customerFamilyCodes=PROFESSIONNEL&options=RADAR_RECUL"
result = requests.get(
    url, proxies={"http": proxy, "https": proxy}, headers=headers
)
print(result)

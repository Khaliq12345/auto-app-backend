from typing import Annotated
from pathlib import Path
from fastapi import (
    Depends,
    FastAPI,
    File,
    UploadFile,
    HTTPException,
)
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from postgrest.types import CountMethod
from supabase import (
    AuthApiError,
    Client,
)
from services import autoscout24, lacentrale, leboncoin
from utilities import utils
from supabase import (
    create_client,
)
from supabase.lib.client_options import SyncClientOptions


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

domains = [lacentrale.domain, autoscout24.domain, leboncoin.domain]
domain_functions = {
    "lacentrale": lacentrale.main,
    "autoscout24": autoscout24.main,
    "leboncoin": leboncoin.main,
}


def get_session() -> Client:
    client: Client = create_client(
        supabase_key=utils.supabase_key,
        supabase_url=utils.url,
        options=SyncClientOptions(postgrest_client_timeout=60000),
    )
    return client



def get_avg_price_based_on_domain(
    records: list[dict],
    percentage_limit: int = 95,
):
    # Get the average price based on the best matching percentage for each domain
    best_prices = []
    for domain in domains:
        for record in records:
            if (record["domain"] == domain) and (
                record["matching_percentage"] >= percentage_limit
            ):
                best_prices.append(record["price"])
    best_prices = [bp for bp in best_prices if bp]
    if best_prices:
        return sum(best_prices) / len(best_prices)
    else:
        return 0

@app.post("/login")
def login(
    client: Annotated[Client, Depends(get_session)],
    email: str,
    password: str,
):
    try:
        response = client.auth.sign_in_with_password(
            credentials={
                "email": email,
                "password": password,
            }
        )
        return {
            "message": "Login successful",
            "details": jsonable_encoder(response),
        }
    except AuthApiError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )


@app.get("/get_all_cars")
def get_all_cars(
    limit: int = 20,
    cursor: int | None = None,  # Changed from offset to cursor
    cut_off_price: int = 500,
    domain: str | None = None,
    percentage_limit: int = 95,
):
    client = get_session()
    try:
        # Base query
        stmt = (
            client.table("Vehicles")
            .select("*, comparisons(*)", count=CountMethod.exact)
            .limit(limit)
            .order("id")  # Primary sort by ID for cursor
            .order(
                "matching_percentage",
                desc=True,
                foreign_table="comparisons",
            )
        )

        # Apply cursor if provided (for subsequent pages)
        if cursor is not None:
            stmt = stmt.gt("id", cursor)

        # Apply domain filter if provided
        if domain:
            stmt = stmt.eq("comparisons.domain", domain)

        response = stmt.execute()
        vehicles = []
        next_cursor = None

        for vehicle in response.data:
            comparison_prices = [x["price"] for x in vehicle["comparisons"]]
            comparison_prices = [0] if not comparison_prices else comparison_prices
            vehicle["lowest_price"] = min(comparison_prices)
            vehicle["average_price"] = sum(comparison_prices) / len(comparison_prices)
            avg_price = get_avg_price_based_on_domain(
                vehicle["comparisons"],
                percentage_limit,
            )
            vehicle["average_price_based_on_best_match"] = avg_price
            vehicle["price_difference_with_avg_price"] = (
                avg_price - vehicle["price_with_tax"]
            )
            if vehicle["price_with_tax"] < avg_price:
                vehicle["card_color"] = "green"
            elif abs(vehicle["price_with_tax"] - avg_price) >= cut_off_price:
                vehicle["card_color"] = "red"
            else:
                vehicle["card_color"] = "yellow"
            best_match_cars = sorted(
                vehicle["comparisons"],
                key=lambda x: x["matching_percentage"],
                reverse=True,
            )
            vehicle["best_match_percentage"] = 0
            vehicle["best_match_link"] = None
            if best_match_cars:
                best_match_car = best_match_cars[0]
                vehicle["best_match_percentage"] = best_match_car.get(
                    "matching_percentage"
                )
                vehicle["best_match_link"] = best_match_car.get("link")
            vehicles.append(vehicle)

        # Set next cursor to the last vehicle's ID
        if vehicles:
            next_cursor = vehicles[-1]["id"]

        return {
            "details": jsonable_encoder(vehicles),
            "total": response.count,
            "next_cursor": next_cursor,  # Return cursor for next page
            "has_more": len(vehicles) == limit,  # Indicate if more pages exist
        }
    except AuthApiError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scrape_status")
def get_status():
    try:
        client = get_session()
        response = client.table("Status").select("*").execute()
        return {
            # "session": jsonable_encoder(auth),
            "details": jsonable_encoder(response),
        }
    except AuthApiError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Crée le dossier si absent


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    # 1. Vérifier le type du fichier
    allowed_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ]
    print("Uploaded file content type:", file.content_type)

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed."
        )

    # 2. Lire le contenu
    try:
        content = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")

    # 3. Nom du fichier
    filename = "25630.xlsx"
    file_path = UPLOAD_DIR / filename

    # 4. Sauvegarde locale
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file locally: {e}",
        )

    return {
        "message": "File uploaded successfully",
        "filename": filename,
        "path": str(file_path),
    }


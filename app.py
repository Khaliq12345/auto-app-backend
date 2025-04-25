from services import autoscout24, lacentrale
import pandas as pd
from utilities import utils
import threading
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from supabase import Client, AuthApiError, create_client
from datetime import datetime
import os
import aiofiles
from config import config

OUT_FILE = config.UPLOAD_FILE
session_deps = Depends()
domains = [lacentrale.domain, autoscout24.domain]
PERCENTAGE_LIMIT = 95


def get_avg_price_based_on_domain(records: list[dict]):
    # Get the average price based on the best matching percentage for each domain
    best_prices = []
    for domain in domains:
        best_perc = 0
        best_price = 0
        for record in records:
            if (
                (record["domain"] == domain)
                and (record["matching_percentage"] > best_perc)
                and (record["matching_percentage"] >= PERCENTAGE_LIMIT)
            ):
                best_price = record["price"]
        best_prices.append(best_price)
    best_prices = [bp for bp in best_prices if bp]
    if best_prices:
        return sum(best_prices) / len(best_prices)
    else:
        return 0


def get_session() -> Client:
    client: Client = create_client(
        supabase_key=utils.supabase_key, supabase_url=utils.url
    )
    return client


@utils.runner
def start_services(dev: bool = True):
    try:
        if dev:
            df = pd.read_excel(OUT_FILE, header=None).sample(10)
        else:
            df = pd.read_excel(OUT_FILE, header=None)

        new_columns = []
        for col in df.columns.to_list():
            new_columns.append(utils.numeric_to_alphabetic_column_name(col))
        df.columns = new_columns
        df.fillna(value=0, inplace=True)

        for row_id in range(len(df)):
            client = get_session()
            car_dict = utils.get_row_dict(df, row_id)
            print(f"Car Info - {car_dict}")
            thread1 = threading.Thread(target=autoscout24.main, args=(car_dict,))
            thread2 = threading.Thread(target=lacentrale.main, args=(car_dict,))
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()
            if (row_id + 1) == len(df):
                stats = "success"
                stopped_at = datetime.now().isoformat()
            else:
                stopped_at = None
                stats = "running"
            client.table("Status").update(
                {
                    "id": 1,
                    "status": stats,
                    "stopped_at": stopped_at,
                    "total_completed": row_id + 1,
                    "total_running": len(df),
                }
            ).eq("id", 1).execute()
    except BaseException as e:
        client.table("Status").update(
            {"id": 1, "status": "failed", "stopped_at": datetime.now().isoformat()}
        ).eq("id", 1).execute()
        raise e


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login")
def login(client: Annotated[Client, Depends(get_session)], email: str, password: str):
    try:
        response = client.auth.sign_in_with_password(
            credentials={"email": email, "password": password}
        )
        return {"message": "Login successful", "details": jsonable_encoder(response)}
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/get_all_cars")
def get_all_cars(
    access_token: str,
    refresh_token: str,
    client: Annotated[Client, Depends(get_session)],
    page: int = 0,
    limit: int = 20,
    cut_off_price: int = 500,
    domain: str = None,
):
    try:
        auth = client.auth.set_session(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        response = (
            client.table("Vehicles")
            .select("*, comparisons(*)")
            .limit(limit)
            .offset(page)
            .order("matching_percentage", desc=True, foreign_table="comparisons")
            .execute()
        )
        vehicles = []
        for vehicle in response.data:
            comparison_prices = [x["price"] for x in vehicle["comparisons"]]
            comparison_prices = [0] if not comparison_prices else comparison_prices
            vehicle["lowest_price"] = min(comparison_prices)
            vehicle["average_price"] = sum(comparison_prices) / len(comparison_prices)

            avg_price = get_avg_price_based_on_domain(vehicle["comparisons"])
            vehicle["average_price_based_on_best_match"] = avg_price
            if vehicle["price_with_tax"] < avg_price:
                vehicle["card_color"] = "green"
            elif abs(vehicle["price_with_tax"] - avg_price) >= cut_off_price:
                vehicle["card_color"] = "red"
            else:
                vehicle["card_color"] = "yellow"

            vehicles.append(vehicle)
        return {
            "session": jsonable_encoder(auth),
            "details": jsonable_encoder(vehicles),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/get_car_comparisons")
def get_car_comparisons(
    access_token: str,
    refresh_token: str,
    client: Annotated[Client, Depends(get_session)],
    car_id: str,
):
    try:
        auth = client.auth.set_session(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        response = (
            client.table("comparisons")
            .select("*")
            .order("matching_percentage", desc=True)
            .eq("parent_car_id", car_id)
            .execute()
        )
        return {
            "session": jsonable_encoder(auth),
            "details": jsonable_encoder(response),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/scrape_status")
def get_status(
    access_token: str,
    refresh_token: str,
    client: Annotated[Client, Depends(get_session)],
):
    try:
        auth = client.auth.set_session(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        response = client.table("Status").select("*").execute()
        return {
            "session": jsonable_encoder(auth),
            "details": jsonable_encoder(response),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/start_scraping")
def get_start_scraping(
    access_token: str,
    refresh_token: str,
    background_task: BackgroundTasks,
    client: Annotated[Client, Depends(get_session)],
    dev: bool = True,
):
    try:
        auth = client.auth.set_session(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        response = client.table("Status").select("status").eq("id", 1).execute()
        if response.data[0]["status"] != "running":
            background_task.add_task(start_services, dev)
            client.table("Status").update(
                {
                    "id": 1,
                    "status": "running",
                    "started_at": datetime.now().isoformat(),
                    "total_completed": 0,
                }
            ).eq("id", 1).execute()
            return {
                "message": "Scraping started",
                "session": jsonable_encoder(auth),
            }
        else:
            return {
                "message": "Scraping already started",
                "session": jsonable_encoder(auth),
            }
    except Exception as e:
        client.table("Status").update(
            {"id": 1, "status": "failed", "stopped_at": datetime.now().isoformat()}
        ).eq("id", 1).execute()
        raise HTTPException(status_code=500, detail=str(e))
    except AuthApiError:
        client.table("Status").update(
            {"id": 1, "status": "failed", "stopped_at": datetime.now().isoformat()}
        ).eq("id", 1).execute()
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/upload")
async def upload_file(file: UploadFile):
    """
    Upload a large file to the server via streaming.

    Args:
        file (UploadFile): The file to upload (.xlsx or .xls)

    Returns:
        dict: Upload status and file path
    """
    # Validate file
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = {".xlsx", ".xls"}
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed"
        )

    try:
        # Stream the file to disk in chunks
        async with aiofiles.open(OUT_FILE, "wb") as out_file:
            while chunk := await file.read(256 * 256):  # Read 1MB chunks
                await out_file.write(chunk)

    except Exception as e:
        # Clean up if something goes wrong
        if os.path.exists(OUT_FILE):
            os.remove(OUT_FILE)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

    finally:
        # Ensure the file is closed
        await file.close()
    return {"message": "File uploaded successfully", "file_path": OUT_FILE}


if __name__ == "__main__":
    client = get_session()
    start_services(dev=True)


# Try to set up the api on the server.

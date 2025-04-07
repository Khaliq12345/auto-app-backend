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

OUT_FILE = "25630.xlsx"
session_deps = Depends()


def get_session() -> Client:
    client: Client = create_client(
        supabase_key=utils.supabase_key, supabase_url=utils.url
    )
    return client


def start_services(client: Client, dev: bool = True):
    if dev:
        df = pd.read_excel("25630.xlsx", header=None).sample(10)
    else:
        df = pd.read_excel("25630.xlsx", header=None)
    for row_id in range(len(df)):
        car_dict = utils.get_row_dict(df, row_id)
        print(f"Car Info - {car_dict}")
        thread1 = threading.Thread(target=autoscout24.main, args=(car_dict,))
        thread2 = threading.Thread(target=lacentrale.main, args=(car_dict,))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        client.table("Status").upsert(
            {
                "id": 1,
                "status": "success",
                "stopped_at": datetime.now().isoformat(),
                "total_completed": row_id + 1,
                "total_running": len(df),
            }
        ).execute()


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
            credentials={"email": "test@gmail.com", "password": "test12345"}
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
):
    try:
        auth = client.auth.set_session(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        response = (
            client.table("Vehicles").select("*").limit(limit).offset(page).execute()
        )
        return {
            "session": jsonable_encoder(auth),
            "details": jsonable_encoder(response),
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
        background_task.add_task(start_services, client, dev)
        return {
            "message": "Scraping started",
            "session": jsonable_encoder(auth),
        }
    except Exception as e:
        client.table("Status").upsert(
            {"id": 1, "status": "failed", "stopped_at": datetime.now().isoformat()}
        ).execute()
        raise HTTPException(status_code=500, detail=str(e))
    except AuthApiError:
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
    start_services(dev=True)


# Try to set up the api on the server.

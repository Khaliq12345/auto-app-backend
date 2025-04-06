from services import autoscout24, lacentrale
import pandas as pd
from utilities import utils
import threading
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from supabase import Client, AuthApiError, create_client
from datetime import datetime


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


if __name__ == "__main__":
    start_services(dev=True)


# Try to set up the api on the server.

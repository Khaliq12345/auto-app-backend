from celery import Celery

from app import start_services
from config import config

# Create Celery app instance
celery_app = Celery(
    "auto_app",
    broker=config.CELERY_BROKER_URL,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="Europe/Paris",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,  # Process one task at a time
)


@celery_app.task(bind=True, name="celery_app.start_services_task")
def start_services_task(
    self,
    mileage_plus_minus: int,
    ignore_old: bool,
    sites_to_scrape: list[str],
    dev: bool = True,
    car_id: int | str | None = None,
):
    try:
        # Update task state to indicate it's running
        self.update_state(state="RUNNING", meta={"status": "Scraping in progress"})

        # Call start_services function
        start_services(
            mileage_plus_minus=mileage_plus_minus,
            ignore_old=ignore_old,
            sites_to_scrape=sites_to_scrape,
            dev=dev,
            car_id=car_id,
        )

        return {"status": "completed", "message": "Scraping completed successfully"}

    except Exception as e:
        raise e

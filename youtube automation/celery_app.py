import os
from celery import Celery
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)

celery_app = Celery(
    "youtube_automation",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

celery_app.conf.task_routes = {
    "tasks.generate_content_task": {"queue": "generation"}
}
celery_app.conf.task_track_started = True
celery_app.conf.result_extended = True
celery_app.conf.worker_send_task_events = True
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"
celery_app.conf.task_serializer = "json"
celery_app.conf.timezone = "UTC"

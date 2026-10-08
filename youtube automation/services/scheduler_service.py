import uuid
from datetime import datetime, timedelta
from typing import List, Dict

from database.database import DatabaseManager
from utils.logger import logger


def schedule_upload(
    video_path: str,
    title: str,
    description: str,
    publish_at: datetime = None,
    privacy_status: str = "private"
) -> Dict:
    """Schedule a video for future publishing and persist the upload queue."""
    DatabaseManager.init_db()

    if publish_at is None:
        publish_at = datetime.utcnow() + timedelta(hours=1)

    if isinstance(publish_at, str):
        publish_at = datetime.fromisoformat(publish_at)

    job_id = uuid.uuid4().hex
    job = {
        "job_id": job_id,
        "video_path": video_path,
        "title": title,
        "description": description,
        "publish_at": publish_at.isoformat(),
        "privacy_status": privacy_status,
        "status": "scheduled",
        "created_at": datetime.utcnow().isoformat(),
        "youtube_url": None
    }

    DatabaseManager.save_schedule_job(job)
    logger.info(f"Scheduled upload {job_id} for {publish_at.isoformat()}")
    return job


def get_upload_queue() -> List[Dict]:
    DatabaseManager.init_db()
    return DatabaseManager.get_schedule_queue()


def mark_upload_completed(job_id: str, youtube_url: str) -> Dict:
    DatabaseManager.init_db()
    DatabaseManager.update_schedule_status(job_id, "uploaded", youtube_url=youtube_url)
    return DatabaseManager.get_schedule_job(job_id)

import uuid
from celery_app import celery_app
from database.database import DatabaseManager
from services.generation_service import run_generation_pipeline


@celery_app.task(bind=True)
def generate_content_task(self, payload: dict):
    task_id = self.request.id or str(uuid.uuid4())
    DatabaseManager.save_task(
        task_id=task_id,
        user_id=payload.get("user_id", "anonymous"),
        topic=payload.get("topic", ""),
        mode=payload.get("mode", "Full AI Auto Mode"),
        payload=payload,
        status="PROCESSING",
        progress=0,
    )

    try:
        result = run_generation_pipeline(payload, task_id)
        DatabaseManager.update_task(
            task_id=task_id,
            status=result.get("status", "COMPLETED"),
            progress=result.get("progress", 100),
            result=result,
            error=None,
        )
        return result
    except Exception as exc:
        DatabaseManager.update_task(
            task_id=task_id,
            status="FAILED",
            progress=0,
            result=None,
            error=str(exc),
        )
        raise

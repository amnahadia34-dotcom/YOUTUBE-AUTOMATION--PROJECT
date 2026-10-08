import json
from fastapi import FastAPI, HTTPException
from models.schemas import TaskRequest
from tasks import generate_content_task
from database.database import DatabaseManager
from utils.logger import logger

app = FastAPI(title="YouTube Automation Backend")


@app.get("/")
def root():
    return {"message": "YouTube Automation API Running 🚀"}


@app.post("/generate-task")
async def create_generation_task(request: TaskRequest):
    payload = request.dict()
    celery_result = generate_content_task.apply_async(args=[payload])
    return {
        "task_id": celery_result.id,
        "status": "QUEUED",
        "detail": "Task accepted for background processing. Poll /task-status/{task_id} for updates."
    }


@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    task_record = DatabaseManager.get_task(task_id)
    if not task_record:
        raise HTTPException(status_code=404, detail="Task not found")
    result = task_record.get("result")
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            pass

    return {
        "task_id": task_id,
        "status": task_record["status"],
        "progress": task_record["progress"],
        "result": result,
        "error": task_record.get("error"),
        "updated_at": task_record.get("updated_at")
    }


@app.get("/tasks")
def list_tasks(user_id: str = None):
    records = DatabaseManager.list_tasks(user_id)
    return {"tasks": records}


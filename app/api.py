from fastapi import APIRouter
from app.tasks import process_image_task
from celery.result import AsyncResult

router = APIRouter()

@router.post("/process-image/")
def process_image(file_key: str):
    """Queue an image processing task."""
    task = process_image_task.delay(file_key)
    return {"task_id": task.id, "status": "queued"}

@router.get("/task/{task_id}")
def get_task_status(task_id: str):
    """Check Celery task status."""
    result = AsyncResult(task_id)
    return {"task_id": task_id, "status": result.status, "result": result.result}

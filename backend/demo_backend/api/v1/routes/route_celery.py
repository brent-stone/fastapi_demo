"""
Celery test routes
"""
from logging import getLogger

from demo_backend.celery import create_task
from demo_backend.schemas.celery_job import CeleryJobCreate
from demo_backend.schemas.celery_job import CeleryJobResponse
from celery.result import AsyncResult
from fastapi import APIRouter
from fastapi import Response
from fastapi import status

logger = getLogger(__name__)

router = APIRouter()


@router.post(
    "/create-task",
    response_model=CeleryJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_task(celery_job: CeleryJobCreate, response: Response):
    """
    Example celery task queuing route
    """
    task_type: int = celery_job.type
    task = create_task.delay(task_type)
    return CeleryJobResponse(
        task_id=task.id, task_status=task.status, task_result=task.result
    )


@router.get(
    "/get/{task_id}",
    response_model=CeleryJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def get_status(task_id: str):
    """
    Example celery task status request route
    """
    task_result = AsyncResult(task_id)
    l_celery_job_response = CeleryJobResponse(
        task_id=task_id,
        task_status=task_result.status,
        task_result=task_result.result,
    )
    return l_celery_job_response

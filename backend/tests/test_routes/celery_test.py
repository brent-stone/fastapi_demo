from logging import getLogger
from typing import List

from demo_backend.schemas.celery_job import CeleryJobCreate
from fastapi import status
from fastapi.responses import Response
from requests import Response

logger = getLogger(__name__)


def test_create_celery_task(client):
    l_tasks: List[CeleryJobCreate] = []
    l_responses: List[Response] = []
    # Enqueue three tasks of varying length
    for i in range(1, 4):
        l_task: CeleryJobCreate = CeleryJobCreate(type=i)
        l_tasks.append(l_task)
        l_response: Response = client.post("/celery/create-task", l_task.json())
        l_responses.append(l_response)
        logger.debug(
            f"[test_create_celery_task] response: [{l_response.status_code}] {l_response.text}"
        )
        assert l_response.status_code == status.HTTP_201_CREATED

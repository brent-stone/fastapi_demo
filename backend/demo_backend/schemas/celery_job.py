from typing import Optional

from pydantic import BaseModel
from pydantic import conint


class CeleryJobCreate(BaseModel):
    """
    Test schema for queueing celery jobs
    """

    type: conint(ge=0)


class CeleryJobResponse(BaseModel):
    """
    Test schema for responding to celery job queue requests
    """

    task_id: str
    task_status: Optional[str] = None
    task_result: Optional[str] = None

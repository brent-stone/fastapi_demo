"""
Example celery hooks into redis
"""
import os
import time

from demo_backend.core.config import core_config
from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = core_config.CELERY_BROKER_URL
celery.conf.result_backend = core_config.CELERY_RESULT_BACKEND


@celery.task(name="create_task")
def create_task(task_type: int):
    """
    testing
    """
    time.sleep(task_type * 2)
    return True

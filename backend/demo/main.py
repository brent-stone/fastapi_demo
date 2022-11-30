"""
Primary FastAPI application instance creation
"""
from demo.core.config import core_config
from demo.core.config import core_logger
from fastapi import FastAPI


def get_application() -> FastAPI:
    """
    FastAPI application creation entrypoint
    """
    _app = FastAPI(title=core_config.PROJECT_NAME, version=core_config.PROJECT_VERSION)
    core_logger.info("Hello, logging!")

    return _app


app = get_application()

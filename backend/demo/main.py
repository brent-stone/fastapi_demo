"""
Primary FastAPI application instance creation
"""
from fastapi import FastAPI
from demo.core.config import core_config, core_logger


def get_application() -> FastAPI:
    """
    FastAPI application creation entrypoint
    """
    _app = FastAPI(title=core_config.PROJECT_NAME, version=core_config.PROJECT_VERSION)
    core_logger.info("Hello, logging!")

    return _app


app = get_application()

"""
Primary FastAPI application instance creation
"""
from demo.core.config import core_config
from demo.core.config import core_logger
from demo.core.handlers import create_start_app_handler
from demo.core.handlers import create_stop_app_handler
from fastapi import FastAPI


def get_application() -> FastAPI:
    """
    FastAPI application creation entrypoint
    """
    _app = FastAPI(title=core_config.PROJECT_NAME, version=core_config.PROJECT_VERSION)
    _app.add_event_handler("startup", create_start_app_handler(_app, core_config))
    _app.add_event_handler("shutdown", create_stop_app_handler(_app))

    core_logger.info("Hello, logging!")

    return _app


app = get_application()

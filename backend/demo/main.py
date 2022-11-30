"""
Primary FastAPI application instance creation
"""
from demo.core.config import core_config
from demo.core.config import CoreConfig
from demo.core.handlers import create_start_app_handler
from demo.core.handlers import create_stop_app_handler
from fastapi import FastAPI


def get_application(a_config: CoreConfig = core_config) -> FastAPI:
    """
    FastAPI application creation entrypoint
    """
    _app = FastAPI(title=a_config.PROJECT_NAME, version=a_config.PROJECT_VERSION)
    _app.add_event_handler("startup", create_start_app_handler(_app, a_config))
    _app.add_event_handler("shutdown", create_stop_app_handler(_app))

    return _app


app = get_application()

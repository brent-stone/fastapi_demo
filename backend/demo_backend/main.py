from demo_backend.api import api_router
from demo_backend.core.config import core_config
from demo_backend.core.tasks import create_start_app_handler
from demo_backend.core.tasks import create_stop_app_handler
from demo_backend.database import Base
from demo_backend.database import engine_default  # , SessionLocal, Base, get_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseSettings
from sqlalchemy.engine import Engine


def create_tables(a_engine: Engine = engine_default) -> None:
    Base.metadata.create_all(bind=a_engine)


def include_routes(app: FastAPI) -> None:
    app.include_router(api_router)


def get_application(a_config: BaseSettings = core_config) -> FastAPI:
    _app = FastAPI(title=core_config.PROJECT_NAME, version=core_config.PROJECT_VERSION)
    include_routes(_app)
    create_tables()

    _app.add_event_handler("startup", create_start_app_handler(_app, a_config))
    _app.add_event_handler("shutdown", create_stop_app_handler(_app))

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in core_config.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()
# if not core_config.DEBUG:
#     # Initialize the database here only if we're not testing. Otherwise, allow pytest
#     # setup to do this. The problem (Brent assumes) is that importing the demo_backend package
#     # will end up importing the fully initialized 'app' with the default engine using
#     # a full postgresql database URI. By skipping this step it allows pytest an
#     # opportunity to initialize the database seperate from the app startup.
#     create_tables()

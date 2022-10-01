from typing import Callable

from demo_backend.database.tasks import close_db_connection
from demo_backend.database.tasks import connect_to_db
from demo_backend.core.config import core_config
from pydantic import BaseSettings
from fastapi import FastAPI


def create_start_app_handler(
    app: FastAPI, a_config: BaseSettings = core_config
) -> Callable:
    """Add additional state attributes to app such as a database connection.

    Args:
        app (FastAPI): The FastAPI object from demo_backend.main
        a_config (BaseSettings, optional): The BaseSettings from demo_backend.core.config.
        Defaults to environment variable populated core_config.

    Returns:
        Callable: A function to modify the original FastAPI app object.
    """

    async def start_app() -> None:
        await connect_to_db(app, a_config)

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await close_db_connection(app)

    return stop_app

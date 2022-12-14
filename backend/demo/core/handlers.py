"""
FastAPI Middleware startup and shutdown handlers
"""
from typing import Callable

from databases import Database
from databases import DatabaseURL
from demo.api.v1 import api_router_v1
from demo.core.config import core_config
from demo.core.config import core_logger as logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseSettings
from starlette.config import Config


def create_start_app_handler(
    a_app: FastAPI, a_config: BaseSettings = core_config
) -> Callable:
    """Add additional state attributes to app such as a database connection.

    Args:
        a_app (FastAPI): The FastAPI object from demo.main
        a_config (BaseSettings, optional): The BaseSettings from demo.core.config
        Defaults to environment variable populated core_config.

    Returns:
        Callable: A function to modify the original FastAPI app object.
    """

    async def start_app() -> None:
        """
        Mutate the FastAPI app instance prior to startup
        :return: Nothing
        """
        a_app.include_router(api_router_v1)
        a_app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in core_config.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Attempt to connect to the database
        config = Config()
        l_db_url = config(
            "DATABASE_URL",
            cast=DatabaseURL,
            default=a_config.DATABASE_URI,
        )
        # these can be configured in config as well
        database = Database(l_db_url)

        try:
            await database.connect()
            a_app.state._db = database
        except Exception as e:
            logger.warning("--- DB CONNECTION ERROR ---")
            logger.warning(e)
            logger.warning("--- DB CONNECTION ERROR ---")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    FastAPI Shutdown functions
    :param app: The FastAPI instance
    :return: A mutated FastAPI instance
    """

    async def stop_app() -> None:
        """
        Mutate the FastAPI app instance prior to shut down
        :return: Nothing
        """
        try:
            await app.state._db.disconnect()
        except Exception as e:
            logger.warning("--- DB DISCONNECT ERROR ---")
            logger.warning(e)
            logger.warning("--- DB DISCONNECT ERROR ---")

    return stop_app

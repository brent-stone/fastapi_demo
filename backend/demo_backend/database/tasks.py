import logging

from demo_backend.core.config import core_config
from pydantic import BaseSettings
from databases import Database
from databases import DatabaseURL
from fastapi import FastAPI
from starlette.config import Config

logger = logging.getLogger(__name__)


async def connect_to_db(app: FastAPI, a_config: BaseSettings = core_config) -> None:
    """Enable a database connection to the FastAPI app.state_db. Pass in a config
    in case we're using pytest and want to override the default postgresql URI generated
    from the .env file with something like a local sqlite database URI.

    Args:
        app (FastAPI): The FastAPI object from demo_backend.main
        a_config (BaseSettings, optional): The BaseSettings from demo_backend.core.config.
        Defaults to environment variable populated core_config.
    """
    # postfix = ""
    # if core_config.DEBUG:
    #     postfix = "_test"

    config = Config()
    l_db_url = config(
        "DATABASE_URL",
        cast=DatabaseURL,
        # default=core_config.DATABASE_URI + postfix,
        default=a_config.DATABASE_URI,
    )
    # these can be configured in config as well
    database = Database(l_db_url)

    try:
        await database.connect()
        app.state._db = database
    except Exception as e:
        logger.warning("--- DB CONNECTION ERROR ---")
        logger.warning(e)
        logger.warning("--- DB CONNECTION ERROR ---")


async def close_db_connection(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
    except Exception as e:
        logger.warning("--- DB DISCONNECT ERROR ---")
        logger.warning(e)
        logger.warning("--- DB DISCONNECT ERROR ---")

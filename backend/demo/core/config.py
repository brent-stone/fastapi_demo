"""
FastAPI App primary global configuration which primarily relies upon .env file provided
values.
"""
from enum import Enum
from logging import captureWarnings
from logging import debug
from logging import error
from logging import getLogger
from logging import info
from logging import warning
from logging.config import dictConfig
from os import getenv
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import quote_plus

from dotenv import find_dotenv
from dotenv import load_dotenv
from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import Field
from pydantic import PostgresDsn
from pydantic import RedisDsn
from pydantic import SecretStr
from pydantic import validator


testing_postfix_str: str = "_test"


if not getenv("PROJECT_NAME"):
    """We may be running Alembic on a host machine so environment variables weren't sent
    via docker. Let's try to find a .env file and load its variables into the
    environment.
    """
    # first try to find a .test.env dev configuration then a production .env
    l_env_targets: List[str] = [".test.env", ".env"]
    l_env_target: str = ""

    for l_env_target in l_env_targets:
        # Iterate through all the backup .env file names
        l_env_path: str = find_dotenv(
            l_env_target, usecwd=True, raise_error_if_not_found=False
        )
        # If we received a non-empty string for the .env path, record the path
        # and proceed
        if bool(l_env_path):
            l_env_target = l_env_path
            info(
                f"No environment variables appear to be set. Using values found in"
                f" {l_env_target}\n"
            )
            break

    # Only attempt to load a .env file if we successfully found one
    if bool(l_env_target):
        load_dotenv(dotenv_path=l_env_target, verbose=True, override=False)


class LogLevel(str, Enum):
    """
    Explicit enumerated class for acceptable Uvicorn log levels.
    This type is primarily consumed by the core_logger setup.
    """

    critical = "critical"
    error = "error"
    warning = "warning"
    info = "info"
    debug = "debug"


class CoreConfig(BaseSettings):
    """
    Primary Pydantic parser for environment variables used throughout the API layer.

    Note: Pydantic's BaseSettings class will automatically pull in environmental
    values when setting the 'env' flag in Field.
    """

    DEBUG: bool = Field(..., env="DEBUG")
    LOG_LEVEL: LogLevel = Field(..., env="LOG_LEVEL")

    PROJECT_NAME: str = Field(..., env="PROJECT_NAME")
    PROJECT_VERSION: str = Field(..., env="PROJECT_VERSION")

    DEFAULT_USERNAME: str = Field(..., env="DEFAULT_USERNAME")
    DEFAULT_USER_PASS: str = Field(..., env="DEFAULT_USER_PASS")
    DEFAULT_EMAIL: str = Field(..., env="DEFAULT_EMAIL")

    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    HASH_ALGORITHM: str = Field(..., env="HASH_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        ..., env="ACCESS_TOKEN_EXPIRE_MINUTES", gt=0
    )
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    POSTGRES_SERVER: str = Field(..., env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    # Note: Pydantic SecretStr requires an explicit call to the .get_secret_value()
    # function to get a cleartext value
    # An example of this in action is the generate_db_uri() function below.
    POSTGRES_PASSWORD: SecretStr = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    POSTGRES_PORT: str = Field(..., env="POSTGRES_PORT")
    DATABASE_URI: Optional[PostgresDsn] = None
    DATABASE_URI_GENERIC: Optional[PostgresDsn] = None

    CELERY_BROKER_URL: RedisDsn = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: RedisDsn = Field(..., env="CELERY_RESULT_BACKEND")
    celery_concurrency_count: int = 0
    celery_worker_count: int = 0

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """
        Pre-parse the string of acceptable CORS origins from environment variable
        :param v: The raw string passed in from the environment variable
        :return: A list of substrings, one entry per URL or IP substring
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Pydantic field ordering rules should ensure that POSTGRES_DB is updated prior to
    # DATABASE_URI. Thus, we can append testing_postfix to POSTGRES_DB here and all
    # areas that would use the modified string, such as Alembic's env.py, automatically
    # get the correct database name.
    # https://pydantic-docs.helpmanual.io/usage/models/#field-ordering

    # Note from Brent: Accessing CLASS (not object) variables is super awkward in Python
    # and prone to difficult bugs. I got this template code from the fastapi
    # auto-template project linked below, but I honestly have no idea how the 'values'
    # dict is making it into this function.
    # https://github.com/ycd/manage-fastapi
    @validator("DATABASE_URI")
    def generate_db_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """
        Populate the primary postgres database URI for the API to find the service.

        NOTE: Docker Compose's service alias' like "db" will include any changes to
        the service's port. Thus, if we specify port here then the connection will
        be refused because SQLAlchemy will be looking for a connection like
        0.0.0.0:57074:57074  Simply let compose handle changes to the port via the
        alias stored in POSTGRES_SERVER.

        Rely upon the DEBUG environment variable to differentiate when and when not
        to include the POSTGRES_PORT in the PostgresDsn creation.
        If True (we expect to be working outside the container like localhost) then
        include POSTGRES PORT.
        If False, don't include POSTGRES_PORT and rely on Docker Compose aliasing
        """
        # Boilerplate which shouldn't be triggered. Warn if it is.
        if isinstance(v, str):
            warning(f"Database URI provided instead of auto-genreated: {v}")
            return v

        debug(
            f"[demo.core.config]: postgresql://{values.get('POSTGRES_USER')}: \
            {values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}: \
                {values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
        )

        if str(values.get("DEBUG")).lower() == "true":
            info(
                "[demo.core.config]: Using internal container Postgres URI that "
                "doesn't include port"
            )
            # Include POSTGRES_PORT
            return PostgresDsn.build(
                scheme="postgresql",
                # It's necessary to escape special characters in order for Pydantic,
                # Alembic, and inter-container comms to Postgres to behave well
                user=quote_plus(values.get("POSTGRES_USER")),
                password=quote_plus(values.get("POSTGRES_PASSWORD").get_secret_value()),
                host=quote_plus(values.get("POSTGRES_SERVER")),
                port=quote_plus(values.get("POSTGRES_PORT")),
                path=f"/{quote_plus(values.get('POSTGRES_DB'))}",
            )
        else:
            info(
                "[demo.core.config]: Using external to container Postgres URI that "
                "does include port"
            )
            # Don't include the POSTGRES_PORT. See discussion above.
            return PostgresDsn.build(
                scheme="postgresql",
                user=quote_plus(values.get("POSTGRES_USER")),
                password=quote_plus(values.get("POSTGRES_PASSWORD").get_secret_value()),
                host=quote_plus(values.get("POSTGRES_SERVER")),
                # port=quote_plus(values.get("POSTGRES_PORT")),
                path=f"/{quote_plus(values.get('POSTGRES_DB'))}",
            )

    @validator("DATABASE_URI_GENERIC")
    def generate_db_uri_generic(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """It's possible (likely even) that the test database doesn't exist yet.
        However, our default DATABASE_URI will return a string with pinpoint info
        to try to connect to a particular database. The result is Alembic, pytest,
        etc. will potentially crash trying to connect directly to a non-existent
        database.

        Thus, we're going to use DATABASE_URI less the POSTGRES_DB portion to open
        a generic connection to Postgres.

        This is primarily used in alembic's env.py run_migrations_online() script.

        Example:
        Original: postgresql://demo:pass@localhost/demo_test
        Rsplit: ['postgresql://dem_backend:pass@localhost', 'demo_test']
        Return value: postgresql://demo:pass@localhost

        Args:
            v (Optional[str]): The auto-generated DATABASE_URI
            values (Dict[str, Any]): Dict of currently processed environment variables

        Returns:
            Any: A database URI less the trailing '/table_name'
        """
        # Right split on the 1st rightmost '/' character, then return leading token.
        try:
            return values.get("DATABASE_URI").rsplit("/", 1)[0]
        except (ValueError, IndexError, AttributeError) as e:
            error(
                f"Failed to generate generic database URI less the specific \
                database target: {e}"
            )
            return values.get("DATABASE_URI")

    class Config:
        """
        Customize the default BaseSettings class behavior
        """

        case_sensitive = True
        # env_file = ".env"


core_config = CoreConfig()


LOG_CONFIG = {
    "version": 1,
    # "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "%(levelname)s:\t [%(filename)s:%(funcName)s:%(lineno)d]:\t %(message)s"
        }
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": core_config.LOG_LEVEL.upper(),
        }
    },
    "root": {"handlers": ["console"], "level": core_config.LOG_LEVEL.upper()},
    "loggers": {
        "gunicorn": {"propagate": True},
        "gunicorn.access": {"propagate": True},
        "gunicorn.error": {"propagate": True},
        "uvicorn": {"propagate": True},
        "uvicorn.access": {"propagate": True},
        "uvicorn.error": {"propagate": True},
        # https://docs.celeryq.dev/en/stable/userguide/tasks.html#logging
        "celery": {"propagate": True},
        "celery.task": {"propagate": True},
        "celery.app.trace": {"propagate": True},
    },
}

captureWarnings(True)
dictConfig(LOG_CONFIG)
core_logger = getLogger(__name__)
core_logger.debug(str(core_config))

from logging import getLogger
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


logger = getLogger(__name__)

testing_postfix_str: str = "_test"


if not getenv("PROJECT_NAME"):
    """We may be running Alembic on a host machine so environment variables weren't sent
    via docker. Let's try to find a .env file and load it's variables into the
    environment.
    """
    # first try to find a .test.env then a production .env
    l_env_targets: List[str] = [".test.env", ".env"]
    l_env_target: Optional[str] = None
    l_env_path: Optional[str] = None

    for l_env_target in l_env_targets:
        l_env_path = find_dotenv(
            l_env_target, usecwd=True, raise_error_if_not_found=False
        )
        if bool(l_env_target):
            logger.warning(
                f"No environment variables appear to be set. Using values found in {l_env_path}\n"
            )
            break

    if bool(l_env_target) and l_env_path is not None:
        load_dotenv(dotenv_path=l_env_path, verbose=True, override=False)


class CoreConfig(BaseSettings):
    """
    Primary Pydantic parser for environment variables used throughout the API layer.
    """

    DEBUG: bool = Field(..., env="DEBUG")

    PROJECT_NAME: str = Field(..., env="PROJECT_NAME")
    PROJECT_VERSION: str = Field(..., env="PROJECT_VERSION")
    DEFAULT_EMAIL: str = Field(..., env="DEFAULT_EMAIL")

    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    HASH_ALGORITHM: str = Field(..., env="HASH_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        ..., env="ACCESS_TOKEN_EXPIRE_MINUTES", gt=0
    )
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Note: Pydantic's BaseSettings class will automatically pull in environmental
    # values when setting the 'env' flag in Field
    POSTGRES_SERVER: str = Field(..., env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    # Note: Pydantic SecretStr requires an explicit call to the .get_secret_value()
    # function to get a cleartext value
    # An example of this in action is the generate_db_uri() function below.
    POSTGRES_PASSWORD: SecretStr = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    POSTGRES_PORT: str = Field(..., env="POSTGRES_PORT")
    DATABASE_URI: Optional[PostgresDsn] = None
    # Default URI used when creating new databases. Doesn't attempt to connect to any pre-existing database.
    DATABASE_URI_GENERIC: Optional[PostgresDsn] = None
    # This is only used to create an empty database for the default user. The official Postgres container image is
    # supposed to do then when provided POSTGRES_USER and POSTGRES_PASSWORD environmental variables; however, as of
    # October 2022, it does not and will complain with 'FATAL:  database "<username>" does not exist.
    DATABASE_URI_USER: Optional[PostgresDsn] = None

    CELERY_BROKER_URL: RedisDsn = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: RedisDsn = Field(..., env="CELERY_RESULT_BACKEND")

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # NOTE: This method for ensuring *_text database names when is left as a reference.
    # However, Brent recommends the more cognitively simple and predictable strategy of
    # relying on a manually named *_test POSTGRES_DB value in .test.env in the /backend
    # or .env in the top-level environment variable file.

    # Pydantic field ordering rules should ensure that POSTGRES_DB is updated prior to
    # DATABASE_URI. Thus, we can append testing_postfix to POSTGRES_DB here and all
    # areas that would use the modified string, such as Alembic's env.py, automatically
    # get the correct database name.
    # https://pydantic-docs.helpmanual.io/usage/models/#field-ordering
    # @validator("POSTGRES_DB")
    # def append_db_name_if_testing(cls, v: Optional[str], values: Dict[str, Any]) -> str:
    #     if not isinstance(v, str):
    #         logger.error(
    #             "Failed to get a valid POSTGRES_DB value from environment or .env"
    #         )
    #         raise ValueError
    #     # Append the testing postfix string to the database name if we're in DEBUG mode.
    #     if values.get("DEBUG") is True:
    #         v += testing_postfix_str
    #         logger.info(f"POSTGRES_DB updated for testing to: {v}")
    #     return v

    # Note from Brent: Accessing CLASS (not object) variables is super awkward in Python
    # and prone to difficult bugs. I got this template code from the fastapi
    # auto-template project linked below but I honestly have no idea how the 'values'
    # dict is making it into this function.
    # https://github.com/ycd/manage-fastapi
    @validator("DATABASE_URI")
    def generate_db_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        # Boilerplate which shouldn't be triggered. Warn if it is.
        if isinstance(v, str):
            logger.warning(f"Database URI provided instead of auto-genreated: {v}")
            return v

        logger.debug(
            f"[demo_backend.core.config]: postgresql://{values.get('POSTGRES_USER')}: \
            {values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}: \
                {values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
        )

        return PostgresDsn.build(
            scheme="postgresql",
            # It's necessary to escape special characters in order for Pydantic,
            # Alembic, and inter-container comms to Postgres to behave well
            user=quote_plus(values.get("POSTGRES_USER")),
            password=quote_plus(values.get("POSTGRES_PASSWORD").get_secret_value()),
            host=quote_plus(values.get("POSTGRES_SERVER")),
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
        Original: postgresql://demo_backend:pass@localhost/demo_pg_test
        Rsplit: ['postgresql://demo_backend:pass@localhost', 'demo_pg_test']
        Return value: postgresql://demo_backend:pass@localhost

        Args:
            v (Optional[str]): The auto-generated DATABASE_URI
            values (Dict[str, Any]): Dict of currently processed environment variables

        Returns:
            Any: A database URI less the trailing '/table_name'
        """
        # Right split on the 1st rightmost '/' character, then return leading token.
        try:
            return values.get("DATABASE_URI").rsplit("/", 1)[0]
        except (ValueError, IndexError) as e:
            logger.error(
                f"Failed to generate generic database URI less the specific \
                database target: {e}"
            )
            return values.get("DATABASE_URI")

    @validator("DATABASE_URI_USER")
    def generate_db_uri_user(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """It's possible (likely even) that the default user database doesn't exist yet.
        The result is postgres will be unhappy when we try to connect with POSTGRES_USER:POSTGRES_PASSWORD credentials.
        Creating a database named the same as the environment variable value for POSTGRES_USER alleviates this problem.
        Note: The official postgres docker container should do this when provided a POSTGRES_USER environment variable;
        however, as of Oct 2022 it doesn't appear to do so and complains that the table is missing.

        This is primarily used in alembic's env.py run_migrations_online() script.

        Args:
            values (Dict[str, Any]): Dict of currently processed environment variables

        Returns:
            Any: A database URI specific to the database with the same name as the value of POSTGRES_USER
        """
        try:
            return PostgresDsn.build(
                scheme="postgresql",
                # It's necessary to escape special characters in order for Pydantic,
                # Alembic, and inter-container comms to Postgres to behave well
                user=quote_plus(values.get("POSTGRES_USER")),
                password=quote_plus(values.get("POSTGRES_PASSWORD").get_secret_value()),
                host=quote_plus(values.get("POSTGRES_SERVER")),
                path=f"/{quote_plus(values.get('POSTGRES_USER'))}",
            )
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to generate user database URI: {e}")
        return ""

    class Config:
        case_sensitive = True
        # env_file = ".env"


core_config = CoreConfig()
logger.debug(str(core_config))

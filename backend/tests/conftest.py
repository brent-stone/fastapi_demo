"""
Shared Pytest fixtures and helper functions

NOTE: Typing Generators follow the pattern Generator[YieldType, SendType, ReturnType]
Generator[str, None, None] is equivalent to Iterator[str] but more precise for the
yield based pytest fixtures below. Iterator[str] was used for clarity and simplicity.
https://docs.python.org/3/library/typing.html#typing.Generator
"""
import secrets
from datetime import date
from datetime import datetime
from logging import getLogger
from string import ascii_letters
from string import ascii_lowercase
from string import digits
from string import punctuation
from typing import Any
from typing import Dict
from typing import Generator
from typing import Optional

import pytest
from demo.core.config import core_config
from demo.core.config import CoreConfig
from demo.main import get_application
from demo.schemas.users import UserAdminCreateUpdateSchema
from demo.schemas.users import UserCreateUpdateSchema
from demo.schemas.users import UserLoginSchema
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from pydantic.errors import EmailError
from pydantic.errors import StrError
from requests import Response

# from fastapi import HTTPException
# from fastapi import status
# from pydantic.errors import MissingError

# from demo.database import Base
# from demo.database import engine_default
# from demo.database import get_db
# from demo.database.repository.users import create_default_admin_db
# from demo.database.repository.users import create_user_db
# from demo.database.repository.users import get_user_by_email_db

# from sqlalchemy import MetaData
# from sqlalchemy.engine.base import Engine
# from sqlalchemy.orm import Session
# from sqlalchemy.orm import sessionmaker


logger = getLogger(__name__)

testing_config: CoreConfig = core_config

# Prep a set of viable characters when generating random passwords
alphabet = ascii_letters + digits + punctuation


@pytest.fixture(scope="session")
def default_test_account() -> UserAdminCreateUpdateSchema:
    """
    Default test account user credentials retrieved from the .env or .test.env file
    :return: A Pydantic schema for the default credentials
    """
    return UserAdminCreateUpdateSchema(
        username=core_config.DEFAULT_USERNAME,
        password=core_config.DEFAULT_USER_PASS,
        email=core_config.DEFAULT_EMAIL,
        is_active=True,
        is_superuser=True,
    )


@pytest.fixture(scope="session")
def default_test_account_login() -> UserLoginSchema:
    """
    Default test account user credentials retrieved from the .env or .test.env file
    :return: A Pydantic schema for the default credentials
    """
    return UserLoginSchema(
        username=core_config.DEFAULT_USERNAME,
        password=core_config.DEFAULT_USER_PASS,
    )


@pytest.fixture(scope="module")
def app() -> Generator[FastAPI, Any, None]:
    """
    Provide an initialized FastAPI fixture for pytest's TestClient wrapper.
    """
    _app: FastAPI = get_application(a_config=testing_config)

    yield _app


# TestingSessionLocal = sessionmaker(
#     autocommit=False, autoflush=False, bind=engine_default
# )


# def override_get_db():
#     """
#     Override the get_db function to ensure a local SQLAlchemy engine is used
#     :return: A SQLAlchemy database Session
#     """
#     db: Optional[TestingSessionLocal] = None
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         if db:
#             db.close()


# @pytest.fixture(scope="module")
# def db_session() -> Generator[TestingSessionLocal, Any, None]:
#     connection = engine_default.connect()
#     transaction = connection.begin()
#     session = TestingSessionLocal(bind=connection)
#     yield session  # use the session in tests.
#     session.close()
#     transaction.rollback()
#     connection.close()


@pytest.fixture(scope="module")
def client(
    app: FastAPI, default_test_account: UserAdminCreateUpdateSchema
) -> Generator[TestClient, Any, None]:
    """
    Create a new pytest TestClient that wraps FastAPI and overrides the `get_db`
    dependency that is injected into routes.

    This also drops and re-initializes the test database tables.
    """
    # app.dependency_overrides[get_db] = override_get_db

    # logger.debug(
    #     f"[client fixture] TestClient creating default user with engine: {db_session.get_bind().engine}"
    # )

    with TestClient(app) as client:
        # Wipe and reset the test database
        # l_metadata: MetaData = Base.metadata
        # l_metadata.drop_all(bind=engine_default, checkfirst=True)
        # l_metadata.create_all(bind=engine_default, checkfirst=True)

        # Add the default account
        # l_session: TestingSessionLocal = next(iter(override_get_db()))
        # l_admin = create_default_admin_db(a_admin=default_test_account, a_db=l_session)

        # if isinstance(l_admin, UserSchema):
        #     logger.info(f"Test client created default user: {l_admin.__dict__}")
        # else:
        #     logger.info("Test client failed to create default user.")
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Failed to instantiate default user account during FastAPI "
        #         "TestClient creation.",
        #     )
        yield client


def user_authentication_headers(
    a_client: TestClient, a_email: str, a_password: str
) -> Optional[Dict[str, str]]:
    """
    Attempt to retrieve an encrypted JWT from the authentication login endpoint
    Args:
        a_client: A FastAPI TestClient instance
        a_email: A valid user email
        a_password: A matching user password

    Returns: An access token upon success; Nothing on error.

    """
    l_data = {"username": a_email, "password": a_password}
    l_response: Response = a_client.post("/v1/login/token", data=l_data)

    if l_response.status_code == 200:
        auth_token = l_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        logger.debug(
            f"[user_authentication_headers] Auth header retrieved for {a_email}"
        )
        return headers
    logger.error(
        f"[user_authentication_headers] Failed to retrieve auth header. Status code: {l_response.status_code} {l_response.text}"
    )
    logger.error(f"[user_authentication_headers request] {l_data}")
    return None


def random_letters(a_length: int = 32) -> str:
    """
    Return a string of random uppercase and lowercase letters a_length long
    Args:
        a_length: Number of characters to return

    Returns: A random string of characters

    """
    return "".join(secrets.choice(ascii_letters) for i in range(a_length))


def random_letters_lower(a_length: int = 32) -> str:
    """
    Return a string of random lowercase letters a_length long

    Args:
        a_length: Number of characters to return

    Returns: A random lowercase string

    """
    return "".join(secrets.choice(ascii_lowercase) for i in range(a_length))


def random_digits(a_length: int = 4) -> str:
    """
    Return a random series of digits a_length long
    Args:
        a_length: Number of digits to return

    Returns: A string of random digits

    """
    return "".join(secrets.choice(digits) for i in range(a_length))


def random_date() -> date:
    """Generate a random date like "YYYY-MM-DD"

    Returns:
        str: A date like "2022-07-20"
    """
    l_year: int = secrets.randbelow(2021)
    if l_year == 0:
        l_year += 1
    l_month: int = secrets.randbelow(12)
    if l_month == 0:
        l_month += 1
    l_day: int = secrets.randbelow(28)
    if l_day == 0:
        l_day += 1
    try:
        return date(l_year, l_month, l_day)
    except ValueError as e:
        logger.error(f"[random_date] Failed to create a random date: {e}")
        return datetime.now().date()


def random_email(
    a_prefix_length: int = 10, a_postfix_length: int = 10, a_top_domain: str = ".com"
) -> str:
    """The database schema normalizes all emails to be case insensitive to
    avoid collisions. This function ensures randomly generated emails don't need to be
    manually altered to be lowercase.

    Args:
        a_prefix_length (int, optional): String length before the @. Defaults to 10.
        a_postfix_length (int, optional): String length after the @. Defaults to 10.
        a_top_domain (str, optional): String after the last '.'. Defaults to ".com".

    Returns:
        str: A random email address with all lowercase characters
    """
    return f"{random_letters_lower(a_prefix_length)}@{random_letters_lower(a_postfix_length)}{a_top_domain}"


def random_password(a_length: int = 16) -> str:
    """
    Generate a random alphanumeric password of a_length characters
    Args:
        a_length: Number of characters the password should contain

    Returns:

    """
    return "".join(secrets.choice(alphabet) for i in range(a_length))


def random_user() -> Optional[UserCreateUpdateSchema]:
    """Generate and create a random user. Ensure an existing email is not used.
    Return UserCreate object.

    Args:
        # db_session (Session): A sqlalchemy Session object

    Returns:
        User: An initialized UserCreate object reflecting the new user info
    """
    # Generate random user email and password info
    l_email = random_email()
    l_password = random_password()

    # # Iterate to ensure the username doesn't already exist
    # logger.debug(f"[random_user] Verifying user doesn't exist: {l_email}")
    # # Iterate over random emails until a collision with an existing user is avoided
    # while get_user_by_email_db(a_email=l_email, a_db=db_session) is not None:
    #     l_email = random_email()
    #     logger.debug(f"[random_user] RETRY: Veryfying user doesn't exist: {l_email}")
    try:
        l_user_create: UserCreateUpdateSchema = UserCreateUpdateSchema(
            username=l_email, email=l_email, password=l_password
        )
    except (ValueError, EmailError, StrError, ValidationError) as e:
        logger.error(f"[random_user] failed to generate random new user: {e}")
        return None

    logger.debug(
        f"[random_user] Returning UserCreate object for: {l_user_create.email}"
    )
    return l_user_create

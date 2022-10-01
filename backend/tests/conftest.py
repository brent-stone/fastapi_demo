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
from typing import Union

import pytest
from demo_backend.core.config import core_config
from demo_backend.core.config import CoreConfig
from demo_backend.database import Base
from demo_backend.database import engine_default
from demo_backend.database import get_db
from demo_backend.database.models.users import User
from demo_backend.database.repository.login import get_user
from demo_backend.database.repository.users import create_new_user
from demo_backend.main import get_application
from demo_backend.schemas.jobs import JobCreate
from demo_backend.schemas.users import UserCreate
from demo_backend.schemas.users import UserLogin
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from fastapi.testclient import TestClient
from pydantic.errors import EmailError
from pydantic.errors import MissingError
from pydantic.errors import StrError
from requests import Response
from sqlalchemy.engine.base import Connection
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

logger = getLogger(__name__)

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# this is to include backend dir in sys.path so that we can import from db,main.py

# Prep a set of viable characters when generating random passwords
alphabet = ascii_letters + digits + punctuation

testing_config: CoreConfig = core_config


@pytest.fixture(scope="session")
def default_test_account() -> UserCreate:
    return UserCreate(
        username=core_config.DEFAULT_EMAIL,
        email=core_config.DEFAULT_EMAIL,
        password=core_config.SECRET_KEY,
    )


@pytest.fixture(scope="session")
def default_test_account_login() -> UserLogin:
    return UserLogin(
        username=core_config.DEFAULT_EMAIL,
        password=core_config.SECRET_KEY,
    )


TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_default
)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# client = TestClient(app)


@pytest.fixture(scope="module")
def app() -> Generator[FastAPI, Any, None]:
    """
    Provide an initialized FastAPI fixture for pytest's TestClient wrapper.
    """
    # _app: FastAPI = get_application(test_engine)
    _app: FastAPI = get_application(a_config=testing_config)

    yield _app


@pytest.fixture(scope="module")
def db_session() -> Generator[TestingSessionLocal, Any, None]:
    connection = engine_default.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session  # use the session in tests.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client(
    app: FastAPI, db_session: TestingSessionLocal, default_test_account: UserCreate
) -> Generator[Optional[TestClient], Any, None]:
    """
    Create a new pytest TestClient that wraps FastAPI and overrides the `get_db`
    dependency that is injected into routes.

    This also drops and re-initializes the test database tables.
    """
    app.dependency_overrides[get_db] = override_get_db

    logger.debug(
        f"[client fixture] TestClient creating default user with engine: {db_session.get_bind().engine}"
    )

    with TestClient(app) as client:
        # Wipe and reset the test database
        Base.metadata.drop_all(engine_default)
        Base.metadata.create_all(bind=engine_default)

        # Add the default account
        l_response = client.post("/users/", data=default_test_account.json())

        if l_response.status_code != status.HTTP_201_CREATED:
            logger.error(
                f"[client fixture] failed to reset test database and create the default account: {default_test_account.email}"
            )
            raise HTTPException(
                status_code=l_response.status_code,
                detail="Failed to instantiate default user account during FastAPI TestClient creation.",
            )
        else:
            logger.info(
                f"[client fixture] created default test account: {default_test_account.email} // {default_test_account.password}"
            )
        yield client


@pytest.fixture(scope="module")  # To support header in requests functionality
def normal_user_token_headers(client: TestClient, db_session: Session):
    return authentication_token_from_email(
        client=client,
        a_email=core_config.DEFAULT_EMAIL,
        a_password=core_config.SECRET_KEY,
        db_session=db_session,
    )


def get_db_session_uri(db_session: Session) -> str:
    """Convenience function to get string representation of Engine's URI from a given
    Session. Session object is likely a fixture from conftest.py

    Args:
        db_session (Session): The active SQLAlchemy Session

    Returns:
        str: A string of the Engine Database URI
    """
    if isinstance(db_session, Session):
        l_engine: Engine = db_session.get_bind()
        return f"{l_engine}"
    else:
        logger.error("db_session is not a valid Session or Connection.")
        return "INVALID_DB_SESSION"


def random_letters(a_length: int = 32) -> str:
    return "".join(secrets.choice(ascii_letters) for i in range(a_length))


def random_letters_lower(a_length: int = 32) -> str:
    return "".join(secrets.choice(ascii_lowercase) for i in range(a_length))


def random_digits(a_length: int = 4) -> str:
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
    # return f"{l_year}-{l_month}-{l_day}"


def random_email(
    prefix_length: int = 10, postfix_length: int = 10, top_domain: str = ".com"
) -> str:
    """The database schema normalizes all emails to be case insentive to avoid
    avoid collisions. This function ensures randomly generated emails don't need to be
    manually altered to be lowercase.

    Args:
        prefix_length (int, optional): String length before the @. Defaults to 10.
        postfix_length (int, optional): String length after the @. Defaults to 10.
        top_domain (str, optional): String after the last '.'. Defaults to ".com".

    Returns:
        str: A random email address with all lowercase characters
    """
    return f"{random_letters_lower(prefix_length)}@{random_letters_lower(postfix_length)}{top_domain}"


def random_password(a_length: int = 16) -> str:
    return "".join(secrets.choice(alphabet) for i in range(a_length))


def random_user(db_session: Session) -> Optional[UserCreate]:
    """Generate and create a random user. Ensure an existing email is not used.
    Return UserCreate object.

    Args:
        db (Session): A sqlalchemy Session object

    Returns:
        User: An initialized UserCreate object reflecting the new user info
    """
    # Generate random user email and password info
    l_email = random_email()
    l_password = random_password()

    # Iterate to ensure the username doesn't already exist
    logger.debug(f"[random_user] Veryfying user doesn't exist: {l_email}")
    # Iterate over random emails until a collision with an existing user is avoided
    while get_user(a_email=l_email, db=db_session) is not None:
        l_email = random_email()
        logger.debug(f"[random_user] RETRY: Veryfying user doesn't exist: {l_email}")

    try:
        l_user_create: UserCreate = UserCreate(
            username=l_email, email=l_email, password=l_password
        )
    except (ValueError, EmailError, StrError) as e:
        logger.error(f"[random_user] failed to generate random new user: {e}")
        return None

    logger.debug(
        f"[random_user] Returning UserCreate object for: {l_user_create.email}"
    )
    return l_user_create


def random_job() -> Optional[JobCreate]:
    try:
        l_job_schema = JobCreate(
            title=random_letters(),
            company=random_letters(),
            company_url=random_letters(),
            location=random_letters(),
            description=random_letters(),
            date_posted=random_date(),
        )
    except (StrError, MissingError, EmailError) as e:
        logger.error(f"[random_job] Failed to create a random job: {e}")
        return None
    return l_job_schema


def user_authentication_headers(
    client: TestClient, a_email: str, a_password: str
) -> Optional[Dict[str, str]]:
    data = {"username": a_email, "password": a_password}
    r: Response = client.post("/login/token", data=data)

    if r.status_code == 200:
        auth_token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        logger.debug(
            f"[user_authentication_headers] Auth header retrieved for {a_email}"
        )
        return headers
    logger.error(
        f"[user_authentication_headers] Failed to retrieve auth header. Status code: {r.status_code} {r.text}"
    )
    logger.error(f"[user_authentication_headers request] {data}")
    return None


def authentication_token_from_email(
    client: TestClient, a_email: str, a_password: str, db_session: Session
) -> Optional[Dict[str, str]]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    logger.debug(f"[authentication_token_from_email] Retrieving user info: {a_email}")
    l_user: Optional[User] = get_user(a_email=a_email, db=db_session)
    if l_user is None:
        # # Create a random new user and ensure there isn't a collision with an existing
        # # user.
        # l_user_create, l_user = random_user(a_db=a_db)
        # Initialize and account for the provided user details
        try:
            l_user_create: UserCreate = UserCreate(
                username=a_email, email=a_email, password=a_password
            )
        except (EmailError, ValueError, StrError) as e:
            logger.error(
                f"[authentication_token_from_email] Failed to create UserCreate object:\
                     {e}"
            )
            return None
        l_user: Optional[User] = create_new_user(a_user=l_user_create, db=db_session)
        if l_user is None:
            logger.debug(
                f"[authentication_token_from_email] Failed to initially register user \
                    {a_email}"
            )
            return None
        else:
            logger.debug(
                f"[authentication_token_from_email] Registered user: {l_user.email}"
            )
    else:
        logger.debug(f"[authentication_token_from_email] User found: {l_user.email}")

    l_header: Optional[Dict[str, str]] = user_authentication_headers(
        client=client, a_email=a_email, a_password=a_password
    )

    if l_header is None:
        logger.debug(
            f"[authentication_token_from_email] Failed to get authentication header for {l_user.email}"
        )
    else:
        logger.debug(
            f"[authentication_token_from_email] Auth token retrieved for {l_user.email}"
        )

    return l_header

from logging import getLogger
from typing import Optional

from demo_backend.schemas.users import UserCreate
from fastapi import status
from fastapi.testclient import TestClient
from requests import Response
from sqlalchemy.orm import Session
from tests.conftest import random_user

logger = getLogger(__name__)


def test_create_user(client: TestClient, db_session: Session) -> None:
    """Demonstrate that a unique new user account creation request succeeds

    Args:
        client (TestClient): A pytest fixture for a FastAPI TestClient
        db_session (Session): A pytest fixture for a SQLAlchemy database Session
    """
    l_new_user: Optional[UserCreate] = random_user(db_session=db_session)
    # Verify random user creation succeeded
    assert l_new_user is not None

    response: Response = client.post("/users/", l_new_user.json())

    logger.debug(
        f"[test_create_user] response: [{response.status_code}] {response.text}"
    )

    assert response.status_code == status.HTTP_201_CREATED
    # NOTE: The random_user function only generates lowercase emails. However, keep in
    # mind the database schema will force all provided emails to be lowercase. Thus,
    # this assert may fail if the l_new_user includes non-lowercase characters since
    # the response will be only lowercase.
    assert response.json()["email"] == l_new_user.email
    assert response.json()["is_active"] is True


def test_create_user_duplicate(client: TestClient, db_session: Session) -> None:
    """Demonstrate that a redundant user account creation request fails as expected

    Args:
        client (TestClient): A pytest fixture for a FastAPI TestClient
        db_session (Session): A pytest fixture for a SQLAlchemy database Session
    """
    l_new_user: Optional[UserCreate] = random_user(db_session=db_session)
    # Verify random user creation succeeded
    assert l_new_user is not None

    response: Response = client.post("/users/", l_new_user.json())

    logger.debug(
        f"[test_create_user_duplicate] response 1: [{response.status_code}] {response.text}"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == l_new_user.email
    assert response.json()["is_active"] is True

    # Now try to add this user a 2nd time
    response = client.post("/users/", l_new_user.json())
    logger.debug(
        f"[test_create_user_duplicate] response 2: [{response.status_code}] {response.text}"
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["email"] == l_new_user.email
    assert response.json()["is_active"] is False

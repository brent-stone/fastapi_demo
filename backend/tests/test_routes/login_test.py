from logging import getLogger
from typing import Dict
from typing import Optional

import jwt
from demo_backend.api.v1.routes.route_login import authenticate_user
from demo_backend.core.config import core_config
from demo_backend.database.models.users import User
from demo_backend.database.repository.login import get_user
from demo_backend.schemas.users import UserCreate
from demo_backend.schemas.users import UserLogin
from fastapi import status
from fastapi.testclient import TestClient
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session


logger = getLogger(__name__)


def test_default_user(
    client: TestClient, db_session: Session, default_test_account: UserCreate
) -> None:
    """Demonstrate that an existing user account is being created and passes the
    internal authentication function.

    Args:
        client (TestClient): A pytest fixture for a FastAPI TestClient
        db_session (Session): A pytest fixture for a SQLAlchemy database Session
        default_test_account (UserCreate): A pytest fixture for a default user/pass
    """
    # Validate that the default account exists in the database
    l_user: Optional[User] = get_user(a_email=default_test_account.email, db=db_session)
    assert l_user is not None

    # Verify a direct call to the authentication function works as expected
    l_user_authenticated: Optional[User] = authenticate_user(
        default_test_account.email, default_test_account.password, db_session
    )
    assert l_user_authenticated is not None
    assert isinstance(l_user_authenticated, User)


def test_default_user_login(
    client: TestClient, db_session: Session, default_test_account_login: UserLogin
) -> None:
    """Demonstrate that an existing user account can login via the FastAPI route.

    Args:
        client (TestClient): A pytest fixture for a FastAPI TestClient
        db_session (Session): A pytest fixture for a SQLAlchemy database Session
        default_test_account (UserCreate): A pytest fixture for a default user/pass
    """
    response = client.post("/login/token", data=default_test_account_login.dict())

    assert response.status_code == status.HTTP_200_OK

    l_response_dict: Dict[str, str] = response.json()
    logger.info(
        f"[test_user_login] user create response: [{response.status_code}] {l_response_dict}"
    )

    assert "access_token" in l_response_dict

    try:
        l_jwt: Dict[str, str] = jwt.decode(
            l_response_dict["access_token"],
            core_config.SECRET_KEY,
            algorithms=[core_config.HASH_ALGORITHM],
        )
    except PyJWTError as e:
        logger.error(f"Failed to decode JWT during login: {e}")

    logger.info(f"[test_user_login] Decoded JWT: {l_jwt}")

    assert l_jwt["sub"] == default_test_account_login.username
    assert isinstance(l_jwt["exp"], int)

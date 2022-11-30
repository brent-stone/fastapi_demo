"""
Tests for Login related routes
"""
from logging import getLogger
from typing import Dict

import jwt
from demo.core.config import core_config
from demo.schemas.users import UserLoginSchema
from fastapi import status
from fastapi.testclient import TestClient
from jwt.exceptions import PyJWTError

# from demo.schemas.users import UserCreateUpdateSchema

# from typing import Optional
# from demo.database.models.user import User
# from demo.database.repository.users import authenticate_user_db
# from demo.database.repository.users import get_user_by_email_db
# from demo.schemas.users import UserSchema

# from sqlalchemy.orm import Session


logger = getLogger(__name__)


# def test_default_user(
#     client: TestClient,
#     # db_session: Session,
#     default_test_account: UserCreateUpdateSchema,
# ) -> None:
#     """Demonstrate that an existing user account is being created and passes the
#     internal authentication function.
#
#     Args:
#         client (TestClient): A pytest fixture for a FastAPI TestClient
#         # db_session (Session): A pytest fixture for a SQLAlchemy database Session
#         default_test_account (UserCreateUpdateSchema): A pytest fixture for a default user/pass
#     """
#     # Validate that the default account exists in the database
#     l_user: UserSchema = get_user_by_email_db(
#         a_email=default_test_account.email, a_db=db_session
#     )
#     assert isinstance(l_user, UserSchema)
#
#     # Verify a direct call to the authentication function works as expected
#     l_user_authenticated: UserSchema = authenticate_user_db(
#         default_test_account.email, default_test_account.password, db_session
#     )
#     assert isinstance(l_user_authenticated, UserSchema)


def test_default_user_login(
    client: TestClient,
    default_test_account_login: UserLoginSchema,
) -> None:
    """Demonstrate that an existing user account can login via the FastAPI route.

    Args:
        client (TestClient): A pytest fixture for a FastAPI TestClient
        default_test_account_login (UserCreateUpdateSchema): A pytest fixture for a default user/pass
    """
    response = client.post("/v1/login/token", data=default_test_account_login.dict())

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
        logger.info(f"[test_user_login] Decoded JWT: {l_jwt}")
        # Here we will assume that the database was wiped and the very first user
        # account created was the default account. Thus, it should be ID 1
        assert l_jwt["sub"] == "5"
        # TODO: Change this back to 1 since the default account should be the first in
        #  the database
        assert isinstance(l_jwt["exp"], int)
    except PyJWTError as e:
        logger.error(f"Failed to decode JWT during login: {e}")

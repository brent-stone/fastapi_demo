"""
Login routes and JWT logic
"""
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import Optional

from demo.core.config import core_config
from demo.core.config import core_logger as logger
from demo.core.security import create_access_token
from demo.core.security import OAuth2PasswordBearerWithCookie
from demo.schemas.users import UserSchema
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from jose import JWTError

# from demo.database import get_db
# from demo.database.repository.users import authenticate_user_db
# from demo.database.repository.users import get_user_by_id_db

# from sqlalchemy.orm import Session

router = APIRouter()

login_route: str = "/v1/login/token"
# This token_url is what Swagger will use for it's "Authenticate" button and appear in
# the routes as the login path.
oauth2_scheme = OAuth2PasswordBearerWithCookie(token_url=login_route)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid user credentials",
)


@router.post("/token")
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    # db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Route for receiving a login/pass from the client and returning a JWT if the
    credentials correspond to an existing l_user.
    :param response: An HTTP response object
    :param form_data: The provided Oauth2 form data
    # :param db: A SQLAlchemy database Session
    :return: An new access_token for the l_user
    """
    logger.info(f"login attempt for: {form_data.username}")

    # TODO: Move away from a trivial login JWT data payload
    l_user: UserSchema = UserSchema(
        id=5,
        username=form_data.username,
        email="todo@github.com",
        is_active=False,
        is_superuser=False,
    )
    # l_user: UserSchema = authenticate_user_db(
    #     form_data.username, form_data.password, db
    # )

    # if not l_user.is_active:
    #     logger.debug(f"{form_data.username} account is deactivated.")
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="User account is disabled. Please contact an administrator.",
    #     )

    access_token_expire = timedelta(minutes=core_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    # What is placed in the data dict is what will be present in decoded JWTs
    access_token = create_access_token(
        data={"sub": str(l_user.id)}, expires_delta=access_token_expire
    )
    # This cookie is what will be expected to be provided by clients in the future when
    # attempting to access 'protected' routes.
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )

    l_return: Dict[str, str] = {"access_token": access_token, "token_type": "bearer"}
    logger.debug(f"Generated token for l_user {l_user.email}: {l_return}")
    return l_return


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    # db: Session = Depends(get_db),
) -> UserSchema:
    """
    Function to take a provided JWT and attempt to retrieve user information
    :param token: A JWT passed in from a REST endpoint
    # :param db: A SQLAlchemy database session
    :return: User information if valid; HTTP exception otherwise
    """
    # Ensure the JWT may be properly decoded and contains the expected 'sub' field
    try:
        payload = jwt.decode(
            token, core_config.SECRET_KEY, algorithms=[core_config.HASH_ALGORITHM]
        )
        l_sub: Optional[Any] = payload.get("sub")
        if l_sub is None:
            logger.debug("JWT token did not contain a 'sub' field")
            raise credentials_exception
        else:
            logger.debug(f"JWT successfully decoded 'sub' field containing: {l_sub}")
    except JWTError:
        logger.debug("JWT is not a valid format")
        raise credentials_exception
    # Ensure the 'sub' field in the JWT is a valid integer
    try:
        l_user_id: int = int(l_sub)
    except ValueError:
        logger.debug("JWT 'sub' field didn't contain an integer user ID")
        raise credentials_exception

    # TODO: Move towards a database enabled user login. Return trivial response for now
    l_user: UserSchema = UserSchema(
        id=l_user_id,
        username="todo",
        email="todo@github.com",
        is_active=False,
        is_superuser=False,
    )
    return l_user

    # Verify that the provided ID corresponds to a user and that the user is active.
    # try:
    #     l_user: UserSchema = get_user_by_id_db(a_id=l_user_id, a_db=db)
    #     if not l_user.is_active:
    #         logger.debug(f"Disabled user attempted to connect: {l_user.email}")
    #
    #     logger.debug(f"Successfully authenticated {l_user.email}")
    #     return l_user
    # except HTTPException:
    #     # Interrupt the default exception (which provides too much info) with a more
    #     # generic response.
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Credentials are no longer associated with an existing user.",
    #     )

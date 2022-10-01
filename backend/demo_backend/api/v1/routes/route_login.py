from datetime import timedelta
from logging import getLogger
from typing import Optional

from demo_backend.api.utils import OAuth2PasswordBearerWithCookie
from demo_backend.core.config import core_config
from demo_backend.core.hashing import Hasher
from demo_backend.core.security import create_access_token
from demo_backend.database import get_db
from demo_backend.database.models.users import User
from demo_backend.database.repository.login import get_user
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from jose import JWTError
from sqlalchemy.orm import Session

logger = getLogger(__name__)

router = APIRouter()


def authenticate_user(a_email: str, password: str, db: Session) -> Optional[User]:
    user: Optional[User] = get_user(a_email=a_email, db=db)
    if not user:
        logger.debug(f"[authenticate_user] user not found: {a_email}")
        return None
    if not Hasher.verify_password(password, user.hashed_password):
        logger.debug(f"[authenticate_user] hash mismatch for {a_email}")
        return None
    return user


@router.post("/token")
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    logger.info(f"[login_for_access_token] login attempt for: {form_data.username}")

    l_found_user: Optional[User] = get_user(a_email=form_data.username, db=db)
    if l_found_user is None:
        l_found_em = "DIDNT_FIND"
    else:
        l_found_em = "FOUND_EM"

    user: Optional[User] = authenticate_user(form_data.username, form_data.password, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Got incorrect credentials [{l_found_em}]: [{type(form_data.username)}]{form_data.username} // {form_data.password}",
            # detail="Incorrect username or password",
        )

    access_token_expire = timedelta(minutes=core_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expire
    )
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token, core_config.SECRET_KEY, algorithms=[core_config.HASH_ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            logger.debug(
                f"[get_current_user_from_token] token is\
                     invalid: {token}"
            )
            raise credentials_exception
    except JWTError:
        logger.debug(
            "[get_current_user_from_token] JWT is not a valid\
                 format"
        )
        raise credentials_exception
    user: Optional[User] = get_user(a_email=username, db=db)
    if user is None:
        logger.debug(
            f"[get_current_user_from_token] user not found: \
                {username}"
        )
        raise credentials_exception
    return user

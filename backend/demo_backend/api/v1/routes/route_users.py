from http import HTTPStatus
from logging import getLogger
from typing import Optional

from demo_backend.database import get_db
from demo_backend.database.models.users import User
from demo_backend.database.repository.users import create_new_user
from demo_backend.schemas.users import ShowUser
from demo_backend.schemas.users import UserCreate
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status
from sqlalchemy.orm import Session


router = APIRouter()

logger = getLogger(__name__)


@router.post("/", response_model=ShowUser, status_code=HTTPStatus.CREATED)
def create_user(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    """Attempt to create a new user record in the database.

    Args:
        user (UserCreate): The requested new user details
        response (Response): The implicitly provided FastAPI response object
        db (Session, optional): Database session dependency injection. Defaults to
        Depends(get_db).

    Returns:
        ShowUser: A populated ShowUser schema and 201 on success; 409 on conflict or
        error
    """
    l_user: Optional[User] = create_new_user(user, db)
    if l_user is None:
        logger.debug(f"Ignoring user creation request: {user.email}")
        # Provide an appropriate negative status code response to the client
        response.status_code = status.HTTP_409_CONFLICT
        l_user_show: ShowUser = ShowUser(
            username=user.username, email=user.email, is_active=False
        )
    else:
        l_user_show: ShowUser = ShowUser(
            username=l_user.username, email=l_user.email, is_active=l_user.is_active
        )
    return l_user_show

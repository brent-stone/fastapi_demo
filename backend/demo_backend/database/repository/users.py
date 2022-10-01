from logging import getLogger
from typing import Optional

from demo_backend.core.hashing import Hasher
from demo_backend.database.models.users import User
from demo_backend.database.repository.login import get_user
from demo_backend.schemas.users import UserCreate
from pydantic.errors import EmailError
from pydantic.errors import MissingError
from pydantic.errors import StrError
from sqlalchemy.orm import Session

logger = getLogger(__name__)


def create_new_user(a_user: UserCreate, db: Session) -> Optional[User]:
    """Attempt to create a new user in the database. Will return None if the email
    already exists.

    Args:
        a_user (UserCreate): The requested user creation information.
        db (Session): A SQLAlchemy database session

    Returns:
        Optional[User]: The populated User schema if the request is for a unique email;
        None otherwise
    """
    # Verify the user email isn't already in the database
    l_user: Optional[User] = get_user(a_email=a_user.email, db=db)
    if l_user is not None:
        logger.info(f"[create_new_user] user already exists: {a_user.email}")
        return None
    try:
        # Note: The UserCreate embedded validator for emails already sanitized any
        # inappropriate characters.
        l_user = User(
            username=a_user.username,
            email=a_user.email,
            hashed_password=Hasher.get_password_hash(a_user.password),
            is_active=True,
            is_superuser=False,
        )
    except (MissingError, StrError, EmailError, ValueError) as e:
        logger.warning(
            f"[database.repository.users.create_new_user] Bad user info: {e}"
        )
        return None
    db.add(l_user)
    db.commit()
    db.refresh(l_user)
    return l_user

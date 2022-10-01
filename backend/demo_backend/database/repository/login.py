from logging import getLogger
from typing import Optional

from demo_backend.core.security import sanitize_email
from demo_backend.database.models.users import User
from sqlalchemy.orm import Session


logger = getLogger(__name__)


def get_user(a_email: str, db: Session) -> Optional[User]:
    # NOTE: sanitize_email will force all emails to lowercase
    l_email: Optional[str] = sanitize_email(a_email=a_email)
    if l_email is None:
        return None
    user = db.query(User).filter(User.email == l_email).first()
    if user is None:
        logger.debug(f"[get_user] {l_email} not found.")
    return user

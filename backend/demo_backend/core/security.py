from datetime import datetime
from datetime import timedelta
from logging import getLogger
from typing import Optional

from demo_backend.core.config import core_config
from email_validator import EmailNotValidError
from email_validator import validate_email
from jose import jwt

logger = getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=core_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, core_config.SECRET_KEY, algorithm=core_config.HASH_ALGORITHM
    )
    return encoded_jwt


def sanitize_email(
    a_email: str, new_account: bool = False, test_environment: bool = core_config.DEBUG
) -> Optional[str]:
    try:
        validation = validate_email(
            a_email, check_deliverability=new_account, test_environment=test_environment
        )
        l_email: str = validation.email
        # Force all emails to lowercase
        return l_email.lower()
    except EmailNotValidError as e:
        logger.warning(f"[sanitize_email] invalid email provided: {e}")
        return None

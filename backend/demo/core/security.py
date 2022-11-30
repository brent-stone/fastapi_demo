"""
Security focused utility functions
"""
from typing import Optional

from demo.core.config import core_config
from demo.core.config import core_logger as logger
from email_validator import EmailNotValidError
from email_validator import validate_email


def sanitize_email(
    a_email: str, new_account: bool = False, test_environment: bool = core_config.DEBUG
) -> Optional[str]:
    """
    Ensure emails meet expectations of an email address and are standardized to all
    lowercase
    """
    try:
        validation = validate_email(
            a_email, check_deliverability=new_account, test_environment=test_environment
        )
        l_email: str = validation.email.lower()
        # Force all emails to lowercase
        logger.debug(f"Received email: {l_email}")
        return l_email
    except EmailNotValidError as e:
        logger.warning(f"[sanitize_email] invalid email provided: {e}")
        return None

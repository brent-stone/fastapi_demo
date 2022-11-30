"""
Security focused utility functions
"""
from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import Optional

from demo.core.config import core_config
from demo.core.config import core_logger as logger
from email_validator import EmailNotValidError
from email_validator import validate_email
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt


def sanitize_email(
    a_email: str, new_account: bool = False, test_environment: bool = core_config.DEBUG
) -> Optional[str]:
    """
    Ensure emails meet expectations of an email address and are standardized to all
    lowercase
    Args:
        a_email: The email address to verify
        new_account: Whether this email is expected to be new and thus more suspicious
        than known good emails
        test_environment: Whether to be less rigorous in the check

    Returns:

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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cryptographically generate an ephemeral access token using a secret key and the
    current time.

    Args:
        data: Any key:value pairs to embed in the JWT
        expires_delta: The duration the token should remain valid

    Returns: The data encrypted as a JSON Web Token using the server's secret key

    """
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


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    JSON Web Token based authentication class
    """

    def __init__(
        self,
        token_url: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        """
        Attempt to decrypt the token and return its payload
        Args:
            request: The token provided by the HTTP client

        Returns: The decrypted payload if valid, raise HTTPException otherwise

        """
        authorization: str = request.headers.get("Authorization")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                logger.debug(
                    f"Rejecting login.\n"
                    f"Authorization: {authorization}\n"
                    f"Scheme: {scheme}\n"
                    f"Param: {param}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="access_token cookie not provided or invalid. "
                    "Please login again to refresh your credentials.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

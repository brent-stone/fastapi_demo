"""
Pydantic schemas for REST endpoint requests and responses.
These both document the expected data for bi-directional communication with clients and
provide validation that clients and this server meet those expectations.

These schemas will generally be paired with
1. SQLAlchemy models in database.models
    Those models will typically be called by...
2. SQLAlchemy focused CRUD functions in database.repository
    Those functions will typically be called by...
3. FastAPI routes in api.*.routes
    Those routes will typically use these Pydantic schemas to document their input and
    output with clients and convert to and from the SQLAlchemy models.
"""
from typing import Optional

from demo.core.security import sanitize_email
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel as PydanticBaseModel
from pydantic import conint
from pydantic import constr
from ujson import loads

# A specific type of constrained strings for usernames and passwords to ensure they're
# reasonable
username_str = constr(strip_whitespace=True, min_length=3, max_length=64)

# A specific type of constrained int for user ID to ensure they're reasonable
user_id_int = conint(ge=1)

# A constrained integer for reasonable year values
year_int = conint(gt=1900, lt=3000)


class BaseModel(PydanticBaseModel):
    """
    Customized global version of the Pydantic BaseModel to leverage a more efficient
    JSON parser.
    """

    class Config:
        """
        Optional modification to BaseModel to use a more efficient parser and enable
        smooth conversion from SQLAlchemy ORM objects
        """

        json_loads = loads
        orm_mode = True


def empty_str_none(a_str: str) -> Optional[str]:
    """
    Ensure database entries are clearly NULL if field values are empty strings by
    explicitly using None instead of ""
    :param a_str: A string to be converted to None if it is ""
    :return: The input str if not empty, None otherwise
    """
    if bool(a_str):
        return a_str
    return None


def render_safe_email(a_email: Optional[str]) -> Optional[str]:
    """
    ensure emails meet basic requirements.
    :param a_email: The client provided email address
    :return: A normalized and vetted version of the provided email
    """
    # Edge case when a validation is run on a schema where email is optional
    if a_email is None:
        return None
    l_sanitized_email: Optional[str] = sanitize_email(a_email=a_email)
    if l_sanitized_email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="e-mail is not valid"
        )
    return l_sanitized_email

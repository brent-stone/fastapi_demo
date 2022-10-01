from typing import Optional

from demo_backend.core.security import sanitize_email
from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from pydantic import validator


class UserCreate(BaseModel):
    username: constr(to_lower=True, strip_whitespace=True, max_length=64)
    email: EmailStr
    password: str

    @validator("email")
    def render_safe_email(cls, a_email):
        l_sanitized_email: Optional[str] = sanitize_email(a_email=a_email)
        if l_sanitized_email is None:
            raise ValueError("e-mail is not valid")
        return l_sanitized_email


class ShowUser(BaseModel):
    username: constr(to_lower=True, strip_whitespace=True, max_length=64)
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    """This schema is primarily used for testing"""

    username: constr(to_lower=True, strip_whitespace=True, max_length=64)
    password: str

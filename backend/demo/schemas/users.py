"""
User Pydantic Schemas
"""
from typing import Optional

from demo.schemas import BaseModel
from demo.schemas import generic_str
from demo.schemas import render_safe_email
from pydantic import EmailStr
from pydantic import validator

# from demo.core.hashing import Hasher


class UserLoginSchema(BaseModel):
    """
    Facilitate user authentication
    """

    username: generic_str
    password: generic_str

    # _hash_pass = validator("password", allow_reuse=True)(Hasher.get_password_hash)


class UserCreateUpdateSchema(UserLoginSchema):
    """
    Extension of UserLoginSchema to include email
    """

    # username inherited from UserLoginSchema
    # password inherited from UserLoginSchema
    email: EmailStr

    _sanitize_email = validator("email", allow_reuse=True)(render_safe_email)


class UserAdminCreateUpdateSchema(UserCreateUpdateSchema):
    """
    Extension of UserCreateUpdateSchema schema to allow modification of features which
    should only be made by admins.

    """

    # username inherited from UserCreateUpdateSchema
    # password inherited from UserCreateUpdateSchema
    # email inherited from UserCreateUpdateSchema
    is_active: bool = True
    is_superuser: bool = False


class UserAdminConfirmDowngradeUpdateSchema(UserAdminCreateUpdateSchema):
    """
    The optional confirm flag must be set to True if an admin is about to downgrade
    their own account from superuser to standard user.
    """

    # username inherited from UserAdminCreateUpdateSchema
    # password inherited from UserAdminCreateUpdateSchema
    # email inherited from UserAdminCreateUpdateSchema
    # is_active inherited from UserAdminCreateUpdateSchema
    # is_superuser inherited from UserAdminCreateUpdateSchema
    confirm_downgrade: Optional[bool] = False


class UserSchema(BaseModel):
    """
    Generic User schema for conveying details about users less sensitive info
    """

    id: int
    username: generic_str
    email: EmailStr
    is_active: bool
    is_superuser: bool

    _sanitize_email = validator("email", allow_reuse=True)(render_safe_email)

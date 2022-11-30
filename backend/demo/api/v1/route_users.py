"""
CRUD routes for Users
"""
from demo.schemas.users import UserCreateUpdateSchema
from demo.schemas.users import UserSchema
from fastapi import APIRouter
from fastapi import status

# from demo.api.v1.route_login import get_current_admin_from_token
# from demo.api.v1.route_login import get_current_user_from_token

router = APIRouter()
router_admin = APIRouter()


@router.post("/create", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user_route(a_user: UserCreateUpdateSchema):
    """Attempt to create a new user record in the database.

    Args:
        a_user (UserCreateUpdateSchema): The requested new user details

    Returns:
        UserSchema: A populated ShowUser schema and 201 on success; HTTPException on
        conflict or error
    """
    l_return: UserSchema = UserSchema(
        id=1,
        is_active=False,
        is_superuser=False,
        **a_user.dict(),
    )
    return l_return


@router.put("/update", response_model=UserSchema, status_code=status.HTTP_202_ACCEPTED)
def update_user_route(a_user: UserCreateUpdateSchema):
    """Attempt to update a user record in the database.

    Args:
        a_user (UserUpdateSchema): The requested new user details

    Returns:
        UserSchema: A populated UserSchema and 201 on success; HTTPException on
        conflict or error.
    """
    l_return: UserSchema = UserSchema(
        id=1,
        is_active=False,
        is_superuser=False,
        **a_user.dict(),
    )
    return l_return


@router.get("/get", response_model=UserSchema, status_code=status.HTTP_200_OK)
def get_my_info():
    """Attempt to get the logged in user record from the database.

    Args:
        a_current_user (UserModel): The user currently logged in making this request
        db (Session): Database session dependency injection.

    Returns:
        UserSchema: A populated UserSchema and 200 on success; HTTPException on
        conflict or error.
    """
    return UserSchema(
        id=1,
        username="TODO",
        email="todo@github.com",
        is_active=False,
        is_superuser=False,
    )
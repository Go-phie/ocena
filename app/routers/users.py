from typing import Optional
from fastapi_users.authentication import JWTAuthentication
from fastapi_users import FastAPIUsers
from app.dependencies import get_user_manager, jwt_authentication
from app.models.models import User, UserCreate, UserUpdate, UserDB


fastapi_users = FastAPIUsers(
    get_user_manager,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

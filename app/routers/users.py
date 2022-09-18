from fastapi_users import FastAPIUsers
import uuid

from app.dependencies import get_user_manager, auth_backend
from app.models.models import User

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

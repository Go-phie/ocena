from httpx_oauth.clients.google import GoogleOAuth2
from fastapi import Depends, Request
from fastapi_users import BaseUserManager
from typing import Optional
from fastapi_users.authentication import JWTAuthentication
from app.models import get_user_db
import logging

from app.models.models import UserCreate, UserDB
from app.settings import settings


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = settings.secret
    verification_token_secret = settings.secret

    async def on_after_register(self, user: UserDB, request: Optional[Request] = None):
        logging.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        logging.info(
            f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        logging.info(
            f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

jwt_authentication = JWTAuthentication(
    secret=settings.secret, lifetime_seconds=3600, tokenUrl="auth/login")

google_oauth_client = GoogleOAuth2(
    settings.google_client_id, settings.google_client_secret)

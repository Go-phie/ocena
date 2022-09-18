from httpx_oauth.clients.google import GoogleOAuth2
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
import logging
from fastapi_users.authentication import JWTStrategy
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from app.models import get_user_db
from app.models.models import User
from app.settings import settings

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret
    verification_token_secret = settings.secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logging.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logging.info(
            f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logging.info(
            f"Verification requested for user {user.id}. Verification token: {token}")


def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

google_oauth_client = GoogleOAuth2(
    settings.google_client_id, settings.google_client_secret)

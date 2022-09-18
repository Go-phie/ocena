from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import UserRead, UserUpdate, UserCreate


# Settings module must be imported before all modules so that it will be available
from app.settings import settings
from .routers import users, movie, music
from .dependencies import auth_backend, google_oauth_client
# from pydantic import BaseConfig

app = FastAPI(title=settings.app_name)
# BaseConfig.arbitrary_types_allowed = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=settings.origins_regex
)

app.include_router(
    users.fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/auth",
    tags=["users"],
)
app.include_router(
    users.fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_oauth_router(
        google_oauth_client, auth_backend, settings.secret, associate_by_email=True),
    prefix="/auth/google",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_oauth_associate_router(
        google_oauth_client, UserRead, settings.secret),
    prefix="/auth/associate/google",
    tags=["auth"],
)
app.include_router(movie.router)
app.include_router(music.router)


# keeps clashing with alembic for table creation
# Uncomment to use poor man's table creation
# models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": f"{settings.app_name}, 'Rating'!"}

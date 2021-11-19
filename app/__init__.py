from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Settings module must be imported before all modules so that it will be available
from app.settings import settings
from app.models import SessionLocal
from .routers import users, movie, music
from .dependencies import jwt_authentication, google_oauth_client

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=settings.origins_regex
)

app.include_router(
    users.fastapi_users.get_register_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_users_router(),
    prefix="/auth",
    tags=["users"],
)
app.include_router(
    users.fastapi_users.get_auth_router(jwt_authentication),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.fastapi_users.get_oauth_router(google_oauth_client, settings.secret),
    prefix="/auth/google",
    tags=["auth"],
)
app.include_router(movie.router)
app.include_router(music.router)


# keeps clashing with alembic for table creation
# Uncomment to use poor man's table creation
# models.Base.metadata.create_all(bind=engine)


def get_db():
    """ Get Database Object"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Ocena, 'Rating'!"}

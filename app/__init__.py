from typing import List
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.settings import (
    settings,
)  # Settings module must be imported before all modules so that it will be available
from app import models
from app.models import SessionLocal, engine
from app.routers import router


app = FastAPI()

if settings.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router)

# keeps clashing with alembic for table creation
# Uncomment to use poor man's table creation
# models.Base.metadata.create_all(bind=engine)


def get_db():
    """Get Database Object"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

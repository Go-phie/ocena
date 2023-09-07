from typing import List
from fastapi import FastAPI

# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.settings import (
    settings,
)  # Settings module must be imported before all modules so that it will be available
from app import models
from app.models import SessionLocal, engine
from app.routers import router


app = FastAPI()

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

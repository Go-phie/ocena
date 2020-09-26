from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import settings  # Settings module must be imported before all modules so that it will be available
from app import models
from app.models import SessionLocal, engine
from app.routers import router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=settings.origins_regex
)

app.include_router(router)

models.Base.metadata.create_all(bind=engine)


def get_db():
    """ Get Database Object"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

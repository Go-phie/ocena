from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

from fastapi_users.db import (
    SQLAlchemyUserDatabase,
)
from fastapi import Depends
from app.settings import settings

from app.models.models import OAuthAccount, User

Base: DeclarativeMeta = declarative_base()

engine = create_engine(settings.database_url)


class HashableSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return str(datetime.now().date())

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class HashableParams(dict):
    def __repr__(self):
        x = ", ".join([str(val) for val in self.values()])
        x += f":-{str(datetime.now().date())}"
        return x

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


SessionLocal = sessionmaker(
    autocommit=False, class_=HashableSession, autoflush=False, bind=engine)


async def get_db():
    """ Get Database Object"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_user_db(session=Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)

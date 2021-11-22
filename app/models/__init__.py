from datetime import datetime
import databases
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTable,
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase,
)
from app import settings

from app.models.models import UserDB

Base = declarative_base()

if settings.debug:
    engine = create_engine(settings.database_url, connect_args={
                           "check_same_thread": False})
else:
    engine = create_engine(settings.database_url)

database = databases.Database(settings.database_url)


class UserTable(Base, SQLAlchemyBaseUserTable):
    pass


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable, Base):
    pass


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


def get_db():
    """ Get Database Object"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


Base.metadata.create_all(engine)

users = UserTable.__table__

oauth_accounts = OAuthAccount.__table__


async def get_user_db():
    yield SQLAlchemyUserDatabase(UserDB, database, users, oauth_accounts)

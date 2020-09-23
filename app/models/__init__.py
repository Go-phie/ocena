import datetime

from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from app import settings

Base = declarative_base()

if settings.debug:
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.database_url)

class HashableSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return datetime.datetime.today().strftime("%d%m%Y")

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

class HashableParams(dict):
    def __repr__(self):
        return ", ".join([str(val) for val in self.values()])

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

SessionLocal = sessionmaker(autocommit=False, class_=HashableSession, autoflush=False, bind=engine)


def get_db():
    """ Get Database Object"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

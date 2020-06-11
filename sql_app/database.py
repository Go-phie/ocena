import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not os.getenv("DATABASE_URL", None):
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{BASE_DIR}/sql_app.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL
    )

Base = declarative_base()

class HashableSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return datetime.datetime.today().strftime("%d%m%Y")

    def __hash__(self):
        return hash(repr(self))
    
    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

SessionLocal = sessionmaker(autocommit=False, class_=HashableSession, autoflush=False, bind=engine)

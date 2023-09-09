import os
from typing import List

from fastapi import FastAPI
from pydantic_settings import BaseSettings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    app_name: str = "Ocena"
    gophie_host: str = "https://gophie.cam"
    gophie_access_key: str = ""
    database_url: str = f"sqlite:///{BASE_DIR}/db.sqlite3"
    debug: bool = True


settings = Settings()

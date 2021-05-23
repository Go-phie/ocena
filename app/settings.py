import os
from typing import List

from fastapi import FastAPI
from pydantic import BaseSettings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "https://gophie.cam").split(",")

class Settings(BaseSettings):
    app_name: str = "Ocena"
    gophie_host: str = "https://deploy-gophie.herokuapp.com"
    gophie_access_key: str = ""
    database_url: str = f"sqlite:///{BASE_DIR}/db.sqlite3"
    debug: bool = True
    origins: list = ALLOWED_HOSTS
    origins_regex = "https://deploy-preview-\d+--gophie\.netlify\.app"  # allow access from staging builds


settings = Settings()

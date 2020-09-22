import os
from typing import List

from fastapi import FastAPI
from pydantic import BaseSettings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    app_name: str = "Ocena"
    gophie_host: str = "https://deploy-gophie.herokuapp.com"
    database_url: str = f"sqlite:///{BASE_DIR}/db.sqlite3"
    debug: bool = True
    origins: list = [
        "http://gophie-ocena.herokuapp.com",
        "http://localhost:3000",
        "https://gophie.netlify.app",
        "https://gophie-ssr.herokuapp.com",
        "https://gophie.cam",
        "https://ssr.gophie.cam",
    ]
    origins_regex = "https://deploy-preview-\d+--gophie\.netlify\.app"  # allow access from staging builds


settings = Settings()

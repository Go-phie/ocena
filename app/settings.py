import os
from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Base = declarative_base()


class Settings(BaseSettings):
    app_name: str = "Ocena"
    gophie_host: str = "https://deploy-gophie.herokuapp.com"
    mythra_host: str = "https://gophie-mythra.herokuapp.com"
    gophie_access_key: str = ""
    database_url: str = f"sqlite:///{BASE_DIR}/db.sqlite3"
    debug: bool = True
    origins: list = [
        "http://gophie-ocena.herokuapp.com",
        "http://localhost:3000",
        "https://gophie.netlify.app",
        "https://gophie-ssr.herokuapp.com",
        "https://gophie-statping.herokuapp.com",
        "https://gophie.cam",
        "https://ssr.gophie.cam",
    ]
    # allow access from staging builds
    origins_regex = "https://deploy-preview-\d+--gophie\.netlify\.app"
    # social auth credentials
    google_client_id: str = ""
    google_client_secret: str = ""
    # app secret
    secret: str = ""


settings = Settings()

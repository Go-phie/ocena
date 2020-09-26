import pytest
import urllib
from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

engines = [
    "fzmovies",
    "netnaija",
    "tvseries",
    "kdramahood",
    "takanimelist",
    "besthdmovies",
    "animeout",
]

def validate_link(link):
    parsed_url = urllib.parse.urlparse(link)
    assert bool(parsed_url.scheme)

def validate_movies(movies):
    for movie in movies:
        if not movie["is_series"]:
            validate_link(movie["download_link"])
        else:
            for link in movie["s_download_link"].values():
                validate_link(link)
    

@pytest.mark.parametrize("engine", engines)
def test_gophie_list(engine):
    response = client.get(f"/list/?engine={engine}&page=1")
    assert response.status_code == 200
    assert len(response.json()) != 0
    movies = response.json()
    validate_movies(movies)

@pytest.mark.parametrize("engine", engines)
def test_gophie_search(engine):
    response = client.get(f"/search/?engine={engine}&query=hello&page=1")
    assert response.status_code == 200
    assert len(response.json()) != 0
    movies = response.json()
    validate_movies(movies)

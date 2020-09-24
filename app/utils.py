import requests
import uuid
import re
from functools import lru_cache
from app.settings import settings
from app.models import HashableSession, HashableParams
from app.models import models, crud


# Pattern for converting camel to snake case, used in parsing json response
camel_to_snake_pattern = re.compile(r'(?<!^)(?=[A-Z])')

def camel_case_to_snake_case(s):
    return camel_to_snake_pattern.sub('_', s).lower()


def keys_to_snake_case(d):
    """ returns a dictionary with keys converted to snake case """
    new_dict = {}
    for k, v in d.items():
        new_dict[camel_case_to_snake_case(k)] = v
    return new_dict

def dict_to_model(movie_dict: dict):
    """ converts a movie_dict to model """
    update = {
        "engine": movie_dict["source"],
        "name": movie_dict["title"],
        "referral_id": str(uuid.uuid4()),
    }
    del movie_dict["index"], movie_dict["source"], movie_dict["title"]
    movie_dict.update(update)
    return models.Movie(**movie_dict)

@lru_cache(maxsize=2000)
def get_movies_from_remote(url: str, params: HashableParams, engine: str, db: HashableSession):
    """ Gets movies from remote url """
    movies = []
    try:
        response = requests.get(url, params)
        if response.status_code != 200 or response.json() in ([], None):
            raise Exception(f"Invalid Response from {settings.gophie_host}")
    except Exception:
        return
    else:
        for m in response.json():
            movie = keys_to_snake_case(m)
            if movie.get("title", None) and movie.get("source", None):
                movie_model = dict_to_model(movie)
                cleaned_movie = crud.create_movie(db, movie_model)
                movies.append(cleaned_movie)
    return movies

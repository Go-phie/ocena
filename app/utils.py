import os
import requests
import uuid
import re
import logging
from functools import lru_cache
from datetime import datetime, timedelta
from app.settings import settings
from app.models import HashableSession, HashableParams
from app.models import models, crud
from sqlalchemy.ext.declarative.api import DeclarativeMeta


# Pattern for converting camel to snake case, used in parsing json response
camel_to_snake_pattern = re.compile(r'(?<!^)(?=[A-Z])')


class GophieHostException(Exception):
    """ Generic Gophie Host Exception """
    pass

class MythraHostException(Exception):
    """ Generic Mythra Host Exception """
    pass

class InvalidResponse(Exception):
    """ If response is not a valid object"""
    pass


class GophieUnresponsive(Exception):
    """ If gophie does not return 200 """
    pass

class MythraUnresponsive(Exception):
    """ If mythra does not return 200 """
    pass

def camel_case_to_snake_case(s):
    return camel_to_snake_pattern.sub('_', s).lower()


def keys_to_snake_case(d):
    """ returns a dictionary with keys converted to snake case """
    new_dict = {}
    for k, v in d.items():
        new_dict[camel_case_to_snake_case(k)] = v
    return new_dict


def dict_to_model(params: HashableParams, movie_dict: dict, model: DeclarativeMeta):
    """ converts a movie_dict to model """
    if model.__tablename__ == "movies":
        update = {
            "engine": movie_dict["source"],
            "name": movie_dict["title"],
            "referral_id": str(uuid.uuid4()),
        }
        # A way to ensure that the recent movies stack at the top of the page
        # Dynamically assign "date_created" attribute so that
        # older movies get pushed further when ordered by desc days
        # and more recent movies cluster at the top
        if params.get("num", None):
            date_created = datetime.today() - timedelta(days=int(params["page"]))
            update["date_created"] = date_created
        else:
            # searched movies will retain their original date_created
            # so as not to pollute the clustering process
            update["date_created"] = None

        del movie_dict["index"], movie_dict["source"], movie_dict["title"]
        movie_dict.update(update)
        return model(**movie_dict)
    elif model.__tablename__ == "music":
        movie_dict["date_created"] = datetime.now()
        del movie_dict["index"]
        return model(**movie_dict)


@lru_cache(maxsize=4096)
def get_movies_from_remote(url: str, params: HashableParams, engine: str, db: HashableSession):
    """ Gets movies from remote url """
    movies = []
    try:
        headers = {'Authorization': f'Bearer {settings.gophie_access_key}'}
        response = requests.get(url, params, headers=headers)
        if response.status_code != 200:
            raise GophieUnresponsive(f"Invalid Response from {settings.gophie_host}: ({response.status_code}): {response.content}")
        if response.json() in ([], None):
            raise InvalidResponse(f"Empty Response from {settings.gophie_host}: {response.content}")
    except Exception as e:
        logging.error(str(e))
        raise GophieHostException(f"Invalid Response from {settings.gophie_host}: {str(e)}")
    else:
        for m in response.json():
            movie = keys_to_snake_case(m)
            if movie.get("title", None) and movie.get("source", None):
                movie_model = dict_to_model(params, movie, models.Movie)
                cleaned_movie = crud.create_movie(db, movie_model)
                movies.append(cleaned_movie)
    return movies

@lru_cache(maxsize=4096)
def get_music_from_remote(url: str, params: HashableParams, engine: str, db: HashableSession):
    """ Gets movies from remote url """
    music_list = []
    try:
        response = requests.get(url, params)
        if response.status_code != 200:
            raise MythraUnresponsive(f"Invalid Response from {settings.mythra_host}: ({response.status_code}): {response.content}")
        if response.json() in ([], None):
            raise InvalidResponse(f"Empty Response from {settings.mythra_host}: {response.content}")
    except Exception as e:
        logging.error(str(e))
        raise MythraHostException(f"Invalid Response from {settings.gophie_host}: {str(e)}")
    else:
        for music in response.json():
            if music.get("title", None) and music.get("source", None):
                music_model = dict_to_model(params, music, models.Music)
                cleaned_music = crud.create_music(db, music_model)
                music_list.append(cleaned_music)
        logging.info(music_list)
    return music_list

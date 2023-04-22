import time
import os
import requests
import uuid
import re
import logging
from functools import lru_cache
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from app.settings import settings
from app.models import HashableSession, HashableParams
from app.models import models, crud


# Pattern for converting camel to snake case, used in parsing json response
camel_to_snake_pattern = re.compile(r'(?<!^)(?=[A-Z])')


class GophieHostException(Exception):
    """ Generic Gophie Host Exception """
    pass


class InvalidResponse(Exception):
    """ If response is not a valid object"""
    pass


class GophieUnresponsive(Exception):
    """ If gophie does not return 200 """
    pass


def camel_case_to_snake_case(s):
    return camel_to_snake_pattern.sub('_', s).lower()


def keys_to_snake_case(d):
    """ returns a dictionary with keys converted to snake case """
    new_dict = {}
    for k, v in d.items():
        new_dict[camel_case_to_snake_case(k)] = v
    return new_dict


def dict_to_model(params: HashableParams, movie_dict: dict):
    """ converts a movie_dict to model """
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
    return models.Movie(**movie_dict)


@lru_cache(maxsize=4096)
def get_movies_from_remote(url: str, params: HashableParams, engine: str, db: HashableSession):
    """ Gets movies from remote url """
    movies = []
    adapter = HTTPAdapter(max_retries=1)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    try:
        headers = {'Authorization': f'Bearer {settings.gophie_access_key}'}
        start = time.time()
        response = http.get(url, params=params, headers=headers, timeout=20)
        if response.status_code != 200:
            raise GophieUnresponsive(f"Invalid Response from {settings.gophie_host} for <{engine}: ({response.status_code}): {response.content}")
        if response.json() in ([], None):
            raise InvalidResponse(f"Empty Response from {settings.gophie_host} for {engine}: {response.content}")
        print("time elapsed: ", time.time() - start)
    except Exception as e:
        logging.error(str(e))
        raise GophieHostException(f"Invalid Response from {settings.gophie_host}: {str(e)}")
    else:
        for m in response.json():
            movie = keys_to_snake_case(m)
            if movie.get("title", None) and movie.get("source", None):
                movie_model = dict_to_model(params, movie)
                cleaned_movie = crud.create_movie(db, movie_model)
#                 cleaned_movie["ratings"] = crud.get_movie_average_ratings(db=db, movie=cleaned_movie)
                movies.append(cleaned_movie)
    return movies

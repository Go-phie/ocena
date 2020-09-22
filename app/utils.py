import requests
import re
import collections
from app.settings import settings
from app.models import schemas


# Pattern for converting camel to snake case, used in parsing json response
camel_to_snake_pattern = re.compile(r'(?<!^)(?=[A-Z])')


def add_ratings(ratings_list):
    counter = 0
    for rating in ratings_list:
        counter += rating.score
    return counter


def get_movie_download(download_queryset):
    movie_download = collections.Counter()
    for instance in download_queryset:
        movie_download[str(instance.movie_id)] += 1
    return movie_download


def camel_case_to_snake_case(s):
    return camel_to_snake_pattern.sub('_', s).lower()


def keys_to_snake_case(d):
    """ returns a dictionary with keys converted to snake case """
    new_dict = {}
    for k, v in d.items():
        new_dict[camel_case_to_snake_case(k)] = v
    return new_dict


def get_movies_from_remote(url: str, params: dict, engine: str):
    """ Gets movies from remote url """
    movies = []
    try:
        response = requests.get(url, params)
        if response.status_code != 200:
            raise Exception(f"Invalid Response from {settings.gophie_host}")
    except Exception:
        return
    else:
        for m in response.json():
            movie = keys_to_snake_case(m)
            movie["name"] = movie["title"]
            movie["id"] = movie["index"]
            movie["engine"] = engine
            cleaned_movie = schemas.MovieReferral(**movie)
            movies.append(cleaned_movie)
    return movies

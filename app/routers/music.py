from typing import List
import contextlib
import logging

from fastapi import Depends, APIRouter

from app.settings import settings
from app import utils
from app.models import schemas, crud, HashableSession, HashableParams, get_db

router = APIRouter()


@router.get("/music/search/", response_model=List[schemas.Music], tags=["music"])
def search_music(engine: str = "freemp3cloud", query: str = "Mirrors Justin Timberlake", db: HashableSession = Depends(get_db)):
    """
    Searches music from an engine using partial ratio

    engine: the engine to list data from
    query: the search term urlencoded
    """
    params = HashableParams({
        "query": query,
        "engine": engine,
    })
    music = []
    with contextlib.suppress(utils.MythraHostException):
        music = utils.get_music_from_remote(
            f"{settings.mythra_host}/search", params, engine, db)
    if not music:
        movies = crud.search_music(db=db, engine=engine, query=query)
        logging.info(utils.get_music_from_remote.cache_info())
    return music

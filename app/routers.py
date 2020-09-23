from typing import List
import requests

from fastapi import Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy.orm import Session

from app.settings import settings
from app import utils
from app.models import SessionLocal, schemas, crud, HashableSession, HashableParams, get_db

router = APIRouter()


@router.post("/movie/ratings/average/", response_model=schemas.AverageRating)
def get_average_ratings(movie: schemas.MovieRating, db: Session = Depends(get_db)):
    """
    Get average movie ratings and number of people who have rated
    """
    return crud.get_movie_average_ratings(db=db, movie=movie)


@router.post("/movie/rating/", response_model=schemas.Rating)
def get_ip_rating(spec_rating: schemas.SpecificRating, db: Session = Depends(get_db)):
    """
    Get Rating of a movie by an ip_address
    """
    return crud.get_rating(db=db, spec_rating=spec_rating)


@router.post("/movie/downloads/", response_model=int)
def get_downloads(movie: schemas.MovieRating, db: Session = Depends(get_db)):
    """
    Gets number of downloads of a movie
    """
    return crud.get_number_of_downloads(db=db, movie=movie)


@router.post("/movie/referrals/", response_model=int)
def get_referrals(movie: schemas.MovieRating, db: Session = Depends(get_db)):
    """
    Gets total number of referrals of a movie
    """
    return crud.get_no_of_referrals(db=db, movie=movie)


@router.post("/rate/", response_model=schemas.Rating)
def create_or_update_rating(spec_rating: schemas.SpecificRatingScore, db: Session = Depends(get_db)):
    """
    Create or update a movie rating by an ip_address
    """
    return crud.create_or_update_rating(db=db, spec_rating=spec_rating)


@router.post("/referral/", response_model=schemas.Referral)
def refer_to_movie(referral: schemas.ReferralCreate, db: Session = Depends(get_db)):
    """
    Create a referral object for a movie and return referral id
    """
    return crud.create_referral(db=db, referral=referral)


@router.post("/referral/id/", response_model=schemas.MovieReferral)
def get_referral_by_id(referral_id: str, db: HashableSession = Depends(get_db)):
    """
    Get movie object by referral id
    """
    return crud.get_movie_by_referral_id(db=db, referral_id=referral_id)


@router.post("/download/", response_model=schemas.Download)
def download_movie(download: schemas.DownloadCreate, db: Session = Depends(get_db)):
    """
    Create a download object for a movie by ip_address
    """
    return crud.create_download(db=db, download=download)


@router.post("/download/highest/", response_model=List[schemas.MovieDownloads])
def filter_highest_downloads(filter_: schemas.DownloadFilter, db: HashableSession = Depends(get_db)):
    """
    Get the most downloaded movies in a period
    """
    highest = crud.get_highest_downloads(db=db, filter_=filter_)
    print(crud.get_highest_downloads.cache_info(), print(db.__hash__(), filter_.__hash__()))
    return highest


@router.post("/movie/", response_model=schemas.Movie)
def get_movie_by_schema(movie: schemas.MovieBase, db: Session = Depends(get_db)):
    """
    Return full schema of a movie
    """
    return crud.get_movie_by_schema(db=db, movie=movie).first()


@router.post("/rating/", response_model=List[schemas.Rating])
def get_ratings(movie: schemas.MovieRating, db: Session = Depends(get_db)):
    """
    Retrieves all the rating objects of a movie
    """
    return crud.get_movie_ratings(db=db, movie=movie)


@router.get("/list/", response_model=List[schemas.MovieReferral])
def list_movies(engine: str = "netnaija", page: int = 1, num: int = 20, db: HashableSession = Depends(get_db)):
    """
    Lists movies from an engine

    engine: the engine to list data from
    page: the page number
    num: the number of results to return per page
    """
    params = HashableParams({
        "num": num,
        "engine": engine,
        "page": page
    })
    movies = utils.get_movies_from_remote(f"{settings.gophie_host}/list", params, engine, db)
    if not movies:
        movies = crud.list_movies(db=db, engine=engine, page=page, num=num)
    return movies


@router.get("/search/", response_model=List[schemas.MovieReferral])
def search_movies(engine: str = "netnaija", query: str = "hello", page: int = 1, num: int = 20, db: HashableSession = Depends(get_db)):
    """
    Searches movies from an engine using partial ratio

    engine: the engine to list data from
    query: the search term urlencoded
    """
    params = HashableParams({
        "query": query,
        "engine": engine,
        "page": page
    })
    movies = utils.get_movies_from_remote(f"{settings.gophie_host}/search", params, engine, db)
    if not movies:
        movies = crud.search_movies(db=db, engine=engine, query=query, page=page, num=num)
    return movies

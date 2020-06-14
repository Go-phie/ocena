from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine, HashableSession

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://gophie-ocena.herokuapp.com",
    "http://localhost:3000",
    "https://gophie.netlify.app",
    "https://gophie-ssr.herokuapp.com",
    "https://gophie.cam",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex="https://deploy-preview-\d+--gophie\.netlify\.app",
)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.post("/movie/ratings/average/", response_model=schemas.AverageRating)
def get_average_ratings(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    """
    Get average movie ratings and number of people who have rated
    """
    return crud.get_movie_average_ratings(db=db, movie=movie)


@app.post("/movie/rating/", response_model=schemas.Rating)
def get_ip_rating(spec_rating: schemas.SpecificRating, db: Session = Depends(get_db)):
    """
    Get Rating of a movie by an ip_address
    """
    return crud.get_rating(db=db, spec_rating=spec_rating)


@app.post("/movie/downloads/", response_model=int)
def get_downloads(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    """
    Gets number of downloads of a movie
    """
    return crud.get_number_of_downloads(db=db, movie=movie)


@app.post("/movie/referrals/", response_model=int)
def get_referrals(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    """
    Gets total number of referrals of a movie
    """
    return crud.get_no_of_referrals(db=db, movie=movie)


@app.post("/rate/", response_model=schemas.Rating)
def create_or_update_rating(spec_rating: schemas.SpecificRatingScore, db: Session = Depends(get_db)):
    """
    Create or update a movie rating by an ip_address
    """
    return crud.create_or_update_rating(db=db, spec_rating=spec_rating)


@app.post("/referral/", response_model=str)
def refer_to_movie(referral: schemas.ReferralCreate, db: Session = Depends(get_db)):
    """
    Create a referral object for a movie and return referral id
    """
    crud.create_referral(db=db, referral=referral)
    return crud.get_referral_id(db=db, movie=schemas.MovieCreate(name=referral.movie_name, engine=referral.engine))


@app.post("/referral/id/", response_model=schemas.MovieReferral)
def get_referral_by_id(referral_id: str, db: HashableSession = Depends(get_db)):
    """
    Get movie object by referral id
    """
    return crud.get_movie_by_referral_id(db=db, referral_id=referral_id)


@app.post("/download/", response_model=schemas.Download)
def download_movie(download: schemas.DownloadCreate, db: Session = Depends(get_db)):
    """
    Create a download object for a movie by ip_address
    """
    return crud.create_download(db=db, download=download)


@app.post("/download/highest/", response_model=List[schemas.MovieDownloads])
def filter_highest_downloads(filter_: schemas.DownloadFilter, db: HashableSession = Depends(get_db)):
    """
    Get the most downloaded movies in a period
    """
    highest = crud.get_highest_downloads(db=db, filter_=filter_)
    print(crud.get_highest_downloads.cache_info(), print(db.__hash__(), filter_.__hash__()))
    return highest


@app.post("/movie/", response_model=schemas.Movie)
def get_movie_by_schema(movie: schemas.MovieBase, db: Session = Depends(get_db)):
    """
    Return full schema of a movie
    """
    return crud.get_movie_by_schema(db=db, movie=movie).first()


@app.post("/rating/", response_model=List[schemas.Rating])
def get_ratings(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    """
    Retrieves all the rating objects of a movie
    """
    return crud.get_movie_ratings(db=db, movie=movie)

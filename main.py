from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://gophie-ocena.herokuapp.com",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.post("/rate/", response_model=schemas.Rating)
def create_or_update_rating(spec_rating: schemas.SpecificRatingScore, db: Session = Depends(get_db)):
    """
    Create or update a movie rating by an ip_address
    """
    return crud.create_or_update_rating(db=db, spec_rating=spec_rating)

@app.post("/movie/rating/", response_model=schemas.Rating)
def get_ip_rating(spec_rating: schemas.SpecificRating, db: Session = Depends(get_db)):
    """
    Get Rating of a movie by an ip_address
    """
    return crud.get_rating(db=db, spec_rating=spec_rating)

@app.post("/movie/", response_model=schemas.Movie)
def get_movie_by_schema(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
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
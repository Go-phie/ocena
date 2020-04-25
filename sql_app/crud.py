from functools import reduce
from sqlalchemy.orm import Session
from sqlalchemy import  exc
from . import models, schemas
from utils import add_ratings


def get_movie(db: Session, movie_id: int):
    """
    Get Movie by Id
    """
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

def get_movie_by_schema(db: Session, movie: schemas.MovieCreate):
    return db.query(models.Movie).filter(models.Movie.name==movie.name, models.Movie.engine==movie.engine)

def get_rating_by_schema(db: Session, rating: schemas.IndexedRating):
    return db.query(models.Rating).filter(models.Rating.ip_address==rating.ip_address, models.Rating.movie_id==rating.movie_id)

def create_movie(db: Session, movie: schemas.MovieCreate):
    """
    Attempts to create a movie, If exist retrieves the movie
    """
    db_movie = models.Movie(name=movie.name, engine=movie.engine)
    db.add(db_movie)
    try:
        db.commit()
        db.refresh(db_movie)
    except (exc.IntegrityError) as e:
        # Incase it breaks unique together constraint, then return
        # The movie
        db.rollback()
        db_movie = get_movie_by_schema(db, movie).first()
    return db_movie

def get_movie_ratings(db: Session, movie: schemas.MovieCreate):
    """
    Get all rating objects of a movie
    """
    movie = create_movie(db, movie)
    return movie.ratings

def get_movie_average_ratings(db: Session, movie: schemas.MovieCreate):
    """
    Get the average ratings and number of raters of a particular movie
    If movie does not exist, creates movie
    """
    db_query = get_movie_by_schema(db, movie)
    if db_query.count() < 1:
        db_movie = create_movie(db, movie)
    else:
        db_movie = db_query.first()
    total_sum = add_ratings(db_movie.ratings)
    if len(db_movie.ratings) > 0:
        average_ratings = total_sum/len(db_movie.ratings)
        return schemas.AverageRating(average_ratings=average_ratings, by=len(db_movie.ratings))
    else:
        return schemas.AverageRating(average_ratings=0, by=0)

def create_or_update_rating(db: Session, spec_rating: schemas.SpecificRatingScore):
    movie = create_movie(db, schemas.MovieCreate(name=spec_rating.movie_name, engine=spec_rating.engine))
    db_rating_query = get_rating_by_schema(db, schemas.IndexedRating(ip_address=spec_rating.ip_address, movie_id=movie.id))
    if db_rating_query.count() < 1 :
        db_rating = models.Rating(ip_address=spec_rating.ip_address, score=spec_rating.score, movie_id=movie.id)
        db.add(db_rating)
    else:
       db_rating = db_rating_query.first()
       db_rating.score = spec_rating.score
    db.commit()
    db.refresh(db_rating)
    return db_rating


def get_rating(db: Session, spec_rating: schemas.SpecificRating):
    """
    Gets the specific rating of a particular movie by an ip_address
    """
    movie = create_movie(db, schemas.MovieCreate(name=spec_rating.movie_name, engine=spec_rating.engine))
    rating = db.query(models.Rating).filter(models.Rating.ip_address==spec_rating.ip_address, models.Rating.movie_id==movie.id).first()
    return rating

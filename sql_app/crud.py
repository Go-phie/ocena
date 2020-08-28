import uuid
import datetime
from functools import lru_cache
from sqlalchemy.orm import Session
from sqlalchemy import exc
from . import models, schemas
from .database import HashableSession
from utils import add_ratings, get_movie_download


def get_movie(db: Session, movie_id: int):
    """
    Get Movie by Id
    """
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


@lru_cache(maxsize=1000)
def list_movies(db: Session, engine: str, page: int, num: int):
    """
    Get List of Movies. With pagination and a total of `num` rows per query
    """
    return list(db.query(models.Movie).filter(models.Movie.engine == engine).limit(num).offset(num * (page-1)))


@lru_cache(maxsize=200)
def get_movie_by_referral_id(db: HashableSession, referral_id: str):
    """
    Get Movie by referral id
    """
    return db.query(models.Movie).filter(models.Movie.referral_id == referral_id).first()


def get_movie_by_schema(db: Session, movie: schemas.MovieCreate):
    return db.query(models.Movie).filter(models.Movie.name == movie.name, models.Movie.engine == movie.engine)


def get_rating_by_schema(db: Session, rating: schemas.IndexedRating):
    return db.query(models.Rating).filter(models.Rating.ip_address == rating.ip_address, models.Rating.movie_id == rating.movie_id)


def create_movie(db: Session, db_movie: models.Movie):
    """
    Attempts to create a movie, If exist retrieves the movie
    """
    db.add(db_movie)
    try:
        db.commit()
        db.refresh(db_movie)
    except (exc.IntegrityError):
        # Incase it breaks unique together constraint, then return
        # The movie but update it's fields
        db.rollback()
        movie = get_movie_by_schema(db, schemas.MovieCreate(
            name=db_movie.name, engine=db_movie.engine)).first()
        movie.download_link = db_movie.download_link if db_movie.download_link else movie.download_link
        movie.description = db_movie.description if db_movie.description else movie.description
        movie.size = db_movie.size if db_movie.size else movie.size
        movie.year = db_movie.year if db_movie.year else movie.year
        movie.cover_photo_link = db_movie.cover_photo_link
        if movie.referral_id == None:
            movie.referral_id = str(uuid.uuid4())
        db.commit()
        db_movie = movie
    return db_movie


def create_movie_by_moviecreate(db: Session, movie: schemas.MovieCreate):
    """
    Creates a movie or retrieves it by using MovieCreate
    """
    db_movie = models.Movie(name=movie.name, engine=movie.engine)
    return create_movie(db, db_movie)


def get_movie_ratings(db: Session, movie: schemas.MovieCreate):
    """
    Get all rating objects of a movie
    """
    movie = create_movie_by_moviecreate(db, movie)
    return movie.ratings


def get_movie_average_ratings(db: Session, movie: schemas.MovieCreate):
    """
    Get the average ratings and number of raters of a particular movie
    If movie does not exist, creates movie
    """
    db_query = get_movie_by_schema(db, movie)
    if db_query.count() < 1:
        movie = models.Movie(
            name=movie.name,
            engine=movie.engine,
            year=movie.year,
            description=movie.description,
            download_link=movie.download_link,
            size=movie.size,
            cover_photo_link=movie.cover_photo_link,
        )
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
    movie = models.Movie(
        name=spec_rating.movie_name,
        engine=spec_rating.engine,
        year=spec_rating.year,
        description=spec_rating.description,
        download_link=spec_rating.download_link,
        size=spec_rating.size,
        cover_photo_link=spec_rating.cover_photo_link,
    )
    movie = create_movie(db, movie)
    db_rating_query = get_rating_by_schema(db, schemas.IndexedRating(
        ip_address=spec_rating.ip_address, movie_id=movie.id))
    if db_rating_query.count() < 1:
        db_rating = models.Rating(
            ip_address=spec_rating.ip_address, score=spec_rating.score, movie_id=movie.id)
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
    db_query = get_movie_by_schema(db, schemas.MovieCreate(
        name=spec_rating.movie_name, engine=spec_rating.engine))
    if db_query.count() >= 1:
        movie = db_query.first()
        rating = db.query(models.Rating).filter(models.Rating.ip_address ==
                                                spec_rating.ip_address, models.Rating.movie_id == movie.id).first()
    else:
        return 0
    return rating


def create_download(db: Session, download: schemas.DownloadCreate):
    """
    Creates a particular download object
    """
    movie = models.Movie(
        name=download.movie_name,
        engine=download.engine,
        year=download.year,
        description=download.description,
        download_link=download.download_link,
        size=download.size,
        cover_photo_link=download.cover_photo_link,
    )
    movie = create_movie(db, movie)
    db_download = models.Download(
        movie_id=movie.id, ip_address=download.ip_address, datetime=datetime.datetime.utcnow())
    db.add(db_download)
    db.commit()
    db.refresh(db_download)
    return db_download


def get_number_of_downloads(db: Session, movie: schemas.MovieCreate):
    """
    Get number of downloads
    """
    db_query = get_movie_by_schema(db, movie)
    if db_query.count() < 1:
        return 0
    else:
        db_movie = db_query.first()
    return len(db_movie.downloads)


@lru_cache(maxsize=100)
def get_highest_downloads(db: HashableSession, filter_: schemas.DownloadFilter):
    """
    Gets the x highest downloaded movies in the last period
    """
    options = {
        "weeks": datetime.timedelta(weeks=filter_.filter_num),
        "hours": datetime.timedelta(hours=filter_.filter_num),
        "days": datetime.timedelta(days=filter_.filter_num)
    }
    x_times_ago = datetime.datetime.utcnow() - options[filter_.filter_by]
    downloads_in_the_last_x_times = db.query(models.Download).filter(
        models.Download.datetime > x_times_ago).all()
    movie_map = get_movie_download(downloads_in_the_last_x_times)
    movie_downloads = [
        schemas.MovieDownloads(
            id=get_movie(db, int(mov_key)).id,
            name=get_movie(db, int(mov_key)).name,
            engine=get_movie(db, int(mov_key)).engine,
            downloads=downloads,
            description=get_movie(db, int(mov_key)).description,
            size=get_movie(db, int(mov_key)).size,
            download_link=get_movie(db, int(mov_key)).download_link,
            cover_photo_link=get_movie(db, int(mov_key)).cover_photo_link,
            referral_id=get_movie(db, int(mov_key)).referral_id,
        )
        for mov_key, downloads in movie_map.most_common(filter_.top)]
    return movie_downloads


def create_referral(db: Session, referral: schemas.ReferralCreate):
    """
    Creates a particular referral object (for data tracking purposes)
    """
    movie = models.Movie(
        name=referral.movie_name,
        engine=referral.engine,
        year=referral.year,
        description=referral.description,
        download_link=referral.download_link,
        cover_photo_link=referral.cover_photo_link,
        size=referral.size,
    )
    movie = create_movie(db, movie)
    db_referral = models.Referral(
        movie_id=movie.id, ip_address=referral.ip_address, datetime=datetime.datetime.utcnow())
    db.add(db_referral)
    db.commit()
    db.refresh(db_referral)
    return db_referral


def get_no_of_referrals(db: Session, movie: schemas.MovieCreate):
    """
    Get number of referrals
    """
    db_query = get_movie_by_schema(db, movie)
    if db_query.count() < 1:
        db_movie = create_movie_by_moviecreate(db, movie)
    else:
        db_movie = db_query.first()
    return len(db_movie.referrals)


def get_referral_id(db: Session, movie: schemas.MovieCreate):
    """
    Get referral_id
    """
    db_query = get_movie_by_schema(db, movie)
    if db_query.count() < 1:
        return "No referral id, save movie first"
    else:
        db_movie = db_query.first()
        if db_movie.referral_id == None:
            db_movie.referral_id = str(uuid.uuid4())
            db.commit()
            db.refresh(db_movie)
    return db_movie.referral_id

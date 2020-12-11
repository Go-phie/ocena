import uuid
import datetime
from functools import lru_cache

from sqlalchemy.orm import Session
from sqlalchemy import exc, func

from app.models import models, schemas, HashableSession
from app.models.utils import add_ratings, get_movie_download


def get_movie(db: Session, movie_id: int):
    """
    Get Movie by Id
    """
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


@lru_cache(maxsize=4096)
def list_movies(db: HashableSession, engine: str, page: int, num: int):
    """
    Get List of Movies. With pagination and a total of `num` rows per query
    """
    return list(db.query(models.Movie)
                .order_by(models.Movie.date_created.desc())
                .filter(func.lower(models.Movie.engine) == engine.lower())
                .limit(num).offset(num * (page-1)))

@lru_cache(maxsize=4096)
def search_music(db: HashableSession, engine: str, query: str):
    """
    Search movies using fuzzy partial
    """
    # TODO Improve fuzzy searching
    return list(db.query(models.Music)
                .filter(models.Music.title.ilike("%"+query+"%"), func.lower(models.Music.source) == engine.lower())
                )

@lru_cache(maxsize=4096)
def search_movies(db: HashableSession, engine: str, query: str, page: int, num: int):
    """
    Search movies using fuzzy partial
    """
    # TODO Improve fuzzy searching
    return list(db.query(models.Movie)
                .filter(models.Movie.name.ilike("%"+query+"%"), func.lower(models.Movie.engine) == engine.lower())
                .limit(num)
                .offset(num * (page-1))
                )


@lru_cache(maxsize=256)
def get_movie_by_referral_id(db: HashableSession, referral_id: str):
    """
    Get Movie by referral id
    """
    return db.query(models.Movie).filter(models.Movie.referral_id == referral_id).first()


def get_movie_by_schema(db: Session, movie: schemas.MovieCreate):
    return db.query(models.Movie).filter(models.Movie.name == movie.name, models.Movie.engine == movie.engine)


def get_rating_by_schema(db: Session, rating: schemas.IndexedRating):
    return db.query(models.Rating).filter(models.Rating.ip_address == rating.ip_address, models.Rating.movie_id == rating.movie_id)

def create_music(db: Session, db_music: models.Music):
    """
    Attempts to create music, If exist retrieves the movie
    """
    db.add(db_music)
    try:
        db.commit()
        db.refresh(db_music)
    except (exc.IntegrityError):
        # Incase it breaks unique together constraint, then return
        # The music but update it's fields
        db.rollback()
        music = db.query(models.Music).filter(models.Music.download_link == db_music.download_link, models.Music.source == db_music.source).first()

        music.download_link = db_music.download_link if db_music.download_link else music.download_link
        music.artiste = db_music.artiste if db_music.artiste else music.artiste
        music.size = db_music.size if db_music.size else music.size
        music.source = db_music.source if db_music.source else music.source
        music.title = db_music.title if db_music.title else music.title
        music.collection = db_music.collection if db_music.collection else music.collection
        music.picture_link = db_music.picture_link if db_music.picture_link else music.picture_link
        music.duration = db_music.duration if db_music.duration else music.duration
        db.commit()
        db_music = music
    return db_music

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
        movie.quality = db_movie.quality if db_movie.quality else movie.quality
        movie.is_series = db_movie.is_series
        movie.s_download_link = db_movie.s_download_link if db_movie.s_download_link else movie.s_download_link
        movie.category = db_movie.category if db_movie.category else movie.category
        movie.cast = db_movie.cast if db_movie.cast else movie.cast
        movie.upload_date = db_movie.upload_date if db_movie.upload_date else movie.upload_date
        movie.subtitle_link = db_movie.subtitle_link if db_movie.subtitle_link else movie.subtitle_link
        movie.subtitle_links = db_movie.subtitle_links if db_movie.subtitle_links else movie.subtitle_links
        movie.imdb_link = db_movie.imdb_link if db_movie.imdb_link else movie.imdb_link
        movie.tags = db_movie.tags if db_movie.tags else movie.tags
        movie.date_created = db_movie.date_created if db_movie.date_created else movie.date_created

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


def get_movie_ratings(db: Session, movie: schemas.MovieRating):
    """
    Get all rating objects of a movie
    """
    movie = db.query(models.Movie).filter(models.Movie.referral_id == movie.referral_id).first()
    if movie:
        return movie.ratings
    else:
        return []


def get_movie_average_ratings(db: Session, movie: schemas.MovieRating):
    """
    Get the average ratings and number of raters of a particular movie
    """
    db_movie = db.query(models.Movie).filter(models.Movie.referral_id == movie.referral_id).first()
    total_sum = add_ratings(db_movie.ratings)
    if len(db_movie.ratings) > 0:
        average_ratings = total_sum/len(db_movie.ratings)
        return schemas.AverageRating(average_ratings=average_ratings, by=len(db_movie.ratings))
    else:
        return schemas.AverageRating(average_ratings=0, by=0)


def create_or_update_rating(db: Session, spec_rating: schemas.SpecificRatingScore):
    movie = db.query(models.Movie).filter(models.Movie.referral_id == spec_rating.referral_id).first()
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
    db_query = db.query(models.Movie).filter(models.Movie.referral_id == spec_rating.referral_id)
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
    movie = db.query(models.Movie).filter(models.Movie.referral_id == download.referral_id).first()
    db_download = models.Download(
        movie_id=movie.id, ip_address=download.ip_address, datetime=datetime.datetime.utcnow())
    db.add(db_download)
    db.commit()
    db.refresh(db_download)
    return db_download


def get_number_of_downloads(db: Session, movie: schemas.MovieRating):
    """
    Get number of downloads
    """
    db_query = db.query(models.Movie).filter(models.Movie.referral_id == movie.referral_id)
    if db_query.count() < 1:
        return 0
    else:
        db_movie = db_query.first()
    return len(db_movie.downloads)


@lru_cache(maxsize=128)
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
            quality=get_movie(db, int(mov_key)).quality,
            is_series=get_movie(db, int(mov_key)).is_series,
            s_download_link=get_movie(db, int(mov_key)).s_download_link,
            category=get_movie(db, int(mov_key)).category,
            cast=get_movie(db, int(mov_key)).cast,
            upload_date=get_movie(db, int(mov_key)).upload_date,
            subtitle_link=get_movie(db, int(mov_key)).subtitle_link,
            subtitle_links=get_movie(db, int(mov_key)).subtitle_links,
            imdb_link=get_movie(db, int(mov_key)).imdb_link,
            tags=get_movie(db, int(mov_key)).tags,
        )
        for mov_key, downloads in movie_map.most_common(filter_.top)]
    return movie_downloads


def create_referral(db: Session, referral: schemas.ReferralCreate):
    """
    Creates a particular referral object (for data tracking purposes)
    """
    movie = db.query(models.Movie).filter(models.Movie.referral_id == referral.referral_id).first()
    db_referral = models.Referral(
        movie_id=movie.id, ip_address=referral.ip_address, datetime=datetime.datetime.utcnow())
    db.add(db_referral)
    db.commit()
    db.refresh(db_referral)
    return db_referral


def get_no_of_referrals(db: Session, movie: schemas.MovieRating):
    """
    Get number of referrals
    """
    db_movie = db.query(models.Movie).filter(models.Movie.referral_id == movie.referral_id).first()
    return len(db_movie.referrals)

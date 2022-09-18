import datetime
from typing import List

from sqlalchemy import (Boolean, Column, ForeignKey,
                        Integer, DateTime, String,
                        UniqueConstraint, JSON, DateTime,
                        )
from sqlalchemy.orm import relationship
from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)

from app.settings import Base


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    oauth_accounts: List[OAuthAccount] = relationship(
        "OAuthAccount", lazy="joined")
    referrals = relationship("Referral",  back_populates="user")
    downloads = relationship("Download", back_populates="user")
    ratings = relationship("Rating", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (UniqueConstraint('name', 'engine'),)

    # meta field names
    id = Column(Integer, primary_key=True, index=True)
    date_created = Column(DateTime)
    # actual field names mapped from gophie_core
    name = Column(String)
    engine = Column(String)
    description = Column(String)
    size = Column(String)
    year = Column(String)
    download_link = Column(String)
    referral_id = Column(String)
    cover_photo_link = Column(String)
    quality = Column(String)
    is_series = Column(Boolean)
    s_download_link = Column(JSON)
    category = Column(String)
    cast = Column(String)
    upload_date = Column(String)
    subtitle_link = Column(String)
    subtitle_links = Column(JSON)
    imdb_link = Column(String)
    tags = Column(String)

    # relationships
    referrals = relationship("Referral", back_populates="owner")
    downloads = relationship("Download", back_populates="owner")
    ratings = relationship("Rating", back_populates="owner")


class Download(Base):
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    ip_address = Column(String)
    datetime = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(ForeignKey("user.id"), nullable=True)

    owner = relationship("Movie", back_populates="downloads")
    user = relationship("User", back_populates="downloads")


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    ip_address = Column(String)
    user_id = Column(ForeignKey("user.id"), nullable=True)

    datetime = Column(DateTime, default=datetime.datetime.utcnow)
    owner = relationship("Movie", back_populates="referrals")
    user = relationship("User", back_populates="referrals")


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint('movie_id', 'ip_address', 'user_id'), )

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    ip_address = Column(String)
    score = Column(Integer)
    user_id = Column(ForeignKey("user.id"), nullable=True)

    owner = relationship("Movie", back_populates="ratings")
    user = relationship("User", back_populates="ratings")


class Music(Base):
    __tablename__ = "music"
    __table_args__ = (UniqueConstraint('source', 'download_link'),)
    index = Column(Integer, primary_key=True, index=True)
    date_created = Column(DateTime)
    # actual field names mapped from mythra
    artiste = Column(String)
    title = Column(String)
    collection = Column(String)
    download_link = Column(String)
    picture_link = Column(String)
    size = Column(String)
    duration = Column(String)
    source = Column(String)

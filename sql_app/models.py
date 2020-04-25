from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (UniqueConstraint('name', 'engine'), )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    engine = Column(String)

    ratings = relationship("Rating", back_populates="owner")

class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint('movie_id', 'ip_address'), )

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    ip_address = Column(String)
    score = Column(Integer)

    owner = relationship("Movie", back_populates="ratings")


from typing import List

from pydantic import BaseModel

class RatingBase(BaseModel):
    ip_address: str

class SpecificRating(RatingBase):
    movie_name: str
    engine: str

class IndexedRating(RatingBase):
    movie_id: int

class SpecificRatingScore(SpecificRating):
    score: str

class Rating(RatingBase):
    id: int
    movie_id: int
    score: int

    class Config:
        orm_mode = True

class AverageRating(BaseModel):
    average_ratings: float
    by: int

class RatingCreate(RatingBase):
    movie_name: str
    engine: str
    score: int

class MovieBase(BaseModel):
    name: str
    engine: str

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    ratings: List[Rating] = []

    class Config:
        orm_mode = True

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

# Rating schemas


class RatingBase(BaseModel):
    ip_address: str


class SpecificRating(RatingBase):
    movie_name: str
    engine: str


class IndexedRating(RatingBase):
    movie_id: int


class SpecificRatingScore(SpecificRating):
    score: str
    description: str
    size: str
    year: str
    download_link: str
    cover_photo_link: str


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


# Download Schemas

class DownloadBase(BaseModel):
    ip_address: str


class DownloadCreate(DownloadBase):
    movie_name: str
    engine: str
    description: str
    size: str
    year: str
    download_link: str
    cover_photo_link: str


class DownloadFilter(BaseModel):
    filter_by: str
    filter_num: int
    top: int

    def __repr__(self):
        day = datetime.today().strftime("%d%m%Y")
        return f"Top {str(self.top)} in the last {str(self.filter_num)} {self.filter_by} on {day}"

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        print(self.__hash__(), other.__hash__())
        return self.__hash__() == other.__hash__()


class Download(DownloadBase):
    id: int
    movie_id: int
    datetime: datetime

    class Config:
        orm_mode = True

# Referral Schemas


class ReferralBase(BaseModel):
    ip_address: str


class ReferralCreate(ReferralBase):
    movie_name: str
    engine: str
    description: str
    size: str
    year: str
    download_link: str
    cover_photo_link: str


class Referral(ReferralBase):
    id: int
    movie_id: int
    datetime: datetime

    class Config:
        orm_mode = True


# Movie Schemas

class MovieBase(BaseModel):
    name: str
    engine: str


class MovieCreate(MovieBase):
    description: Optional[str]
    size: Optional[str]
    year: Optional[str]
    download_link: Optional[str]
    cover_photo_link: Optional[str]


class MovieComplete(MovieCreate):
    id: int
    referral_id: Optional[str]


class MovieReferral(MovieComplete):

    class Config:
        orm_mode = True


class MovieDownloads(MovieComplete):
    downloads: int


class Movie(MovieReferral):
    ratings: List[Rating] = []
    referrals: List[Referral] = []
    downloads: List[Download] = []

    class Config:
        orm_mode = True
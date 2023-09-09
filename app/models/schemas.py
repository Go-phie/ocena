from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, model_validator

# Rating schemas


class MovieORM(BaseModel):
    description: Optional[str] = None
    size: Optional[str] = None
    year: Optional[str] = None
    download_link: Optional[str] = None
    cover_photo_link: Optional[str] = None
    quality: Optional[str] = None
    is_series: Optional[bool] = None
    s_download_link: Optional[dict] = None
    category: Optional[str] = None
    cast: Optional[str] = None
    upload_date: Optional[str] = None
    subtitle_link: Optional[str] = None
    subtitle_links: Optional[dict] = None
    imdb_link: Optional[str] = None
    tags: Optional[str] = None


class RatingBase(BaseModel):
    ip_address: str


class SpecificRating(RatingBase):
    referral_id: str


class IndexedRating(RatingBase):
    movie_id: int


class SpecificRatingScore(SpecificRating):
    score: int


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
    referral_id: str


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
    referral_id: str


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


class MovieRating(BaseModel):
    referral_id: str


class MovieCreate(MovieBase, MovieORM):
    pass


class MovieComplete(MovieCreate):
    id: int
    referral_id: Optional[str] = None


class MovieReferral(MovieComplete):
    class Config:
        orm_mode = True


class MovieDownloads(MovieComplete):
    downloads: int


class Movie(MovieReferral):
    ratings: List[Rating] = []
    referrals: List[Referral] = []
    downloads: List[Download] = []

    average_ratings: Optional[AverageRating] = None

    class Config:
        orm_mode = True

    @model_validator(mode="after")
    def get_average_ratings(self):
        if not self.ratings:
            self.average_ratings = AverageRating(average_ratings=0, by=0)
            return self

        average = sum(rating.score for rating in self.ratings) / len(self.ratings)
        self.average_ratings = AverageRating(
            average_ratings=average, by=len(self.ratings)
        )
        return self

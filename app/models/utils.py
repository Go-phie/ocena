import sqlalchemy
import collections
from functools import lru_cache
from sqlalchemy import and_, func

from app.models import HashableSession


def column_windows(session, column, windowsize):
    """Return a series of WHERE clauses against
    a given column that break it into windows.

    Result is an iterable of tuples, consisting of
    ((start, end), whereclause), where (start, end) are the ids.

    Requires a database that supports window functions,
    i.e. Postgresql, SQL Server, Oracle.

    Enhance this yourself !  Add a "where" argument
    so that windows of just a subset of rows can
    be computed.

    """
    def int_for_range(start_id, end_id):
        if end_id:
            return and_(
                column >= start_id,
                column < end_id
            )
        else:
            return column >= start_id

    q = session.query(column, func.row_number().over(
        order_by=column).label('rownum'))
    if windowsize > 1:
        q = q.filter(sqlalchemy.text("movies.id %% %d=1" % windowsize))

    intervals = [id for id in q]

    while intervals:
        start = intervals.pop(0)
        if intervals:
            end = intervals[0]
        else:
            end = None
        yield int_for_range(start, end)


@lru_cache(maxsize=1024)
def windowed_query(q: HashableSession, column, windowsize):
    """"Break a Query into windows on a given column."""
    return list(q.filter(whereclause).order_by(column))


def add_ratings(ratings_list):
    counter = 0
    for rating in ratings_list:
        counter += rating.score
    return counter


def get_movie_download(download_queryset):
    movie_download = collections.Counter()
    for instance in download_queryset:
        movie_download[str(instance.movie_id)] += 1
    return movie_download

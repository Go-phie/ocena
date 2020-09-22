import collections


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

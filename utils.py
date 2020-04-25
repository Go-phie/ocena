def add_ratings(ratings_list):
    counter = 0
    for rating in ratings_list:
        counter += rating.score
    return counter
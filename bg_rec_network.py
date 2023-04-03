from bg_redis import BoardGameAPI
import csv
import time
from functools import lru_cache, reduce
from itertools import accumulate

QUANT_FEATS = {'GameWeight': 2, 'MinPlayers': 4, 'MaxPlayers': 4, 'ComAgeRec': 4, 'MfgPlaytime': 180,
               'ComMinPlaytime': 180, 'ComMaxPlaytime': 180, 'MfgAgeRec': 4}


# for collaborative recs
def write_user_sim_score(writer, user_a, user_a_ratings_tuple, user_b, game_db, min_score=0):
    user_b_ratings_tuple = game_db.get_transform_users_ratings(user_b)
    user_a_ratings = user_a_ratings_tuple[1]
    user_b_ratings = user_b_ratings_tuple[1]

    users_a_b_games = user_a_ratings_tuple[0].intersection(user_b_ratings_tuple[0])

    score = len(set(filter(lambda book: user_a_ratings[book][1] <= user_b_ratings[book][0] <=
                                        user_a_ratings[book][2], users_a_b_games)))
    if score >= min_score:
        row = [str(user_a), str(user_b), str(score)]
        writer.writerow(row)


# for collaborative recs
def generate_colab_file(book_db, min_sim_score=1):
    users = [int(user) for user in book_db.get_all_users()]
    # initialize writer and add header to file
    with open('edges_colab.csv', 'w') as infile:
        writer = csv.writer(infile)
        header = ['to_node', 'from_node', 'sim_score']
        writer.writerow(header)
        for i in range(len(users) - 1):
            outer_user = users[i]
            outer_ratings = book_db.get_transform_users_ratings(outer_user)
            for inner_user in users[i + 1:]:
                write_user_sim_score(writer, outer_user, outer_ratings, inner_user, book_db,
                                     min_score=min_sim_score)


# for content recs
def write_game_sim_score(writer, game_a, game_a_data, game_b, game_db, min_score=0):
    game_b_data = game_db.get_game_data(game_b)
    """
    score = []
    for feature in game_a_data.keys():
        if feature in QUANT_FEATS.keys():
            if abs(game_a_data[feature] - game_b_data[feature] <= QUANT_FEATS[feature]):
                score.append(1)
        else:
            if game_a_data[feature] == game_b_data[feature]:
                score.append(1)
    """
    score = sum([1 for feature in game_a_data.keys() if
                 (feature in QUANT_FEATS.keys() and abs(game_a_data[feature] - game_b_data[feature]) <= QUANT_FEATS[
                     feature]) or
                 (feature not in QUANT_FEATS.keys() and
                  game_a_data[feature] == game_b_data[feature])])
    if score >= min_score:
        writer.writerow([str(game_a), str(game_b), str(score)])


# for content recs
def generate_content_file(game_db, min_sim_score=5):
    games = list({game for game in game_db.get_all_games()})
    # initialize writer and add header to file
    with open('edges_colab.csv', 'w') as infile:
        writer = csv.writer(infile)
        header = ['to_node', 'from_node', 'sim_score']
        writer.writerow(header)
        for i in range(len(games) - 1):
            outer_game = games[i]
            outer_data = game_db.get_game_data(outer_game)
            for inner_game in games[i + 1:]:
                write_game_sim_score(writer, outer_game, outer_data, inner_game, game_db,
                                     min_score=min_sim_score)


"""
For every game combo: 
for quant features:
see if within threshold
for other features, check equality
"""

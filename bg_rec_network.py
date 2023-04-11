from bg_redis import BoardGameAPI
import csv
import time
from functools import lru_cache, reduce
from itertools import accumulate

QUANT_FEATS = {'GameWeight': 1, 'MinPlayers': 1, 'MaxPlayers': 1, 'ComAgeRec': 2, 'MfgPlaytime': 30,
               'ComMinPlaytime': 30, 'ComMaxPlaytime': 30, 'MfgAgeRec':2}
ALL_FEATS = ['GameWeight', 'MinPlayers', 'MaxPlayers', 'MfgPlaytime', 'ComMinPlaytime', 'ComMaxPlaytime',
             'MfgAgeRec', 'Cat:Thematic', 'Cat:Strategy', 'Cat:War', 'Cat:Family', 'Cat:CGS', 'Cat:Abstract',
             'Cat:Party', 'Cat:Childrens', 'Alliances', 'Area Majority / Influence', 'Auction/Bidding',
             'Dice Rolling', 'Hand Management', 'Simultaneous Action Selection', 'Trick-taking', 'Hexagon Grid',
             'Once-Per-Game Abilities', 'Set Collection', 'Tile Placement', 'Action Points', 'Investment',
             'Market', 'Square Grid', 'Stock Holding', 'Victory Points as a Resource', 'Enclosure',
             'Pattern Building', 'Pattern Recognition', 'Modular Board', 'Network and Route Building',
             'Point to Point Movement', 'Melding and Splaying', 'Negotiation', 'Trading', 'Push Your Luck',
             'Income', 'Race', 'Random Production', 'Variable Set-up', 'Roll / Spin and Move',
             'Variable Player Powers', 'Action Queue', 'Bias', 'Grid Movement', 'Lose a Turn',
             'Programmed Movement', 'Scenario / Mission / Campaign Game', 'Voting', 'Events', 'Paper-and-Pencil',
             'Player Elimination', 'Role Playing', 'Movement Points', 'Simulation', 'Variable Phase Order',
             'Area Movement', 'Commodity Speculation', 'Cooperative Game', 'Deduction', 'Sudden Death Ending',
             'Connections', 'Highest-Lowest Scoring', 'Betting and Bluffing', 'Memory', 'Score-and-Reset Game',
             'Layering', 'Map Addition', 'Secret Unit Deployment', 'Increase Value of Unchosen Resources',
             'Ratio / Combat Results Table', 'Take That', 'Team-Based Game', 'Campaign / Battle Card Driven',
             'Tech Trees / Tech Tracks', 'Player Judge', 'Chit-Pull System', 'Three Dimensional Movement',
             'Action Drafting', 'Minimap Resolution', 'Stat Check Resolution', 'Action Timer',
             'Pick-up and Deliver', 'Map Deformation', 'Bingo', 'Crayon Rail System', 'Multiple Maps',
             'Hidden Roles', 'Line Drawing', 'Tug of War', 'Pattern Movement', 'Static Capture',
             'Different Dice Movement', 'Chaining', 'Ladder Climbing', 'Predictive Bid', 'Solo / Solitaire Game',
             'Line of Sight', 'Critical Hits and Failures', 'Interrupts', 'Zone of Control', 'Bribery',
             'End Game Bonuses', 'Area-Impulse', 'Worker Placement', 'Measurement Movement', 'Map Reduction',
             'Real-Time', 'Resource to Move', 'Mancala', 'Ownership', 'Kill Steal', 'Hidden Movement',
             'Track Movement', 'Deck Construction', 'Drafting', 'TableauBuilding', "Prisoner's Dilemma",
             'Hidden Victory Points', 'Movement Template', 'Slide/Push', 'Targeted Clues', 'Command Cards',
             'Grid Coverage', 'Relative Movement', 'Action/Event', 'Card Play Conflict Resolution',
             'I Cut You Choose', 'Die Icon Resolution', 'Elapsed Real Time Ending', 'Advantage Token',
             'Storytelling', 'Catch the Leader', 'Roles with Asymmetric Information', 'Traitor Game',
             'Moving Multiple Units', 'Semi-Cooperative Game', 'Communication Limits', 'Time Track',
             'Speed Matching', 'Cube Tower', 'Re-rolling and Locking', 'Impulse Movement', 'Loans',
             'Delayed Purchase', 'Deck Bag and Pool Building', 'Move Through Deck', 'Single Loser Game',
             'Matching', 'Induction', 'Physical Removal', 'Narrative Choice / Paragraph', 'Pieces as Map',
             'Follow', 'Finale Ending', 'Order Counters', 'Contracts', 'Passed Action Token', 'King of the Hill',
             'Action Retrieval', 'Force Commitment', 'Rondel', 'Automatic Resource Growth', 'Legacy Game',
             'Dexterity', 'Physical']


# for collaborative recs
def write_user_sim_score(writer, user_a, user_a_ratings_tuple, user_b, game_db, min_score=0):
    user_b_ratings_tuple = game_db.get_transform_users_ratings(user_b)
    user_a_ratings = user_a_ratings_tuple[1]
    user_b_ratings = user_b_ratings_tuple[1]

    users_a_b_games = user_a_ratings_tuple[0].intersection(user_b_ratings_tuple[0])
    score = 0
    for game in users_a_b_games:
        user_a_rating = user_a_ratings[game][0]
        user_b_rating = user_b_ratings[game][0]
        if abs(user_a_rating - user_b_rating) <= 2:
            print('True')
            score += 1
    '''
    score = sum([1 if abs(user_a_ratings[game][0] - user_b_ratings[game][0]) <= 2
                 else 0 for game in users_a_b_games])
    
    score = len(set(filter(lambda book: user_a_ratings[book][1] <= user_b_ratings[book][0] <=
                                        user_a_ratings[book][2], users_a_b_games)))
    '''
    if score >= min_score:
        row = [str(user_a), str(user_b), str(score)]
        writer.writerow(row)


# for collaborative recs
def generate_colab_file(book_db, min_sim_score=1):
    print(len(ALL_FEATS))
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
    # game_b_data = {key: 0 if value == '' else value for key, value in game_db.get_game_data(game_b).items()}
    # game_a_data = {key: 0 if value == '' else value for key, value in game_a_data.items()}
    game_b_data = game_db.get_game_data(game_b)
    '''
    game_data = {}
    for key, value in game_a_data.items():
        if value == '':
            game_data[key] = 0
        else:
            game_data[key] = value
    '''

    """
    score = []
    for feature in game_a_data.keys():
        if feature in QUANT_FEATS.keys():
            if abs(game_a_data[feature] - game_b_data[feature] <= QUANT_FEATS[feature]):
                score.append(1)
        else:
            if game_a_data[feature] == game_b_data[feature]:
                score.append(1)
    print('----------------')
    print(game_a_data)
    print(game_b_data)
    print(game_a_data.keys())
    print(game_b_data.keys())
    """
    score = sum([1 for feature in ALL_FEATS if
                 (feature in QUANT_FEATS.keys() and abs(float(game_a_data[feature]) - float(game_b_data[feature])) <=
                  QUANT_FEATS[feature]) or
                 (feature not in QUANT_FEATS.keys() and
                  game_a_data[feature] == game_b_data[feature])])
    if score >= min_score:
        row = [str(game_a), str(game_b), str(score)]
        writer.writerow(row)


# for content recs
def generate_content_file(game_db, min_sim_score=5):
    games = list({game for game in game_db.get_all_games()})
    # initialize writer and add header to file
    with open('edges_content.csv', 'w') as infile:
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

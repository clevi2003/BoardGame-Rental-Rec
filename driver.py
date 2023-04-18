from bg_redis import BoardGameAPI
from bg_neo4j import neo4jAPI
from bg_rec_network import generate_colab_file, generate_content_file


def main():

    redis_api = BoardGameAPI()
    neo4j_api = neo4jAPI()

    # populate game nodes to neo4j
    neo4j_api.add_node('game_nodes.csv', 'Game', ['BGGId'])

    # populate user nodes to neo4j
    neo4j_api.add_node('user_nodes.csv', 'User', ['ID'])

    # populate content based edges to neo4j
    neo4j_api.add_edge('content_edges.csv', 'BGGId', 'BGGId', 'Game', 'Game', 'SIM_GAME', 'score', ['to_node', 'from_node', 'sim_score'])

    # populate collaborative based edges to neo4j
    neo4j_api.add_edge('edges_colab.csv', 'ID', 'ID', 'User', 'User', 'SIM_USER', 'score', ['to_node', 'from_node', 'sim_score'])

    # populate user rating edges to neo4j
    neo4j_api.add_edge('ratings_edges.csv', 'BGGId', 'ID', 'Game', 'User', 'RATED', 'score',
                       ['to_node', 'from_node', 'Rating'])

    # populate claudia's rating edges to neo4j for validation
    neo4j_api.add_edge('claudia_ratings.csv', 'BGGId', 'ID', 'Game', 'User', 'RATED', 'score',
                       ['to_node', 'from_node', 'Rating'])

    # change game ids to int type
    neo4j_api.change_id_toint('Game', 'BGGId')

    # change user ids to int type
    neo4j_api.change_id_toint('User', 'ID')

    # change relationship properties between users to int type
    neo4j_api.change_prop_toint('User', 'User', 'SIM_USER', 'score')

    # change relationship properties between games to int type
    neo4j_api.change_prop_toint('Game', 'Game', 'SIM_GAME', 'score')

    # change relationship properties between user and games to int type
    neo4j_api.change_prop_toint('Game', 'User', 'RATED', 'score')

    print("Claudia's recommendations:")
    print(neo4j_api.get_all_recs(redis_api, 1000))

    # adds book data
    redis_api.add_users('redis_users.csv', 1000)

    # adds game data
    redis_api.add_games("redis_games.csv", 5000)

    # adds ratings data
    redis_api.add_ratings("relevant_ratings.csv")

    # adds claudia's ratings for validation
    redis_api.add_ratings("claudia_ratings_redis.csv")

    # makes collaborative edge file
    # generate_colab_file(redis_api, min_sim_score=1)

    # makes content based edge file
    # generate_content_file(redis_api, min_sim_score=0)



if __name__ == "__main__":
    main()


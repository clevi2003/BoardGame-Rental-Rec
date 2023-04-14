from bg_redis import BoardGameAPI
from bg_neo4j import neo4jAPI
from pprint import pprint
from bg_rec_network import generate_colab_file, generate_content_file
import pandas as pd
import numpy as np
import csv


def main():
    #'''
    redis_api = BoardGameAPI()
    neo4j_api = neo4jAPI()

    # edges = pd.read_csv("final_content_edges.csv")
    # edges = edges[edges.sim_score != 166]
    # edges = edges[edges.sim_score != 167]
    # edges.to_csv('168_content_edges.csv', index=False)


    # populate game nodes to neo4j
    #neo4j_api.add_node('game_nodes_int.csv', 'Game', ['BGGId'])

    # populate user nodes to neo4j
    #df = pd.read_csv("user_nodes.csv")
    #df.to_csv('user_nodes1.csv', index=True)
    #neo4j_api.add_node('user_nodes_int.csv', 'User', ['ID'])

    # populate content based edges to neo4j
    #neo4j_api.add_edge('168_content_edges.csv', 'BGGId', 'BGGId', 'Game', 'Game', 'SIM_GAME', 'score', ['to_node', 'from_node', 'sim_score'])

    # populate collaborative based edges to neo4j
    #neo4j_api.add_edge('colab_int.csv', 'ID', 'ID', 'User', 'User', 'SIM_USER', 'score', ['to_node', 'from_node', 'sim_score'])

    # populate user rating edges to neo4j
    #neo4j_api.add_edge('ratings_int.csv', 'BGGId', 'ID', 'Game', 'User', 'RATED', 'score',
    #                   ['to_node', 'from_node', 'Rating'])

    # change game ids to int type
    #neo4j_api.change_id_toint('Game', 'BGGId')

    # change user ids to int type
    #neo4j_api.change_id_toint('User', 'ID')

    # change relationship properties between users to int type
    #neo4j_api.change_prop_toint('User', 'User', 'SIM_USER', 'score')

    # change relationship properties between games to int type
    #neo4j_api.change_prop_toint('Game', 'Game', 'SIM_GAME', 'score')

    # change relationship properties between user and games to int type
    #neo4j_api.change_prop_toint('Game', 'User', 'RATED', 'score')

    # get recommended games
    print(neo4j_api.get_all_recs(redis_api, 7))

    print(neo4j_api.get_all_recs(redis_api, 200))



    # adds book data
    # redis_api.add_users('unique_users.csv', 1000)
    # print('users added')

    # adds game data
    # redis_api.add_games("final_games.csv", 5000)
    # print('games added')

    # adds ratings data
    # df_ratings = pd.read_csv('user_ratings.csv')
    # df_ratings = df_ratings[df_ratings['Username'].isin(redis_api.get_all_usernames())]
    # df_ratings = df_ratings[df_ratings['BGGId'].isin([int(game) for game in redis_api.get_all_games()])]
    # df_ratings.to_csv('relevant_ratings.csv', index=False)
    # redis_api.add_ratings("relevant_ratings.csv")
    # print('ratings added')


    # makes_edge_file
    #generate_colab_file(redis_api, min_sim_score=1)
    #print('colab file made')
    #generate_content_file(redis_api, min_sim_score=0)
    #print('content file made')

    '''
    df_ratings = pd.read_csv('user_ratings.csv')
    df_user = pd.red_csv('unique_users.csv')
    df_ratings = df_ratings[df_ratings['Username'].isin(df_user['Username'])]
    df_ratings = df_ratings[d_ratings['BGGId].isin(api.get_all_games())]
    
    df_mech = pd.read_csv('mechanics.csv')
    df_mech.columns = [col.replace(',', '') for col in df_mech.columns]
    df = pd.read_csv('games.csv')
    df.columns = [col.replace(',', '') for col in df.columns]

    df = df.merge(df_mech, on='BGGId')
    df = df.replace(',', '', regex=True)
    df = df.sort_values('NumUserRatings')
    print(df.head(10)['NumUserRatings'])
    print(df_mech.columns)
    img = df[['BGGId', 'ImagePath']]
    mech_cols = list(df_mech.columns)
    mech_cols.remove('BGGId')
    cols = ['BGGId', 'Name', 'GameWeight', 'MinPlayers', 'MaxPlayers',
            'MfgPlaytime', 'ComMinPlaytime',
            'ComMaxPlaytime', 'MfgAgeRec', 'Cat:Thematic',
            'Cat:Strategy', 'Cat:War', 'Cat:Family', 'Cat:CGS', 'Cat:Abstract',
            'Cat:Party', 'Cat:Childrens'] + mech_cols
    df_game = df[cols]
    #df_name = df[['BGGId', 'Name']]
    df_game.to_csv('final_games.csv', index=False)
    #df_name.to_csv('game_names.csv', index=False)
    # img.to_csv('game_images.csv')
    '''


if __name__ == "__main__":
    main()

'''
Questions and bugs:
    - Are these games all actually so similar?? 
'''

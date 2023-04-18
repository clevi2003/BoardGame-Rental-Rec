import pandas as pd
from bg_redis import BoardGameAPI


def main():
    redis_api = BoardGameAPI

    # reading in ratings and user files
    df_ratings = pd.read_csv('user_ratings.csv')
    df_user = pd.red_csv('unique_users.csv')
    # filtering for ratings by users in the user df
    df_ratings = df_ratings[df_ratings['Username'].isin(df_user['Username'])]
    df_ratings = df_ratings[df_ratings['BGGId'].isin(redis_api.get_all_games())]

    # reading in and cleaning mechanics file
    df_mech = pd.read_csv('mechanics.csv')
    df_mech.columns = [col.replace(',', '') for col in df_mech.columns]
    # reading in and cleaning games file
    df = pd.read_csv('games.csv')
    df.columns = [col.replace(',', '') for col in df.columns]

    # merging games and mechanics dfs by game id
    df = df.merge(df_mech, on='BGGId')
    df = df.replace(',', '', regex=True)
    df = df.sort_values('NumUserRatings')

    # filtering only for game image data
    img = df[['BGGId', 'ImagePath']]
    mech_cols = list(df_mech.columns)
    mech_cols.remove('BGGId')
    cols = ['BGGId', 'Name', 'GameWeight', 'MinPlayers', 'MaxPlayers',
            'MfgPlaytime', 'ComMinPlaytime',
            'ComMaxPlaytime', 'MfgAgeRec', 'Cat:Thematic',
            'Cat:Strategy', 'Cat:War', 'Cat:Family', 'Cat:CGS', 'Cat:Abstract',
            'Cat:Party', 'Cat:Childrens'] + mech_cols
    df_game = df[cols]
    df_name = df[['BGGId', 'Name']]

    # converting game data to csv files
    df_game.to_csv('final_games.csv', index=False)
    df_name.to_csv('game_names.csv', index=False)
    img.to_csv('game_images.csv')




if __name__ == "__main__":
    main()

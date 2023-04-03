from bg_redis import BoardGameAPI
from bg_rec_network import generate_colab_file, generate_content_file


def main():
    api = BoardGameAPI()

    # adds book data
    api.add_users('unique_users.csv', 500)

    # adds ratings data
    api.add_ratings("user_ratings.csv")

    # adds game data
    api.add_games("final_games.csv", 1000)

    print(api.get_transform_users_ratings(12))

    # makes_edge_file
    generate_colab_file(api, min_sim_score=0)
    generate_content_file(api, min_sim_score=0)


if __name__ == "__main__":
    main()
"""
API for Redis
"""
import redis
from datetime import date
import datetime
from functools import lru_cache
from pprint import pprint

HEADERS = ['BGGId', 'Name', 'GameWeight', 'MinPlayers', 'MaxPlayers', 'ComAgeRec', 'MfgPlaytime', 'ComMinPlaytime',
           'ComMaxPlaytime', 'MfgAgeRec', 'NumUserRatings', 'Cat:Thematic', 'Cat:Strategy', 'Cat:War', 'Cat:Family',
           'Cat:CGS', 'Cat:Abstract', 'Cat:Party', 'Cat:Childrens']


class BoardGameAPI:

    def __init__(self, host='localhost', port=6379, db=0, decode_responses=True):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)
        self.money = 0
        #self.r.flushall()

    def add_users(self, filename, max_users):
        with open(filename, "r") as infile:
            infile.readline()
            # while True:
            for i in range(max_users):
                line = infile.readline().strip()
                if len(line) == 0:
                    break
                # make set of unique user ids
                self.r.sadd('unique_ids', i)
                self.r.sadd('unique_usernames', line)



                # make mapping of username to user id
                self.r.hset('user_id_mapping', mapping={line: i})
                # self.r.sadd('usernames', line)
                # user_id += 1
                # if user_id >= max_users + 1:
                #    break

    @lru_cache(10000)
    def get_user_id(self, username):
        return self.r.hget('user_id_mapping', username)

    def add_ratings(self, file_name):
        """Creates hash for each user and their ratings"""
        with open(file_name, "r") as file:
            # skipping header of csv file
            header = file.readline()
            while True:
                rating = file.readline().strip().split(',')
                # stops if reached the end of file
                if len(rating) < 2:
                    break
                user_id = self.get_user_id(rating[2])
                if not user_id:
                    pass
                if not self.r.sismember('unique_games', rating[0]):
                    pass

                # adds user to list of users who have rated the game
                self.r.hset(rating[0] + ':rated_by', mapping={str(user_id): rating[1]})

                # adds book rating to user's hash of ratings (bgg_id: rating)
                self.r.hset(str(user_id) + ':rated', mapping={rating[0]: rating[1]})
                # self.r.zadd(str(rating[0]), {rating[1]: rating[2]})

    def add_games(self, file_name, max_game_num):
        """Creates hashes containing book info,
         creates lists of all books by a given author,
         creates set of all BGGIds with same title"""
        # opening csv file and reading it
        with open(file_name, "r") as file:
            # header of csv file
            headers = file.readline().strip().split(',')
            for i in range(max_game_num):
                # while True:
                game_lst = file.readline().strip().split(",")
                # stops if reached the end of file
                if len(game_lst) < 2:
                    break
                # if int(len(self.r.smembers('unique_games'))) > max_game_id:
                #    break
                game_data = {headers[i]: game_lst[i] for i in range(1, len(headers))}

                # adds game information to hash, named by bgg id
                self.r.hset('game:' + game_lst[0], mapping=game_data)

                # adds game availability
                # this code can easily be changed to support multiple copies of the same game
                self.r.hset('availability', mapping={game_lst[0]: 1})
                self.r.sadd('unique_games', game_lst[0])

    def get_game_availability(self, bgg_id):
        return int(self.r.hget('availability', str(bgg_id)))

    def rent_book(self, user, bgg_id):
        """rents book by creating hash"""
        avail = self.get_game_availability(bgg_id)
        if avail >= 1:
            today = date.today().strftime('%Y-%m-%d')
            week = today + datetime.timedelta(days=7)
            # add to user rentals
            self.hset('rentals:' + str(user), mapping={bgg_id: week})
            # self.r.hset(f'{user}:{bgg_id}', mapping={'rentDate': today, 'returnDate': week})

            # decrement the availability of the book
            self.r.hincrby('availability', str(bgg_id), -1)
            # assume each game is $20 to rent?
            self.money += 20
        else:
            self.rpush('waitlist:' + str(bgg_id), user)

    def calc_late_fee(self, user, bgg_id):
        expected_return = self.r.hget('rental:' + str(user), bgg_id)
        today = date.today().strftime('%Y-%m-%d')
        diff = (expected_return - today).days
        if diff < 0:
            self.money -= diff * 5

    def rent_after_return(self, user, bgg_id):
        self.r.lpop('waitlist:' + str(bgg_id))
        today = date.today().strftime('%Y-%m-%d')
        week = today + datetime.timedelta(days=7)
        # add to user rentals
        self.hset('rentals:' + str(user), mapping={bgg_id: week})
        # assume each game is $20 to rent?
        self.money += 20

    def return_book(self, user, bgg_id):
        self.calc_late_fee(user, bgg_id)
        next_renter = self.r.lindex('waitlist:' + str(bgg_id), 0)
        if next_renter:
            self.rent_after_return(next_renter, bgg_id)
        else:
            self.r.hincrby('availability', str(bgg_id), 1)

    @lru_cache(maxsize=15000)
    def get_transform_users_ratings(self, user):
        user_ratings = self.r.hgetall(str(user) + ':rated')
        return ({game for game in user_ratings.keys()},
                {game: (float(score), float(score) - 4, float(score) + 4) for game, score in user_ratings.items()})

    def get_all_users(self):
        return self.r.smembers('unique_ids')

    def get_all_usernames(self):
        return self.r.smembers('unique_usernames')

    def get_all_games(self):
        return self.r.smembers('unique_games')

    def get_game_data(self, bgg_id):
        return self.r.hgetall('game:' + str(bgg_id))

    def get_user_ratings(self, user_id):
        return self.r.hgetall(str(user_id) + ':rated')

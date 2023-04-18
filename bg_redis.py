"""
API for Redis
"""
import redis
from datetime import date, datetime
import datetime
from functools import lru_cache
import random
from collections import Counter

HEADERS = ['BGGId', 'Name', 'GameWeight', 'MinPlayers', 'MaxPlayers', 'ComAgeRec', 'MfgPlaytime', 'ComMinPlaytime',
           'ComMaxPlaytime', 'MfgAgeRec', 'NumUserRatings', 'Cat:Thematic', 'Cat:Strategy', 'Cat:War', 'Cat:Family',
           'Cat:CGS', 'Cat:Abstract', 'Cat:Party', 'Cat:Childrens']


class BoardGameAPI:

    def __init__(self, host='localhost', port=6379, db=0, decode_responses=True):
        self.next_user_id = None
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)
        self.money = 0
        #self.r.flushall()

    def add_users(self, filename, max_users):
        """
        adds users to redis database
        :param filename: string
            csv file name
        :param max_users: int
            max # users to be added to database
        :return: None
        """
        self.next_user_id = max_users
        with open(filename, "r") as infile:
            infile.readline()
            for i in range(max_users):
                line = infile.readline().strip()
                if len(line) == 0:
                    break
                # make set of unique user ids
                self.r.sadd('unique_ids', i)
                self.r.sadd('unique_usernames', line)

                # make mapping of username to user id
                self.r.hset('user_id_mapping', mapping={line: i})
        self.r.sadd('unique_ids', i + 1)
        self.r.sadd('unique_usernames', 'validation')

        # make mapping of username to user id
        self.r.hset('user_id_mapping', mapping={'validation': i+1})
        print(i+1)


    @lru_cache(10000)
    def get_user_id(self, username):
        """
        gets user id based on username
        :param username: string
            username string
        :return: int of corresponding user id
        """
        return self.r.hget('user_id_mapping', username)

    def add_ratings(self, file_name):
        """
        Creates hash for each user and their ratings
        :param file_name: string
            csv file name
        :return: None
        """
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

                # adds game rating to user's hash of ratings (bgg_id: rating)
                self.r.hset(str(user_id) + ':rated', mapping={rating[0]: rating[1]})

    def add_games(self, file_name, max_game_num):
        """
        creates hashes containing game info
        :param file_name: string
            csv file string
        :param max_game_num: int
            max number of games to be added into database
        :return:
        """
        conditions = ['new', 'gently used', 'used', 'heavily used', 'poor']
        price_mapping = {'new': 16, 'gently used': 13, 'used': 10, 'heavily used': 7, 'poor': 3}
        self.r.hset('price_mapping', mapping=price_mapping)
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
                game_data = {headers[i]: game_lst[i] for i in range(1, len(headers))}

                # adds game information to hash, named by bgg id
                self.r.hset('game:' + game_lst[0], mapping=game_data)

                # adds game availability
                copies = random.randint(1, 10)
                [self.r.lpush(str(game_lst[0]) + 'ids:', i) for i in range(copies)]
                self.r.hset('availability', mapping={game_lst[0]: copies})
                self.r.sadd('unique_games', game_lst[0])
                game_conditions = [random.choice(conditions[:3]) for num in range(copies)]
                self.r.hset(str(game_lst[0]) + ':conditions:', mapping={i: game_conditions[i] for i in
                                                                         range(len(game_conditions))})

    def add_new_game(self, bgg_id, game_price, game_data=None):
        """
        adds new game to database
        :param bgg_id: int or string
            the id of the game to add
        :param game_price: float
            how much the game costs to purchase
        :param game_data: dict
            contains the relevant game data such as game weight, playtime, themes, etc.
        :return: None
        """
        # if the game is a new copy of an existing game, increment availability and add new copy data
        if bgg_id in self.r.smembers('unique_games'):
            next_id = max(self.r.lrange(str(bgg_id) + 'ids:', 0, -1)) + 1
            self.r.hincrby('availability', str(bgg_id), 1)
        # if the game is a totally new game, add game data to db
        else:
            next_id = 0
            self.r.hset('availability', mapping={bgg_id: 1})
            self.r.hset('game:' + str(bgg_id), mapping=game_data)
            self.r.sadd('unique_games', bgg_id)
        self.r.lpush(str(bgg_id) + 'ids:', next_id)
        self.r.hset(str(bgg_id) + ':conditions:', mapping={next_id: 'new'})
        self.money -= game_price

    def add_new_user(self, username):
        """
        adds a new user to the database
        :param username: string
            username of new user
        :return: None
        """
        self.r.sadd('unique_ids', self.next_user_id)
        self.r.sadd('unique_usernames', username)

        # make mapping of username to user id
        self.r.hset('user_id_mapping', mapping={username: self.next_user_id})
        self.next_user_id += 1

    def get_game_availability(self, bgg_id):
        """
        getting availability of game
        :param bgg_id: int
            game id
        :return: integer of how many games are available
        """
        return int(self.r.hget('availability', str(bgg_id)))

    def get_next_avail_game(self, bgg_id):
        """
        getting next available game
        :param bgg_id: int or string
            the id of the game to get the next available sub id for
        :return: int
            the next available game sub id
        """
        avail_games = self.r.lrange(str(bgg_id) + 'ids:', 0, -1)
        if avail_games:
            return avail_games[0]

    def get_game_condition(self, bgg_id, game_id):
        """
        getting condition of a game
        :param bgg_id: int
            id of game
        :param game_id: int
            id of copy of specific game
        :return: string
            the condition of the input bgg and game id
        """
        return self.r.hget(str(bgg_id) + ':conditions:', game_id)

    def get_game_price(self, bgg_id, game_id):
        """
        getting price of game based on condition
        :param bgg_id: int
            id of game
        :param game_id: int
            id of copy of specific game
        :return: float of game price
        """
        cond = self.get_game_condition(bgg_id, game_id)
        return float(self.r.hget('price_mapping', cond))

    def rent_game(self, user, bgg_id, after_return=False, old_renter=None, game_id=None):
        """
        rents game by creating hash
        :param user: int or string
            user id to rent to
        :param bgg_id: int or string
            id of the game to be rented
        :param after_return: binary flag
            whether this instance of renting is automatic after the game is being returned or if its a
            user requesting to rent the game
        :param old_renter: int or string
            the user id of the previous renter, only input if after_return
        :param game_id: int or string
            the sub id of the game to be rented, only input if after_return
        :return: None
        """
        if after_return:
            self.rent_after_return(user, bgg_id, old_renter, game_id)

        else:
            sub_id = self.get_next_avail_game(bgg_id)
            if sub_id:
                today = date.today()
                week = today + datetime.timedelta(days=7)
                # add to user rentals
                self.r.hset('rentals:' + str(user), mapping={bgg_id: sub_id})
                self.r.hset('return_dates:' + str(user), mapping={bgg_id: week.strftime('%Y-%m-%d')})

                # decrement the availability of the game
                self.r.hincrby('availability', str(bgg_id), -1)
                self.r.lpop(str(bgg_id) + 'ids:')
                # add rental fee based on game condition
                self.money += self.get_game_price(bgg_id, sub_id)
            else:
                self.r.rpush('waitlist:' + str(bgg_id), user)

    def apply_late_fee(self, user, bgg_id):
        """
        applies a late fee to the specific user's account for late games
        :param user: int
            user id
        :param bgg_id: int
            id of game
        :return: None
        """
        # determine if the user retured the game late. If so, late fee is 5 dollars per day past expected return date
        expected_return = self.r.hget('return_dates:' + str(user), bgg_id)
        today = date.today().strftime('%Y-%m-%d')
        diff = (datetime.datetime.strptime(expected_return, '%Y-%m-%d').date() -
                datetime.datetime.strptime(today, '%Y-%m-%d').date())
        diff = diff.days
        if diff < 0:
            self.money -= diff * 5

    def rent_after_return(self, user, bgg_id, sub_id):
        """
        rents game out after game has been returned
        :param user: int or string
            the user id for the next renter
        :param bgg_id: int or string
            id for the game being rented
        :param sub_id: int or string
            id for the copy of the game being rented
        :return: None
        """
        # remove the renter from the waitlist
        self.r.lpop('waitlist:' + str(bgg_id))
        today = date.today()
        week = today + datetime.timedelta(days=7)
        # add game to user rentals and add expected return date
        self.r.hset('rentals:' + str(user), mapping={bgg_id: sub_id})
        self.r.hset('return_dates:' + str(user), mapping={bgg_id: week.strftime('%Y-%m-%d')})
        # add money for rental fee
        self.money += self.get_game_price(bgg_id, sub_id)

    def check_condition(self, bgg_id, sub_id):
        """
        checking condition and removing game if condition is poor or worse
        :param bgg_id: int or string
            game id
        :param sub_id: int or string
            game copy id
        :return: Boolean
            whether the game can return to rental circulation
        """
        # get condition, see if poor or worse, if so, remove from circulation, else check next renter
        cond = input('Please input the updated game condition: ')
        if cond == 'poor':
            return False
        else:
            self.r.hset(str(bgg_id) + ':conditions:', mapping={sub_id: cond})
            return True

    def return_game(self, user, bgg_id):
        """
        returns game
        :param user: int or string
            the user id returning the game
        :param bgg_id: int or string
            id of game being returned
        :return:
        """
        # calculate and apply any late fees
        self.apply_late_fee(user, bgg_id)
        # update user rentals to show that the game has been returned
        self.r.hset('return_dates:' + str(user), mapping={bgg_id: 'returned'})
        sub_id = self.r.hget('rentals:' + str(user), bgg_id)
        # check if game condition allows the game to return to rental circulation
        if self.check_condition(bgg_id, sub_id):
            # if there's a waitlist for the game, automatically rent it back out
            next_renter = self.r.lindex('waitlist:' + str(bgg_id), 0)
            if next_renter:
                self.rent_game(next_renter, bgg_id, after_return=True, game_id=sub_id)
            # if there's not a waitlist, put the game back in inventory
            else:
                self.r.hincrby('availability', str(bgg_id), 1)
                self.r.rpush(str(bgg_id) + 'ids:', sub_id)

    @lru_cache(maxsize=15000)
    def get_transform_users_ratings(self, user):
        """
        stores games rated by a single user and their ratings
        :param user: int
            user id integer
        :return: tuple consisting of a set of games rated by the user and a dict of the corresponding ratings
        """
        user_ratings = self.r.hgetall(str(user) + ':rated')
        return ({game for game in user_ratings.keys()},
                {game: (float(score), float(score) - 4, float(score) + 4) for game, score in user_ratings.items()})

    def get_all_users(self):
        """
        getting all user ids from the redis database
        :return: dict of all user ids
        """
        return self.r.smembers('unique_ids')

    def get_all_usernames(self):
        """
        getting all usernames from the redis database
        :return: dict of all usernames
        """
        return self.r.smembers('unique_usernames')

    def get_all_games(self):
        """
        getting all game ids from the redis database
        :return: dict of all game ids
        """
        return self.r.smembers('unique_games')

    def get_game_data(self, bgg_id):
        """
        getting all data for an inputted game id
        :param bgg_id: int
            game id integer
        :return: dictionary of game data
        """
        return self.r.hgetall('game:' + str(bgg_id))

    def get_user_ratings(self, user_id):
        """
        getting all user ratings
        :param user_id: int
            user id integer
        :return: dictionary of all games the user rated and the ratings
        """
        return self.r.hgetall(str(user_id) + ':rated')




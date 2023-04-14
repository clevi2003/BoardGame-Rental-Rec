from neo4j import GraphDatabase
import random


with open('password.txt') as infile:
    PASS = infile.readline().strip()


class neo4jAPI:
    def __init__(self, user='neo4j', password=PASS, port="bolt://localhost:7687"):
        self.driver = GraphDatabase.driver(port, auth=(user, password))

    def run_cmd(self, cmd):
        with self.driver.session() as session:
            res = session.run(cmd)
            return res.data()

    def add_edge(self, filename, source_id, target_id, source_label, target_label, rel_label, rel_prop, header):
        """
        adds relationships to graph
        :param filename: string
            the name of the file path containing the edge data to be added to neo4j
        :param source_id: string
            the id of the source node to be added as a property
        :param target_id: string
            the id of the target node to be added as a property
        :param source_label: string
            the name of the source node to be added as a property
        :param target_label: string
            the name of the target node to be added as a property
        :param rel_label: string
            the name of the relationship type
        :param rel_prop: string
            the name of the relationship property
        :param header: list
            list of file header columns

        :return: None
        """
        cmd = """ 
        LOAD CSV WITH HEADERS FROM "file:///""" + filename + """" AS row
        MATCH (source: """ + source_label + "{" + source_id + """: row.""" + header[0] + """})
        MATCH (target: """ + target_label + "{" + target_id + """: row.""" + header[1] + """})
        CREATE (source)-[:""" + rel_label + "{" + rel_prop + ": toInteger(row.""" + header[2] + ")}]->(target);"
        self.run_cmd(cmd)

    def add_node(self, filename, node_label, properties):
        """adds nodes to graph
        filename: str, path of file containing node information"""
        props = []
        for p in properties:
            props.append(str(p + ":row." + p))
        prop_str = ", ".join(props)
        cmd = """
        LOAD CSV WITH HEADERS FROM "file:///""" + filename + """" AS row
        CREATE (:""" + node_label + " {" + prop_str + "});"
        self.run_cmd(cmd)

    def get_collab_recs(self, user_id, game_db, n, min_rating):
        """gets n recommendations based on reference songs"""
        user_games = [game for game, rating in game_db.get_user_ratings(user_id).items()]
        sim_users = []
        cmd = """
        MATCH (s:User)-[r:SIM_USER]-(u:User)
        WHERE s.ID = """ + str(user_id) + """
        RETURN u.ID
        ORDER BY r.score DESC
        LIMIT 10"""
        sim_users.extend(self.run_cmd(cmd))
        sim_users = [elem['u.ID'] for elem in sim_users]
        sim_games = []
        for sim_user in sim_users:
            cmd = """
            MATCH (s:User {ID: """ + str(sim_user) + """})-[r:RATED]-(b:Game)
            WHERE r.score > toFloat(""" + str(min_rating) + """)
            RETURN b.BGGId"""
            self.run_cmd(cmd)
            sim_games.extend(self.run_cmd(cmd))
        game_names = list(set([game_db.get_game_data(game['b.BGGId'])['Name'] for game in sim_games if game['b.BGGId'] not in user_games]))
        if len(game_names) >= n:
            return random.sample(list(set(game_names)), n)
        else:
            return game_names

    def get_content_recs(self, game_db, user_id, n, min_rating, min_percentile, max_percentile):
        """gets nth percentile recommendations based on user's top-rated games"""
        user_games = [game for game, rating in game_db.get_user_ratings(user_id).items() if float(rating) > min_rating]
        sim_games = []
        for game_id in user_games:
            cmd = """
            MATCH (s:Game {BGGId:""" + game_id + """})-[r:SIM_GAME]-(t:Game)
            WITH percentileCont(r.score, toFloat(""" + str(min_percentile) + ")) as min_cutoff, percentileCont(r.score, toFloat(" + str(max_percentile) + """)) as max_cutoff
            MATCH (s:Game {BGGId:""" + game_id + """})-[r:SIM_GAME]-(t:Game)
            WHERE r.score >= min_cutoff AND r.score < max_cutoff
            RETURN t.BGGId"""
            sim_games.extend(self.run_cmd(cmd))
        game_names = list(set([game_db.get_game_data(game['t.BGGId'])['Name'] for game in sim_games if game['t.BGGId'] not in user_games]))
        if len(game_names) >= n:
            return random.sample(game_names, n)
        else:
            return game_names


    def get_all_recs(self, game_db, user_id, n_collab=3, n_content=3, min_rating=6, min_percentile=.85, max_percentile=.95):
        """gets final recommended subset from collaborative and content based recommendations"""
        content_recs = self.get_content_recs(game_db=game_db, user_id=user_id, n=n_content, min_rating=min_rating, min_percentile=min_percentile, max_percentile=max_percentile)
        collab_recs = self.get_collab_recs(user_id=user_id, game_db=game_db, n=n_collab, min_rating=min_rating)
        print("Content Recs: ", content_recs)
        print("Collaborative Recs: ", collab_recs)
        all_recs = content_recs + collab_recs
        with open("most_popular_games.csv") as infile:
            infile.readline()
            pop_ids = [id.strip() for id in infile.readlines()]
        pop_recs = list(set([game_db.get_game_data(id)['Name'] for id in pop_ids if game_db.get_game_data(id)['Name'] not in all_recs]))
        #print(pop_recs)
        diff_num = len(pop_recs) - len(all_recs)
        return all_recs + random.sample(pop_recs, diff_num)

    def change_id_toint(self, node_label, node_id):
        toint_cmd = """
                MATCH (s:""" + node_label + ") SET s." + node_id + " = toInteger(s." + node_id + ")"
        self.run_cmd(toint_cmd)

    def change_prop_toint(self, source_label, targ_label, rel_label, rel_prop):
        toint_cmd = """
            MATCH (:""" + source_label + ")-[r:""" + rel_label + "]->(:""" + targ_label + """)
            SET r.""" + rel_prop + " = toInteger(r.""" + rel_prop + ")"
        self.run_cmd(toint_cmd)




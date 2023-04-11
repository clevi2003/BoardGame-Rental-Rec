from neo4j import GraphDatabase
import random
# from bg_redis import BoardGameAPI


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
        WHERE s.user_id = '""" + user_id + """'
        RETURN u.user_id
        ORDER BY r.score DESC
        LIMIT 10"""
        sim_users.extend(self.run_cmd(cmd))
        sim_games = []
        for sim_user in sim_users:
            cmd = """
            MATCH (s:User {user_id: '""" + sim_user + """'})-[r:RATED]-(b:GAME)
            WHERE all(a in r where a.score > """ + min_rating + """
            RETURN b.BGGId"""
            self.run_cmd(cmd)
            sim_games.extend(self.run_cmd(cmd))
        BGGIds = [game['b.BGGId'] for game in sim_games if game['b.BGGId'] not in user_games]
        print("collab recs: ", BGGIds)
        return random.sample(list(set(BGGIds)), n)

    def get_content_recs(self, game_db, user_id, n, min_rating, min_percentile, max_percentile):
        """gets nth percentile recommendations based on user's top-rated games"""
        user_games = [game for game, rating in game_db.get_user_ratings(user_id).items() if rating > min_rating]
        sim_games = []
        for game_id in user_games:
            cmd = """
            MATCH (s:Game {BGGId: '""" + game_id + """'})-[r:SIM_GAME]->(t:Game)
            WITH percentileCont(collect(r.score), '""" + min_percentile + "') as min_cutoff, percentileCont(collect(r.score), '" + max_percentile + """') as max_cutoff
            MATCH (s:Game {BGGId: '""" + game_id + """'})-[r:SIM_GAME]->(t:Game)
            WHERE r.score >= min_cutoff AND r.weight < max_cutoff
            RETURN t:Game"""
            sim_games.extend(self.run_cmd(cmd))
        game_names = [game_db.get_game_data[game['b.BGGId']]['Name'] for game in sim_games if game['b.BGGId'] not in user_games]
        print("content recs:", game_names)
        return random.sample(list(set(game_names)), n)

    def get_all_recs(self, game_db, user_id, n_collab=2, n_content=2, min_rating=6, min_percentile=.85, max_percentile=.95):
        """gets final recommended subset from collaborative and content based recommendations"""
        content_recs = self.get_content_recs(game_db=game_db, user_id=user_id, n=n_content, min_rating=min_rating, min_percentile=min_percentile, max_percentile=max_percentile)
        collab_recs = self.get_collab_recs(user_id=user_id, game_db=game_db, n=n_collab, min_rating=min_rating)
        return content_recs + collab_recs

    def change_id_toint(self, node_label, node_id):
        toint_cmd = """
                MATCH (s:""" + node_label + ") SET s." + node_id + " = toInteger(s." + node_id + ")"
        self.run_cmd(toint_cmd)

    def change_prop_toint(self, source_label, targ_label, rel_label, rel_prop):
        toint_cmd = """
            MATCH (:""" + source_label + ")-[r:""" + rel_label + "]->(:""" + targ_label + """)
            SET r.""" + rel_prop + " = toInteger(r.""" + rel_prop + ")"
        self.run_cmd(toint_cmd)




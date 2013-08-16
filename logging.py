import sqlite3 as sql
import data
from subprocess import Popen


class Sqlobj(object):
    def __init__(self, dbtype):
        
        # initialize
        self.index_counter = 0
        self.dbtype = dbtype

        if self.dbtype == data.ENTITY_DB:
            script="""
            CREATE TABLE IF NOT EXISTS entity_stats (
                game_id INT,
                entity_id INT,
                name TEXT,
                tick INT,
                hp INT,
                hp_max INT,
                power INT,
                power_base INT,
                defense INT,
                defense_base INT,
                xp INT,
                xp_level INT,
                speed_counter INT,
                regen_counter INT,
                alive_or_dead INT,
                dungeon_level INT,
                dungeon_levelname TEXT,
                x INT,
                y INT
            );
            CREATE INDEX IF NOT EXISTS game_idx ON entity_stats(game_id);
            CREATE INDEX IF NOT EXISTS entity_idx ON entity_stats(entity_id);
            """
        elif self.dbtype == data.MESSAGE_DB:
            script="""
            CREATE TABLE IF NOT EXISTS game_log (
                game_id INT,
                msg_id INT,
                name TEXT,
                tick INT
            );
            CREATE INDEX IF NOT EXISTS game_idx ON game_log(game_id);
            CREATE INDEX IF NOT EXISTS msg_idx ON game_log(msg_id);
            """
        
        self.DB_FILE = self.dbtype  + '.db'
        self.conn = sql.connect(self.DB_FILE)
        self.cursor = self.conn.cursor()
        self.cursor.executescript(script)
        self.game_id = self.cursor.execute("SELECT IFNULL(MAX(game_id), 0) + 1 FROM " + self.dbtype).fetchone()[0]

    def log_entity(self, Game, thing):

        if self.dbtype == data.ENTITY_DB:
            entity = thing
            if not hasattr(thing, 'entity_id'):
                self.index_counter += 1
                entity.entity_id = self.index_counter
            
        if self.dbtype == data.MESSAGE_DB:
            message = thing
            entity = thing
            if not hasattr(thing, 'msg_id'):
                self.index_counter += 1
                msg_id = self.index_counter

        if self.dbtype == data.ENTITY_DB:            
            the_data = {
                "game_id": self.game_id,
                "entity_id": entity.entity_id,
                "name": entity.name,
                "tick": Game.tick,
                "hp": entity.fighter.hp,
                "hp_max": entity.fighter.max_hp(Game),
                "power": entity.fighter.power(Game),
                "power_base": entity.fighter.base_power,
                "defense": entity.fighter.defense(Game),
                "defense_base": entity.fighter.base_defense,
                "xp": entity.fighter.xp,
                "xp_level": entity.fighter.xplevel,
                "speed_counter": entity.fighter.speed_counter,
                "regen_counter": entity.fighter.regen_counter,
                "alive_or_dead": int(entity.fighter.alive),
                "dungeon_level": entity.dungeon_level,
                "dungeon_levelname": data.maplist[entity.dungeon_level],
                "x": entity.x,
                "y": entity.y
            }

        elif self.dbtype == data.MESSAGE_DB:            
            the_data = {
                "game_id": self.game_id,
                "msg_id": msg_id,
                "name": message,
                "tick": Game.tick
            }

        dict_insert(self.cursor, self.dbtype, the_data)

    def log_event(self):
        pass

    def log_flush(self):
        self.conn.commit()

    def export_csv(self):
        p = Popen("export_sql2csv.bat " + self.dbtype + ' ' + self.DB_FILE )
        p.communicate()

# this is silly, should be builtin
def dict_insert(cursor, table, data):
    query = "INSERT INTO " + table + "(" + ", ".join(data.keys()) + ") VALUES (:" + ", :".join(data.keys()) + ")"
    try:
        return cursor.execute(query, data)
    except:
        print "Query failure! Query was:", query
        return None




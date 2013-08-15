import sqlite3 as sql
import data

DB_FILE = "stats.db"

# initialize
conn = sql.connect(DB_FILE)
cursor = conn.cursor()
entity_counter = 0
cursor.executescript("""
CREATE TABLE IF NOT EXISTS entity_stats (
    game_id INT,
    entity_id INT,
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
""")
game_id = cursor.execute("SELECT IFNULL(MAX(game_id), 0) + 1 FROM entity_stats").fetchone()[0]


# this is silly, should be builtin
def dict_insert(cursor, table, data):
    query = "INSERT INTO " + table + "(" + ", ".join(data.keys()) + ") VALUES (:" + ", :".join(data.keys()) + ")"
    try:
        return cursor.execute(query, data)
    except:
        print "Query failure! Query was:", query
        return None


def log_entity(game, entity):
    global entity_counter, game_id

    if not hasattr(entity, 'entity_id'):
        entity_counter += 1
        entity.entity_id = entity_counter

    entity_data = {
        "game_id": game_id,
        "entity_id": entity.entity_id,
        "tick": game.tick,
        "hp": entity.fighter.hp,
        "hp_max": entity.fighter.max_hp(game),
        "power": entity.fighter.power(game),
        "power_base": entity.fighter.base_power,
        "defense": entity.fighter.defense(game),
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
    dict_insert(cursor, 'entity_stats', entity_data)


def log_event():
    pass


def log_flush():
    conn.commit()

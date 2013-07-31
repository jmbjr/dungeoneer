#standard imports
import libtcodpy as libtcod
from gamestuff import *
import data

#specific imports needed for this module
import entities
import entitydata

#functions to create matp shapes and rooms
def create_h_tunnel(x1, x2, y, Game):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        Game.map[x][y].blocked = False
        Game.map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x, Game):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        Game.map[x][y].blocked = False
        Game.map[x][y].block_sight = False

def create_room(room, Game):
    #go through tiles in rect to make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
                Game.map[x][y].blocked = False
                Game.map[x][y].block_sight = False



#map helper functions. create the fov map, go to next level, and lookup dungeon level percentages for objects
def initialize_fov(Game):
    Game.fov_recompute = True
    #create FOV map according to the generated map
    Game.fov_map = libtcod.map_new(data.MAP_WIDTH, data.MAP_HEIGHT)
    for y in range(data.MAP_HEIGHT):
        for x in range(data.MAP_WIDTH):
            libtcod.map_set_properties(Game.fov_map, x, y, not Game.map[x][y].block_sight, not Game.map[x][y].blocked)

    libtcod.console_clear(Game.con)

def next_level(Game):
    #advance to next level
    message('You head down the stairs', Game, libtcod.red)
    Game.dungeon_level +=1
    make_map(Game) #create fresh new level
    initialize_fov(Game)

def from_dungeon_level(table, Game):
        #returns a value that depends on level. table specifies what value occurs after each level. default = 0
        for (value, level) in reversed(table):
            if Game.dungeon_level >= level:
                return value
        return 0



#Primary map generator and object placement routines.
def make_map(Game):
    Game.objects = [Game.player]
    #fill map with "blocked" tiles
    Game.map = [[ Tile(True)
        for y in range(data.MAP_HEIGHT) ]
            for x in range(data.MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    for r in range(data.MAX_ROOMS):
        #get random width/height
        w = libtcod.random_get_int(0, data.ROOM_MIN_SIZE, data.ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, data.ROOM_MIN_SIZE, data.ROOM_MAX_SIZE)
        #get random positions, but stay within map
        x = libtcod.random_get_int(0, data.MAP_PAD_W, data.MAP_WIDTH - w - data.MAP_PAD_W)
        y = libtcod.random_get_int(0, data.MAP_PAD_H, data.MAP_HEIGHT - h - data.MAP_PAD_H)

        new_room = Rect(x, y, w, h)

        #check for intersection with this room
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #no intersections

            create_room(new_room, Game)
            (new_x, new_y) = new_room.center()

            #add some contents to the room
            place_objects(new_room, Game)

            if num_rooms == 0:
                #first room. start player here
                Game.player.x = new_x
                Game.player.y = new_y

            else:
                #for all other rooms, need to connect to previous room with a tunnel

                #get center coords of previous room
                (prev_x, prev_y) = rooms[num_rooms -1].center()

                #flip coin
                if flip_coin() == 1:
                    #move h then v
                    create_h_tunnel(prev_x, new_x, prev_y, Game)
                    create_v_tunnel(prev_y, new_y, new_x, Game)
                else:
                    #move v then h
                    create_v_tunnel(prev_y, new_y, prev_x, Game)
                    create_h_tunnel(prev_x, new_x, new_y, Game)
            
            #add to rooms list
            rooms.append(new_room)
            num_rooms +=1

    #create stairs at the center of the last room
    Game.stairs = entities.Object(new_x, new_y, '>', 'stairs', libtcod.white, always_visible = True)
    Game.objects.append(Game.stairs)
    Game.stairs.send_to_back(Game) #so it's drawn below the monsters

def place_objects(room, Game):
    #choose random number of monsters
    #max number monsters per room

    max_monsters = from_dungeon_level([[3, 1], [4, 3], [5, 6], [7, 10]], Game)
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
    monster_chances = get_monster_chances(Game)

    max_items = from_dungeon_level([[1, 1], [2, 4]], Game)
    num_items = libtcod.random_get_int(0, 0, max_items)
    item_chances = get_item_chances(Game)

    for i in range(num_monsters):
        #choose random spot for this monster
        x =  libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y =  libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        if not entities.is_blocked(x, y, Game):
            #create a monster
            choice = random_choice(monster_chances)

            monster             = entities.Object(**entitydata.mobs[choice])
            monster.name        = choice  
            monster.blocks      = True        
            monster.ai          = entities.BasicMonster()  #how do I set different ai?
            monster.ai.owner    = monster

            #give monster items if they have them
            if entitydata.mobitems[choice]:
                for itemname in entitydata.mobitems[choice]:
                    item = entities.Object(**entitydata.items[itemname])
                    monster.fighter.add_item(item)

            monster.set_location(x, y, Game)
            #print 'Added a ' + choice
            Game.objects.append(monster)


    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        #only place it if the tile is not blocked
        if not entities.is_blocked(x, y,Game):
            #create an item
            choice = random_choice(item_chances)

            item = entities.Object(**entitydata.items[choice])
            item.always_visible = True

            item.set_location(x, y, Game)

            Game.objects.append(item)
            item.send_to_back(Game) #items appear below other objects

def get_monster_chances(Game):
    #chance of each monster
    monster_chances = {}

    for mobname in entitydata.mobchances:
        monster_chances[mobname] = from_dungeon_level(entitydata.mobchances[mobname], Game)

    return monster_chances

def get_item_chances(Game):
    #chance of each monster
    item_chances = {}

    for itemname in entitydata.itemchances:
        item_chances[itemname] = from_dungeon_level(entitydata.itemchances[itemname], Game)

    return item_chances
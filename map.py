#standard imports
import libtcodpy as libtcod
from gamestuff import *
import data

#specific imports needed for this module
import entities
import entitydata
import itertools

#functions to create matp shapes and rooms
def create_h_tunnel(x1, x2, y, Game):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        Game.map[Game.dungeon_levelname][x][y].blocked = False
        Game.map[Game.dungeon_levelname][x][y].block_sight = False

def create_v_tunnel(y1, y2, x, Game):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        Game.map[Game.dungeon_levelname][x][y].blocked = False
        Game.map[Game.dungeon_levelname][x][y].block_sight = False

def create_room(room, Game):
    #go through tiles in rect to make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
                Game.map[Game.dungeon_levelname][x][y].blocked = False
                Game.map[Game.dungeon_levelname][x][y].block_sight = False

#map helper functions. create the fov map, go to next level, and lookup dungeon level percentages for objects
def initialize_fov(Game):
    Game.fov_recompute = True
    #create FOV map according to the generated map
    Game.player.fighter.fov = libtcod.map_new(data.MAP_WIDTH, data.MAP_HEIGHT)
    for y in range(data.MAP_HEIGHT):
        for x in range(data.MAP_WIDTH):
            libtcod.map_set_properties(Game.player.fighter.fov, x, y, not Game.map[Game.dungeon_levelname][x][y].block_sight, not Game.map[Game.dungeon_levelname][x][y].blocked)

    libtcod.console_clear(Game.con)

def next_level(Game):
    #advance to next level
    message('You head down the stairs', Game, libtcod.red)
    Game.player.dungeon_level +=1
    Game.dungeon_levelname = data.maplist[Game.player.dungeon_level]

    if not Game.dungeon_levelname in Game.map:
        make_map(Game) #create fresh new level

    Game.player.x = Game.upstairs[Game.dungeon_levelname].x
    Game.player.y = Game.upstairs[Game.dungeon_levelname].y
    initialize_fov(Game)

def prev_level(Game):
    #advance to next level
    message('You head up the stairs', Game, libtcod.red)
    Game.player.dungeon_level -=1
    Game.dungeon_levelname = data.maplist[Game.player.dungeon_level]

    if Game.player.dungeon_level <= 0: #leave dungeon      
        message('You\'ve left the dungeon!', Game, libtcod.red)
        Game.player.dungeon_level =1 #workaround to prevent game from complaining. 
        return data.STATE_EXIT
    else:
        #make_map(Game) #create fresh new level
        #assume map already made. bad long-term assumption
        if not Game.dungeon_levelname in Game.map:
            make_map(Game) #create fresh new level

        Game.player.x = Game.downstairs[Game.dungeon_levelname].x
        Game.player.y = Game.downstairs[Game.dungeon_levelname].y
        initialize_fov(Game)

def from_dungeon_level(table, dungeon_level):
        #returns a value that depends on level. table specifies what value occurs after each level. default = 0
        for (value, level) in reversed(table):
            if dungeon_level >= level:
                return value
        return 0


def make_dungeon(Game):
    for index,level in enumerate(data.maplist):
        if index > 0: #skip intro level
            print 'MAPGEN--\t ' + str(Game.tick) + '\t' + Game.dungeon_levelname + '\t' + ' creating level ' + level
            Game.player.dungeon_level = index
            Game.dungeon_levelname = level
            make_map(Game)

    Game.player.dungeon_level = 1
    Game.dungeon_levelname = data.maplist[Game.player.dungeon_level]

    Game.player.x = Game.upstairs[Game.dungeon_levelname].x
    Game.player.y = Game.upstairs[Game.dungeon_levelname].y
    initialize_fov(Game)

#Primary map generator and object placement routines.
def make_map(Game):
    Game.objects[Game.dungeon_levelname] = [Game.player]
    #fill map with "blocked" tiles

    print 'MAPGEN--\t ' + str(Game.tick) + '\t' + Game.dungeon_levelname + '\t' + ' creating map:' + str(Game.dungeon_levelname)
    Game.map[Game.dungeon_levelname] = [[ Tile(True)
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
                #create upstairs at the center of the first room
                Game.upstairs[Game.dungeon_levelname] = entities.Object(new_x, new_y, '<', 'upstairs', libtcod.white, always_visible = True)
                Game.objects[Game.dungeon_levelname].append(Game.upstairs[Game.dungeon_levelname])
                Game.upstairs[Game.dungeon_levelname].send_to_back(Game) #so it's drawn below the monsters

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
    Game.downstairs[Game.dungeon_levelname] = entities.Object(new_x, new_y, '>', 'downstairs', libtcod.white, always_visible = True)
    Game.objects[Game.dungeon_levelname].append(Game.downstairs[Game.dungeon_levelname])
    Game.downstairs[Game.dungeon_levelname].send_to_back(Game) #so it's drawn below the monsters

    #create generic fov map to use for this floor
    Game.fov_map[Game.dungeon_levelname] = libtcod.map_new(data.MAP_WIDTH, data.MAP_HEIGHT)
    for yy in range(data.MAP_HEIGHT):
        for xx in range(data.MAP_WIDTH):
            libtcod.map_set_properties(Game.fov_map[Game.dungeon_levelname], xx, yy, not Game.map[Game.dungeon_levelname][xx][yy].block_sight, not Game.map[Game.dungeon_levelname][xx][yy].blocked)



def place_objects(room, Game):
    #choose random number of monsters
    #max number monsters per room
    nextid = 1
    max_monsters = from_dungeon_level([[10, 1], [40, 3], [50, 6], [70, 10]], data.maplist.index(Game.dungeon_levelname))
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
    monster_chances = get_monster_chances(Game)

    max_items = from_dungeon_level([[10, 1], [2, 4]], data.maplist.index(Game.dungeon_levelname))
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
            monster.dungeon_level = data.maplist.index(Game.dungeon_levelname) 
            monster.blocks      = True        
            monster.ai          = entities.BasicMonster()  #how do I set different ai?
            monster.ai.owner    = monster
            monster.id          = str(monster.dungeon_level) + '.' + str(nextid)
            monster.name        = choice + ' (' + str(monster.id) + ')'
            if data.FREE_FOR_ALL_MODE:
                monster.fighter.clan        = monster.name
            nextid+=1
            monster.fighter.set_fov(Game)


            print 'MAPGEN--\t ' + str(Game.tick) + '\t' + Game.dungeon_levelname + '\t' + ' made a ' + monster.name

            #give monster items if they have them
            if entitydata.mobitems[choice]:
                for itemname in entitydata.mobitems[choice]:
                    item = entities.Object(**entitydata.items[itemname])
                    monster.fighter.add_item(item)

            monster.set_location(x, y, Game)
            Game.objects[Game.dungeon_levelname].append(monster)


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
            item.dungeon_level = data.maplist.index(Game.dungeon_levelname)

            Game.objects[Game.dungeon_levelname].append(item)
            item.send_to_back(Game) #items appear below other objects

def get_monster_chances(Game):
    #chance of each monster
    monster_chances = {}

    for mobname in entitydata.mobchances:
        monster_chances[mobname] = from_dungeon_level(entitydata.mobchances[mobname], data.maplist.index(Game.dungeon_levelname))

    return monster_chances

def get_item_chances(Game):
    #chance of each monster
    item_chances = {}

    for itemname in entitydata.itemchances:
        item_chances[itemname] = from_dungeon_level(entitydata.itemchances[itemname], data.maplist.index(Game.dungeon_levelname))

    return item_chances
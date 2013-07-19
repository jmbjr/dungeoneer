#standard imports
import libtcodpy as libtcod
from gamestuff import *
from constants import *

#specific imports needed for this module
import entities

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
        x = libtcod.random_get_int(0, 0, data.MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, data.MAP_HEIGHT - h - 1)

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
    max_monsters = from_dungeon_level([[3, 1], [4, 3], [5, 6], [7, 10]], Game)
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
    #max number monsters per room

    #chance of each monster
    monster_chances = {}
    monster_chances['johnstein']    = 75 #johnstein always shows up, even if all other monsters have 0 chance
    monster_chances['greynaab']     = from_dungeon_level([[60, 1], [35, 3], [10, 5]], Game)
    monster_chances['jerbear']      = from_dungeon_level([[50, 1], [30, 3], [15, 5]], Game)
    monster_chances['zombiesheep']  = from_dungeon_level([[40, 1], [25, 3], [20, 5]], Game)
    monster_chances['odiv']         = from_dungeon_level([[25, 2], [30, 4], [40, 6]], Game)
    monster_chances['slitherrr']    = from_dungeon_level([[20, 2], [30, 4], [50, 6]], Game)
    monster_chances['neckro']       = from_dungeon_level([[15, 2], [30, 4], [60, 6]], Game)
    monster_chances['chan']         = from_dungeon_level([[25, 3], [30, 5], [40, 7]], Game)
    monster_chances['ashandarei']   = from_dungeon_level([[20, 3], [30, 5], [50, 7]], Game)
    monster_chances['zureal']       = from_dungeon_level([[15, 3], [30, 5], [60, 7]], Game)
    monster_chances['demiurge']     = from_dungeon_level([[25, 4], [30, 6], [40, 8]], Game)
    monster_chances['hargrimm']     = from_dungeon_level([[20, 4], [30, 6], [50, 8]], Game)
    monster_chances['frisco']       = from_dungeon_level([[15, 4], [30, 6], [60, 8]], Game)
    monster_chances['toomuchpete']  = from_dungeon_level([[25, 5], [30, 7], [40, 9]], Game)
    monster_chances['flatluigi']    = from_dungeon_level([[20, 5], [30, 7], [50, 9]], Game)
    monster_chances['spanktrunk']   = from_dungeon_level([[15, 5], [30, 7], [60, 9]], Game)
    monster_chances['stavros']      = from_dungeon_level([[100, 10]], Game)

    max_items = from_dungeon_level([[1, 1], [2, 4]], Game)
    num_items = libtcod.random_get_int(0, 0, max_items)
    
    #chance of each item (by default they have chance of 0 at level 1 which goes up)
    item_chances = {}
    item_chances['heal'] = 70 #healing potion always shows up even if all other items have 0 chance
    item_chances['lightning']   = from_dungeon_level([[10, 1], [25, 3], [50, 5]], Game)
    item_chances['fireball']    = from_dungeon_level([[10, 1], [25, 3], [50, 5]], Game)
    item_chances['confuse']     = from_dungeon_level([[10, 1], [25, 3], [50, 5]], Game)
    item_chances['sword']       = from_dungeon_level([[10, 1], [20, 3], [30, 5]], Game)
    item_chances['shield']      = from_dungeon_level([[10, 1], [20, 3], [30, 5]], Game)

    for i in range(num_monsters):
        #choose random spot for this monster
        x =  libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y =  libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        if not entities.is_blocked(x, y, Game):
            choice = random_choice(monster_chances)

            if choice == 'johnstein':
                fighter_component = entities.Fighter(hp=10, defense=0, power=2, xp=20, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'J', 'johnstein', libtcod.white, blocks=True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'greynaab':
                fighter_component = entities.Fighter(hp=20, defense=1, power=4, xp=40, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'g', 'greynaab', libtcod.light_blue, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'jerbear':
                fighter_component = entities.Fighter(hp=25, defense=1, power=5, xp=50, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'j', 'jerbear', libtcod.green, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'zombiesheep':
                fighter_component = entities.Fighter(hp=30, defense=2, power=6, xp=60, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'z', 'zombiesheep', libtcod.yellow, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'odiv':
                fighter_component = entities.Fighter(hp=25, defense=2, power=5, xp=60, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'o', 'odiv', libtcod.darker_orange, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'slitherrr':
                fighter_component = entities.Fighter(hp=30, defense=2, power=6, xp=70, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 's', 'slitherrr', libtcod.darker_green, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'neckro':
                fighter_component = entities.Fighter(hp=35, defense=3, power=7, xp=80, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'n', 'neckro', libtcod.lighter_blue, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'chan':
                fighter_component = entities.Fighter(hp=30, defense=3, power=6, xp=80, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'c', 'chan', libtcod.darker_red, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'ashandarei':
                fighter_component = entities.Fighter(hp=35, defense=3, power=7, xp=90, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'a', 'ashandarei', libtcod.darker_yellow, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'zureal':
                fighter_component = entities.Fighter(hp=40, defense=4, power=8, xp=100, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'z', 'zureal', libtcod.dark_green, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'demiurge':
                fighter_component = entities.Fighter(hp=35, defense=4, power=7, xp=100, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'd', 'demiurge', libtcod.darker_violet, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'hargrimm':
                fighter_component = entities.Fighter(hp=40, defense=4, power=8, xp=125, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'h', 'hargrimm', libtcod.lighter_green, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'frisco':
                fighter_component = entities.Fighter(hp=45, defense=5, power=9, xp=150, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'f', 'frisco', libtcod.lighter_red, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'toomuchpete':
                fighter_component = entities.Fighter(hp=40, defense=5, power=8, xp=150, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 't', 'toomuchpete', libtcod.light_blue, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'flatluigi':
                fighter_component = entities.Fighter(hp=50, defense=5, power=9, xp=200, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'f', 'flatluigi', libtcod.light_orange, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'spanktrunk':
                fighter_component = entities.Fighter(hp=60, defense=6, power=10, xp=250, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 's', 'spanktrunk', libtcod.red, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'stavros':
                fighter_component = entities.Fighter(hp=99, defense=10, power=5, xp=500, death_function=entities.monster_death)
                ai_component = entities.BasicMonster()
                monster = entities.Object(x, y, 'S', 'Stavros the Wonder Chicken', libtcod.light_cyan, blocks= True, fighter=fighter_component, ai=ai_component)
            else:
                print 'ERROR!'
                break

            Game.objects.append(monster)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        #only place it if the tile is not blocked
        if not entities.is_blocked(x, y,Game):
            #create an item
            choice = random_choice(item_chances)
            if choice == 'heal':
                #healing potion
                item_component = entities.Item(use_function = entities.cast_heal)
                item = entities.Object(x, y, '!', 'healing potion', libtcod.red, always_visible = True, item = item_component)
                #print 'Healing Potion'
            elif choice == 'lightning':
                #lightning scroll
                item_component = entities.Item(use_function = entities.cast_lightning)
                item = entities.Object(x, y, '?', 'scroll of lightning bolt', libtcod.yellow, always_visible = True, item = item_component)
                #print 'Lightning Scroll'
            elif choice == 'fireball':
                #fireball scroll
                item_component = entities.Item(use_function=entities.cast_fireball)
                item = entities.Object(x, y, '?', 'scroll of fireball', libtcod.red, always_visible = True, item = item_component)
                #print 'Fireball Scroll'
            elif choice == 'confuse':
                #confusion scroll
                item_component = entities.Item(use_function = entities.cast_confusion)
                item = entities.Object(x, y, '?', 'scroll of confusion', libtcod.light_violet, always_visible = True, item = item_component)
                #print 'Confusion Scroll'
            elif choice == 'sword':
                #sword
                equipment_component = entities.Equipment(slot='right hand', power_bonus = 5)
                item = entities.Object(x, y, '/', 'sword', libtcod.sky, always_visible = True, equipment = equipment_component)
            elif choice == 'shield':
                #create a shield
                equipment_component = entities.Equipment(slot = 'left hand', defense_bonus = 3)
                item = entities.Object(x, y, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)
            else:
                print 'ERROR!'
                break

            Game.objects.append(item)
            item.send_to_back(Game) #items appear below other objects

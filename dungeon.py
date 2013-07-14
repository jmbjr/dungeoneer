import libtcodpy as libtcod
import math
import textwrap
import shelve

from objects import Rect, Tile
from constants import *
from ui import *
from gamestuff import *
from entities import *
from world import *
from abilities import *

#main module

class Game(object): 
    game_msgs = []


#MAIN MENU GAME OPTIONS
def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show game title and credits
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 4, libtcod.BKGND_NONE, libtcod.CENTER, 'MeFightRogues!')
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER, 'by johnstein!')

        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24, Game)

        if choice == 0: #new game
            new_game()
            play_game()

        if choice == 1: #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load. \n', Game, 24)
                continue
            play_game()
        elif choice == 2: #quit
            try:
                save_game()
            except:
                msgbox('Bye!', Game, 24)
            break

def new_game():
    #create object representing the player
    fighter_component = Fighter(hp=100, defense=3, power=6, xp=0, death_function=player_death)
    Game.player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', 'Roguetato', libtcod.white, blocks=True, fighter=fighter_component)

    Game.player.level = 1
    #generate map (at this point it's not drawn to screen)
    Game.dungeon_level = 1
    make_map(Game)

    initialize_fov(Game)

    Game.game_state = 'playing'
    Game.inventory = []

    #create the list of the game messages and their colors, starts empty
    Game.player.game_turns = 0

    #initial equipment
    equipment_component = Equipment(slot='wrist', max_hp_bonus = 5)
    obj = Object(0, 0, '-', 'wristguards of the whale', libtcod.gold, equipment=equipment_component)
    Game.inventory.append(obj)
    equipment_component.equip(Game)
    obj.always_visible = True

    #a warm welcoming message!
    message('Welcome to MeFightRogues! Good Luck! Don\'t suck!', Game, libtcod.blue)

def save_game(filename='savegame'):
    #open a new empty shelve (or overwrite old one) to write the game data
    print 'file saved!'
    file = shelve.open(filename, 'n')
    file['map'] = Game.map
    file['objects'] = Game.objects
    file['player_index'] = Game.objects.index(Game.player) #index of player in the objects list
    file['inventory'] = Game.inventory
    file['game_msgs'] = Game.game_msgs
    file['game_state'] = Game.game_state
    file['stairs_index'] = Game.objects.index(Game.stairs)
    file['dungeon_level'] = Game.dungeon_level
    file.close()

def load_game(filename='savegame'):
    file = shelve.open(filename, 'r')
    Game.map = file['map']
    Game.objects = file['objects'] 
    Game.player = Game.objects[file['player_index']]  #get index of player in the objects list
    Game.inventory = file['inventory']
    Game.game_msgs = file['game_msgs']
    Game.game_state = file['game_state']
    Game.stairs = Game.objects[file['stairs_index']]
    Game.dungeon_level = file['dungeon_level']
    file.close()

    initialize_fov(Game)

def play_game():
    player_action = None

    #mouse stuff
    Game.mouse = libtcod.Mouse()
    Game.key = libtcod.Key()    

    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, Game.key, Game.mouse)

        #render the screen
        render_all(Game)

        libtcod.console_flush()
        check_level_up(Game)

        #erase objects from old position, before they move
        for object in Game.objects:
            object.clear(Game)

        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            break

        #give monsters a turn
        if Game.game_state == 'playing' and player_action != 'no_action':
            for object in Game.objects:
                if object.ai:
                    object.ai.take_turn(Game)


#KEYPRESS CHECKS
def handle_keys():
    #for real-time, uncomment
    #key = libtcod.console_check_for_keypress()

    #for turn-based, uncomment
    #key = libtcod.console_wait_for_keypress(True)
    key_char = chr(Game.key.c)

    if Game.key.vk == libtcod.KEY_ENTER and Game.key.lalt:
        #ALT + ENTER: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif Game.key.vk == libtcod.KEY_ESCAPE:
        return 'exit' #exit game

    if Game.game_state == 'playing':
        #rest
        if Game.key.vk == libtcod.KEY_KPDEC or Game.key.vk == libtcod.KEY_KP5:
            player_resting(Game)
            pass
        #movement keys
        elif Game.key.vk == libtcod.KEY_UP or key_char == 'k' or Game.key.vk == libtcod.KEY_KP8 :
            player_move_or_attack(0, -1, Game)

        elif Game.key.vk == libtcod.KEY_DOWN or key_char == 'j' or Game.key.vk == libtcod.KEY_KP2 :
            player_move_or_attack(0, 1, Game)

        elif Game.key.vk == libtcod.KEY_LEFT or key_char == 'h' or Game.key.vk == libtcod.KEY_KP4 :
            player_move_or_attack(-1, 0, Game)

        elif Game.key.vk == libtcod.KEY_RIGHT or key_char == 'l' or Game.key.vk == libtcod.KEY_KP6 :
            player_move_or_attack(1, 0, Game)

        #handle diagonal. 11 oclock -> clockwise
        elif key_char == 'y' or Game.key.vk == libtcod.KEY_KP7 :
            player_move_or_attack(-1, -1, Game)

        elif key_char == 'u' or Game.key.vk == libtcod.KEY_KP9 :
            player_move_or_attack(1, -1, Game)

        elif key_char == 'n' or Game.key.vk == libtcod.KEY_KP3 :
            player_move_or_attack(1, 1, Game)

        elif key_char == 'b' or Game.key.vk == libtcod.KEY_KP1 :
            player_move_or_attack(-1, 1, Game)

        else:
            #test for other keys
            if key_char == 'g':
                #pick up an item
                for object in Game.objects: #look for items in the player's title
                    if object.x == Game.player.x and object.y == Game.player.y and object.item:
                        Game.player.game_turns +=1
                        return object.item.pick_up(Game)
                        #break

            if key_char == 'i':
                #show inv. if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it. \nPress ESC to return to game\n', Game)
                if chosen_item is not None:
                    Game.player.game_turns +=1
                    return chosen_item.use(Game)

            if key_char == 'd':
                #show the inventory. if item is selected, drop it
                chosen_item = inventory_menu('Press the key next to the item to drop. \nPress ESC to return to game\n', Game)
                if chosen_item is not None:
                    Game.player.game_turns +=1
                    chosen_item.drop(Game.inventory, Game)

            if key_char == 'c':
                #show character info
                level_up_xp = LEVEL_UP_BASE + Game.player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(Game.player.level) + '\nExperience: ' + str(Game.player.fighter.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(Game.player.fighter.max_hp(Game)) +
                    '\nAttack: ' + str(Game.player.fighter.power(Game)) + '\nDefense: ' + str(Game.player.fighter.defense(Game)), Game, CHARACTER_SCREEN_WIDTH)

            if key_char == 'x':
                #debug key to automatically level up
                msgbox('You start to meditate!', Game, CHARACTER_SCREEN_WIDTH)
                level_up_xp = LEVEL_UP_BASE + Game.player.level * LEVEL_UP_FACTOR
                Game.player.fighter.xp = level_up_xp
                check_level_up(Game)
                Game.player.game_turns +=1       

            if key_char == 'a':
                #debug key to set all objects to visible
                msgbox('You can smell them all!', Game, CHARACTER_SCREEN_WIDTH)
                set_objects_visible(Game)

            if key_char == 'q':
                #go down stairs, if the player is on them
                msgbox('You feel your inner dwarf admiring the dungeon walls!', Game, CHARACTER_SCREEN_WIDTH)
                set_map_explored(Game)   

            if key_char == 'z':
                #debug key to automatically go to next level
                msgbox('You start digging at your feet!', Game, CHARACTER_SCREEN_WIDTH)
                next_level(Game)           

            if key_char == '>':
                #go down stairs, if the player is on them
                if Game.stairs.x == Game.player.x and Game.stairs.y == Game.player.y:
                    Game.player.game_turns +=1
                    next_level(Game)

            if key_char == 'w':
                #give all items
                give_items(Game)

            return 'no_action'


#DEBUG FUNCTIONS
def give_items(Game):
    #healing potion
    x = 0
    y = 0
    item_component = Item(use_function = cast_heal)
    item = Object(x, y, '!', 'healing potion', libtcod.red, always_visible = True, item = item_component)
    item.always_visible = True
    Game.inventory.append(item)


    #lightning scroll
    item_component = Item(use_function = cast_lightning)
    item = Object(x, y, '?', 'scroll of lightning bolt', libtcod.yellow, always_visible = True, item = item_component)
    Game.inventory.append(item)

    #fireball scroll
    item_component = Item(use_function=cast_fireball)
    item = Object(x, y, '?', 'scroll of fireball', libtcod.red, always_visible = True, item = item_component)
    Game.inventory.append(item)

    #confusion scroll
    item_component = Item(use_function = cast_confusion)
    item = Object(x, y, '?', 'scroll of confusion', libtcod.light_violet, always_visible = True, item = item_component)
    Game.inventory.append(item)

    #sword
    equipment_component = Equipment(slot='right hand', power_bonus = 5)
    item = Object(x, y, '/', 'sword', libtcod.sky, always_visible = True, equipment = equipment_component)
    Game.inventory.append(item)

    #create a shield
    equipment_component = Equipment(slot = 'left hand', defense_bonus = 3)
    item = Object(x, y, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)
    Game.inventory.append(item)

    #wristguards
    equipment_component = Equipment(slot='wrist', max_hp_bonus = 5)
    item = Object(0, 0, '-', 'wristguards of the whale', libtcod.gold, equipment=equipment_component)
    Game.inventory.append(item)

def set_map_explored(Game):
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            Game.map[x][y].explored = True
    Game.fov_recompute = True        

def set_objects_visible(Game):
    for object in Game.objects:
        object.always_visible = True


#MAP FUNCTIONS
def next_level(Game):
    #advance to next level
    message('You head down the stairs', Game, libtcod.red)
    Game.dungeon_level +=1
    make_map(Game) #create fresh new level
    initialize_fov(Game)

def create_room(room, Game):
    #go through tiles in rect to make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
                Game.map[x][y].blocked = False
                Game.map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y, Game):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        Game.map[x][y].blocked = False
        Game.map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x, Game):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        Game.map[x][y].blocked = False
        Game.map[x][y].block_sight = False

def make_map(Game):
    Game.objects = [Game.player]
    #fill map with "blocked" tiles
    Game.map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #get random width/height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #get random positions, but stay within map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

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
    Game.stairs = Object(new_x, new_y, '>', 'stairs', libtcod.white, always_visible = True)
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

        if not is_blocked(x, y, Game):
            choice = random_choice(monster_chances)

            if choice == 'johnstein':
                fighter_component = Fighter(hp=10, defense=0, power=2, xp=20, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'J', 'johnstein', libtcod.white, blocks=True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'greynaab':
                fighter_component = Fighter(hp=20, defense=1, power=4, xp=40, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'g', 'greynaab', libtcod.light_blue, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'jerbear':
                fighter_component = Fighter(hp=25, defense=1, power=5, xp=50, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'j', 'jerbear', libtcod.green, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'zombiesheep':
                fighter_component = Fighter(hp=30, defense=2, power=6, xp=60, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'z', 'zombiesheep', libtcod.yellow, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'odiv':
                fighter_component = Fighter(hp=25, defense=2, power=5, xp=60, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'o', 'odiv', libtcod.darker_orange, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'slitherrr':
                fighter_component = Fighter(hp=30, defense=2, power=6, xp=70, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 's', 'slitherrr', libtcod.darker_green, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'neckro':
                fighter_component = Fighter(hp=35, defense=3, power=7, xp=80, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'n', 'neckro', libtcod.lighter_blue, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'chan':
                fighter_component = Fighter(hp=30, defense=3, power=6, xp=80, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'c', 'chan', libtcod.darker_red, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'ashandarei':
                fighter_component = Fighter(hp=35, defense=3, power=7, xp=90, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'a', 'ashandarei', libtcod.darker_yellow, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'zureal':
                fighter_component = Fighter(hp=40, defense=4, power=8, xp=100, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'z', 'zureal', libtcod.dark_green, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'demiurge':
                fighter_component = Fighter(hp=35, defense=4, power=7, xp=100, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'd', 'demiurge', libtcod.darker_violet, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'hargrimm':
                fighter_component = Fighter(hp=40, defense=4, power=8, xp=125, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'h', 'hargrimm', libtcod.lighter_green, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'frisco':
                fighter_component = Fighter(hp=45, defense=5, power=9, xp=150, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'f', 'frisco', libtcod.lighter_red, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'toomuchpete':
                fighter_component = Fighter(hp=40, defense=5, power=8, xp=150, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 't', 'toomuchpete', libtcod.light_blue, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'flatluigi':
                fighter_component = Fighter(hp=50, defense=5, power=9, xp=200, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'f', 'flatluigi', libtcod.light_orange, blocks= True, fighter=fighter_component, ai=ai_component)
            elif choice == 'spanktrunk':
                fighter_component = Fighter(hp=60, defense=6, power=10, xp=250, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 's', 'spanktrunk', libtcod.red, blocks= True, fighter=fighter_component, ai=ai_component)
            
            elif choice == 'stavros':
                fighter_component = Fighter(hp=99, defense=10, power=5, xp=500, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'S', 'Stavros the Wonder Chicken', libtcod.light_cyan, blocks= True, fighter=fighter_component, ai=ai_component)
            else:
                print 'ERROR!'
                break

            Game.objects.append(monster)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        #only place it if the tile is not blocked
        if not is_blocked(x, y,Game):
            #create an item
            #roll = roll_dice([[0,100]])[0]
            choice = random_choice(item_chances)
            if choice == 'heal':
                #healing potion
                item_component = Item(use_function = cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.red, always_visible = True, item = item_component)
                #print 'Healing Potion'
            elif choice == 'lightning':
                #lightning scroll
                item_component = Item(use_function = cast_lightning)
                item = Object(x, y, '?', 'scroll of lightning bolt', libtcod.yellow, always_visible = True, item = item_component)
                #print 'Lightning Scroll'
            elif choice == 'fireball':
                #fireball scroll
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '?', 'scroll of fireball', libtcod.red, always_visible = True, item = item_component)
                #print 'Fireball Scroll'
            elif choice == 'confuse':
                #confusion scroll
                item_component = Item(use_function = cast_confusion)
                item = Object(x, y, '?', 'scroll of confusion', libtcod.light_violet, always_visible = True, item = item_component)
                #print 'Confusion Scroll'
            elif choice == 'sword':
                #sword
                equipment_component = Equipment(slot='right hand', power_bonus = 5)
                item = Object(x, y, '/', 'sword', libtcod.sky, always_visible = True, equipment = equipment_component)
            elif choice == 'shield':
                #create a shield
                equipment_component = Equipment(slot = 'left hand', defense_bonus = 3)
                item = Object(x, y, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)
            else:
                print 'ERROR!'
                break

            Game.objects.append(item)
            item.send_to_back(Game) #items appear below other objects


########################################################
#init and main loop
########################################################
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'MeFightRogues!', False)
libtcod.sys_set_fps(LIMIT_FPS)
Game.con = libtcod.console_new(MAP_WIDTH,MAP_HEIGHT)
Game.panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

main_menu()


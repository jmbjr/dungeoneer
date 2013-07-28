#standard imports
import libtcodpy as libtcod
from gamestuff import *
import data
import entitydata

#specific imports needed for this module
import shelve #for save and load
import entities
import map


#global class pattern
class Game(object): 
    game_msgs = []


#MAIN MENU GAME OPTIONS
def main_menu():
    img = libtcod.image_load(data.MAIN_MENU_BKG)

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show game title and credits
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, data.SCREEN_WIDTH/2, data.SCREEN_HEIGHT/2 - 4, libtcod.BKGND_NONE, libtcod.CENTER, 'MeFightRogues!')
        libtcod.console_print_ex(0, data.SCREEN_WIDTH/2, data.SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER, 'by johnstein!')

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
    fighter_component = entities.Fighter(hp=100, defense=3, power=6, xp=0, death_function=entities.player_death, speed = 3)
    Game.player = entities.Object(data.SCREEN_WIDTH/2, data.SCREEN_HEIGHT/2, '@', 'Roguetato', libtcod.white, tilechar=data.TILE_MAGE, blocks=True, fighter=fighter_component)

    Game.player.level = 1
    #generate map (at this point it's not drawn to screen)
    Game.dungeon_level = 1

    map.make_map(Game)
    map.initialize_fov(Game)

    Game.game_state = data.STATE_PLAYING
    Game.inventory = []

    #create the list of the game messages and their colors, starts empty
    Game.player.game_turns = 0

    #initial equipment
    equipment_component = entities.Equipment(slot='wrist', max_hp_bonus = 5)
    obj = entities.Object(0, 0, '-', 'wristguards of the whale', libtcod.gold, equipment=equipment_component)
    Game.inventory.append(obj)
    equipment_component.equip(Game)
    obj.always_visible = True
    Game.player.fighter.hp = Game.player.fighter.max_hp(Game)

    #a warm welcoming message!
    message('Welcome to MeFightRogues! Good Luck! Don\'t suck!', Game, libtcod.blue)
    libtcod.console_set_keyboard_repeat(data.KEYS_INITIAL_DELAY,data.KEYS_INTERVAL)


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

    map.initialize_fov(Game)

def play_game():
    Game.player_action = None

    #mouse stuff
    Game.mouse = libtcod.Mouse()
    Game.key = libtcod.Key()  

    (Game.camera_x, Game.camera_y) = (0, 0)  
    
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
        if Game.player.fighter.speed_counter <= 0: #player can take a turn-based            
            Game.player_action = handle_keys()

            if Game.player_action != data.STATE_NOACTION:
                #player actually did something. we can reset counter
                Game.player.fighter.speed_counter = Game.player.fighter.speed(Game)

        if Game.player_action == data.STATE_EXIT:
            break

        #print str(Game.player_action) + ' ' + str(Game.player.fighter.speed_counter)
        #give monsters a turn
        if Game.game_state == data.STATE_PLAYING and Game.player_action != data.STATE_NOACTION:
            for object in Game.objects:
                if object.fighter:
                    if object.fighter.speed_counter <= 0: #only allow a turn if the counter = 0. 
                        if object.ai:
                            object.ai.take_turn(Game)
                            object.fighter.speed_counter = object.fighter.speed(Game)

                    object.fighter.speed_counter -= 1

                    if object.fighter.regen_counter <= 0: #only regen if the counter = 0. 
                        object.fighter.hp += int(object.fighter.max_hp(Game) * data.REGEN_MULTIPLIER)
                        object.fighter.regen_counter = object.fighter.regen(Game)

                        if object.fighter.hp > object.fighter.max_hp(Game):
                                object.fighter.hp = object.fighter.max_hp(Game)

                    object.fighter.regen_counter -= 1
         
                    if object.fighter.buffs:
                        for buff in object.fighter.buffs:
                            buff.duration -= buff.decay_rate
                            if buff.duration <= 0:
                                object.fighter.remove_buff(buff)

                elif object.ai:
                    object.ai.take_turn(Game)

            
def check_level_up(Game):
    #see if the player's experience is enough to level-up
    level_up_xp = data.LEVEL_UP_BASE + Game.player.level * data.LEVEL_UP_FACTOR
    if Game.player.fighter.xp >= level_up_xp:
        Game.player.level += 1
        Game.player.fighter.xp -= level_up_xp
        message('You have reached level ' + str(Game.player.level) + '!', Game, libtcod.yellow)

        choice = None
        while choice == None: #keep asking till a choice is made
            choice = menu('Level up! Choose a stat to raise:\n', 
                ['Constitution (+25 HP, from ' + str(Game.player.fighter.max_hp(Game)) + ')',
                'Strength (+2 attack, from ' + str(Game.player.fighter.power(Game)) + ')', 
                'Agility (+2 defense, from ' + str(Game.player.fighter.defense(Game)) + ')'], data.LEVEL_SCREEN_WIDTH, Game)

        if choice == 0:
            Game.player.fighter.base_max_hp += 25
        elif choice == 1:
            Game.player.fighter.base_power += 2
        elif choice == 2:
            Game.player.fighter.base_defense += 2

        Game.player.fighter.hp = Game.player.fighter.max_hp(Game)


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
        return data.STATE_EXIT #exit game

    if Game.game_state == data.STATE_PLAYING:
        #rest
        if Game.key.vk == libtcod.KEY_KPDEC or Game.key.vk == libtcod.KEY_KP5:
            player_resting(Game)
            Game.fov_recompute = True
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
                        Game.player.game_turns += 1
                        return object.item.pick_up(Game)
                        #break

            if key_char == 'i':
                #show inv. if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it. \nPress ESC to return to game\n', Game)
                if chosen_item is not None:
                    Game.player.game_turns += 1
                    return chosen_item.use(Game)

            if key_char == 'd':
                #show the inventory. if item is selected, drop it
                chosen_item = inventory_menu('Press the key next to the item to drop. \nPress ESC to return to game\n', Game)
                if chosen_item is not None:
                    Game.player.game_turns += 1
                    chosen_item.drop(Game)

            if key_char == 'c':
                #show character info
                level_up_xp = data.LEVEL_UP_BASE + Game.player.level * data.LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(Game.player.level) + '\nExperience: ' + str(Game.player.fighter.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(Game.player.fighter.max_hp(Game)) +
                    '\nAttack: ' + str(Game.player.fighter.power(Game)) + '\nDefense: ' + str(Game.player.fighter.defense(Game)), Game, data.CHARACTER_SCREEN_WIDTH)

            if key_char == 'x':
                #debug key to automatically level up
                msgbox('You start to meditate!', Game, data.CHARACTER_SCREEN_WIDTH)
                level_up_xp = data.LEVEL_UP_BASE + Game.player.level * data.LEVEL_UP_FACTOR
                Game.player.fighter.xp = level_up_xp
                check_level_up(Game)
                Game.player.game_turns += 1       

            if key_char == 'a':
                #debug key to set all objects to visible
                msgbox('You can smell them all!', Game, data.CHARACTER_SCREEN_WIDTH)
                set_objects_visible(Game)

            if key_char == 'q':
                #go down stairs, if the player is on them
                msgbox('You feel your inner dwarf admiring the dungeon walls!', Game, data.CHARACTER_SCREEN_WIDTH)
                set_map_explored(Game)   

            if key_char == 'z':
                #debug key to automatically go to next level
                msgbox('You start digging at your feet!', Game, data.CHARACTER_SCREEN_WIDTH)
                map.next_level(Game)           

            if key_char == '>':
                #go down stairs, if the player is on them
                if Game.stairs.x == Game.player.x and Game.stairs.y == Game.player.y:
                    Game.player.game_turns +=1
                    map.next_level(Game)

            if key_char == 's': #general status key
                print str(Game.player.fighter.buffs)

            if key_char == 'p':
                print 'RELOADING GAME DATA'
                reload(data)
                reload(entitydata) 
                #update_entities()   #need to find a way to update all objects to current data
                Game.fov_recompute = True
                libtcod.console_set_keyboard_repeat(data.KEYS_INITIAL_DELAY,data.KEYS_INTERVAL)

                buff_component = entities.Buff('Super Strength', power_bonus=20)
                Game.player.fighter.add_buff(buff_component)
                msgbox ('YOU ROAR WITH BERSERKER RAGE!', Game, data.CHARACTER_SCREEN_WIDTH)

            if key_char == 'w':
                #give all items
                msgbox('You fashion some items from the scraps at your feet', Game, data.CHARACTER_SCREEN_WIDTH)
                give_items(Game)

            return data.STATE_NOACTION


#DEBUG FUNCTIONS
def give_items(Game):
    #healing potion
    x = 0
    y = 0
    item_component = entities.Item(use_function = entities.cast_heal)
    item = entities.Object(x, y, '!', 'healing potion', libtcod.red, always_visible = True, item = item_component)
    item.always_visible = True
    Game.inventory.append(item)

    #lightning scroll
    item_component = entities.Item(use_function = entities.cast_lightning)
    item = entities.Object(x, y, '?', 'scroll of lightning bolt', libtcod.yellow, always_visible = True, item = item_component)
    Game.inventory.append(item)

    #fireball scroll
    item_component = entities.Item(use_function = entities.cast_fireball)
    item = entities.Object(x, y, '?', 'scroll of fireball', libtcod.red, always_visible = True, item = item_component)
    Game.inventory.append(item)

    #confusion scroll
    item_component = entities.Item(use_function = entities.cast_confusion)
    item = entities.Object(x, y, '?', 'scroll of confusion', libtcod.light_violet, always_visible = True, item = item_component)
    Game.inventory.append(item)

    #sword
    equipment_component = entities.Equipment(slot='right hand', power_bonus = 5)
    item = entities.Object(x, y, '/', 'sword', libtcod.sky, always_visible = True, equipment = equipment_component)
    Game.inventory.append(item)

    #create a shield
    equipment_component = entities.Equipment(slot = 'left hand', defense_bonus = 3)
    item = entities.Object(x, y, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)
    Game.inventory.append(item)

    #wristguards
    equipment_component = entities.Equipment(slot='wrist', max_hp_bonus = 5)
    item = entities.Object(0, 0, '-', 'wristguards of the whale', libtcod.gold, equipment=equipment_component)
    Game.inventory.append(item)

def set_map_explored(Game):
    for y in range(data.MAP_HEIGHT):
        for x in range(data.MAP_WIDTH):
            Game.map[x][y].explored = True
    Game.fov_recompute = True        

def set_objects_visible(Game):
    for object in Game.objects:
        object.always_visible = True


########################################################
#init and main loop
########################################################
libtcod.console_set_custom_font('oryx_tiles3.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 12)
libtcod.console_init_root(data.SCREEN_WIDTH, data.SCREEN_HEIGHT, 'MeFightRogues!', False, libtcod.RENDERER_SDL)
libtcod.sys_set_fps(data.LIMIT_FPS)

libtcod.console_map_ascii_codes_to_font(256   , 32, 0, 5)  #map all characters in 1st row
libtcod.console_map_ascii_codes_to_font(256+32, 32, 0, 6)  #map all characters in 2nd row

Game.con = libtcod.console_new(data.MAP_WIDTH,data.MAP_HEIGHT)
Game.panel = libtcod.console_new(data.SCREEN_WIDTH, data.PANEL_HEIGHT)

main_menu()


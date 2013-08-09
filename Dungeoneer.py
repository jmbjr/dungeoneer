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
    msg_history = []

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
        choice = menu('', [Menuobj('Play a new game'), Menuobj('Continue last game'), Menuobj('Quit')], 24, Game, letterdelim=')')

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
    fighter_component = entities.Fighter(hp=300, defense=10, power=20, xp=0, xpvalue=10000, clan='player', death_function=entities.player_death, speed = 10)
    Game.player = entities.Object(data.SCREEN_WIDTH/2, data.SCREEN_HEIGHT/2, '@', 'Roguetato', libtcod.white, tilechar=data.TILE_MAGE, blocks=True, fighter=fighter_component)
    Game.player.dungeon_level = 1
    Game.dungeon_level = data.maplist[Game.player.dungeon_level]
    Game.player.xplevel = 1
    Game.game_state = data.STATE_PLAYING
    Game.player.game_turns = 0
    Game.set_auto = False

    Game.map = {}
    Game.objects = {}
    Game.upstairs = {}
    Game.downstairs = {}
    Game.tick = 0

    #generate map (at this point it's not drawn to screen)
    map.make_dungeon(Game)
    Game.tick = 1

    Game.fov_recompute = True
    Game.player.fighter.set_fov(Game)
    libtcod.console_clear(Game.con)

    #initial equipment
    equipment_component = entities.Equipment(slot='wrist', max_hp_bonus = 5)
    obj = entities.Object(0, 0, '-', 'wristguards of the whale', libtcod.gold, equipment=equipment_component)
    Game.player.fighter.add_item(obj)

    equipment_component.equip(Game)
    obj.always_visible = True
    Game.player.fighter.hp = Game.player.fighter.max_hp(Game)

    #a warm welcoming message!
    message('Welcome to MeFightRogues! Good Luck! Don\'t suck!', Game, libtcod.blue)
    libtcod.console_set_keyboard_repeat(data.KEYS_INITIAL_DELAY,data.KEYS_INTERVAL)

def save_game(filename='savegame'):
    #open a new empty shelve (or overwrite old one) to write the game data
    print 'SYSTEM--\t file saved!'
    file = shelve.open(filename, 'n')
    file['map'] = Game.map
    file['objects'] = Game.objects[Game.dungeon_level]
    file['player_index'] = Game.objects[Game.dungeon_level].index(Game.player) #index of player in the objects list
    file['game_msgs'] = Game.game_msgs
    file['msg_history'] = Game.msg_history
    file['game_state'] = Game.game_state
    file['stairs_index'] = Game.objects[Game.dungeon_level].index(Game.stairs)
    file['dungeon_level'] = Game.player.dungeon_level
    file.close()

def load_game(filename='savegame'):
    file = shelve.open(filename, 'r')
    Game.map = file['map']
    Game.objects[Game.dungeon_level] = file['objects'] 
    Game.player = Game.objects[Game.dungeon_level][file['player_index']]  #get index of player in the objects list
    Game.game_msgs = file['game_msgs']
    Game.msg_history = file['msg_history']
    Game.game_state = file['game_state']
    Game.stairs = Game.objects[Game.dungeon_level][file['stairs_index']]
    Game.player.dungeon_level = file['dungeon_level']
    file.close()

    map.initialize_fov(Game)

def play_game():
    Game.player_action = None

    #mouse stuff
    Game.mouse = libtcod.Mouse()
    Game.key = libtcod.Key()  

    (Game.camera_x, Game.camera_y) = (0, 0)  

    if data.AUTOMODE:
        set_objects_visible(Game)
        set_map_explored(Game)          
    
    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, Game.key, Game.mouse)

        #render the screen
        render_all(Game)
        libtcod.console_flush()
        check_level_up(Game)

        #erase objects from old position on current map, before they move
        for object in Game.objects[data.maplist[Game.player.dungeon_level]]:
            object.clear(Game)

        #only let player move if speed counter is 0 (or dead).  Don't allow player to move if controlled by AI.
        Game.dungeon_level = data.maplist[Game.player.dungeon_level]

        if not data.AUTOMODE:    
            if (Game.player.fighter.speed_counter <= 0 and not Game.player.ai) or Game.game_state == data.STATE_DEAD: #player can take a turn-based unless it has an AI         
                Game.player_action = handle_keys()

                if Game.player_action != data.STATE_NOACTION:
                    #player actually did something. we can reset counter
                    Game.player.fighter.speed_counter = Game.player.fighter.speed(Game)

        if Game.player_action == data.STATE_EXIT:
            break

        #handle monsters
        if Game.game_state == data.STATE_PLAYING and Game.player_action != data.STATE_NOACTION:
            Game.fov_recompute = True
            
            for index,Game.dungeon_level in enumerate(data.maplist):
                if index > 0: #skip intro level
                    for object in Game.objects[Game.dungeon_level]:
                        if object.fighter:
                            
                            if object.fighter.speed_counter <= 0: #only allow a turn if the counter = 0. 
                                if object.ai:
                                    if object.ai.take_turn(Game): #only reset speed_counter if monster is still alive
                                        object.fighter.speed_counter = object.fighter.speed(Game)

                            #this is clunky, but have to again check if monster is still alive
                            if object.fighter:
                                if object.fighter.regen_counter <= 0: #only regen if the counter = 0. 
                                    object.fighter.hp += int(object.fighter.max_hp(Game) * data.REGEN_MULTIPLIER)
                                    object.fighter.regen_counter = object.fighter.regen(Game)

                                object.fighter.regen_counter -= 1
                                object.fighter.speed_counter -= 1
                     
                                if object.fighter.buffs:
                                    for buff in object.fighter.buffs:
                                        buff.duration -= buff.decay_rate
                                        if buff.duration <= 0:
                                            message('*The effects of ' + buff.name + ' has worn off!', Game, libtcod.light_red)
                                            object.fighter.remove_buff(buff)

                                #always check to ensure hp <= max_hp
                                if object.fighter.hp > object.fighter.max_hp(Game):
                                        object.fighter.hp = object.fighter.max_hp(Game)

                        elif object.ai:
                            object.ai.take_turn(Game)
            Game.tick+=1

        Game.dungeon_level = data.maplist[Game.player.dungeon_level]

def check_level_up(Game):
    #see if the player's experience is enough to level-up
    level_up_xp = data.LEVEL_UP_BASE + Game.player.xplevel * data.LEVEL_UP_FACTOR
    if Game.player.fighter.xp >= level_up_xp:
        Game.player.xplevel += 1
        Game.player.fighter.xp -= level_up_xp
        message('You have reached level ' + str(Game.player.xplevel) + '!', Game, libtcod.yellow)

        choice = None
        while choice == None: #keep asking till a choice is made
                choice = menu('Level up! Choose a stat to raise:\n', 
                [Menuobj('Constitution (+25 HP, from ' + str(Game.player.fighter.max_hp(Game)) + ')',color=libtcod.green),
                Menuobj('Strength (+2 attack, from ' + str(Game.player.fighter.power(Game)) + ')', color=libtcod.red), 
                Menuobj('Defense (+2 defense, from ' + str(Game.player.fighter.defense(Game)) + ')', color=libtcod.blue)], data.LEVEL_SCREEN_WIDTH, Game, letterdelim=')')

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
            return player_move_or_attack(0, -1, Game)

        elif Game.key.vk == libtcod.KEY_DOWN or key_char == 'j' or Game.key.vk == libtcod.KEY_KP2 :
            return player_move_or_attack(0, 1, Game)

        elif Game.key.vk == libtcod.KEY_LEFT or key_char == 'h' or Game.key.vk == libtcod.KEY_KP4 :
            return player_move_or_attack(-1, 0, Game)

        elif Game.key.vk == libtcod.KEY_RIGHT or key_char == 'l' or Game.key.vk == libtcod.KEY_KP6 :
            return player_move_or_attack(1, 0, Game)

        #handle diagonal. 11 oclock -> clockwise
        elif key_char == 'y' or Game.key.vk == libtcod.KEY_KP7 :
            return player_move_or_attack(-1, -1, Game)

        elif key_char == 'u' or Game.key.vk == libtcod.KEY_KP9 :
            return player_move_or_attack(1, -1, Game)

        elif key_char == 'n' or Game.key.vk == libtcod.KEY_KP3 :
            return player_move_or_attack(1, 1, Game)

        elif key_char == 'b' or Game.key.vk == libtcod.KEY_KP1 :
            return player_move_or_attack(-1, 1, Game)

        else:
            #test for other keys
            if key_char == 'g':
                #pick up an item
                for object in Game.objects[data.maplist[Game.player.dungeon_level]]: #look for items in the player's title on the same floor of the player
                    if object.x == Game.player.x and object.y == Game.player.y and object.item:
                        Game.player.game_turns += 1
                        return object.item.pick_up(Game, Game.player)
                        #break

            if key_char == 'i':
                #show inv. if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it. \nPress ESC to return to game\n', Game)
                if chosen_item is not None:
                    Game.player.game_turns += 1
                    return chosen_item.use(Game, user=Game.player)

            if key_char == 'd':
                #show the inventory. if item is selected, drop it
                chosen_item = inventory_menu('Press the key next to the item to drop. \nPress ESC to return to game\n', Game)
                if chosen_item is not None:
                    Game.player.game_turns += 1
                    chosen_item.drop(Game, Game.player)

            if key_char == 'c':
                #show character info
                level_up_xp = data.LEVEL_UP_BASE + Game.player.xplevel * data.LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(Game.player.xplevel) + '\nExperience: ' + str(Game.player.fighter.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(Game.player.fighter.max_hp(Game)) +
                    '\nAttack: ' + str(Game.player.fighter.power(Game)) + '\nDefense: ' + str(Game.player.fighter.defense(Game)), Game, data.CHARACTER_SCREEN_WIDTH)

            if key_char == 'x':
                #debug key to automatically level up
                msgbox('You start to meditate!', Game, data.CHARACTER_SCREEN_WIDTH)
                level_up_xp = data.LEVEL_UP_BASE + Game.player.xplevel * data.LEVEL_UP_FACTOR
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
                if Game.downstairs[data.maplist[Game.player.dungeon_level]].x == Game.player.x and Game.downstairs[data.maplist[Game.player.dungeon_level]].y == Game.player.y:
                    Game.player.game_turns +=1
                    map.next_level(Game)

            if key_char == '<':
                #go up stairs, if the player is on them
                if Game.upstairs[data.maplist[Game.player.dungeon_level]].x == Game.player.x and Game.upstairs[data.maplist[Game.player.dungeon_level]].y == Game.player.y:
                    Game.player.game_turns +=1
                    map.prev_level(Game)

            if key_char == 's': #general status key
                #debug key to automatically go to prev level
                msgbox('You start digging above your head!', Game, data.CHARACTER_SCREEN_WIDTH)
                map.prev_level(Game)    

            if key_char == 'p': #display log
                width = data.SCREEN_WIDTH
                height = data.SCREEN_HEIGHT

                history = [[]]
                count = 0
                page = 1
                numpages = int(float(len(Game.msg_history))/data.MAX_NUM_ITEMS + 1)

                for thepage in range(numpages):
                    history.append([])

                for obj in reversed(Game.msg_history):
                    line = obj.text
                    color = obj.color
                    history[page].append(Menuobj(line, color = color))
                    count += 1

                    if count >= data.MAX_NUM_ITEMS:
                        page +=1
                        count = 0

                for thepage in range(numpages):
                    window = libtcod.console_new(width, height)
                    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, '')
                    libtcod.console_blit(window, 0, 0, width, height, 0, 0, 0, 1.0, 1)
                    menu ('Message Log: (Sorted by Most Recent Turn) Page ' + str(thepage+1) + '/' + str(numpages), history[thepage+1], data.SCREEN_WIDTH, Game, letterdelim=None)

                Game.fov_recompute = True           



            if key_char == 'r':
                print 'SYSTEM--\t RELOADING GAME DATA'
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

    for item in entitydata.items:
        theitem = entities.Object(**entitydata.items[item])
        theitem.always_visible = True
        Game.player.fighter.add_item(theitem)

def set_map_explored(Game):
    for y in range(data.MAP_HEIGHT):
        for x in range(data.MAP_WIDTH):
            Game.map[data.maplist[Game.player.dungeon_level]][x][y].explored = True
    Game.fov_recompute = True        

def set_objects_visible(Game):
    for object in Game.objects[data.maplist[Game.player.dungeon_level]]:
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


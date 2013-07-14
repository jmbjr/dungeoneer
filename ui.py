import libtcodpy as libtcod
import textwrap
from constants import *
#primarily concerned with displaying info to the screen

def message(new_msg, Game, color = libtcod.white):
    #split message if necessary
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(Game.game_msgs) == MSG_HEIGHT:
            del Game.game_msgs[0]

        #add the new line as a tuple, with the txt and the color
        Game.game_msgs.append((line, color))

def menu(header, options, width, Game):
    if len(options) > MAX_NUM_ITEMS: raise ValueError('Cannot have a menu with more than ' + MAX_NUM_ITEMS + ' options.')

    #calculate total height of the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(Game.con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit contents of window to root console
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for a keypress
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt: # full screen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    #convert ASCII code to an index. if it's valid, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options):
        return index
    else:
        return None

def msgbox(text, Game, width = 50):
    menu(text, [], width, Game) #use menu as a sort-of message box

def inventory_menu(header, Game):
	#show a menu with each item of the inventory as an option
	if len(Game.inventory) == 0:
	    options = ['inventory is empty!']
	else:
	    #options = [item.name for item in inventory]
	    options = []
	    for item in Game.inventory:
	        text = item.name
	        #show additional info, in case it's equipped
	        if item.equipment and item.equipment.is_equipped:
	            text = text + ' (on ' + item.equipment.slot + ')'
	        options.append(text)

	index = menu(header, options, INVENTORY_WIDTH, Game)

	if (index is None or len(Game.inventory) == 0) or index == 'ESC':
	    return None
	else:
	    return Game.inventory[index].item


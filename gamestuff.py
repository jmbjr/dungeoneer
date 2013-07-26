#standard imports
import libtcodpy as libtcod
import data

#specific imports needed for this module
import math
import textwrap

#common class objects for shapes and tiles
class Rect(object):
    #a rectangle on the map. used to characterize a room
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2)/2
        center_y = (self.y1 + self.y2)/2
        return (center_x, center_y)

    def intersect(self, other):
        #returns True if this rect intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Tile(object):
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #all tiles start out unexplored
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight


#User Interface routines
def message(new_msg, Game, color = libtcod.white):
    #split message if necessary
    new_msg_lines = textwrap.wrap(new_msg, data.MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(Game.game_msgs) == data.MSG_HEIGHT:
            del Game.game_msgs[0]

        #add the new line as a tuple, with the txt and the color
        Game.game_msgs.append((line, color))

def menu(header, options, width, Game):
    if len(options) > data.MAX_NUM_ITEMS: 
        message('Cannot have a menu with more than ' + str(data.MAX_NUM_ITEMS) + ' options.', Game)

    #calculate total height of the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(Game.con, 0, 0, width, data.SCREEN_HEIGHT, header)
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
    x = data.SCREEN_WIDTH / 2 - width / 2
    y = data.SCREEN_HEIGHT / 2 - height / 2
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

    index = menu(header, options, data.INVENTORY_WIDTH, Game)

    if (index is None or len(Game.inventory) == 0) or index == 'ESC':
        return None
    else:
        return Game.inventory[index].item



#common gamestuff routines.  random number routines and distance calculators
def flip_coin():
    return (libtcod.random_get_int(0,0,1))

def random_choice(chances_dict):
    #choose one option from dict of chances and return key
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]

def random_choice_index(chances): #choose one option from list of chances. return index
    #the dice will land on some number between 1 and sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds with this choice
        if dice <= running_sum:
            return choice
        choice +=1

def get_distance(dx, dy):
    return math.sqrt(dx ** 2 + dy ** 2)

def roll_dice(dicelist):
    dice=[]
    #print dicelist
    for [die_low, die_high] in dicelist:
        roll = libtcod.random_get_int(0,die_low,die_high)
        dice.append(roll)

    return [sum(dice), dice]



#render routines
def render_all(Game):

    move_camera(Game.player.x, Game.player.y, Game)

    if Game.fov_recompute:
        #recompute FOV if needed (if player moved or something else happened)
        Game.fov_recompute = False
        libtcod.map_compute_fov(Game.fov_map, Game.player.x, Game.player.y, data.TORCH_RADIUS, data.FOV_LIGHT_WALLS, data.FOV_ALGO)
        libtcod.console_clear(Game.con)

        for y in range(data.CAMERA_HEIGHT):
            for x in range(data.CAMERA_WIDTH):
                (map_x, map_y) = (Game.camera_x + x, Game.camera_y + y)
                visible = libtcod.map_is_in_fov(Game.fov_map, map_x, map_y)
                wall = Game.map[map_x][map_y].block_sight

                if data.ASCIIMODE:
                    thewallchar  = data.WALL_CHAR
                    thegroundchar = data.GROUND_CHAR
                else:
                    thewallchar  = data.TILE_WALL
                    thegroundchar = data.TILE_GROUND

                #thegroundchar = data.GROUND_CHAR
                if not visible:
                    #tile not visible
                    if wall:
                        color_wall_ground = data.COLOR_DARK_WALL
                        char_wall_ground = thewallchar
                    else:
                        color_wall_ground = data.COLOR_DARK_GROUND
                        char_wall_ground = thegroundchar
                    fov_wall_ground = libtcod.grey
                else:
                    #tile is visible
                    Game.map[map_x][map_y].explored = True
                    if wall:
                        color_wall_ground = data.COLOR_LIGHT_WALL
                        char_wall_ground = thewallchar
                    else:
                        color_wall_ground = data.COLOR_LIGHT_GROUND
                        char_wall_ground = thegroundchar
                    fov_wall_ground = libtcod.white

                if Game.map[map_x][map_y].explored:
                    libtcod.console_put_char_ex(Game.con, x, y, char_wall_ground, fov_wall_ground, color_wall_ground)
                

    #draw all objects in the list
    for object in Game.objects:
        if object != Game.player:
            object.draw(Game)
    #ensure we draw player last
    Game.player.draw(Game)

    #blit contents of con to root console
    libtcod.console_blit(Game.con, 0, 0, data.SCREEN_WIDTH, data.SCREEN_HEIGHT, 0, 0, 0)

    #show player's stats via GUI panel
    libtcod.console_set_default_background(Game.panel, libtcod.black)
    libtcod.console_clear(Game.panel)

    #show player stats
    render_bar(1, 1, data.BAR_WIDTH, 'HP', Game.player.fighter.hp, Game.player.fighter.max_hp(Game), libtcod.light_red, libtcod.darker_red, Game)
    libtcod.console_print_ex(Game.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level: ' + str(Game.dungeon_level))
    libtcod.console_print_ex(Game.panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT, 'Turn: ' + str(Game.player.game_turns))

    #print the game messages, one line at a time
    y = 1
    for (line, color) in Game.game_msgs:
        libtcod.console_set_default_foreground(Game.panel, color)
        libtcod.console_print_ex(Game.panel, data.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(Game.panel, libtcod.light_gray)
    libtcod.console_print_ex(Game.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse(Game))

    #blit panel to root console
    libtcod.console_blit(Game.panel, 0, 0, data.SCREEN_WIDTH, data.PANEL_HEIGHT, 0, 0, data.PANEL_Y)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color, Game):
    #render a bar (HP, exp, etc). first calc the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(Game.panel, back_color)
    libtcod.console_rect(Game.panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(Game.panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(Game.panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #lastly add text
    libtcod.console_set_default_foreground(Game.panel, libtcod.white)
    libtcod.console_print_ex(Game.panel, x + total_width/2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))



#get info from world. check/select tiles. select objects
def get_names_under_mouse(Game):
    #return a string with the names of all objects under the mouse
    (x, y) = (Game.mouse.cx, Game.mouse.cy)
    (x, y) = (Game.camera_x + x, Game.camera_y + y)  #from screen to map coords

    #create list with the names of all objects at the mouse's coords and in FOV
    names = [obj.name for obj in Game.objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(Game.fov_map, obj.x, obj.y)]
    
    names = ', '.join(names) #join names separated by commas
    return names.capitalize()



#player movement routines
def player_move_or_attack(dx, dy, Game):
    #the coords the player is moving-to/attacking
    x = Game.player.x + dx
    y = Game.player.y + dy

    #try to find attackable object there
    target = None
    for object in Game.objects:
        if object.x == x and object.y == y and object.fighter:
            target = object
            break

    #attack if target found. else, move
    if target is not None:
        Game.player.fighter.attack(target, Game)
        Game.player.game_turns +=1
    else:
        Game.player.move(dx, dy, Game)
        Game.player.game_turns +=1
    
    Game.fov_recompute = True

def player_resting(Game):
    #Game.player.fighter.hp += 2
    Game.player.game_turns += 1

#camera stuff for scrolling
def move_camera(target_x, target_y, Game):
     #new camera coordinates (top-left corner of the screen relative to the map)
    x = target_x - data.CAMERA_WIDTH / 2  #coordinates so that the target is at the center of the screen
    y = target_y - data.CAMERA_HEIGHT / 2
 
    #make sure the camera doesn't see outside the map
    if x < 0: x = 0
    if y < 0: y = 0
    if x > data.MAP_WIDTH - data.CAMERA_WIDTH - 1: x = data.MAP_WIDTH - data.CAMERA_WIDTH - 1
    if y > data.MAP_HEIGHT - data.CAMERA_HEIGHT - 1: y = data.MAP_HEIGHT - data.CAMERA_HEIGHT - 1
 
    if x != Game.camera_x or y != Game.camera_y: Game.fov_recompute = True
 
    (Game.camera_x, Game.camera_y) = (x, y)
 
def to_camera_coordinates(x, y, Game):
    #convert coordinates on the map to coordinates on the screen
    (x, y) = (x - Game.camera_x, y - Game.camera_y)
 
    if (x < 0 or y < 0 or x >= data.CAMERA_WIDTH or y >= data.CAMERA_HEIGHT):
        return (None, None)  #if it's outside the view, return nothing
 
    return (x, y)





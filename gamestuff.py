#standard imports
import gamedata

#specific imports needed for this module
import math
import textwrap
import colors
import keys
import guistuff

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

class Menuobj(object):
    def __init__(self, text, color=None, char=None):
        self.text = text
        self.color = color
        self.char = char


def mapname(Game):
    return(Game.dat.maplist[Game.player.dungeon_level])

#User Interface routines
def message(new_msg, Game, color = None, displaymsg=True):
    #split message if necessary
    if color is None:
        color = Game.col.WHITE

    if Game.dat.PRINT_MESSAGES:
        if Game.dat.FREE_FOR_ALL_MODE:
            Game.message_sql.log_entity(Game, new_msg)

        print 'MSG--\t ' + str(Game.tick) + '\t' + Game.dungeon_levelname + '\t' + new_msg

    if displaymsg:
        turn = Game.player.game_turns
        new_msg_lines = textwrap.wrap(new_msg, Game.dat.MSG_WIDTH)

        for line in new_msg_lines:
            #if the buffer is full, remove the first line to make room for the new one
            if len(Game.game_msgs) == Game.dat.MSG_HEIGHT:
                del Game.game_msgs[0]

            #add the new line as a tuple, with the txt and the color
            Game.msg_history.append(Menuobj(str(turn) + ' : ' + line, color=color))
            Game.game_msgs.append((line, color))



def menu(rootcon, header, options, width, Game, letterdelim=None):
    if len(options) > Game.dat.MAX_NUM_ITEMS: 
        message('Cannot have a menu with more than ' + str(Game.dat.MAX_NUM_ITEMS) + ' options.', Game)

    #calculate total height of the header (after auto-wrap) and one line per option
    header_height = Game.gui.get_height_rect(Game.con, 0, 0, width, Game.dat.SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create off-screen console that represents the menu's window
    window = Game.gui.console(width, height)
    Game.gui.print_rect(window, 0, 0, width, height, val=header, fg_color=Game.col.WHITE)

    #print all the options
    y = header_height
    letter_index = ord('a')

    for obj in options:
        text = obj.text
        color = obj.color
        char = obj.char

        if color is None: color = Game.col.WHITE
        if char is None: char = ''
        if letterdelim is None: 
            letterchar = ''
        else:
            letterchar = chr(letter_index) + letterdelim

        Game.gui.print_str(window, 0, y, val=letterchar + ' ' + char + ' ' + text, fg_color=color) 

        y += 1
        letter_index += 1

    #blit contents of window to root console
    x = Game.dat.SCREEN_WIDTH / 2 - width / 2
    y = Game.dat.SCREEN_HEIGHT / 2 - height / 2
    Game.gui.con_blit(window, 0, 0, width, height, rootcon, x, y, 1.0, 0.7)
    Game.gui.flush(rootcon)
    Game.gui.prep_keyboard(0,0)

    goodchoice = False
    while not goodchoice:
        key = Game.gui.getkey(Game.con, Game.mouse, Game.key, wait=True)
        if key.pressed == False: continue
        #convert ASCII code to an index. if it's valid, return it

        index = key.charcode - ord('a')

        if index >= 0 and index < len(options):
            goodchoice = True
            retval = index
        elif key.keycode == keys.ESC or key.keycode == keys.SPACE:
            goodchoice = True
            retval = None

    Game.gui.prep_keyboard(Game.dat.KEYS_INITIAL_DELAY,Game.dat.KEYS_INTERVAL)
    return retval

def msgbox(text, Game, width = 50):
    menu(rootcon, text, [], width, Game) #use menu as a sort-of message box

def inventory_menu(rootcon, header, Game, user):
    if user.fighter:
        options = []
        #show a menu with each item of the inventory as an option
        if not len(user.fighter.inventory):
            obj = Menuobj('inventory is empty!', color=Game.col.WHITE, char='?')
            options.append(obj)
        else:
            #options = [item.name for item in inventory]
            
            for item in user.fighter.inventory:
                text = item.name
                #show additional info, in case it's equipped
                if item.equipment and item.equipment.is_equipped:
                    text = text + ' (on ' + item.equipment.slot + ')'
                
                obj = Menuobj(text, color=item.color, char=item.char)    
                options.append(obj)

        index = menu(rootcon, header, options, Game.dat.INVENTORY_WIDTH, Game, letterdelim='')

        if (index is None or len(user.fighter.inventory) == 0) or index == 'ESC':
            return None
        else:
            return user.fighter.inventory[index].item
    else:
        return None

def get_distance(dx, dy):
    return math.sqrt(dx ** 2 + dy ** 2)

#render routines
def render_all(Game):
    move_camera(Game.player.x, Game.player.y, Game)

    if Game.fov_recompute:
        #recompute FOV if needed (if player moved or something else happened)
        Game.fov_recompute = False
        Game.player.fighter.fov_recompute(Game)
        Game.gui.clear(Game.con)

        for y in range(Game.dat.CAMERA_HEIGHT):
            for x in range(Game.dat.CAMERA_WIDTH):
                (map_x, map_y) = (Game.camera_x + x, Game.camera_y + y)
                visible = Game.fov.map_is_in_fov(Game.player.fighter.fov, map_x, map_y)
                wall = Game.map[Game.dungeon_levelname].block_sight(map_x, map_y)

                if gamedata.ASCIIMODE:
                    thewallchar  = Game.dat.WALL_CHAR
                    thegroundchar = Game.dat.GROUND_CHAR
                else:
                    thewallchar  = Game.dat.TILE_WALL
                    thegroundchar = Game.dat.TILE_GROUND

                #thegroundchar = Game.dat.GROUND_CHAR
                if not visible:
                    #tile not visible
                    if wall:
                        color_wall_ground = Game.dat.COLOR_DARK_WALL
                        char_wall_ground = thewallchar
                    else:
                        color_wall_ground = Game.dat.COLOR_DARK_GROUND
                        char_wall_ground = thegroundchar
                    fov_wall_ground = Game.col.DARK_GREY
                else:
                    #tile is visible
                    Game.map[Game.dungeon_levelname].set_explored(map_x, map_y)
                    if wall:
                        color_wall_ground = Game.dat.COLOR_LIGHT_WALL
                        char_wall_ground = thewallchar
                    else:
                        color_wall_ground = Game.dat.COLOR_LIGHT_GROUND
                        char_wall_ground = thegroundchar
                    fov_wall_ground = Game.col.WHITE

                if Game.map[Game.dungeon_levelname].explored(map_x, map_y):
                    Game.gui.print_char(Game.con, x, y, val=char_wall_ground, fg_color=fov_wall_ground, bg_color=color_wall_ground)
                

    #draw all objects in the list
    for object in Game.objects[Game.dungeon_levelname]:
        if object != Game.player:
            object.draw(Game)
    #ensure we draw player last
    Game.player.draw(Game)

    #blit contents of con to root console
    Game.gui.con_blit(Game.con, 0, 0, Game.dat.SCREEN_WIDTH, Game.dat.SCREEN_HEIGHT, 0, 0, 0)

    #show player's stats via GUI panel
    Game.gui.clear(Game.panel)

    #show player stats
    render_bar(1, 1, Game.dat.BAR_WIDTH, 'HP', Game.player.fighter.hp, Game.player.fighter.max_hp(Game), Game.col.LIGHT_RED, Game.col.RED, Game)
    Game.gui.print_str(Game.panel, 1, 3, val=Game.dungeon_levelname, fg_color=Game.col.WHITE, bg_color=Game.col.BLACK)
    Game.gui.print_str(Game.panel, 1, 4, val='Dungeon level: ' + str(Game.player.dungeon_level), fg_color=Game.col.WHITE, bg_color=Game.col.BLACK)
    Game.gui.print_str(Game.panel, 1, 5, val='Turn: ' + str(Game.player.game_turns) + ' (' + str(Game.tick) +')', fg_color=Game.col.WHITE, bg_color=Game.col.BLACK)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in Game.game_msgs:
        Game.gui.print_str(Game.panel, Game.dat.MSG_X, y, val=line, fg_color=color)
        y += 1

    #display names of objects under the mouse
    Game.gui.print_str(Game.panel, 1, 0, val=get_names_under_mouse(Game), fg_color=Game.col.LIGHT_GREY)

    #blit panel to root console
    Game.gui.con_blit(Game.panel, 0, 0, Game.dat.SCREEN_WIDTH, Game.dat.PANEL_HEIGHT, 0, 0, Game.dat.PANEL_Y)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color, Game):
    #render a bar (HP, exp, etc). first calc the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    Game.gui.draw_rect(Game.panel, x, y, total_width, 1, False, bg_color=back_color)

    #now render the bar on top
    if bar_width > 0:
        Game.gui.draw_rect(Game.panel, x, y, bar_width, 1, False, bg_color=bar_color)

    #lastly add text
    Game.gui.print_str(Game.panel, x + total_width/2, y, align=guistuff.CENTER, val=name + ': ' + str(value) + '/' + str(maximum), fg_color=Game.col.WHITE)

#get info from world. check/select tiles. select objects
def get_names_under_mouse(Game):
    #return a string with the names of all objects under the mouse
    (x, y) = (Game.mouse.cx, Game.mouse.cy)
    (x, y) = (Game.camera_x + x, Game.camera_y + y)  #from screen to map coords

    #create list with the names of all objects at the mouse's coords and in FOV
    names = [obj.name for obj in Game.objects[Game.dungeon_levelname]
        if obj.x == x and obj.y == y and Game.fov.map_is_in_fov(Game.player.fighter.fov, obj.x, obj.y)]
    
    names = ', '.join(names) #join names separated by commas
    return names.capitalize()



#player movement routines
def player_move_or_attack(dx, dy, Game):
    #the coords the player is moving-to/attacking
    x = Game.player.x + dx
    y = Game.player.y + dy

    #try to find attackable object there
    target = None
    #only check objects on the same floor as the player
    for object in Game.objects[Game.dat.maplist[Game.player.dungeon_level]]:
        if object.x == x and object.y == y and object.fighter:
            target = object
            break

    #attack if target found. else, move
    if target is not None:
        Game.player.fighter.attack(target, Game)
        Game.player.game_turns +=1
        state = Game.dat.STATE_PLAYING
    else:
        if Game.player.move(dx, dy, Game):
            Game.player.game_turns +=1
            state = Game.dat.STATE_PLAYING

            for object in Game.objects[Game.dat.maplist[Game.player.dungeon_level]]: #look for items in the player's title
                if object.x == Game.player.x and object.y == Game.player.y and object is not Game.player:
                    message('* You see ' + object.name + ' at your feet *', Game, Game.col.YELLOW)

        else:
            state = Game.dat.STATE_NOACTION

    Game.fov_recompute = True
    return state

def player_resting(Game):
    #Game.player.fighter.hp += 2
    Game.player.game_turns += 1

#camera stuff for scrolling
def move_camera(target_x, target_y, Game):
     #new camera coordinates (top-left corner of the screen relative to the map)
    x = target_x - Game.dat.CAMERA_WIDTH / 2  #coordinates so that the target is at the center of the screen
    y = target_y - Game.dat.CAMERA_HEIGHT / 2
 
    #make sure the camera doesn't see outside the map
    if x < 0: x = 0
    if y < 0: y = 0
    if x > Game.dat.MAP_WIDTH - Game.dat.CAMERA_WIDTH - 1: x = Game.dat.MAP_WIDTH - Game.dat.CAMERA_WIDTH - 1
    if y > Game.dat.MAP_HEIGHT - Game.dat.CAMERA_HEIGHT - 1: y = Game.dat.MAP_HEIGHT - Game.dat.CAMERA_HEIGHT - 1
 
    if x != Game.camera_x or y != Game.camera_y: Game.fov_recompute = True
 
    (Game.camera_x, Game.camera_y) = (x, y)
 
def to_camera_coordinates(x, y, Game):
    #convert coordinates on the map to coordinates on the screen
    (x, y) = (x - Game.camera_x, y - Game.camera_y)
 
    if (x < 0 or y < 0 or x >= Game.dat.CAMERA_WIDTH or y >= Game.dat.CAMERA_HEIGHT):
        return (None, None)  #if it's outside the view, return nothing
 
    return (x, y)

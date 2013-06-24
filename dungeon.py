import libtcodpy as libtcod


SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 45


ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30


FOV_ALGO = 0 #default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

WALL_CHAR = '#'
GROUND_CHAR  = '.'

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)


class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #all tiles start out unexplored
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect:
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

class Object:
    #this is a generic object: player, monster, item, stairs
    #always represented by a character on the screen
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):

        if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    def draw(self):
        #only draw if in field of view of player
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            #set the color then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase char that represents this object
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_put_char_ex(con, self.x, self.y, GROUND_CHAR, libtcod.white, color_light_ground)


def create_room(room):
    global map
    #go through tiles in rect to make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
                map[x][y].blocked = False
                map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map

    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map

    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def make_map():
    global map, player
    #EXAMPLE 1: TWO PILLARS
    #fill map with "unblocked" tiles
    # map = [[Tile(False)
    #     for y in range(MAP_HEIGHT) ]
    #         for x in range(MAP_WIDTH) ]

    # map[30][22].blocked = True
    # map[30][22].block_sight = True
    # map[50][22].blocked = True
    # map[50][22].block_sight = True

    #EXAMPLE 2: TWO ROOMS
    #fill map with "blocked" tiles
    map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    # #create two rooms
    # room1 = Rect(20, 15, 10, 15)
    # room2 = Rect(50, 15, 10, 15)
    # create_room(room1)
    # create_room(room2)
    # create_h_tunnel(25, 55, 23)

    #EXAMPLE 3: random rooms
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

            create_room(new_room)
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #first room. start player here
                player.x = new_x
                player.y = new_y

            else:
                #for all other rooms, need to connect to previous room with a tunnel

                #get center coords of previous room
                (prev_x, prev_y) = rooms[num_rooms -1].center()

                #flip coin
                if flip_coin() == 1:
                    #move h then v
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #move v then h
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
            
            #add to rooms list
            rooms.append(new_room)
            num_rooms +=1

def render_all():
    global color_light_wall, color_dark_wall
    global color_light_ground, color_dark_ground
    global fov_recompute, fov_map

    if fov_recompute:
        #recompute FOV if needed (if player moved or something else happened)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #tile not visible
                    if wall:
                        color_wall_ground = color_dark_wall
                        char_wall_ground = WALL_CHAR
                    else:
                        color_wall_ground = color_dark_ground
                        char_wall_ground = GROUND_CHAR
                    fov_wall_ground = libtcod.grey
                else:
                    #tile is visible
                    map[x][y].explored = True
                    if wall:
                        color_wall_ground = color_light_wall
                        char_wall_ground = WALL_CHAR
                    else:
                        color_wall_ground = color_light_ground
                        char_wall_ground = GROUND_CHAR
                    fov_wall_ground = libtcod.white

                if map[x][y].explored:
                    libtcod.console_put_char_ex(con, x, y, char_wall_ground, fov_wall_ground, color_wall_ground)
                

    #draw all objects in the list
    for object in objects:
        object.draw()

    #blit contents of con to root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

def handle_keys():
    global fov_recompute

    #for real-time, uncomment
    #key = libtcod.console_check_for_keypress()

    #for turn-based, uncomment
    key = libtcod.console_wait_for_keypress(True)
    key_char = chr(key.c)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #ALT + ENTER: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return True #exit game

    #movement keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP) or key_char == 'k' or libtcod.console_is_key_pressed(libtcod.KEY_KP8) :
        player.move(0, -1)
        fov_recompute = True
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN) or key_char == 'j' or libtcod.console_is_key_pressed(libtcod.KEY_KP2) :
        player.move(0, 1)
        fov_recompute = True
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT) or key_char == 'h' or libtcod.console_is_key_pressed(libtcod.KEY_KP4) :
        player.move(-1, 0)
        fov_recompute = True
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT) or key_char == 'l' or libtcod.console_is_key_pressed(libtcod.KEY_KP6) :
        player.move(1, 0)
        fov_recompute = True
    #handle diagonal. 11 oclock -> clockwise
    elif key_char == 'y' or libtcod.console_is_key_pressed(libtcod.KEY_KP7) :
        player.move(-1, -1)
        fov_recompute = True
    elif key_char == 'u' or libtcod.console_is_key_pressed(libtcod.KEY_KP9) :
        player.move(1, -1)
        fov_recompute = True
    elif key_char == 'n' or libtcod.console_is_key_pressed(libtcod.KEY_KP3) :
        player.move(1, 1)
        fov_recompute = True
    elif key_char == 'b' or libtcod.console_is_key_pressed(libtcod.KEY_KP1) :
        player.move(-1, 1)
        fov_recompute = True



def flip_coin():
    return (libtcod.random_get_int(0,0,1))

########################################################
#init and main loop
########################################################

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)


player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)


npc = Object(SCREEN_WIDTH/2 -5, SCREEN_HEIGHT/2, '@', libtcod.yellow)  


objects = [npc, player]


make_map()

#create FOV map according to the generated map
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

fov_recompute = True

while not libtcod.console_is_window_closed():
    #render the screen
    render_all()

    libtcod.console_flush()

    #erase objects from old position, before they move
    for object in objects:
        object.clear()

    #handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        break

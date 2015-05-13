import libtcod

#DON'T EDIT DATA BETWEEN X's WHILE GAME IS RUNNING, UNLESS YOU WANT THE GAME TO CRASH
#.............................................
#EDITABLE MAP DATA
WALL_CHAR          = 'X'
GROUND_CHAR        = ' '

COLOR_DARK_WALL    = libtcod.darker_grey
COLOR_LIGHT_WALL   = libtcod.light_grey
COLOR_DARK_GROUND  = libtcod.dark_sepia
COLOR_LIGHT_GROUND = libtcod.sepia

FOV_ALGO           = 2 #FOV ALGORITHM. values = 0 to 4
FOV_LIGHT_WALLS    = True
TORCH_RADIUS       = 80 #AFFECTS FOV RADIUS

TILE_WALL          = 256  #first tile in the first row of tiles
TILE_GROUND        = 256 + 1
TILE_MAGE          = 256 + 32  #first tile in the 2nd row of tiles
TILE_SKEL_WHITE    = 256 + 32 + 1  #2nd tile in the 2nd row of tiles
TILE_SKEL_RED      = 256 + 32 + 2  #2nd tile in the 2nd row of tiles
TILE_SKEL_BLUE     = 256 + 32 + 3  #2nd tile in the 2nd row of tiles
TILE_SKEL_GREEN    = 256 + 32 + 4  #2nd tile in the 2nd row of tiles
TILE_SKEL_ORANGE   = 256 + 32 + 5  #2nd tile in the 2nd row of tiles
TILE_SKEL_MAGENTA  = 256 + 32 + 6  #2nd tile in the 2nd row of tiles
TILE_SKEL_TEAL     = 256 + 32 + 7  #2nd tile in the 2nd row of tiles
TILE_SKEL_YELLOW   = 256 + 32 + 8  #2nd tile in the 2nd row of tiles
TILE_SKEL_PURPLE   = 256 + 32 + 9  #2nd tile in the 2nd row of tiles

maplist =[]

maplist.append('Intro')
maplist.append('Brig')
#maplist.append('Engineering')
#maplist.append('Bridge')
#maplist.append('Sick Bay')

#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#probably shouldn't edit these when the game is running
SCREEN_WIDTH       = 80  #SETS OVERALL SCREEN WIDTH. MUST BE > MAP_WIDTH
SCREEN_HEIGHT      = 60  #SETS OVERALL SCREEN HEIGHT. MUST BE > MAP_HEIGHT

#camera info
#size of the map portion shown on-screen
CAMERA_WIDTH = 80
CAMERA_HEIGHT = 40

MAP_WIDTH          = 100
MAP_HEIGHT         = 60
MAP_PAD_W          = CAMERA_WIDTH  / 2  #don't allow rooms to touch edges. ideally also don't get close enough to edge of map to stop the scrolling effect
MAP_PAD_H          = CAMERA_HEIGHT / 2


#room info
ROOM_MAX_SIZE      = 25
ROOM_MIN_SIZE      = 25
MAX_ROOMS          = ((MAP_WIDTH - CAMERA_WIDTH) + (MAP_HEIGHT - CAMERA_HEIGHT)) / 3
MAX_ROOMS = 2
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

#.............................................
#SQL DATA
ENTITY_DB          = 'entity_stats'
MESSAGE_DB         = 'game_log'
SQL_COMMIT_TICK_COUNT = 5

#.............................................
#EDITABLE ENTITIES GENERAL DATA
LEVEL_UP_BASE     = 2
LEVEL_UP_FACTOR   = 2
AUTOEQUIP         = True #ARE ITEMS AUTO-EQUIPPED ON PICKUP?
#ASCIIMODE         = True #use Object.char for graphics if True. use tilechar if False.
AUTOMODE          = False
#GRAPHICSMODE      = 'curses' #curses, libtcod (TODO: should roll in ASCIIMODE into this as libtcod-console and libtcod-ascii)
FREE_FOR_ALL_MODE = True  #if true, all monsters on diffent clans by default
PRINT_MESSAGES	  = True  #if true, print messages to log
TURNBASED         = True #not working yet
SPEED_DEFAULT     = 5  # speed delay. higher = slower. How many game ticks to wait between turns
REGEN_DEFAULT     = 100000  # regen delay. higher = slower. How many game ticks to wait between regeneration
REGEN_MULTIPLIER  = 0.00001 # % of life to regen 

KEYS_INITIAL_DELAY= 0
KEYS_INTERVAL     = 0
BUFF_DECAYRATE    = 1  #amount to reduce per tick
BUFF_DURATION     = 30 #in game ticks

#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#probably shouldn't edit these when the game is running
#ITEM INFO
MAX_NUM_ITEMS     = 26
INVENTORY_WIDTH   = 50
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx




#.............................................
#EDITABLE GENERAL DATA
CHARACTER_SCREEN_WIDTH = 30  #WIDTH USED IN MSGBOX DISPLAYING MESSAGES TO PLAYER
LEVEL_SCREEN_WIDTH     = 40  #WIDTH USED IN MSGBOX FOR LEVEL UP
LIMIT_FPS              = 20  #LIMITS FPS TO A REASONABLE AMOUNT
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#probably shouldn't edit these when the game is running
#GUI rendering
BAR_WIDTH         = 20
PANEL_HEIGHT      = SCREEN_HEIGHT - CAMERA_HEIGHT
PANEL_Y           = SCREEN_HEIGHT - PANEL_HEIGHT

#combat log
MSG_X             = BAR_WIDTH + 2
MSG_WIDTH         = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT        = PANEL_HEIGHT - 1

#graphics
MAIN_MENU_BKG     = 'menu_background.png'

#STATE STRINGS (change to enums one day?)
STATE_PLAYING     = 'playing'
STATE_NOACTION    = 'no_action'
STATE_DEAD        = 'dead'
STATE_EXIT        = 'exit'
STATE_USED        = 'used'
STATE_CANCELLED   = 'cancelled'
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx




#.............................................
#EDITABLE SPELL DATA
HEAL_AMOUNT = 50
LIGHTNING_DAMAGE = 25
LIGHTNING_RANGE = 5
FIREBALL_DAMAGE = 25
FIREBALL_RADIUS = 3
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx





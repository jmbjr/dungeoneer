import colors
import gamedata #TODO move gamedata stuff back into here.

class Datastuff(object):
    def __init__(self):
        self.col = colors.Colorstuff(gamedata.GRAPHICSMODE)
        self.col.init_colors()

        self.SHOW_PANEL         = False

        #DON'T EDIT DATA BETWEEN X's WHILE GAME IS RUNNING, UNLESS YOU WANT THE GAME TO CRASH
        #.............................................
        #EDITABLE MAP DATA
        self.WALL_CHAR          = 'X'
        self.GROUND_CHAR        = ' '

        self.COLOR_DARK_WALL    = self.col.DARK_GREY
        self.COLOR_LIGHT_WALL   = self.col.LIGHT_GREY
        self.COLOR_DARK_GROUND  = self.col.DARK_SEPIA
        self.COLOR_LIGHT_GROUND = self.col.SEPIA

        self.FOV_ALGO           = 2 #FOV ALGORITHM. values = 0 to 4
        self.FOV_LIGHT_WALLS    = True
        self.TORCH_RADIUS       = 80 #AFFECTS FOV RADIUS

        self.TILE_WALL          = 256  #first tile in the first row of tiles
        self.TILE_GROUND        = 256 + 1
        self.TILE_MAGE          = 256 + 32  #first tile in the 2nd row of tiles
        self.TILE_SKEL_WHITE    = 256 + 32 + 1  #2nd tile in the 2nd row of tiles
        self.TILE_SKEL_RED      = 256 + 32 + 2  #2nd tile in the 2nd row of tiles
        self.TILE_SKEL_BLUE     = 256 + 32 + 3  #2nd tile in the 2nd row of tiles
        self.TILE_SKEL_GREEN    = 256 + 32 + 4  #2nd tile in the 2nd row of tiles
        self.TILE_SKEL_ORANGE   = 256 + 32 + 5  #2nd tile in the 2nd row of tiles
        self.TILE_SKEL_MAGENTA  = 256 + 32 + 6  #2nd tile in the 2nd row of tiles
        self.TILE_SKEL_TEAL     = 256 + 32 + 7  #2nd tile in the 2nd row of tiles
        self.TILE_SKEL_YELLOW   = 256 + 32 + 8  #2nd tile in the 2nd row of tiles
        self.TILE_SKEL_PURPLE   = 256 + 32 + 9  #2nd tile in the 2nd row of tiles

        self.maplist =[]

        self.maplist.append('Intro')
        self.maplist.append('Brig')
        #maplist.append('Engineering')
        #maplist.append('Bridge')
        #maplist.append('Sick Bay')

        #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        #probably shouldn't edit these when the game is running
        self.SCREEN_WIDTH       = 80  #SETS OVERALL SCREEN WIDTH. MUST BE > MAP_WIDTH
        self.SCREEN_HEIGHT      = 60  #SETS OVERALL SCREEN HEIGHT. MUST BE > MAP_HEIGHT

        #camera info
        #size of the map portion shown on-screen
        self.CAMERA_WIDTH = 80
        self.CAMERA_HEIGHT = 40

        self.MAP_WIDTH          = 100
        self.MAP_HEIGHT         = 60
        self.MAP_PAD_W          = self.CAMERA_WIDTH  / 2  #don't allow rooms to touch edges. ideally also don't get close enough to edge of map to stop the scrolling effect
        self.MAP_PAD_H          = self.CAMERA_HEIGHT / 2


        #room info
        self.ROOM_MAX_SIZE      = 25
        self.ROOM_MIN_SIZE      = 25
        self.MAX_ROOMS          = ((self.MAP_WIDTH - self.CAMERA_WIDTH) + (self.MAP_HEIGHT - self.CAMERA_HEIGHT)) / 3
        self.MAX_ROOMS = 2
        #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        #.............................................
        #SQL DATA
        self.ENTITY_DB          = 'entity_stats'
        self.MESSAGE_DB         = 'game_log'
        self.SQL_COMMIT_TICK_COUNT = 5

        #.............................................
        #EDITABLE ENTITIES GENERAL DATA
        self.LEVEL_UP_BASE     = 2
        self.LEVEL_UP_FACTOR   = 2
        self.AUTOEQUIP         = True #ARE ITEMS AUTO-EQUIPPED ON PICKUP?
        #ASCIIMODE         = True #use Object.char for graphics if True. use tilechar if False.
        self.AUTOMODE          = False
        #GRAPHICSMODE      = 'curses' #curses, libtcod (TODO: should roll in ASCIIMODE into this as libtcod-console and libtcod-ascii)
        self.FREE_FOR_ALL_MODE = True  #if true, all monsters on diffent clans by default
        self.PRINT_MESSAGES	  = True  #if true, print messages to log
        self.TURNBASED         = True #not working yet
        self.SPEED_DEFAULT     = 5  # speed delay. higher = slower. How many game ticks to wait between turns
        self.REGEN_DEFAULT     = 100000  # regen delay. higher = slower. How many game ticks to wait between regeneration
        self.REGEN_MULTIPLIER  = 0.00001 # % of life to regen 

        self.KEYS_INITIAL_DELAY= 0
        self.KEYS_INTERVAL     = 0
        self.BUFF_DECAYRATE    = 1  #amount to reduce per tick
        self.BUFF_DURATION     = 30 #in game ticks

        #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        #probably shouldn't edit these when the game is running
        #ITEM INFO
        self.MAX_NUM_ITEMS     = 26
        self.INVENTORY_WIDTH   = 50
        #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx




        #.............................................
        #EDITABLE GENERAL DATA
        self.CHARACTER_SCREEN_WIDTH = 30  #WIDTH USED IN MSGBOX DISPLAYING MESSAGES TO PLAYER
        self.LEVEL_SCREEN_WIDTH     = 40  #WIDTH USED IN MSGBOX FOR LEVEL UP
        self.LIMIT_FPS              = 20  #LIMITS FPS TO A REASONABLE AMOUNT
        #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        #probably shouldn't edit these when the game is running
        #GUI rendering
        self.BAR_WIDTH         = 20
        self.PANEL_HEIGHT      = self.SCREEN_HEIGHT - self.CAMERA_HEIGHT
        self.PANEL_Y           = self.SCREEN_HEIGHT - self.PANEL_HEIGHT

        #combat log
        self.MSG_X             = self.BAR_WIDTH + 2
        self.MSG_WIDTH         = self.SCREEN_WIDTH - self.BAR_WIDTH - 2
        self.MSG_HEIGHT        = self.PANEL_HEIGHT - 1

        #graphics
        self.MAIN_MENU_BKG     = 'menu_background.png'
        self.MAIN_MENU_BKG_ASCII = 'menu_background'

        #STATE STRINGS (change to enums one day?)
        self.STATE_PLAYING     = 'playing'
        self.STATE_NOACTION    = 'no_action'
        self.STATE_DEAD        = 'dead'
        self.STATE_EXIT        = 'exit'
        self.STATE_USED        = 'used'
        self.STATE_CANCELLED   = 'cancelled'
        #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx




        #.............................................
        #EDITABLE SPELL DATA
        self.HEAL_AMOUNT = 50
        self.LIGHTNING_DAMAGE = 25
        self.LIGHTNING_RANGE = 5
        self.FIREBALL_DAMAGE = 25
        self.FIREBALL_RADIUS = 3
        self.CONFUSE_NUM_TURNS = 10
        self.CONFUSE_RANGE = 8
        #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx





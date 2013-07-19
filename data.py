import libtcodpy as libtcod

#DON'T EDIT DATA BETWEEN X's WHILE GAME IS RUNNING, UNLESS YOU WANT THE GAME TO CRASH

#.............................................
#EDITABLE MAP DATA
WALL_CHAR          = 'X'
GROUND_CHAR        = ' '

COLOR_DARK_WALL    = libtcod.Color(0, 0, 100)
COLOR_LIGHT_WALL   = libtcod.Color(130, 110, 50)
COLOR_DARK_GROUND  = libtcod.Color(50, 50, 150)
COLOR_LIGHT_GROUND = libtcod.Color(25, 25, 25)

FOV_ALGO           = 2 #FOV ALGORITHM. values = 0 to 4
FOV_LIGHT_WALLS    = True
TORCH_RADIUS       = 10 #AFFECTS FOV RADIUS
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#probably shouldn't edit these when the game is running
SCREEN_WIDTH       = 80  #SETS OVERALL SCREEN WIDTH. MUST BE > MAP_WIDTH
SCREEN_HEIGHT      = 50  #SETS OVERALL SCREEN HEIGHT. MUST BE > MAP_HEIGHT

MAP_WIDTH          = 80
MAP_HEIGHT         = 40

#room info
ROOM_MAX_SIZE      = 15
ROOM_MIN_SIZE      = 4
MAX_ROOMS          = 40
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx




#.............................................
#EDITABLE ENTITIES GENERAL DATA
LEVEL_UP_BASE     = 200
LEVEL_UP_FACTOR   = 150
AUTOEQUIP         = True #ARE ITEMS AUTO-EQUIPPED ON PICKUP?
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#probably shouldn't edit these when the game is running
#ITEM INFO
MAX_NUM_ITEMS     = 30
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
PANEL_HEIGHT      = SCREEN_HEIGHT - MAP_HEIGHT
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



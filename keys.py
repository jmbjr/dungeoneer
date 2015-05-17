import libtcod
import data
import gamedata
import cursesx
    
#key vars. TODO put this in a module or something
if gamedata.GRAPHICSMODE == 'libtcod':
    ESC  = libtcod.KEY_ESCAPE
    TAB  = libtcod.KEY_TAB
    UP   = libtcod.KEY_UP
    DOWN = libtcod.KEY_DOWN
    RIGHT= libtcod.KEY_RIGHT
    LEFT = libtcod.KEY_LEFT
    KP1  = libtcod.KEY_KP1
    KP2  = libtcod.KEY_KP2
    KP3  = libtcod.KEY_KP3    
    KP4  = libtcod.KEY_KP4
    KP5  = libtcod.KEY_KP5
    KP6  = libtcod.KEY_KP6
    KP7  = libtcod.KEY_KP7
    KP8  = libtcod.KEY_KP8
    KP9  = libtcod.KEY_KP9
    KPDEC= libtcod.KEY_KPDEC
    ENTER= libtcod.KEY_ENTER
    SPACE= libtcod.KEY_SPACE
elif gamedata.GRAPHICSMODE == 'curses':
    ESC  = 27
    TAB  = ord('\t')
    UP   = cursesx.KEY_UP
    DOWN = cursesx.KEY_DOWN
    RIGHT= cursesx.KEY_RIGHT
    LEFT = cursesx.KEY_LEFT
else:
    print('Error in key-set. wrong GRAPHICSMODE')

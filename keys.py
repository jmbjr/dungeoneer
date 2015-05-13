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
elif gamedata.GRAPHICSMODE == 'curses':
    ESC  = 27
    TAB  = ord('\t')
    UP   = cursesx.KEY_UP
    DOWN = cursesx.KEY_DOWN
    RIGHT= cursesx.KEY_RIGHT
    LEFT = cursesx.KEY_LEFT
else:
    print('Error in key-set. wrong GRAPHICSMODE')

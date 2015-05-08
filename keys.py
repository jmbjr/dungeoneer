import libtcodpy as libtcod
import data
import curses

#key vars. TODO put this in a module or something
if data.GRAPHICSMODE == 'libtcod':
    keys.ESC  = libtcod.KEY_ESCAPE
    keys.TAB  = libtcod.KEY_TAB
    keys.UP   = libtcod.KEY_UP
    keys.DOWN = libtcod.KEY_DOWN
    keys.RIGHT= libtcod.KEY_RIGHT
    keys.LEFT = libtcod.KEY_LEFT
elif data.GRAPHICSMODE == 'curses':
    keys.ESC  = 27
    keys.TAB  = ord('\t')
    keys.UP   = curses.KEY_UP
    keys.DOWN = curses.KEY_DOWN
    keys.RIGHT= curses.KEY_RIGHT
    keys.LEFT = curses.KEY_LEFT
else:
    print('Error in key-set. wrong GRAPHICSMODE')

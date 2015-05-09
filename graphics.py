import libtcodpy as libtcod
import curses

class Graphics(object):
    def __init__(self, graphicsmode):
        self.graphicsmode = graphicsmode
        
    def isgameover(self):
        if self.graphicsmode == 'libtcod': 
            return libtcod.console_is_window_closed()
        elif self.graphicsmode == 'curses':
            return False
        else:
            print('Error in graphics.isgameover. wrong GRAPHICSMODE')
            return False

import libtcodpy as libtcod
try:
    import curses
except ImportError:
    print 'curses not available'

#TODO replace with select case
#TODO specifically require con for things that need it. don't save it. could get messy. See the flush() for example.
class Guistuff(object):
    def __init__(self, graphicsmode):
        self.graphicsmode = graphicsmode
        
    def isgameover(self):
        if self.graphicsmode == 'libtcod': 
            return libtcod.console_is_window_closed()
        elif self.graphicsmode == 'curses':
            return False
        else:
            print('Error in guistuff.isgameover. wrong GRAPHICSMODE')
            return False

    def console(self, nwidth, nheight):
        if self.graphicsmode == 'libtcod':
            con = libtcod.console_new(nwidth, nheight)
        elif self.graphicsmode == 'curses':
            con = curses.newwin(nheight, nwidth)
        else:
            print('ERROR in guistuff.console. GRAPHICSMODE incorrect')
            return False
        return con

    def clear(self, con):
        if self.graphicsmode == 'libtcod':
            libtcod.console_clear(con)
        elif self.graphicsmode == 'curses':
            con.clear()
        else:
            print('ERROR in guistuff.sclear. GRAPHICSMODE incorrect')

    def printstr(self, con, xx, yy, entity, my_color):
        if self.graphicsmode == 'libtcod':
            libtcod.console_set_default_foreground(con, my_color)
            libtcod.console_print_ex(con, xx, yy, libtcod.BKGND_NONE, libtcod.LEFT, entity)
        elif self.graphicsmode == 'curses':
            try:
                con.addstr(yy, xx, entity, my_color)
            except curses.error:
                pass
        else:
            print('Error in guistuff.printstr. wrong GRAPHICSMODE')

    def prep_console(self, con, nwidth, nheight):
        if self.graphicsmode == 'libtcod':
            libtcod.console_set_custom_font('oryx_tiles3.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 12)
            libtcod.console_init_root(nwidth, nheight, 'johnstein\'s Game of RogueLife!', False, libtcod.RENDERER_SDL)
            libtcod.sys_set_fps(30)

            libtcod.console_map_ascii_codes_to_font(256   , 32, 0, 5)  #map all characters in 1st row
            libtcod.console_map_ascii_codes_to_font(256+32, 32, 0, 6)  #map all characters in 2nd row

            mouse = libtcod.Mouse()
            key = libtcod.Key()  
        elif self.graphicsmode == 'curses':
            con.nodelay(1)
            con.keypad(1)
            mouse = None
            key = None
        else:
            print('Error in guistuff.prep_console. wrong GRAPHICSMODE')
        return mouse,key

    def getkey(self, con, mouse, key):
        if self.graphicsmode == 'libtcod':
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
            thekey = key.vk
        elif self.graphicsmode == 'curses':
            thekey = con.getch()
        else:
            print('Error in guistuff.getkey. wrong GRAPHICSMODE')
        return thekey

    def flush(self,con, nwidth, nheight):
        if self.graphicsmode == 'libtcod':
            libtcod.console_blit(con, 0, 0, nwidth, nheight, 0, 0, 0)
            libtcod.console_flush()
        elif self.graphicsmode == 'curses':
            con.refresh()
        else:
            print('Error in guistuff.flush. wrong GRAPHICSMODE')


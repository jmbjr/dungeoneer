import libtcod
import cursesx

# alignment
LEFT=0
RIGHT=1
CENTER=2

#TODO replace with select case
#TODO specifically require con for things that need it. don't save it. could get messy. See the flush() for example.
class Keyobj(object):
    def __init__(self, keycode, charcode, keychar, pressed=False, lalt=False, lctrl=False, ralt=False, rctrl=False, shift=False):
        self.keycode = keycode
        self.charcode= charcode
        self.keychar = keychar
        self.pressed = pressed
        self.lalt    = lalt
        self.lctrl   = lctrl
        self.ralt    = ralt
        self.rctrl   = rctrl
        self.shift   = shift

class Guistuff(object):
    def __init__(self, graphicsmode):
        self.graphicsmode = graphicsmode
        
    def isgameover(self):
        if self.graphicsmode == 'libtcod': 
            return libtcod.console_is_window_closed()
        elif self.graphicsmode == 'curses':
            return False
        else:
            self.err_graphicsmode('isgameover')
            return False

    def console(self, nwidth, nheight):
        if self.graphicsmode == 'libtcod':
            con = libtcod.console_new(nwidth, nheight)
        elif self.graphicsmode == 'curses':
            con = cursesx.newwin(nheight, nwidth)
        else:
            self.err_graphicsmode('console')
            return False
        return con

    def clear(self, con):
        if self.graphicsmode == 'libtcod':
            libtcod.console_clear(con)
        elif self.graphicsmode == 'curses':
            con.clear()
        else:
            self.err_graphicsmode('clear')

    def draw_rect(self, con, xx, yy, nwidth, nheight, clear, bkg=libtcod.BKGND_SCREEN, bg_color=None):
        if self.graphicsmode == 'libtcod':
            #libtcod.console_rect only uses default background color
            if bg_color:
                libtcod.console_set_default_background(con, bg_color)

            libtcod.console_rect(con, xx, yy, nwidth, nheight, clear, bkg)

        elif self.graphicsmode == 'curses':
            try:
                print('curses!') #not sure how to do this yet
            except cursesx.error:
                pass
        else:
            self.err_graphicsmode('draw_rect')

#print_rect and print_str need to prompt for fg and bg Game.col... or maybe we should rethink how colors are set
    def print_rect(self, con, xx, yy, nwidth, nheight, bkg=libtcod.BKGND_NONE, align=libtcod.LEFT, val='', fg_color=None, bg_color=None):
        if self.graphicsmode == 'libtcod':
            if fg_color:
                libtcod.console_set_default_foreground(con, fg_color)
            if bg_color:
                libtcod.console_set_default_background(con, bg_color)

            libtcod.console_print_rect_ex(con, xx, yy, nwidth, nheight, bkg, align, val)
        elif self.graphicsmode == 'curses':
            try:
                print('curses!') #not sure how to do this yet
            except cursesx.error:
                pass
        else:
            self.err_graphicsmode('print_rect')

    def print_str(self, con, xx, yy, bkg=libtcod.BKGND_NONE, align=libtcod.LEFT, val='', fg_color=None, bg_color=None):
        if self.graphicsmode == 'libtcod':
            if fg_color:
                libtcod.console_set_default_foreground(con, fg_color)
            if bg_color:
                libtcod.console_set_default_background(con, bg_color)

            libtcod.console_print_ex(con, xx, yy, bkg, align, val)
        elif self.graphicsmode == 'curses':
            try:
                con.addstr(yy, xx, val, fg_color)
            except cursesx.error:
                pass
        else:
            self.err_graphicsmode('print_str')

#this does colors differently than print_str... this vexes me and probably means I should refactor how this works....
#TODO: remove defaults to None. this screws things up. removing the None will require re-ordering the parameters
    def print_char(self, con, xx, yy, bkg=libtcod.BKGND_NONE, align=libtcod.LEFT, val='', fg_color=None, bg_color=None):         
        if self.graphicsmode == 'libtcod':
            libtcod.console_put_char_ex(con, xx, yy, val, fg_color, bg_color)                

        elif self.graphicsmode == 'curses':
            try:
                con.addstr(yy, xx, val, fg_color)
            except cursesx.error:
                pass
        else:
            self.err_graphicsmode('print_char')

    def get_height_rect(self, con, xx, yy, nwidth, nheight, val):
        if self.graphicsmode == 'libtcod':
            return libtcod.console_get_height_rect(con, xx, yy, nwidth, nheight, val)
        elif self.graphicsmode == 'curses':
            try:
                return 0 #not sure what equiv here is
            except cursesx.error:
                pass
        else:
            self.err_graphicsmode('get_height_rect')


    def prep_keyboard(self, delay, interval): #can this be combined with prep_console?
        if self.graphicsmode == 'libtcod':
            libtcod.console_set_keyboard_repeat(delay, interval)
        elif self.graphicsmode == 'curses':
            print('curses keyboard!')
        else:
            self.err_graphicsmode('prep_keyboard')      

    def prep_console(self, con, nwidth, nheight):
        if self.graphicsmode == 'libtcod':
            libtcod.console_set_custom_font('oryx_tiles3.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 12)
            libtcod.console_init_root(nwidth, nheight, 'johnstein\'s Game of RogueLife!', False, libtcod.RENDERER_SDL)
            libtcod.sys_set_fps(30)
            rootcon = 0

            libtcod.console_map_ascii_codes_to_font(256   , 32, 0, 5)  #map all characters in 1st row
            libtcod.console_map_ascii_codes_to_font(256+32, 32, 0, 6)  #map all characters in 2nd row

            mouse = libtcod.Mouse()
            key = libtcod.Key()  
        elif self.graphicsmode == 'curses':
            con.nodelay(1)
            con.keypad(1)
            mouse = None
            key = None
            rootcon = con
        else:
            self.err_graphicsmode('prep_console')
        return mouse,key,rootcon

    def getkey(self, con, mouse, key, wait=False):
        if self.graphicsmode == 'libtcod':
            if wait:
                print('waiting for key')
                key = libtcod.console_wait_for_keypress(True)
            else:
                libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
            thekey = Keyobj(key.vk, key.c, chr(key.c), key.pressed, key.lalt, key.lctrl, key.ralt, key.rctrl, key.shift)
        elif self.graphicsmode == 'curses':
            key = con.getch()
            if key>256 or key<0:
                keychar=''
            else:
                keychar=chr(key)

            thekey = Keyobj(key, key, keychar, False, False, False, False, False, False)
        else:
            self.err_graphicsmode('getkey')
        return thekey

    def flush(self,con):
        if self.graphicsmode == 'libtcod':
            libtcod.console_flush()
        elif self.graphicsmode == 'curses':
            con.refresh()
        else:
            self.err_graphicsmode('flush')

    def con_blit(self, con, xx, yy, nwidth, nheight, dest, dest_xx, dest_yy, ffade=1.0, bfade=1.0): 
        if self.graphicsmode == 'libtcod':
            libtcod.console_blit(con, xx, yy, nwidth, nheight, dest, dest_xx, dest_yy, ffade, bfade)
        elif self.graphicsmode == 'curses':
            print('curses!') #not sure what the equiv is yet
        else:
            self.err_graphicsmode('con_blit')
            
    def img_blit2x(self, img, con, xx, yy):
        if self.graphicsmode == 'libtcod':
            libtcod.image_blit_2x(img, con, xx, yy)
        elif self.graphicsmode == 'curses':
            print(img) #not sure what the equiv is yet
        else:
            self.err_graphicsmode('img_blit2x')

    def load_image(self, img, img_ascii):
        if self.graphicsmode == 'libtcod':
            return libtcod.image_load(img)
        elif self.graphicsmode == 'curses':
            return img_ascii #not sure what the equiv is yet
        else:
            self.err_graphicsmode('load_image')

    def toggle_fullscreen(self):
        if self.graphicsmode == 'libtcod':
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        elif self.graphicsmode == 'curses':
            return True #not sure what the equiv is yet
        else:
            self.err_graphicsmode('toggle_fullscreen')

#TODO: generalize this by using it in other routines.
    def set_default_color(self, con, fg_color=None, bg_color=None):
        if self.graphicsmode == 'libtcod':
            if fg_color is not None:
                libtcod.console_set_default_foreground(con, fg_color)
            if bg_color is not None:
                libtcod.console_set_default_background(con, bg_color)
        elif self.graphicsmode == 'curses':
            return True #not sure what the equiv is yet
        else:
            self.err_graphicsmode('set_default_color')

    def err_graphicsmode(self, func):
        print('Error in guistuff.' + func + '. wrong GRAPHICSMODE: ' + self.graphicsmode)

import libtcod
import cursesx

class Colorstuff(object):
    def __init__(self, graphicsmode):
        self.graphicsmode = graphicsmode

    def init_colors(self):
        if self.graphicsmode == 'libtcod':
            self.BLACK   = libtcod.black
            self.RED     = libtcod.red
            self.GREEN   = libtcod.green
            self.YELLOW  = libtcod.yellow
            self.BLUE    = libtcod.blue
            self.MAGENTA = libtcod.magenta
            self.CYAN    = libtcod.cyan
            self.WHITE   = libtcod.white

            self.DARK_GREY     = libtcod.dark_grey
            self.LIGHT_RED     = libtcod.light_red
            self.LIGHT_GREEN   = libtcod.light_green
            self.LIGHT_YELLOW  = libtcod.light_yellow
            self.LIGHT_BLUE    = libtcod.light_blue
            self.LIGHT_MAGENTA = libtcod.light_magenta
            self.LIGHT_CYAN    = libtcod.light_cyan
            self.LIGHT_GREY    = libtcod.light_grey

            self.DARK_SEPIA    = libtcod.dark_sepia
            self.SEPIA         = libtcod.sepia

        elif self.graphicsmode == 'curses':
            for col in range(0,8):
                cursesx.init_pair(col, col, cursesx.COLOR_BLACK)

            self.BLACK   = cursesx.color_pair(0)
            self.RED     = cursesx.color_pair(1)
            self.GREEN   = cursesx.color_pair(2)
            self.YELLOW  = cursesx.color_pair(3)
            self.BLUE    = cursesx.color_pair(4)
            self.MAGENTA = cursesx.color_pair(5)
            self.CYAN    = cursesx.color_pair(6)
            self.WHITE   = cursesx.color_pair(7)

            self.DARK_GREY     = cursesx.color_pair(0) | cursesx.A_BOLD
            self.LIGHT_RED     = cursesx.color_pair(1) | cursesx.A_BOLD
            self.LIGHT_GREEN   = cursesx.color_pair(2) | cursesx.A_BOLD
            self.LIGHT_YELLOW  = cursesx.color_pair(3) | cursesx.A_BOLD
            self.LIGHT_BLUE    = cursesx.color_pair(4) | cursesx.A_BOLD
            self.LIGHT_MAGENTA = cursesx.color_pair(5) | cursesx.A_BOLD
            self.LIGHT_CYAN    = cursesx.color_pair(6) | cursesx.A_BOLD
            self.LIGHT_GREY    = cursesx.color_pair(7) | cursesx.A_BOLD

            self.DARK_SEPIA    = MAGENTA
            self.SEPIA         = LIGHT_YELLOW
        else:
            print('Error in Game.col. wrong GRAPHICSMODE')
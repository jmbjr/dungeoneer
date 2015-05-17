import libtcod
import data
import gamedata
import cursesx

if gamedata.GRAPHICSMODE == 'libtcod':
    BLACK   = libtcod.black
    RED     = libtcod.red
    GREEN   = libtcod.green
    YELLOW  = libtcod.yellow
    BLUE    = libtcod.blue
    MAGENTA = libtcod.magenta
    CYAN    = libtcod.cyan
    WHITE   = libtcod.white

    DARK_GREY     = libtcod.dark_grey
    LIGHT_RED     = libtcod.light_red
    LIGHT_GREEN   = libtcod.light_green
    LIGHT_YELLOW  = libtcod.light_yellow
    LIGHT_BLUE    = libtcod.light_blue
    LIGHT_MAGENTA = libtcod.light_magenta
    LIGHT_CYAN    = libtcod.light_cyan
    LIGHT_GREY    = libtcod.light_grey

    DARK_SEPIA    = libtcod.dark_sepia
    SEPIA         = libtcod.sepia

elif gamedata.GRAPHICSMODE == 'curses':
    for col in range(0,8):
        cursesx.init_pair(col, col, cursesx.COLOR_BLACK)

    BLACK   = cursesx.color_pair(0)
    RED     = cursesx.color_pair(1)
    GREEN   = cursesx.color_pair(2)
    YELLOW  = cursesx.color_pair(3)
    BLUE    = cursesx.color_pair(4)
    MAGENTA = cursesx.color_pair(5)
    CYAN    = cursesx.color_pair(6)
    WHITE   = cursesx.color_pair(7)

    DARK_GREY     = cursesx.color_pair(0) | cursesx.A_BOLD
    LIGHT_RED     = cursesx.color_pair(1) | cursesx.A_BOLD
    LIGHT_GREEN   = cursesx.color_pair(2) | cursesx.A_BOLD
    LIGHT_YELLOW  = cursesx.color_pair(3) | cursesx.A_BOLD
    LIGHT_BLUE    = cursesx.color_pair(4) | cursesx.A_BOLD
    LIGHT_MAGENTA = cursesx.color_pair(5) | cursesx.A_BOLD
    LIGHT_CYAN    = cursesx.color_pair(6) | cursesx.A_BOLD
    LIGHT_GREY    = cursesx.color_pair(7) | cursesx.A_BOLD

    DARK_SEPIA    = MAGENTA
    SEPIA         = LIGHT_YELLOW
else:
    print('Error in colors. wrong GRAPHICSMODE')
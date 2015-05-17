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

elif gamedata.GRAPHICSMODE == 'curses':
    for col in range(0,8):
        cursesx.init_pair(col, col, cursesx.COLOR_BLACK)

    BLACK   = cursesx.color_pair(0)
    RED     = libtcod.color_pair(1)
    GREEN   = libtcod.color_pair(2)
    YELLOW  = libtcod.color_pair(3)
    BLUE    = libtcod.color_pair(4)
    MAGENTA = libtcod.color_pair(5)
    CYAN    = libtcod.color_pair(6)
    WHITE   = libtcod.color_pair(7)

    DARK_GREY     = libtcod.color_pair(0) | cursesx.A_BOLD
    LIGHT_RED     = libtcod.color_pair(1) | cursesx.A_BOLD
    LIGHT_GREEN   = libtcod.color_pair(2) | cursesx.A_BOLD
    LIGHT_YELLOW  = libtcod.color_pair(3) | cursesx.A_BOLD
    LIGHT_BLUE    = libtcod.color_pair(4) | cursesx.A_BOLD
    LIGHT_MAGENTA = libtcod.color_pair(5) | cursesx.A_BOLD
    LIGHT_CYAN    = libtcod.color_pair(6) | cursesx.A_BOLD
    LIGHT_GREY    = libtcod.color_pair(7) | cursesx.A_BOLD
else:
    print('Error in colors. wrong GRAPHICSMODE')
import textwrap
from constants import *

global game_msgs
game_msgs = []

def message(new_msg, color = libtcod.white):
    #split message if necessary
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the txt and the color
        game_msgs.append((line, color))
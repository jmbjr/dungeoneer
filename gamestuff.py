import libtcodpy as libtcod
import math
from constants import *
from ui import *

#if it needs more than libtcod or basic python modules, it probably shouldn't go in here
#also, best not to pass Game to any of these. Use a different module
class Rect(object):
    #a rectangle on the map. used to characterize a room
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2)/2
        center_y = (self.y1 + self.y2)/2
        return (center_x, center_y)

    def intersect(self, other):
        #returns True if this rect intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Tile(object):
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #all tiles start out unexplored
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

def flip_coin():
    return (libtcod.random_get_int(0,0,1))

def random_choice(chances_dict):
    #choose one option from dict of chances and return key
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]

def random_choice_index(chances): #choose one option from list of chances. return index
    #the dice will land on some number between 1 and sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds with this choice
        if dice <= running_sum:
            return choice
        choice +=1

def get_distance(dx, dy):
    return math.sqrt(dx ** 2 + dy ** 2)

def roll_dice(dicelist):
    dice=[]
    #print dicelist
    for [die_low, die_high] in dicelist:
        roll = libtcod.random_get_int(0,die_low,die_high)
        dice.append(roll)

    return [sum(dice), dice]

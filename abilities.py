import libtcodpy as libtcod
from constants import *
from world import *
from ui import *
from gamestuff import *


def cast_confusion(Game):
    ##find nearest enemy and confuse it
    #monster = closest_monster(CONFUSE_RANGE)
    #if monster is None:
    #    message ('No enemy is close enough to confuse', libtcod.red)
    #    return 'cancelled'

    #ask player for target to confuse
    message('Left-click an enemy to confuse. Right-click or ESC to cancel', Game, libtcod.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None:
        return 'cancelled'

    #replace monster's AI with confuse
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster #tell the new component who owns it
    message('The ' + monster.name + ' is confused!', Game, libtcod.light_green)

def cast_fireball(Game):
    #ask the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball. Right-Click or ESC to cancel', Game, libtcod.light_cyan)
    (x,y) = target_tile(Game)
    if x is None: 
        return 'cancelled'
    else:
        message('The fireball explodes', Game, libtcod.orange)

    theDmg = roll_dice([[FIREBALL_DAMAGE/2, FIREBALL_DAMAGE*2]])[0]
    for obj in Game.objects: #damage all fighters within range
        if obj.distance(x,y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' is burned for '+ str(theDmg) + ' HP', Game, libtcod.orange)
            obj.fighter.take_damage(theDmg)

def cast_heal(Game):
    #heal the player
    if Game.player.fighter.hp == Game.player.fighter.max_hp(Game):
        message('You are already at full health.', Game, libtcod.red)
        return 'cancelled'

    message('You feel better', Game, libtcod.light_violet)
    Game.player.fighter.heal(HEAL_AMOUNT)

def cast_lightning(Game):
    #find nearest enemy (within range) and damage it
    monster = closest_monster(LIGHTNING_RANGE, Game)
    if monster is None:
        message('No enemy is close enough to strike', Game, libtcod.red)
        return 'cancelled'

    theDmg = roll_dice([[LIGHTNING_DAMAGE/2, LIGHTNING_DAMAGE]])[0]

    message('A lightning bolt strikes the ' + monster.name + '! \n DMG = ' + str(theDmg) + ' HP.', Game, libtcod.light_blue)
    monster.fighter.take_damage(theDmg, Game)
from ui import *
from gamestuff import *
from constants import *
import math
from world import *

class Fighter(object):
    #combat-related properties and methods (monster, Game.player, NPC, etc)
    def __init__(self, hp, defense, power, xp, death_function=None):
        self.base_max_hp = hp
        self.hp = hp
        self.xp = xp
        self.base_defense = defense
        self.base_power = power
        self.death_function=death_function

    #@property
    def power(self, Game):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner, Game))
        return self.base_power + bonus

    #@property
    def defense(self, Game):
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner, Game))
        return self.base_defense + bonus

    #@property
    def max_hp(self, Game):
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner, Game))
        return self.base_max_hp + bonus

    def heal(self, amount):
        #heal by the given amount
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def take_damage(self, damage, Game):
        #inflict dmg if possible
        if damage > 0:
            self.hp -= damage

        #check for death and call death_function (if set)
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)
            if self.owner != Game.player: #yield experience to the Game.player
                Game.player.fighter.xp += self.xp

    def attack(self, target, Game):
        #very simple formula for attack damage
        damage = self.power(Game) - target.fighter.defense(Game)

        if damage > 0:
            #make target take some damage
            message (self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' +str(damage) + ' HP.', Game, libtcod.yellow)
            target.fighter.take_damage(damage, Game)
        else:
            message (self.owner.name.capitalize() + ' attacks ' + target.name + ' but there is no effect.', Game, libtcod.white)

class BasicMonster(object):
    #AI for basic monster
    def take_turn(self, Game):
        #basic monsters can see you if you can see them
        monster = self.owner
        if libtcod.map_is_in_fov(Game.fov_map, monster.x, monster.y):
            #move towards Game.player if far enough away
            if flip_coin() and flip_coin() and flip_coin():
                 message ('The ' + self.owner.name + ' clears its throat!', Game, monster.color)
            if monster.distance_to(Game.player) >= 2:
                monster.move_towards(Game.player.x, Game.player.y, Game)

                #close enough to attack (if the Game.player is alive)
            elif Game.player.fighter.hp > 0:
                monster.fighter.attack(Game.player, Game)

class Object(object):
    #this is a generic object: Game.player, monster, item, stairs
    #always represented by a character on the screen
    def __init__(self, x, y, char, name, color, blocks = False, always_visible = False, fighter = None, ai = None, item = None, equipment = None):
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.always_visible = always_visible

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.item = item
        if self.item: 
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self

            #there must be an Item component for the equipment component to work properly
            self.item = Item()
            self.item.owner = self

    def move(self, dx, dy, Game):
        if not is_blocked(self.x + dx, self.y + dy, Game):
        #if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy
            return True
        else:
            return False

    def draw(self, Game):
        #only draw if in field of view of Game.player or it's set to always visible and on explored tile
        if (libtcod.map_is_in_fov(Game.fov_map, self.x, self.y) or (self.always_visible and Game.map[self.x][self.y].explored)):
            #set the color then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(Game.con, self.color)
            libtcod.console_put_char(Game.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self, Game):
        #erase char that represents this object
        if libtcod.map_is_in_fov(Game.fov_map, self.x, self.y):
            libtcod.console_put_char_ex(Game.con, self.x, self.y, GROUND_CHAR, libtcod.white, COLOR_LIGHT_GROUND)

    def move_towards(self, target_x, target_y, Game):
        #vector from this object to the target, and distance
        dx1 = target_x - self.x
        dy1 = target_y - self.y
        #print str(target_x) + '/' + str(target_y) + '::' + str(self.x) + '/' + str(self.y)
        distance = get_distance(dx1, dy1)
        
        #normalize vector and round accordingly and convert to int
        dx = int(round(dx1 / distance))
        dy = int(round(dy1 / distance))

        #print str(dx) + '/' + str(dx1) + ', ' + str(dy) + '/' + str(dy) + ', ' + str(distance)
        if not self.move(dx, dy, Game):
        #if monster didn't move. Try diagonal
            if dx1 != 0:
                dx = abs(dx1) / dx1
            elif target_x < self.x:
                dx = -1
            else:
                dx = 1

            if dy != 0:
                dy = abs(dy1) / dy1
            elif target_y < self.y:
                dy = -1
            else:
                dy = 1
            #print 'trying diagonal:' +str(dx) + ', ' + str(dy) + ', ' + str(distance)
            self.move(dx, dy, Game)

    def distance_to(self, other):
        #return distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return get_distance(dx, dy)

    def distance(self, x, y):
        #return distance to some coord
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self, Game):
        #make this object be drawn first, so all others appear above it if they are in the same tile
        Game.objects.remove(self)
        Game.objects.insert(0, self)

class Item(object):
    def __init__(self, use_function=None):
        self.use_function = use_function

    def use(self, Game):
        #special case: if the object has the equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip(Game)
            return

        #call the 'use_function' if defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.', Game)
            return 'no_action'
        else:
            if self.use_function(Game) != 'cancelled':
                Game.inventory.remove(self.owner) #destror after use, unless cancelled
                return 'used'
            else:
                return 'no_action'

    #an item that can be picked up and used
    def pick_up(self, Game):
        #add to the Game.player's Game.inventory and remove from the map
        if len(Game.inventory) >= 26:
            message('Your Game.inventory is full! Cannot pick up ' + self.owner.name +'.', Game, libtcod.dark_red)
            return 'no_action'
        else:
            Game.inventory.append(self.owner)
            Game.objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', Game, libtcod.green)
            return 'picked_up'

        #special case: auto equip if the slot is unused
        equipment = self.owner.equipment
        if equipment and get_equipped_in_slot(equipment.slot) is None and AUTOEQUIP:
            equipment.equip(Game)

    def drop(self, Game):
        #add to the map and remove from the Game.player's Game.inventory. also, place it at the Game.player's coordinates
        Game.objects.append(self.owner)
        Game.inventory.remove(self.owner)
        self.owner.x = Game.player.x
        self.owner.y = Game.player.y
        message('You dropped a ' + self.owner.name + '.', Game, libtcod.yellow)

        #special case: if the object has the equip component, dequip before dropping it
        if self.owner.equipment:
            self.owner.equipment.dequip(Game)

class Equipment(object):
    #an object that can be equipped, yielding bonuses. automatically adds the Item component
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.is_equipped = False

    def toggle_equip(self, Game): #toggle equip/dequip status
        if self.is_equipped:
            self.dequip(Game)
        else:
            self.equip(Game)

    def equip(self, Game):
        #if the slot is already being used, dequip whatever is there
        old_equipment = get_equipped_in_slot(self.slot, Game)
        if old_equipment is not None:
            old_equipment.dequip(Game)

        #equip object and show a message about it
        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', Game, libtcod.light_green)

    def dequip(self, Game):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        message('Unequipped ' + self.owner.name + ' from ' + self.slot + '.', Game, libtcod.light_green)          

class ConfusedMonster(object):
    def __init__(self, old_ai, num_turns = CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    #AI for confused monster
    def take_turn(self, Game):
        if self.num_turns > 0: #still confused
            #move in random direction
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1

        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused', Game, libtcod.red) 


#standard imports
import libtcodpy as libtcod
from gamestuff import *
import data


#Classes:  Object player, enemies, items, etc
class Object(object):
    #this is a generic object: Game.player, monster, item, stairs
    #always represented by a character on the screen
    def __init__(self, x=0, y=0, char='?', name=None, color=libtcod.white, tilechar = None, blocks = False, always_visible = False, fighter = None, caster = None, ai = None, item = None, equipment = None):
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.always_visible = always_visible

        self.tilechar = tilechar
        if self.tilechar is None:
            self.tilechar = self.char

        self.fighter = fighter
        if self.fighter:
            if type(fighter) is dict:
                self.fighter = Fighter(**fighter)
            self.fighter.owner = self

        self.caster = caster
        if self.caster:
            if type(caster) is dict:
                self.caster = Caster(**caster)
            self.caster.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self            

        self.item = item
        if self.item: 
            if type(item) is dict:
                self.item = Item(**item)
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:
            if type(equipment) is dict:
                self.equipment = Equipment(**equipment)
            self.equipment.owner = self

            #there must be an Item component for the equipment component to work properly
            self.item = Item()
            self.item.owner = self

    def set_location(self, x, y, Game):
        if not is_blocked(x, y, Game):
            self.x = x
            self.y = y
            return True
        else:
            return False

    def move(self, dx, dy, Game):
        if not is_blocked(self.x + dx, self.y + dy, Game):
        #if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy
            return True
        else:
            return False

    def move_random(self, Game):
        self.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1), Game)


    def draw(self, Game):
        #only draw if in field of view of Game.player or it's set to always visible and on explored tile
        if (libtcod.map_is_in_fov(Game.fov_map, self.x, self.y) or (self.always_visible and Game.map[self.x][self.y].explored)):
            (x, y) = to_camera_coordinates(self.x, self.y, Game)

            if x is not None:
                #set the color then draw the character that represents this object at its position
                libtcod.console_set_default_foreground(Game.con, self.color)
                if data.ASCIIMODE:
                    thechar = self.char
                else:
                    thechar = self.tilechar

                libtcod.console_put_char(Game.con, x, y, thechar, libtcod.BKGND_NONE)

    def clear(self, Game):
        #erase char that represents this object
        (x, y) = to_camera_coordinates(self.x, self.y, Game)
        if x is not None and libtcod.map_is_in_fov(Game.fov_map, self.x, self.y):
            libtcod.console_put_char_ex(Game.con, x, y, data.GROUND_CHAR, libtcod.white, data.COLOR_LIGHT_GROUND)

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
        return get_distance(x - self.x, y - self.y)

    def send_to_back(self, Game):
        #make this object be drawn first, so all others appear above it if they are in the same tile
        Game.objects.remove(self)
        Game.objects.insert(0, self)


#fighters, spells, abilities
class Fighter(object):
    #combat-related properties and methods (monster, Game.player, NPC, etc)
    def __init__(self, hp, defense, power, xp, speed = data.SPEED_DEFAULT, regen = data.REGEN_DEFAULT, death_function=None, buffs = None, inventory = None):
        self.base_max_hp = hp
        self.hp = hp
        self.xp = xp
        self.base_defense = defense
        self.base_power = power
        self.death_function=death_function
        self.base_speed = speed
        self.speed_counter = 0
        self.base_regen = regen
        self.regen_counter = regen

        self.inventory = inventory
        if self.inventory:
            self.inventory.owner = self

        self.buffs = buffs
        if self.buffs:
            self.buffs.owner = self

    def add_item(self, item):
        if not self.inventory:
            self.inventory = []

        self.inventory.append(item)

    def remove_item(self, item):
        self.inventory.remove(item)

    def add_buff(self, buff):
        if not self.buffs:
            self.buffs = []

        self.buffs.append(buff)

    def remove_buff(self, buff):
        self.buffs.remove(buff)

    def regen(self, Game):
        bonus = sum(equipment.regen_bonus for equipment in get_all_equipped(self.owner, Game))
        if self.buffs:
            bonus += sum(buff.regen_bonus for buff in self.buffs)
        return self.base_regen + bonus

    def speed(self, Game):
        bonus = sum(equipment.speed_bonus for equipment in get_all_equipped(self.owner, Game))
        if self.buffs:
            bonus += sum(buff.speed_bonus for buff in self.buffs)
        return self.base_speed + bonus

    #@property
    def power(self, Game):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner, Game))
        if self.buffs:
            bonus += sum(buff.power_bonus for buff in self.buffs)
        return self.base_power + bonus

    #@property
    def defense(self, Game):
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner, Game))
        if self.buffs:
            bonus += sum(buff.defense_bonus for buff in self.buffs)
        return self.base_defense + bonus

    #@property
    def max_hp(self, Game):
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner, Game))
        if self.buffs:
            bonus += sum(buff.max_hp_bonus for buff in self.buffs)
        return self.base_max_hp + bonus

    def heal(self, amount, Game):
        #heal by the given amount
        self.hp += amount
        if self.hp > self.max_hp(Game):
            self.hp = self.max_hp(Game)

    def take_damage(self, damage, Game):
        #inflict dmg if possible
        if damage > 0:
            self.hp -= damage

        #check for death and call death_function (if set)
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner, Game)
            if self.owner != Game.player: #yield experience to the Game.player
                Game.player.fighter.xp += self.xp

    def attack(self, target, Game):
        #very simple formula for attack damage
        damage = self.power(Game) - target.fighter.defense(Game)

        if damage > 0:
            #make target take some damage
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' +str(damage) + ' HP.', Game, libtcod.yellow)
            target.fighter.take_damage(damage, Game)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but there is no effect.', Game, libtcod.white)

class Buff(object):
    def __init__(self, name, power_bonus=0, defense_bonus=0, max_hp_bonus=0, speed_bonus=0, regen_bonus=0, decay_rate=data.BUFF_DECAYRATE, duration=data.BUFF_DURATION):
        self.name = name
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.speed_bonus = speed_bonus
        self.regen_bonus = regen_bonus

        self.decay_rate = decay_rate #if 0, buff does not decay. use positive numbers to make buffs decrement
        self.duration = duration

class Caster(object):
    def __init__(self, mp, spells=None):
        self.base_max_mp = mp
        self.mp = mp

        self.spells = spells
        if self.spells:
            self.spells.owner = self

    def learn_spell(self, spell):
        if not self.spells:
            self.spells = []

        self.spells.append(spell)

    def forget_spell(self, spell):
        self.spells.remove(spell)

class Spell(object):
    def __init__(self, name, use_function=None):
        self.name = name
        self.use_function = use_function

    def use(self, Game):
        if self.use_function is None:
            message('This spell sucks! Abracadabra!', Game)
            return 'no_action'


#Items and Equipment

class Item(object):
    def __init__(self, use_function=None):
        self.use_function = use_function

    def use(self, Game, user):
        #special case: if the object has the equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip(Game)
            return

        #call the 'use_function' if defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.', Game)
            return data.STATE_NOACTION
        else:
            if self.use_function(Game, user) != 'cancelled':
                #need to remove it from the user's inventory if the user is still alive
                if user.fighter:
                    user.fighter.remove_item(self.owner)

                Game.fov_recompute = True
                return data.STATE_USED
            else:
                return data.STATE_NOACTION

    #an item that can be picked up and used
    def pick_up(self, Game, user):
        #add to the player's inventory and remove from the map
        if len(Game.player.fighter.inventory) >= 26:
            message('Your inventory is full! Cannot pick up ' + self.owner.name +'.', Game, libtcod.dark_red)
            retval = data.STATE_NOACTION
        else:
            user.fighter.add_item(self.owner)
            Game.objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', Game, libtcod.green)

            #special case: auto equip if the slot is unused
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot, Game) is None and data.AUTOEQUIP:
                equipment.equip(Game)

            retval = data.STATE_PLAYING

        return retval

    def drop(self, Game):
        #add to the map and remove from the player's inventory. also, place it at the Game.player's coordinates
        Game.objects.append(self.owner)
        Game.player.fighter.remove_item(self.owner)
        self.owner.x = Game.player.x
        self.owner.y = Game.player.y
        message('You dropped a ' + self.owner.name + '.', Game, libtcod.yellow)

        #special case: if the object has the equip component, dequip before dropping it
        if self.owner.equipment:
            self.owner.equipment.dequip(Game)

class Equipment(object):
    #an object that can be equipped, yielding bonuses. automatically adds the Item component
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0, speed_bonus=0, regen_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.is_equipped = False
        self.speed_bonus = speed_bonus
        self.regen_bonus = regen_bonus

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


#AI
class ConfusedMonster(object):
    def __init__(self, old_ai, num_turns = data.CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    #AI for confused monster
    def take_turn(self, Game):
        if self.num_turns > 0: #still confused
            #move in random direction
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1), Game)
            self.num_turns -= 1

        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused', Game, libtcod.red)

        if self.owner.fighter:
            return True
        else:
            return False

class BasicMonster(object):
    #AI must return True or False to indicate if still alive
    #AI for basic monster
    def take_turn(self, Game):
        #basic monsters can see you if you can see them
        useditem = None
        picked_up_items = False

        monster = self.owner
        if libtcod.map_is_in_fov(Game.fov_map, monster.x, monster.y):
            #move or use item
            #for now, use items or lose them
            if monster.fighter.inventory:
                #get random item from inv
                index = libtcod.random_get_int(0, 0, len(monster.fighter.inventory)-1)
                item = monster.fighter.inventory[index].item
                #item = monster.fighter.inventory[0].item
                useditem = item.use(Game, user=monster)
                print useditem + ': ' + monster.name + ' used ' + item.owner.name

            #if monster didn't use item, then move
            if useditem is not data.STATE_USED:
                #move towards Game.player if far enough away
                if flip_coin() and flip_coin() and flip_coin():
                     message('The ' + self.owner.name + ' clears its throat!', Game, monster.color)
                if monster.distance_to(Game.player) >= 2:
                    monster.move_towards(Game.player.x, Game.player.y, Game)

                    #close enough to attack (if the Game.player is alive)
                elif Game.player.fighter.hp > 0:
                    monster.fighter.attack(Game.player, Game)
        else: #wander
            #check if there's an item under the monster's feet
            for obj in Game.objects: #look for items in the user's title
                if obj.x == monster.x and obj.y == monster.y and obj.item:
                    picked_up_item = True
                    obj.item.pick_up(Game, monster)
                    print monster.name + ' has picked up ' + obj.item.owner.name
                    break

            #if monster picked up objects, don't move
            if not picked_up_items:
                monster.move_random(Game)

        #check if monster is still alive
        if monster.fighter:
            return True
        else:
            return False

#spells/abilities functions
def use_red_crystal(Game, user):
    if user is Game.player:
        message('You become ENRAGED!', Game, libtcod.red)
    else:
        message('The ' + user.name + ' beomes ENRAGED!', Game, libtcod.red)

    buff_component = Buff('Super Strength', power_bonus=10)
    user.fighter.add_buff(buff_component)

def use_blue_crystal(Game, user):
    if user is Game.player:
        message('You feel well-protected!', Game, libtcod.sky)
    else:
        message('The ' + user.name + ' looks well protected!', Game, libtcod.red)

    buff_component = Buff('Super Defense', defense_bonus=10)
    user.fighter.add_buff(buff_component)

def use_green_crystal(Game, user):
    if user is Game.player:
        message('You feel more resilient!', Game, libtcod.green)
    else:
        message('The ' + user.name + ' feels more resilient!', Game, libtcod.red)

    buff_component = Buff('Super Health', max_hp_bonus=50)
    user.fighter.add_buff(buff_component)
    user.fighter.hp = Game.player.fighter.max_hp(Game)

def use_yellow_crystal(Game, user):
    if user is Game.player:
        message('You feel healthy!', Game, libtcod.yellow)
    else:
        message('The ' + user.name + ' looks healthier!', Game, libtcod.red)

    buff_component = Buff('Super Regen', regen_bonus=-20)
    user.fighter.add_buff(buff_component)

def use_orange_crystal(Game, user):
    if user is Game.player:
        message('You feel speedy!', Game, libtcod.orange)
    else:
        message('The ' + user.name + ' looks speedy!')

    buff_component = Buff('Super Speed', speed_bonus=-3)
    user.fighter.add_buff(buff_component)


#spells
def cast_confusion(Game, user):
    target = None

    if user is Game.player:
        #ask player for target to confuse
        message('Left-click an enemy to confuse. Right-click or ESC to cancel', Game, libtcod.light_cyan)
        target = target_monster(Game, data.CONFUSE_RANGE)
    
    elif libtcod.map_is_in_fov(Game.fov_map, user.x, user.y):
        target = Game.player

    if target is None:
        return data.STATE_CANCELLED

    #replace target's AI with confuse
    if target.ai:
        old_ai = target.ai
    else:
        old_ai = None

    target.ai = ConfusedMonster(old_ai)
    target.ai.owner = target #tell the new component who owns it
    if user is Game.player:
        message('The ' + target.name + ' is confused!', Game, libtcod.light_green)
    else:
        message('You\'ve been confused!!', Game, libtcod.red)

def cast_fireball(Game, user):
    (x,y) = (None, None)

    if user is Game.player: 
        #ask the player for a target tile to throw a fireball at
        message('Left-click a target tile for the fireball. Right-Click or ESC to cancel', Game, libtcod.light_cyan)
        (x,y) = target_tile(Game)
        message('The fireball explodes', Game, libtcod.orange)

    #otherwise this is a mob
    elif libtcod.map_is_in_fov(Game.fov_map, user.x, user.y):
        (x,y) = (Game.player.x, Game.player.y)

    if x is None or y is None:
        return data.STATE_CANCELLED
    else:
        theDmg = roll_dice([[data.FIREBALL_DAMAGE/2, data.FIREBALL_DAMAGE*2]])[0]
        for obj in Game.objects: #damage all fighters within range
            if obj.distance(x,y) <= data.FIREBALL_RADIUS and obj.fighter:
                message('The ' + obj.name + ' is burned for '+ str(theDmg) + ' HP', Game, libtcod.orange)
                obj.fighter.take_damage(theDmg, Game)
        
def cast_heal(Game, user):
    #heal the player or monster
    if user.fighter.hp == user.fighter.max_hp(Game):
        if user is Game.player:
            message('You are already at full health.', Game, libtcod.red)
        return data.STATE_CANCELLED

    if user is Game.player:
        message('You feel better', Game, libtcod.light_violet)
    else:
        message('The ' + user.name + ' looks healthier!', Game, libtcod.red)
    user.fighter.heal(data.HEAL_AMOUNT, Game)

def cast_lightning(Game, user):
    #find nearest enemy (within range) and damage it
    target = None
    if user is Game.player:
        target = closest_monster(data.LIGHTNING_RANGE, Game)

    #otherwise, this is a mob
    elif libtcod.map_is_in_fov(Game.fov_map, user.x, user.y):
        #ensure monster is within player's fov
        target = Game.player

    if target is None:
        if user is Game.player:
            message('No enemy is close enough to strike', Game, libtcod.red)
        return 'cancelled'
    else:
        theDmg = roll_dice([[data.LIGHTNING_DAMAGE/2, data.LIGHTNING_DAMAGE]])[0]

        if user is Game.player:
            message('A lightning bolt strikes the ' + target.name + '! \n DMG = ' + str(theDmg) + ' HP.', Game, libtcod.light_blue)

        target.fighter.take_damage(theDmg, Game)


#death routines
def player_death(player, Game):
    #the game has ended
    message('YOU DIED! YOU SUCK!', Game, libtcod.red)
    Game.game_state = data.STATE_DEAD

    #turn player into corpse
    player.char = '%'
    player.color = libtcod.dark_red

def monster_death(monster, Game):
    #transform into corpse
    #doesn't block, can't be attacked, cannot move
    print monster.name + ' DIED!'
    message(monster.name.capitalize() + ' is DEAD!', Game, libtcod.orange)
    message('You gain ' + str(monster.fighter.xp) + 'XP', Game, libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.always_visible = True
    monster.send_to_back(Game)


#check equip and inventory and buffs
def get_buffs_in_slot(slot, Game):
    for obj in Game.player.buffs:
        print obj.name

def get_equipped_in_slot(slot, Game): #returns the equipment in a slot, or None if it's empty
    for obj in Game.player.fighter.inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def get_all_equipped(obj, Game): #returns list of equipped items
    if obj == Game.player:
        equipped_list = []
        for item in Game.player.fighter.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return [] #other Game.objects have no equipment


#target monsters/tiles and check for blocked tiles
def target_monster(Game, max_range = None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(Game, max_range)
        if x is None: #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in Game.objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != Game.player:
                return obj

def closest_monster(max_range, Game):
    #find closest enemy up to max range in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1 #start with slightly higher than max range

    for object in Game.objects:
        if object.fighter and not object == Game.player and libtcod.map_is_in_fov(Game.fov_map, object.x, object.y):
            #calculate the distance between this and the player
            dist = Game.player.distance_to(object)
            if dist < closest_dist:
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def target_tile(Game, max_range = None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range) or (None, None) if right-clicked
    while True:
        #render screen. this erases the inv and shows the names of objects under the mouse
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, Game.key, Game.mouse)
        render_all(Game)

        (x, y) = (Game.mouse.cx, Game.mouse.cy)
        (x, y) = (Game.camera_x + x, Game.camera_y + y) #from screen to map coords

        if (Game.mouse.lbutton_pressed and libtcod.map_is_in_fov(Game.fov_map, x, y) and (max_range is None or Game.player.distance(x,y) <= max_range)):
            return (x, y)

        if Game.mouse.rbutton_pressed or Game.key.vk == libtcod.KEY_ESCAPE:
            return (None, None)

def is_blocked(x, y, Game):
    #first test the map tile
    if Game.map[x][y].blocked:
        return True

    #now check for any blocking objects
    for object in Game.objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False



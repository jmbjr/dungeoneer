#standard imports
import libtcodpy as libtcod
from gamestuff import *
import data


#Classes:  Object player, enemies, items, etc
class Object(object):
    #this is a generic object: Game.player, monster, item, stairs
    #always represented by a character on the screen
    def __init__(self, x=0, y=0, char='?', name=None, color=libtcod.white, tilechar = None, blocks = False, xplevel = 1, dungeon_level=None, always_visible = False, fighter = None, caster = None, ai = None, item = None, equipment = None):
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.always_visible = always_visible
        self.xplevel = xplevel
        self.dungeon_level = dungeon_level
        self.id = id(self)
        print self.name + ':' + str(self.id)

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
        if (libtcod.map_is_in_fov(Game.player.fighter.fov, self.x, self.y) or (self.always_visible and Game.map[Game.dungeon_level][self.x][self.y].explored)):
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
        if x is not None and libtcod.map_is_in_fov(Game.player.fighter.fov, self.x, self.y):
            libtcod.console_put_char_ex(Game.con, x, y, data.GROUND_CHAR, libtcod.white, data.COLOR_LIGHT_GROUND)

    def move_away(self, target, Game):
        if self.dungeon_level == target.dungeon_level:
            #vector from this object to the target, and distance
            dx1 = target.x - self.x
            dy1 = target.y - self.y

            distance = get_distance(dx1, dy1)
            
            #normalize vector and round accordingly and convert to int
            dx = -1*int(round(dx1 / distance))
            dy = -1*int(round(dy1 / distance))


            if not self.move(dx, dy, Game):
            #if monster didn't move. Try diagonal
                if dx1 != 0:
                    dx = -1 * abs(dx1) / dx1
                elif target.x < self.x:
                    dx = 1
                else:
                    dx = -1

                if dy1 != 0:
                    dy = -1*abs(dy1) / dy1
                elif target.y < self.y:
                    dy = 1
                else:
                    dy = -1

                self.move(dx, dy, Game)        

    def move_towards(self, target, Game):
        if self.dungeon_level == target.dungeon_level:
            #vector from this object to the target, and distance
            dx1 = target.x - self.x
            dy1 = target.y - self.y
            distance = get_distance(dx1, dy1)
            
            #normalize vector and round accordingly and convert to int
            dx = int(round(dx1 / distance))
            dy = int(round(dy1 / distance))

            if not self.move(dx, dy, Game):
            #if monster didn't move. Try diagonal
                if dx1 != 0:
                    dx = abs(dx1) / dx1
                elif target.x < self.x:
                    dx = -1
                else:
                    dx = 1

                if dy1 != 0:
                    dy = abs(dy1) / dy1
                elif target.y < self.y:
                    dy = -1
                else:
                    dy = 1
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
        Game.objects[Game.dungeon_level].remove(self)
        Game.objects[Game.dungeon_level].insert(0, self)


#fighters, spells, abilities
class Fighter(object):
    #combat-related properties and methods (monster, Game.player, NPC, etc)
    def __init__(self, hp, defense, power, xp, clan=None, xpvalue=0, speed=data.SPEED_DEFAULT, regen=data.REGEN_DEFAULT, death_function=None, buffs=None, inventory=None):
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
        self.clan = clan
        self.fov = None
        self.xpvalue = xpvalue

        self.inventory = inventory
        if self.inventory:
            self.inventory.owner = self

        self.buffs = buffs
        if self.buffs:
            self.buffs.owner = self

    def set_fov(self, Game):
        self.fov = libtcod.map_new(data.MAP_WIDTH, data.MAP_HEIGHT)
        for yy in range(data.MAP_HEIGHT):
            for xx in range(data.MAP_WIDTH):
                libtcod.map_set_properties(self.fov, xx, yy, not Game.map[Game.dungeon_level][xx][yy].block_sight, not Game.map[Game.dungeon_level][xx][yy].blocked)
        return self.fov   

    def fov_recompute(self, Game):
        libtcod.map_compute_fov(self.fov, self.owner.x, self.owner.y, data.TORCH_RADIUS, data.FOV_LIGHT_WALLS, data.FOV_ALGO)
        return self.fov


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

    def take_damage(self, attacker, damage, Game):
        #inflict dmg if possible
        if damage > 0:
            self.hp -= damage

        #check for death and call death_function (if set)
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner, attacker, Game)



    def attack(self, target, Game):
        #very simple formula for attack damage
        damage = self.power(Game) - target.fighter.defense(Game)

        if damage > 0:
            #make target take some damage
            if self is Game.player:
                message('You attack ' + target.name  + '!', Game, libtcod.yellow)
            elif entity_sees(Game.player, self.owner):
                message(self.owner.name.capitalize() + ' attacks ' + target.name, Game, libtcod.yellow)
            elif entity_sees(Game.player, target):
                message(target.name + ' has been attacked! ', Game, libtcod.yellow)

            target.fighter.take_damage(self.owner, damage, Game)
        else:
            if self is Game.player:
                message('You tried to attack ' + target.name + ' but there is no effect.', Game, libtcod.white)

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
            if user is Game.player:
                message('Your inventory is full! Cannot pick up ' + self.owner.name +'.', Game, libtcod.dark_red)
            retval = data.STATE_NOACTION
        else:
            user.fighter.add_item(self.owner)
            Game.objects[Game.dungeon_level].remove(self.owner)
            if user is Game.player:
                message('You picked up a ' + self.owner.name + '!', Game, libtcod.green)
            else:
                print 'STATS--\t ' + str(Game.tick) + '\t' + Game.dungeon_level + '\t' + user.name + ' picked up ' + self.owner.name

            #special case: auto equip if the slot is unused
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot, Game) is None and data.AUTOEQUIP:
                equipment.equip(Game)

            retval = data.STATE_PLAYING

        return retval

    def drop(self, Game, user):
        #add to the map and remove from the player's inventory. also, place it at the Game.player's coordinates
        Game.objects[Game.dungeon_level].append(self.owner)
        user.fighter.remove_item(self.owner)
        self.owner.x = user.x
        self.owner.y = user.y
        self.owner.send_to_back(Game)
        if user is Game.player:
            message('You dropped a ' + self.owner.name + '.', Game, libtcod.yellow)

        #special case: if the object has the equip component, dequip before dropping it
        if self.owner.equipment:
            self.owner.equipment.dequip(Game)

        print 'STATS--\t ' + str(Game.tick) + '\t' + Game.dungeon_level + '\t' + user.name + ' dropped ' + self.owner.name

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
            message('The ' + self.owner.name + ' is STILL confused!', Game, libtcod.red)

        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused', Game, libtcod.green)

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
        #find nearest non-clan object
        nearest_nonclan = closest_nonclan(data.TORCH_RADIUS, Game, monster)
        nearest_item    = closest_item(data.TORCH_RADIUS, Game, monster)
    
        if nearest_nonclan:
            if libtcod.map_is_in_fov(monster.fighter.fov, nearest_nonclan.x, nearest_nonclan.y): #nearest_nonclan ensures same level
                #move or use item
                #for now, use items or lose them
                if monster.fighter.inventory:
                    #get random item from inv
                    index = libtcod.random_get_int(0, 0, len(monster.fighter.inventory)-1)
                    item = monster.fighter.inventory[index].item
                    useditem = item.use(Game, user=monster)

                #if monster didn't use item, then move
                if useditem is not data.STATE_USED:
                    #move towards Game.player if far enough away

                    if monster.distance_to(nearest_nonclan) >= 2:
                        monster.move_towards(nearest_nonclan, Game)

                        #close enough to attack (if the Game.player is alive)
                    elif nearest_nonclan.fighter.hp > 0:
                        monster.fighter.attack(nearest_nonclan, Game)
        else: #wander
            #check if there's an item under the monster's feet
            for obj in Game.objects[Game.dungeon_level]: #look for items in the user's title
                if obj.x == monster.x and obj.y == monster.y and obj.item and obj.dungeon_level == monster.dungeon_level:
                    picked_up_item = True
                    obj.item.pick_up(Game, monster)
                    break

            #if monster picked up objects, don't move
            if not picked_up_items:
                monster.move_random(Game)

        #check if monster is still alive
        if monster.fighter:
            return True
        else:
            return False

def entity_sees(entity, target):
    if libtcod.map_is_in_fov(entity.fighter.fov, target.x, target.y) and entity.dungeon_level == target.dungeon_level:
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
        message('The ' + user.name + ' looks speedy!', Game, libtcod.orange)

    buff_component = Buff('Super Speed', speed_bonus=-3)
    user.fighter.add_buff(buff_component)


#spells
def cast_confusion(Game, user):
    target = None
    target = closest_nonclan(data.TORCH_RADIUS, Game, user)

    if user is Game.player:
        #ask player for target to confuse
        message('Left-click an enemy to confuse. Right-click or ESC to cancel', Game, libtcod.light_cyan)
        target = target_monster(Game, data.CONFUSE_RANGE)
    
    elif not target is None:
        target = closest_nonclan(data.TORCH_RADIUS, Game, user)
        print 'STATS--\t ' + str(Game.tick) + '\t' + Game.dungeon_level + '\t' + user.name + ' confused ' + target.name

    else:
        #target is None:
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
    target = None
    target = closest_nonclan(data.TORCH_RADIUS, Game, user)

    if user is Game.player: 
        #ask the player for a target tile to throw a fireball at
        message('Left-click a target tile for the fireball. Right-Click or ESC to cancel', Game, libtcod.light_cyan)
        (x,y) = target_tile(Game)
        message('The fireball explodes', Game, libtcod.orange)

    #otherwise this is a mob
    elif target:
        if libtcod.map_is_in_fov(user.fighter.fov, target.x, target.y) and target.dungeon_level == user.dungeon_level:
            (x,y) = (target.x, target.y)

    if x is None or y is None:
        return data.STATE_CANCELLED
    else:
        theDmg = roll_dice([[data.FIREBALL_DAMAGE/2, data.FIREBALL_DAMAGE*2]])[0]
        
        #create fireball fov based on x,y coords of target
        fov_map_fireball = libtcod.map_new(data.MAP_WIDTH, data.MAP_HEIGHT)
        for yy in range(data.MAP_HEIGHT):
            for xx in range(data.MAP_WIDTH):
                libtcod.map_set_properties(fov_map_fireball, xx, yy, not Game.map[Game.dungeon_level][xx][yy].block_sight, not Game.map[Game.dungeon_level][xx][yy].blocked)

        libtcod.map_compute_fov(fov_map_fireball, x, y, data.FIREBALL_RADIUS, data.FOV_LIGHT_WALLS, data.FOV_ALGO)

        for obj in Game.objects[Game.dungeon_level]: #damage all fighters within range
            if libtcod.map_is_in_fov(fov_map_fireball, obj.x, obj.y) and obj.fighter:
                message('The ' + obj.name + ' is burned for '+ str(theDmg) + ' HP', Game, libtcod.orange)
                obj.fighter.take_damage(user, theDmg, Game)
        
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

def cast_push(Game, user):
    push(Game, user, 3)

def cast_bigpush(Game, user):
    push(Game, user, 5)

def push(Game, user, numpushes):
    #find nearest enemy (within range) and damage it
    target = None
    if user is Game.player:
        target = closest_monster(data.TORCH_RADIUS, Game)

    #otherwise, this is a mob
    else:
        target = closest_nonclan(data.TORCH_RADIUS, Game, user)

    if target is None:
        if user is Game.player:
            message('No enemy is close enough to strike', Game, libtcod.red)
        return 'cancelled'
    else:
        dist = user.distance_to(target)
        if dist < 1.5: #adjacent
            #push
            if user is Game.player:
                message('You pushed the ' + target.name + '!', Game, libtcod.magenta)
            else:
                message(user.name + ' pushed ' + target.name + '!', Game, libtcod.magenta)

            for times in range(numpushes-1):
                target.move_away(user, Game)
            #last push is random
            target.move_random(Game)

        else:
            if user is Game.player:
                message('Too Far away to push!', Game, libtcod.red)
            return 'cancelled'

def cast_lightning(Game, user):
    #find nearest enemy (within range) and damage it
    target = None
    target = closest_nonclan(data.LIGHTNING_RANGE, Game, user)

    if user is Game.player:
        target = closest_monster(data.LIGHTNING_RANGE, Game)

    #otherwise, this is a mob
    elif target:
        if not (libtcod.map_is_in_fov(user.fighter.fov, target.x, target.y) and target.dungeon_level == user.dungeon_level):
            target = None
        #ensure monster is within player's fov
        
    if target is None:
        if user is Game.player:
            message('No enemy is close enough to strike', Game, libtcod.red)
        return 'cancelled'
    else:
        theDmg = roll_dice([[data.LIGHTNING_DAMAGE/2, data.LIGHTNING_DAMAGE]])[0]

        if user is Game.player:
            message('Your lightning bolt strikes the ' + target.name + '!  DMG = ' + str(theDmg) + ' HP.', Game, libtcod.light_blue)
        else:
            message(user.name + '\'s lightning bolt strikes the ' + target.name + '!  DMG = ' + str(theDmg) + ' HP.', Game, libtcod.light_blue)

        target.fighter.take_damage(user, theDmg, Game)


#death routines
def player_death(player, killer, Game):
    #the game has ended

    if killer.fighter:
        killer.fighter.xp += player.fighter.xpvalue
        print 'STATS--\t ' + str(Game.tick) + '\t' + Game.dungeon_level + '\t' + killer.name + '.xp = ' + str(killer.fighter.xp)  + '(' + player.name + ')'
    
    if not data.AUTOMODE: 
        message('YOU DIED! YOU SUCK!', Game, libtcod.red)
        Game.game_state = data.STATE_DEAD

        #turn player into corpse
        player.char = '%'
        player.color = libtcod.dark_red

def monster_death(monster, killer, Game):
    #transform into corpse
    #doesn't block, can't be attacked, cannot move

    message(monster.name.capitalize() + ' is DEAD!', Game, libtcod.orange)
    monster.send_to_back(Game)
    
    if killer.fighter:
        killer.fighter.xp += monster.fighter.xpvalue
        print 'STATS--\t ' + str(Game.tick) + '\t' + Game.dungeon_level + '\t' + killer.name + '.xp = ' + str(killer.fighter.xp) + '(' + monster.name + ')'
    if killer is Game.player:
        message('You gain ' + str(monster.fighter.xpvalue) + 'XP', Game, libtcod.orange)

    for equip in monster.fighter.inventory:
        equip.item.drop(Game, monster)

    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.always_visible = True
    


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
        return [] #other Game.objects[Game.dungeon_level] have no equipment


#target monsters/tiles and check for blocked tiles
def target_monster(Game, max_range = None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(Game, max_range)
        if x is None: #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in Game.objects[Game.dungeon_level]:
            if obj.x == x and obj.y == y and obj.fighter and obj != Game.player and obj.dungeon_level == Game.player.dungeon_level:
                return obj

def closest_monster(max_range, Game):
    #find closest enemy up to max range in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1 #start with slightly higher than max range

    for object in Game.objects[Game.dungeon_level]:
        if object.fighter and not object == Game.player and libtcod.map_is_in_fov(Game.player.fighter.fov, object.x, object.y):
            #calculate the distance between this and the player
            dist = Game.player.distance_to(object)
            if dist < closest_dist:
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def fov_map(max_range, Game, dude):
    #create fovmap for this dude
    fov_map_dude = libtcod.map_new(data.MAP_WIDTH, data.MAP_HEIGHT)
    for yy in range(data.MAP_HEIGHT):
        for xx in range(data.MAP_WIDTH):
            libtcod.map_set_properties(fov_map_dude, xx, yy, not Game.map[Game.dungeon_level][xx][yy].block_sight, not Game.map[Game.dungeon_level][xx][yy].blocked)

    libtcod.map_compute_fov(fov_map_dude, dude.x, dude.y, max_range, data.FOV_LIGHT_WALLS, data.FOV_ALGO)
    return fov_map_dude

def closest_item(max_range, Game, dude):
    #find closest nonclan entity up to max range in the object's FOV
    closest_item = None
    closest_dist = max_range + 1 #start with slightly higher than max range

    if dude.fighter.fov is None:
        fov_map_dude = dude.fighter.set_fov(Game)

    fov_map_dude = dude.fighter.fov_recompute(Game)

    for object in Game.objects[Game.dungeon_level]:
        if object.item and libtcod.map_is_in_fov(fov_map_dude, object.x, object.y) and object.dungeon_level == dude.dungeon_level:
            #calculate the distance between this and the dude
            dist = dude.distance_to(object)
            if dist < closest_dist:
                closest_item = object
                closest_dist = dist           
    return closest_item

def closest_nonclan(max_range, Game, dude):
    #find closest nonclan entity up to max range in the object's FOV
    closest_nonclan = None
    closest_dist = max_range + 1 #start with slightly higher than max range

    if dude.fighter.fov is None:
        fov_map_dude = dude.fighter.set_fov(Game)

    fov_map_dude = dude.fighter.fov_recompute(Game)

    for object in Game.objects[Game.dungeon_level]:
        if object.fighter and  object.fighter.clan != dude.fighter.clan and libtcod.map_is_in_fov(fov_map_dude, object.x, object.y) and object.dungeon_level == dude.dungeon_level:
            #calculate the distance between this and the dude
            dist = dude.distance_to(object)
            if dist < closest_dist:
                closest_nonclan = object
                closest_dist = dist           
    return closest_nonclan


def get_next_fighter(Game):
    for index,level in enumerate(data.maplist):
        if index > 0:
            for object in Game.objects[data.maplist[index]]:
                if object.fighter:
                    return object

def target_tile(Game, max_range = None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range) or (None, None) if right-clicked
    while True:
        #render screen. this erases the inv and shows the names of objects under the mouse
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, Game.key, Game.mouse)
        render_all(Game)

        (x, y) = (Game.mouse.cx, Game.mouse.cy)
        (x, y) = (Game.camera_x + x, Game.camera_y + y) #from screen to map coords

        if (Game.mouse.lbutton_pressed and libtcod.map_is_in_fov(Game.player.fighter.fov, x, y) and (max_range is None or Game.player.distance(x,y) <= max_range)):
            return (x, y)

        if Game.mouse.rbutton_pressed or Game.key.vk == libtcod.KEY_ESCAPE:
            return (None, None)

def is_blocked(x, y, Game):
    #first test the map tile
    if Game.map[Game.dungeon_level][x][y].blocked:
        return True

    #now check for any blocking objects
    for object in Game.objects[Game.dungeon_level]:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False



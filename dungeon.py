import libtcodpy as libtcod
import math
import textwrap
import shelve

CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 40

#GUI rendering
BAR_WIDTH = 20
PANEL_HEIGHT = SCREEN_HEIGHT - MAP_HEIGHT
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

#combat log
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

#items
MAX_NUM_ITEMS = 26
INVENTORY_WIDTH = 50

#spell info
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 25
LIGHTNING_RANGE = 5
FIREBALL_DAMAGE = 25
FIREBALL_RADIUS = 3
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8

#room info
ROOM_MAX_SIZE = 12
ROOM_MIN_SIZE = 4
MAX_ROOMS = 40

FOV_ALGO = 2 #FOV_SHADOW
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

WALL_CHAR = '#'
GROUND_CHAR  = '.'

#dice
D6=[1,6]
D4=[1,4]
D8=[1,8]
D10=[1,10]

#player
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(25, 25, 25)

class Tile(object):
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #all tiles start out unexplored
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

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

class Object(object):
    #this is a generic object: player, monster, item, stairs
    #always represented by a character on the screen
    def __init__(self, x, y, char, name, color, blocks = False, always_visible = False, fighter = None, ai = None, item = None):
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


    def move(self, dx, dy):

        if not is_blocked(self.x + dx, self.y + dy):
        #if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy
            return True
        else:
            return False

    def draw(self):
        #only draw if in field of view of player or it's set to always visible and on explored tile
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or (self.always_visible and map[self.x][self.y].explored)):
            #set the color then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase char that represents this object
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_put_char_ex(con, self.x, self.y, GROUND_CHAR, libtcod.white, color_light_ground)

    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx1 = target_x - self.x
        dy1 = target_y - self.y
        #print str(target_x) + '/' + str(target_y) + '::' + str(self.x) + '/' + str(self.y)
        distance = get_distance(dx1, dy1)
        
        #normalize vector and round accordingly and convert to int
        dx = int(round(dx1 / distance))
        dy = int(round(dy1 / distance))

        #print str(dx) + '/' + str(dx1) + ', ' + str(dy) + '/' + str(dy) + ', ' + str(distance)
        if not self.move(dx, dy):
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
            self.move(dx, dy)

    def distance_to(self, other):
        #return distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return get_distance(dx, dy)

    def distance(self, x, y):
        #return distance to some coord
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they are in the same tile
        global objects
        objects.remove(self)
        objects.insert(0, self)

class Fighter(object):
    #combat-related properties and methods (monster, player, NPC, etc)
    def __init__(self, hp, defense, power, xp, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.xp = xp
        self.defense = defense
        self.power = power  
        self.death_function=death_function

    def heal(self, amount):
        #heal by the given amount
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def take_damage(self, damage):
        #inflict dmg if possible
        if damage > 0:
            self.hp -= damage

        #check for death and call death_function (if set)
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)
            if self.owner != player: #yield experience to the player
                player.fighter.xp += self.xp

    def attack(self, target):
        #very simple formula for attack damage
        damage = self.power - target.fighter.defense

        if damage > 0:
            #make target take some damage
            message (self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' +str(damage) + ' HP.', libtcod.yellow)
            target.fighter.take_damage(damage)
        else:
            message (self.owner.name.capitalize() + ' attacks ' + target.name + ' but there is no effect.', libtcod.white)

class BasicMonster(object):
    #AI for basic monster
    def take_turn(self):
        #basic monsters can see you if you can see them
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            #move towards player if far enough away
            if flip_coin() and flip_coin() and flip_coin():
                 message ('The ' + self.owner.name + ' clears its throat!', monster.color)
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)

                #close enough to attack (if the player is alive)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

class ConfusedMonster(object):
    def __init__(self, old_ai, num_turns = CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    #AI for confused monster
    def take_turn(self):
        if self.num_turns > 0: #still confused
            #move in random direction
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1

        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused', libtcod.red) 

class Item(object):
    def __init__(self, use_function=None):
        self.use_function = use_function

    def use(self):
        #call the 'use_function' if defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
            return 'no_action'
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner) #destror after use, unless cancelled
                return 'used'
            else:
                return 'no_action'
    #an item that can be picked up and used
    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(inventory) >= 26:
            message('Your inventory is full! Cannot pick up ' + self.owner.name +'.', libtcod.dark_red)
            return 'no_action'
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)
            return 'picked_up'

    def drop(self):
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

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

def check_level_up():
    #see if the player's experience is enough to level-up
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        player.level += 1
        player.fighter.xp -=level_up_xp
        message('You have reached level ' + str(player.level) + '!', libtcod.yellow)

        choice = None
        while choice == None: #keep asking till a choice is made
            choice = menu('Level up! Choose a stat to raise:\n', 
                ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                'Strength (+1 attack, from ' + str(player.fighter.power) + ')', 
                'Agility (+1 defense, from ' + str(player.fighter.defense) + ')'], LEVEL_SCREEN_WIDTH)

        if choice == 0:
            player.fighter.max_hp += 20
        elif choice == 1:
            player.fighter.power += 1
        elif choice ==2:
            player.fighter.defense += 1

        player.fighter.hp = player.fighter.max_hp

def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show game title and credits
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 4, libtcod.BKGND_NONE, libtcod.CENTER, 'Dungeoneer!')
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER, 'by johnstein!')

        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0: #new game
            new_game()
            play_game()
        if choice == 1: #load last game
            #try:
            load_game()
            #except:
            #    msgbox('\n No saved game to load. \n', 24)
            #    continue
            play_game()
        elif choice == 2: #quit
            save_game()
            break

def msgbox(text, width = 50):
    menu(text, [], width) #use menu as a sort-of message box

def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level

    #create object representing the player
    fighter_component = Fighter(hp=100, defense=1, power=4, xp=0, death_function=player_death)
    player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', 'Bobb', libtcod.white, blocks=True, fighter=fighter_component)

    player.level = 1
    #generate map (at this point it's not drawn to screen)
    dungeon_level = 1
    make_map()
    initialize_fov()

    game_state = 'playing'
    inventory = []

    #create the list of the game messages and their colors, starts empty
    game_msgs = []

    #a warm welcoming message!
    message('Welcome to Dungeoneer! Good Luck! Don\'t suck!', libtcod.blue)

def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True

    #create FOV map according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

    libtcod.console_clear(con)

def save_game(filename='savegame'):
    #open a new empty shelve (or overwrite old one) to write the game data
    file = shelve.open(filename, 'n')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player) #index of player in the objects list
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['stairs_index'] = objects.index(stairs)
    file['dungeon_level'] = dungeon_level
    file.close()

def load_game(filename='savegame'):
    global map, objects, player, inventory, game_msgs, game_state, dungeon_level, stairs
    
    file = shelve.open(filename, 'r')
    map = file['map']
    objects = file['objects'] 
    player = objects[file['player_index']]  #get index of player in the objects list
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    stairs = objects[file['stairs_index']]
    dungeon_level = file['dungeon_level']
    file.close()

    initialize_fov()

def play_game():
    global key, mouse

    player_action = None

    #mouse stuff
    mouse = libtcod.Mouse()
    key = libtcod.Key()    

    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        #render the screen
        render_all()

        libtcod.console_flush()
        check_level_up()

        #erase objects from old position, before they move
        for object in objects:
            object.clear()

        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            break

        #give monsters a turn
        if game_state == 'playing' and player_action != 'no_action':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

def cast_confusion():
    ##find nearest enemy and confuse it
    #monster = closest_monster(CONFUSE_RANGE)
    #if monster is None:
    #    message ('No enemy is close enough to confuse', libtcod.red)
    #    return 'cancelled'

    #ask player for target to confuse
    message('Left-click an enemy to confuse. Right-click or ESC to cancel', libtcod.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None:
        return 'cancelled'

    #replace monster's AI with confuse
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster #tell the new component who owns it
    message('The ' + monster.name + ' is confused!', libtcod.light_green)

def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball. Right-Click or ESC to cancel', libtcod.light_cyan)
    (x,y) = target_tile()
    if x is None: 
        return 'cancelled'
    else:
        message('The fireball explodes', libtcod.orange)

    theDmg = roll_dice([[FIREBALL_DAMAGE/2, FIREBALL_DAMAGE*2]])[0]
    for obj in objects: #damage all fighters within range
        if obj.distance(x,y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' is burned for '+ str(theDmg) + ' HP', libtcod.orange)
            obj.fighter.take_damage(theDmg)

def cast_heal():
    #heal the player
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'

    message('You feel better', libtcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT)

def cast_lightning():
    #find nearest enemy (within range) and damage it
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:
        message('No enemy is close enough to strike', libtcod.red)
        return 'cancelled'

    theDmg = roll_dice([[LIGHTNING_DAMAGE/2, LIGHTNING_DAMAGE]])[0]

    message('A lightning bolt strikes the ' + monster.name + '! \n DMG = ' + str(theDmg) + ' HP.', libtcod.light_blue)
    monster.fighter.take_damage(theDmg)

def closest_monster(max_range):
    #find closest enemy up to max range in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1 #start with slightly higher than max range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate the distance between this and the player
            dist = player.distance_to(object)
            if dist < closest_dist:
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True

    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def create_room(room):
    global map
    #go through tiles in rect to make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
                map[x][y].blocked = False
                map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map

    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map

    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def make_map():
    global map, objects, stairs

    objects = [player]

    #fill map with "blocked" tiles
    map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #get random width/height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #get random positions, but stay within map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)

        #check for intersection with this room
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #no intersections

            create_room(new_room)
            (new_x, new_y) = new_room.center()

            #add some contents to the room
            place_objects(new_room)

            if num_rooms == 0:
                #first room. start player here
                player.x = new_x
                player.y = new_y

            else:
                #for all other rooms, need to connect to previous room with a tunnel

                #get center coords of previous room
                (prev_x, prev_y) = rooms[num_rooms -1].center()

                #flip coin
                if flip_coin() == 1:
                    #move h then v
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #move v then h
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
            
            #add to rooms list
            rooms.append(new_room)
            num_rooms +=1

    #create stairs at the center of the last room
    stairs = Object(new_x, new_y, '>', 'stairs', libtcod.white, always_visible = True)
    objects.append(stairs)
    stairs.send_to_back() #so it's drawn below the monsters

def from_dungeon_level(table):
        #returns a value that depends on level. table specifies what value occurs after each level. default = 0
        for (value, level) in reversed(table):
            if dungeon_level >= level:
                return value
        return 0

def place_objects(room):
    #choose random number of monsters
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
    #max number monsters per room

    #chance of each monster
    monster_chances = {}
    monster_chances['orc'] = 75 #orc always shows up, even if all other monsters have 0 chance
    monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])

    max_items = from_dungeon_level([[1, 1], [2, 4]])
    num_items = libtcod.random_get_int(0, 0, max_items)
    
    #chance of each item (by default they have chance of 0 at level 1 which goes up)
    item_chances = {}
    item_chances['heal'] = 35 #healing potion always shows up even if all other items have 0 chance
    item_chances['lightning'] = from_dungeon_level([[25, 4]])
    item_chances['fireball'] = from_dungeon_level([[25, 6]])
    item_chances['confuse'] = from_dungeon_level([[25, 2]])

    #monster_chances = {'orc':75, 'troll':25}
    #item_chances = {'heal':60, 'lightning':10, 'fireball':10, 'confuse':10}

    for i in range(num_monsters):
        #choose random spot for this monster
        x =  libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y =  libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        if not is_blocked(x, y):
            choice = random_choice(monster_chances)

            if choice == 'orc':
                #create orc
                fighter_component = Fighter(hp=20, defense=0, power=4, xp=35, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'o', 'orcy', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
            elif choice == 'troll':
                #create a troll
                fighter_component = Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'T', 'TROLLY', libtcod.darker_green, blocks= True, fighter=fighter_component, ai=ai_component)
            else:
                print 'ERROR!'
                break

            objects.append(monster)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            #create an item
            #roll = roll_dice([[0,100]])[0]
            choice = random_choice(item_chances)
            if choice == 'heal':
                #healing potion
                item_component = Item(use_function = cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.red, always_visible = True, item = item_component)
                #print 'Healing Potion'
            elif choice == 'lightning':
                #lightning scroll
                item_component = Item(use_function = cast_lightning)
                item = Object(x, y, '?', 'scroll of lightning bolt', libtcod.yellow, always_visible = True, item = item_component)
                #print 'Lightning Scroll'
            elif choice == 'fireball':
                #fireball scroll
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '?', 'scroll of fireball', libtcod.red, always_visible = True, item = item_component)
                #print 'Fireball Scroll'
            elif choice == 'confuse':
                #confusion scroll
                item_component = Item(use_function = cast_confusion)
                item = Object(x, y, '?', 'scroll of confusion', libtcod.light_violet, always_visible = True, item = item_component)
                #print 'Confusion Scroll'
            else:
                print 'ERROR!'
                break

            objects.append(item)
            item.send_to_back() #items appear below other objects

def get_distance(dx, dy):
    return math.sqrt(dx ** 2 + dy ** 2)

def render_all():
    global color_light_wall, color_dark_wall
    global color_light_ground, color_dark_ground
    global fov_recompute, fov_map

    if fov_recompute:
        #recompute FOV if needed (if player moved or something else happened)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #tile not visible
                    if wall:
                        color_wall_ground = color_dark_wall
                        char_wall_ground = WALL_CHAR
                    else:
                        color_wall_ground = color_dark_ground
                        char_wall_ground = GROUND_CHAR
                    fov_wall_ground = libtcod.grey
                else:
                    #tile is visible
                    map[x][y].explored = True
                    if wall:
                        color_wall_ground = color_light_wall
                        char_wall_ground = WALL_CHAR
                    else:
                        color_wall_ground = color_light_ground
                        char_wall_ground = GROUND_CHAR
                    fov_wall_ground = libtcod.white

                if map[x][y].explored:
                    libtcod.console_put_char_ex(con, x, y, char_wall_ground, fov_wall_ground, color_wall_ground)
                

    #draw all objects in the list
    for object in objects:
        if object != player:
            object.draw()
    #ensure we draw player last
    player.draw()

    #blit contents of con to root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #show player's stats via GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #show player stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)
    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level' + str(dungeon_level))

    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    #blit panel to root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def get_names_under_mouse():
    global mouse
    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    #create list with the names of all objects at the mouse's coords and in FOV
    names = [obj.name for obj in objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
    
    names = ', '.join(names) #join names separated by commas
    return names.capitalize()

def handle_keys():
    global fov_recompute
    global key

    #for real-time, uncomment
    #key = libtcod.console_check_for_keypress()

    #for turn-based, uncomment
    #key = libtcod.console_wait_for_keypress(True)
    key_char = chr(key.c)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #ALT + ENTER: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit' #exit game

    if game_state == 'playing':
        #rest
        if key.vk == libtcod.KEY_KPDEC or key.vk == libtcod.KEY_KP5:
            player_resting()
            pass
        #movement keys
        elif key.vk == libtcod.KEY_UP or key_char == 'k' or key.vk == libtcod.KEY_KP8 :
            player_move_or_attack(0, -1)

        elif key.vk == libtcod.KEY_DOWN or key_char == 'j' or key.vk == libtcod.KEY_KP2 :
            player_move_or_attack(0, 1)

        elif key.vk == libtcod.KEY_LEFT or key_char == 'h' or key.vk == libtcod.KEY_KP4 :
            player_move_or_attack(-1, 0)

        elif key.vk == libtcod.KEY_RIGHT or key_char == 'l' or key.vk == libtcod.KEY_KP6 :
            player_move_or_attack(1, 0)

        #handle diagonal. 11 oclock -> clockwise
        elif key_char == 'y' or key.vk == libtcod.KEY_KP7 :
            player_move_or_attack(-1, -1)

        elif key_char == 'u' or key.vk == libtcod.KEY_KP9 :
            player_move_or_attack(1, -1)

        elif key_char == 'n' or key.vk == libtcod.KEY_KP3 :
            player_move_or_attack(1, 1)

        elif key_char == 'b' or key.vk == libtcod.KEY_KP1 :
            player_move_or_attack(-1, 1)

        else:
            #test for other keys
            if key_char == 'g':
                #pick up an item
                for object in objects: #look for items in the player's title
                    if object.x == player.x and object.y == player.y and object.item:
                        return object.item.pick_up()
                        #break

            if key_char == 'i':
                #show inv. if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it. \nPress ESC to return to game\n')
                if chosen_item is not None:
                    return chosen_item.use()

            if key_char == 'd':
                #show the inventory. if item is selected, drop it
                chosen_item = inventory_menu('Press the key next to the item to drop. \nPress ESC to return to game\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == 'c':
                #show character info
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(player.fighter.max_hp) +
                    '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.defense), CHARACTER_SCREEN_WIDTH)

            if key_char == '>':
                #go down stairs, if the player is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()

            return 'no_action'

def next_level():
    global dungeon_level
    #advance to next level
    message('You head down the stairs', libtcod.red)
    dungeon_level +=1
    make_map() #create fresh new level
    initialize_fov()

def player_resting():
    player.fighter.hp += 2
    
def player_move_or_attack(dx, dy):
    global fov_recompute

    #the coords the player is moving-to/attacking
    x = player.x + dx
    y = player.y + dy

    #try to find attackable object there
    target = None
    for object in objects:
        if object.x == x and object.y == y and object.fighter:
            target = object
            break

    #attack if target found. else, move
    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True

def flip_coin():
    return (libtcod.random_get_int(0,0,1))

def roll_dice(dicelist):
    dice=[]
    #print dicelist
    for [die_low, die_high] in dicelist:
        roll = libtcod.random_get_int(0,die_low,die_high)
        dice.append(roll)

    return [sum(dice), dice]

def player_death(player):
    #the game has ended
    global game_state
    message ('YOU DIED! YOU SUCK!', libtcod.red)
    game_state = 'dead'

    #turn player into corpse
    player.char = '%'
    player.color = libtcod.dark_red

def monster_death(monster):
    #transform into corpse
    #doesn't block, can't be attacked, cannot move
    message (monster.name.capitalize() + ' is DEAD!', libtcod.orange)
    message ('You gain ' + str(monster.fighter.xp) + 'XP', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.always_visible = True
    monster.send_to_back()

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, exp, etc). first calc the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #lastly add text
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width/2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

def message(new_msg, color = libtcod.white):
    #split message if necessary
    #print new_msg
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the txt and the color
        game_msgs.append((line, color))

def menu(header, options, width):
    if len(options) > MAX_NUM_ITEMS: raise ValueError('Cannot have a menu with more than ' + MAX_NUM_ITEMS + ' options.')

    #calculate total height of the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit contents of window to root console
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for a keypress
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt: # full screen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    #convert ASCII code to an index. if it's valid, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options):
        return index
    else:
        return None

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty!']
    else:
        options = [item.name for item in inventory]

    index = menu(header, options, INVENTORY_WIDTH)
    
    if (index is None or len(inventory) == 0) or index == 'ESC':
        return None
    else:
        return inventory[index].item

def target_tile(max_range = None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range) or (None, None) if right-clicked
    global key, mouse
    while True:
        #render screen. this erases the inv and shows the names of objects under the mouse
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        (x, y) = (mouse.cx, mouse.cy)

        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and (max_range is None or player.distance(x,y) <= max_range)):
            return (x, y)

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)

def target_monster(max_range = None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None: #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj

########################################################
#init and main loop
########################################################

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'DUNGEONEER!', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH,MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

main_menu()


import libtcodpy as libtcod
from constants import *
from ui import *
#functions to get info from world or interact with it.
#also handles rendering

def is_blocked(x, y, Game):
    #first test the map tile
    if Game.map[x][y].blocked:
        return True

    #now check for any blocking objects
    for object in Game.objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def get_equipped_in_slot(slot, Game): #returns the equipment in a slot, or None if it's empty
    for obj in Game.inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def get_all_equipped(obj, Game): #returns list of equipped items
    if obj == Game.player:
        equipped_list = []
        for item in Game.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return [] #other Game.objects have no equipment

def check_level_up(Game):
    #see if the player's experience is enough to level-up
    level_up_xp = LEVEL_UP_BASE + Game.player.level * LEVEL_UP_FACTOR
    if Game.player.fighter.xp >= level_up_xp:
        Game.player.level += 1
        Game.player.fighter.xp -=level_up_xp
        message('You have reached level ' + str(Game.player.level) + '!', Game, libtcod.yellow)

        choice = None
        while choice == None: #keep asking till a choice is made
            choice = menu('Level up! Choose a stat to raise:\n', 
                ['Constitution (+25 HP, from ' + str(Game.player.fighter.max_hp(Game)) + ')',
                'Strength (+2 attack, from ' + str(Game.player.fighter.power(Game)) + ')', 
                'Agility (+2 defense, from ' + str(Game.player.fighter.defense(Game)) + ')'], LEVEL_SCREEN_WIDTH, Game)

        if choice == 0:
            Game.player.fighter.base_max_hp += 25
        elif choice == 1:
            Game.player.fighter.base_power += 2
        elif choice ==2:
            Game.player.fighter.base_defense += 2

        Game.player.fighter.hp = Game.player.fighter.max_hp(Game)

def initialize_fov(Game):
    Game.fov_recompute = True
    #create FOV map according to the generated map
    Game.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(Game.fov_map, x, y, not Game.map[x][y].block_sight, not Game.map[x][y].blocked)

    libtcod.console_clear(Game.con)

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

        if (Game.mouse.lbutton_pressed and libtcod.map_is_in_fov(Game.fov_map, x, y) and (max_range is None or Game.player.distance(x,y) <= max_range)):
            return (x, y)

        if Game.mouse.rbutton_pressed or Game.key.vk == libtcod.KEY_ESCAPE:
            return (None, None)

def render_all(Game):
    global COLOR_LIGHT_WALL, COLOR_DARK_WALL
    global COLOR_LIGHT_GROUND, COLOR_DARK_GROUND

    if Game.fov_recompute:
        #recompute FOV if needed (if player moved or something else happened)
        Game.fov_recompute = False
        libtcod.map_compute_fov(Game.fov_map, Game.player.x, Game.player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(Game.fov_map, x, y)
                wall = Game.map[x][y].block_sight
                if not visible:
                    #tile not visible
                    if wall:
                        color_wall_ground = COLOR_DARK_WALL
                        char_wall_ground = WALL_CHAR
                    else:
                        color_wall_ground = COLOR_DARK_GROUND
                        char_wall_ground = GROUND_CHAR
                    fov_wall_ground = libtcod.grey
                else:
                    #tile is visible
                    Game.map[x][y].explored = True
                    if wall:
                        color_wall_ground = COLOR_LIGHT_WALL
                        char_wall_ground = WALL_CHAR
                    else:
                        color_wall_ground = COLOR_LIGHT_GROUND
                        char_wall_ground = GROUND_CHAR
                    fov_wall_ground = libtcod.white

                if Game.map[x][y].explored:
                    libtcod.console_put_char_ex(Game.con, x, y, char_wall_ground, fov_wall_ground, color_wall_ground)
                

    #draw all objects in the list
    for object in Game.objects:
        if object != Game.player:
            object.draw(Game)
    #ensure we draw player last
    Game.player.draw(Game)

    #blit contents of con to root console
    libtcod.console_blit(Game.con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #show player's stats via GUI panel
    libtcod.console_set_default_background(Game.panel, libtcod.black)
    libtcod.console_clear(Game.panel)

    #show player stats
    render_bar(1, 1, BAR_WIDTH, 'HP', Game.player.fighter.hp, Game.player.fighter.max_hp(Game), libtcod.light_red, libtcod.darker_red, Game)
    libtcod.console_print_ex(Game.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level' + str(Game.dungeon_level))
    libtcod.console_print_ex(Game.panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT, 'Turn: ' + str(Game.player.game_turns))

    #print the game messages, one line at a time
    y = 1
    for (line, color) in Game.game_msgs:
        libtcod.console_set_default_foreground(Game.panel, color)
        libtcod.console_print_ex(Game.panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(Game.panel, libtcod.light_gray)
    libtcod.console_print_ex(Game.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse(Game))

    #blit panel to root console
    libtcod.console_blit(Game.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color, Game):
    #render a bar (HP, exp, etc). first calc the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(Game.panel, back_color)
    libtcod.console_rect(Game.panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(Game.panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(Game.panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #lastly add text
    libtcod.console_set_default_foreground(Game.panel, libtcod.white)
    libtcod.console_print_ex(Game.panel, x + total_width/2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse(Game):
    #return a string with the names of all objects under the mouse
    (x, y) = (Game.mouse.cx, Game.mouse.cy)

    #create list with the names of all objects at the mouse's coords and in FOV
    names = [obj.name for obj in Game.objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(Game.fov_map, obj.x, obj.y)]
    
    names = ', '.join(names) #join names separated by commas
    return names.capitalize()

def from_dungeon_level(table, Game):
        #returns a value that depends on level. table specifies what value occurs after each level. default = 0
        for (value, level) in reversed(table):
            if Game.dungeon_level >= level:
                return value
        return 0

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

def player_death(player, Game):
    #the game has ended
    message ('YOU DIED! YOU SUCK!', Game, libtcod.red)
    Game.game_state = 'dead'

    #turn player into corpse
    player.char = '%'
    player.color = libtcod.dark_red

def monster_death(monster, Game):
    #transform into corpse
    #doesn't block, can't be attacked, cannot move
    message (monster.name.capitalize() + ' is DEAD!', Game, libtcod.orange)
    message ('You gain ' + str(monster.fighter.xp) + 'XP', Game, libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.always_visible = True
    monster.send_to_back(Game)

def player_move_or_attack(dx, dy, Game):
    #the coords the player is moving-to/attacking
    x = Game.player.x + dx
    y = Game.player.y + dy

    #try to find attackable object there
    target = None
    for object in Game.objects:
        if object.x == x and object.y == y and object.fighter:
            target = object
            break

    #attack if target found. else, move
    if target is not None:
        Game.player.fighter.attack(target, Game)
        Game.player.game_turns +=1
    else:
        Game.player.move(dx, dy, Game)
        Game.player.game_turns +=1
        Game.fov_recompute = True

def player_resting(Game):
    Game.player.fighter.hp += 2
    Game.player.game_turns += 1






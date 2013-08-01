import entities
import libtcodpy as libtcod
import data

#.............................................
#EDITABLE MOB DATA
mobs={}
mobs = {
 'johnstein':      {'char':'j', 'color':libtcod.white,       'tilechar':data.TILE_SKEL_WHITE,   'fighter':{'hp':10 , 'defense':0 , 'power':2 , 'xp':20 , 'death_function': entities.monster_death, 'speed':1}, 'caster':{'mp':10}}, 
 'greynaab':       {'char':'g', 'color':libtcod.light_blue,  'tilechar':data.TILE_SKEL_RED  ,   'fighter':{'hp':20 , 'defense':1 , 'power':4 , 'xp':40 , 'death_function': entities.monster_death, 'speed':3}}, 
 'jerbear':        {'char':'j', 'color':libtcod.green,       'tilechar':data.TILE_SKEL_BLUE ,   'fighter':{'hp':25 , 'defense':1 , 'power':5 , 'xp':50 , 'death_function': entities.monster_death, 'speed':5}}, 
 'zombiesheep':    {'char':'z', 'color':libtcod.yellow,      'tilechar':data.TILE_SKEL_GREEN,   'fighter':{'hp':30 , 'defense':2 , 'power':6 , 'xp':60 , 'death_function': entities.monster_death, 'speed':7}}, 

 'JOHNSTEIN':      {'char':'J', 'color':libtcod.black,       'tilechar':data.TILE_SKEL_WHITE,   'fighter':{'hp':100 , 'defense':3, 'power':5 , 'xp':200 , 'death_function': entities.monster_death, 'speed':1}}, 
 'GREYNAAB':       {'char':'G', 'color':libtcod.red,         'tilechar':data.TILE_SKEL_RED  ,   'fighter':{'hp':200 , 'defense':6, 'power':10, 'xp':400 , 'death_function': entities.monster_death, 'speed':3}}, 
 'JERBEAR':        {'char':'J', 'color':libtcod.blue,        'tilechar':data.TILE_SKEL_BLUE ,   'fighter':{'hp':250 , 'defense':9, 'power':15, 'xp':500 , 'death_function': entities.monster_death, 'speed':5}}, 
 'ZOMBIESHEEP':    {'char':'Z', 'color':libtcod.green,       'tilechar':data.TILE_SKEL_GREEN,   'fighter':{'hp':300 , 'defense':12,'power':20, 'xp':600 , 'death_function': entities.monster_death, 'speed':7}}, 

}

mobitems = {}
mobitems = {
	'johnstein':   ['heal', 'heal', 'heal', 'heal'],
	'greynaab':    ['fireball', 'heal', 'fireball'],
	'jerbear':     ['confuse', 'heal', 'confuse'],
	'zombiesheep': ['lightning','lightning','heal','lightning'],
	'JOHNSTEIN':   ['heal', 'heal', 'heal', 'heal'],
	'GREYNAAB':    ['fireball', 'heal', 'fireball'],
	'JERBEAR':     ['confuse', 'heal', 'confuse'],
	'ZOMBIESHEEP': ['lightning','lightning','heal', 'lightning']
}
#add help on how to use this
#basically, set = to list of lists. Each list gives a chance (arbitrary units) and a level
#map.py will use this info to create monster_chances list to figure out which monsters to select for map
#[[chance, dungeon_level]]

mobchances = {}
mobchances = {
	'johnstein':    [[100,1], [25, 3]],
	'greynaab':     [[60, 1], [25, 3]],
	'jerbear':      [[50, 1], [25, 3]],
	'zombiesheep':  [[40, 1], [25, 3]],

	'JOHNSTEIN':    [[100,3], [35, 5]],
	'GREYNAAB':     [[60, 3], [35, 5]],
	'JERBEAR':      [[50, 3], [30, 5]],
	'ZOMBIESHEEP':  [[40, 3], [25, 5]]
}

items={}
items = {
	'heal':       {'name':'healing potion',           'char':'!', 'color':libtcod.red,          'item':{'use_function': entities.cast_heal}}, 
	'lightning':  {'name':'scroll of lightning bolt', 'char':'?', 'color':libtcod.yellow,       'item':{'use_function': entities.cast_lightning}}, 
	'fireball':   {'name':'scroll of fireball',       'char':'?', 'color':libtcod.red,          'item':{'use_function': entities.cast_fireball}}, 
	'confuse':    {'name':'scroll of confusion',      'char':'?', 'color':libtcod.light_violet, 'item':{'use_function': entities.cast_confusion}}, 

	'sword':      {'name':'sword',  'char':'/', 'color':libtcod.sky,           'equipment':{'slot':'right hand' ,   'power_bonus'  :5  }}, 
	'shield':     {'name':'shield', 'char':'[', 'color':libtcod.darker_orange, 'equipment':{'slot':'left hand'  ,   'defense_bonus':3  }},

	'blue_crystal':     {'name':'blue power crystal',    'char':'$', 'color':libtcod.sky,    'item':{'use_function': entities.use_blue_crystal}},
	'red_crystal':      {'name':'red power crystal',     'char':'$', 'color':libtcod.red,    'item':{'use_function': entities.use_red_crystal}},
	'green_crystal':    {'name':'green power crystal',   'char':'$', 'color':libtcod.green,  'item':{'use_function': entities.use_green_crystal}},
	'yellow_crystal':   {'name':'yellow power crystal',  'char':'$', 'color':libtcod.yellow, 'item':{'use_function': entities.use_yellow_crystal}},
	'orange_crystal':   {'name':'orange power crystal',  'char':'$', 'color':libtcod.orange, 'item':{'use_function': entities.use_orange_crystal}}

}

itemchances = {}
itemchances = {
	'heal':          [[5,1]],
	'lightning':     [[10, 1], [25, 3], [50, 5]],
	'fireball':      [[10, 1], [25, 3], [50, 5]],
	'confuse':       [[10, 1], [25, 3], [50, 5]],
	'sword':         [[10, 1], [25, 3], [50, 5]],
	'shield':        [[10, 1], [25, 3], [50, 5]],
    'blue_crystal':  [[10, 1], [30, 3], [50, 5]],
    'red_crystal':   [[10, 1], [30, 3], [50, 5]],
    'green_crystal': [[10, 1], [30, 3], [50, 5]],
    'yellow_crystal':[[10, 1], [30, 3], [50, 5]],
    'orange_crystal':[[10, 1], [30, 3], [50, 5]]
}

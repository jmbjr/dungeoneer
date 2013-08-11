import entities
import libtcodpy as libtcod
import data

#.............................................
#EDITABLE MOB DATA
mobs={}
mobs = {
 'johnstein':      {'char':'j', 'color':libtcod.light_gray,  'tilechar':data.TILE_SKEL_WHITE,   'fighter':{'hp':100 , 'defense':0 , 'power':20 , 'xp':0, 'xpvalue':20 , 'clan':'monster', 'death_function': entities.monster_death, 'speed':5}, 'caster':{'mp':10}}, 
 'greynaab':       {'char':'g', 'color':libtcod.light_blue,  'tilechar':data.TILE_SKEL_RED  ,   'fighter':{'hp':200 , 'defense':1 , 'power':40 , 'xp':0, 'xpvalue':40 , 'clan':'monster', 'death_function': entities.monster_death, 'speed':5}}, 
 'jerbear':        {'char':'j', 'color':libtcod.green,       'tilechar':data.TILE_SKEL_BLUE ,   'fighter':{'hp':250 , 'defense':1 , 'power':50 , 'xp':0, 'xpvalue':50 , 'clan':'monster', 'death_function': entities.monster_death, 'speed':5}}, 
 'zombiesheep':    {'char':'z', 'color':libtcod.yellow,      'tilechar':data.TILE_SKEL_GREEN,   'fighter':{'hp':300 , 'defense':2 , 'power':60 , 'xp':0, 'xpvalue':60 , 'clan':'monster', 'death_function': entities.monster_death, 'speed':5}}, 
 'pushy':          {'char':'p', 'color':libtcod.pink,        'tilechar':data.TILE_SKEL_MAGENTA, 'fighter':{'hp':400 , 'defense':2 , 'power':00 , 'xp':0, 'xpvalue':100, 'clan':'monster', 'death_function': entities.monster_death, 'speed':5}}, 

 'JOHNSTEIN':      {'char':'J', 'color':libtcod.black,       'tilechar':data.TILE_SKEL_WHITE,   'fighter':{'hp':1000 , 'defense':3, 'power':5 , 'xp':0, 'xpvalue':200 , 'clan':'monster', 'death_function': entities.monster_death, 'speed':1}}, 
 'GREYNAAB':       {'char':'G', 'color':libtcod.red,         'tilechar':data.TILE_SKEL_RED  ,   'fighter':{'hp':2000 , 'defense':6, 'power':10, 'xp':0, 'xpvalue':400 , 'clan':'monster', 'death_function': entities.monster_death, 'speed':3}}, 
 'JERBEAR':        {'char':'J', 'color':libtcod.blue,        'tilechar':data.TILE_SKEL_BLUE ,   'fighter':{'hp':2500 , 'defense':9, 'power':15, 'xp':0, 'xpvalue':500 , 'clan':'monster', 'death_function': entities.monster_death, 'speed':5}}, 
 'ZOMBIESHEEP':    {'char':'Z', 'color':libtcod.green,       'tilechar':data.TILE_SKEL_GREEN,   'fighter':{'hp':3000 , 'defense':12,'power':20, 'xp':0, 'xpvalue':600 , 'clan':'monster', 'death_function': entities.monster_death, 'speed':7}}, 
 'PUSHY':          {'char':'P', 'color':libtcod.pink,        'tilechar':data.TILE_SKEL_MAGENTA, 'fighter':{'hp':5000 , 'defense':20,'power':0 , 'xp':0, 'xpvalue':1000 ,'clan':'monster', 'death_function': entities.monster_death, 'speed':1}}, 

}

mobitems = {}
mobitems = {
	'johnstein':   ['heal', 'fireball', 'lightning', 'confuse', 'push', 'bigpush'],
	'greynaab':    ['fireball', 'fireball', 'fireball'],
	'jerbear':     ['fireball', 'fireball', 'fireball'],
	'zombiesheep': ['fireball','fireball','fireball','fireball'],
	'pushy':       ['push','push','push','push','push','push','push','push','push','push','push','push','push','push','push','push','push','push'],
	'JOHNSTEIN':   ['heal', 'heal', 'heal', 'heal'],
	'GREYNAAB':    ['fireball', 'heal', 'fireball'],
	'JERBEAR':     ['confuse', 'heal', 'heal'],
	'ZOMBIESHEEP': ['lightning','lightning','heal', 'lightning'],
	'PUSHY':       ['bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush','bigpush']

}
#add help on how to use this
#basically, set = to list of lists. Each list gives a chance (arbitrary units) and a level
#map.py will use this info to create monster_chances list to figure out which monsters to select for map
#[[chance, dungeon_level]]

mobchances = {}
mobchances = {
	'johnstein':    [[10, 1], [50, 3]],
	'greynaab':     [[10, 2], [25, 3]],
	'jerbear':      [[10, 2], [25, 3]],
	'zombiesheep':  [[10, 2], [25, 3]],
	'pushy'      :  [[10, 2], [50,3]],

	'JOHNSTEIN':    [[10, 3], [35, 5]],
	'GREYNAAB':     [[10, 3], [35, 5]],
	'JERBEAR':      [[10, 3], [30, 5]],
	'ZOMBIESHEEP':  [[10, 3], [25, 5]],
	'PUSHY':        [[10, 3], [50, 5]]
}

items={}
items = {
	'heal':       {'name':'healing potion',           'char':'!', 'color':libtcod.red,          'item':{'use_function': entities.cast_heal}}, 
	'lightning':  {'name':'scroll of lightning bolt', 'char':'?', 'color':libtcod.yellow,       'item':{'use_function': entities.cast_lightning}}, 
	'fireball':   {'name':'scroll of fireball',       'char':'?', 'color':libtcod.red,          'item':{'use_function': entities.cast_fireball}}, 
	'confuse':    {'name':'scroll of confusion',      'char':'?', 'color':libtcod.light_violet, 'item':{'use_function': entities.cast_confusion}}, 
	'push'   :    {'name':'scroll of push',           'char':'?', 'color':libtcod.magenta,      'item':{'use_function': entities.cast_push}},
	'bigpush':    {'name':'scroll of bigpush',        'char':'?', 'color':libtcod.dark_magenta, 'item':{'use_function': entities.cast_bigpush}},

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

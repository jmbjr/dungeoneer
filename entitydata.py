import entities
import libtcodpy as libtcod
import data

#.............................................
#EDITABLE MOB DATA
mobs={}
mobs = {
 'johnstein':      {'char':'J', 'color':libtcod.white,       'tilechar':data.TILE_SKEL_WHITE,   'fighter':{'hp':10 , 'defense':0 , 'power':2 , 'xp':20 , 'death_function': entities.monster_death, 'speed':1}}, 
 'greynaab':       {'char':'g', 'color':libtcod.light_blue,  'tilechar':data.TILE_SKEL_RED  ,   'fighter':{'hp':20 , 'defense':1 , 'power':4 , 'xp':40 , 'death_function': entities.monster_death, 'speed':3}}, 
 'jerbear':        {'char':'j', 'color':libtcod.green,       'tilechar':data.TILE_SKEL_BLUE ,   'fighter':{'hp':25 , 'defense':1 , 'power':5 , 'xp':50 , 'death_function': entities.monster_death, 'speed':5}}, 
 'zombiesheep':    {'char':'z', 'color':libtcod.yellow,      'tilechar':data.TILE_SKEL_GREEN,   'fighter':{'hp':30 , 'defense':2 , 'power':6 , 'xp':60 , 'death_function': entities.monster_death, 'speed':7}}, 
}

#add help on how to use this
#basically, set = to list of lists. Each list gives a chance (arbitrary units) and a level
#map.py will use this info to create monster_chances list to figure out which monsters to select for map
#[[chance, dungeon_level]]

mobchances = {}
mobchances = {
	'johnstein':    [[100,1]],
	'greynaab':     [[60, 1], [35, 3], [10, 5]],
	'jerbear':      [[50, 1], [30, 3], [15, 5]],
	'zombiesheep':  [[40, 1], [25, 3], [20, 5]]
}

items={}
items = {
	'heal':       {'name':'healing potion',           'char':'!', 'color':libtcod.red,          'item':{'use_function': entities.cast_heal}}, 
	'lightning':  {'name':'scroll of lightning bolt', 'char':'?', 'color':libtcod.yellow,       'item':{'use_function': entities.cast_lightning}}, 
	'fireball':   {'name':'scroll of fireball',       'char':'?', 'color':libtcod.red,          'item':{'use_function': entities.cast_fireball}}, 
	'confuse':    {'name':'scroll of confusion',      'char':'?', 'color':libtcod.light_violet, 'item':{'use_function': entities.cast_confusion}}, 

	'sword':      {'name':'sword',  'char':'/', 'color':libtcod.sky,           'equipment':{'slot':'right hand' ,   'power_bonus'  :5  }}, 
	'shield':     {'name':'shield', 'char':'[', 'color':libtcod.darker_orange, 'equipment':{'slot':'left hand'  ,   'defense_bonus':3  }},

	'crystal':    {'name':'power crystal',      'char':'$', 'color':libtcod.sky, 'item':{'use_function': entities.use_crystal}}

}

itemchances = {}
itemchances = {
	'heal':       [[100,1]],
	'lightning':  [[10, 1], [25, 3], [50, 5]],
	'fireball':   [[10, 1], [25, 3], [50, 5]],
	'confuse':    [[10, 1], [25, 3], [50, 5]],
	'sword':      [[10, 1], [25, 3], [50, 5]],
	'shield':     [[10, 1], [25, 3], [50, 5]],
    'crystal':    [[1000,1]]
}

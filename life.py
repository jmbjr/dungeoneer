import libtcodpy as libtcod
from gamestuff import *
import data
import entitydata
import time

class World(object):
	def __init__(self, nwidth, nheight, alivechar, deadchar):
		self.nwidth = nwidth
		self.nheight = nheight
		self.alive = alivechar
		self.dead = deadchar
		self.world =[]
		self.con = libtcod.console_new(self.nwidth,self.nheight)

		self.init_world()

	def init_world(self):
		self.world = [[ self.random_cell()
		for yy in range(self.nheight) ]
			for xx in range(self.nwidth) ]

	def get_world(self):
		libtcod.console_clear(self.con)
		for yy in range(self.nheight):		
			for xx in range(self.nwidth):	
				libtcod.console_print_ex(self.con, xx, yy, libtcod.BKGND_NONE, libtcod.LEFT,self.world[xx][yy])
		return self.con

	def update(self):
		new_world = []
		new_world = [[ self.dead
			for yy in range(self.nheight) ]
				for xx in range(self.nwidth) ]

		for yy in range(self.nheight):		
			for xx in range(self.nwidth):	
				state = self.world[xx][yy]
				num_neighbors = self.neighbors(xx,yy)
				#print str(xx) + '/' + str(yy) + ':' + str(state) + '\t' + str(num_neighbors)
				if state == self.alive:
					#check rules 1 & 3 (rule 2, nothing happens)
					if num_neighbors <2 or num_neighbors >3:
						#rule 1: #neighbors < 2, alive->dead
						#rule 3: #neighbors = 4, alive->dead
						new_world[xx][yy] = self.dead
						#print '!!! DEATH !!!'
					else:
						new_world[xx][yy] = self.alive
						#print 'STAYIN ALIVE!'
				else: #dead
					#check rule 4
					if num_neighbors == 3:
						#rule 4: #neighbors = 3 alive, dead->alive
						new_world[xx][yy] = self.alive
						#print '??? BACK FROM DEATH ???'

		self.world = new_world
			
	def random_cell(self):
		if flip_coin() == 0:
			return self.dead
		else:
			return self.alive

	def neighbors(self, xx,yy):
		num_neighbors=0

		if xx != 0: #not far left
			if self.world[xx-1][yy] == self.alive:
				num_neighbors+=1

		if xx !=self.nwidth-1: #not far right
			if self.world[xx+1][yy] == self.alive:
				num_neighbors+=1			

		if yy != 0: #not far bottom
			if self.world[xx][yy-1] == self.alive:
				num_neighbors+=1

		if yy != self.nheight-1: #not far top
			if self.world[xx][yy+1] == self.alive:
				num_neighbors+=1

		if xx != 0 and yy != 0: #not bottom left
			if self.world[xx-1][yy-1] == self.alive:
				num_neighbors+=1

		if xx != 0 and yy != self.nheight-1: #not top left
			if self.world[xx-1][yy+1] == self.alive:
				num_neighbors+=1

		if xx != nwidth-1 and yy != 0: #not bottom right
			if self.world[xx+1][yy-1] == self.alive:
				num_neighbors+=1

		if xx != nwidth-1 and yy != nheight-1: #not top right
			if self.world[xx+1][yy+1] == self.alive:
				num_neighbors+=1

		return num_neighbors



	def __str__(self):
		ret=''
		for yy in range(self.nheight):	
			ret= ret + '|'		
			for xx in range(self.nwidth):
				ret= ret + str(self.world[xx][yy])
			ret= ret + '|\n'
		return(ret)


#create world
nwidth = 50
nheight = 50
alivechar = '+'
deadchar = ' '
speed = .5
inc = 0.1

world = World(nwidth,nheight, alivechar, deadchar)

libtcod.console_set_custom_font('oryx_tiles3.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 12)
libtcod.console_init_root(nwidth, nheight, 'johnstein\'s Game of RogueLife!', False, libtcod.RENDERER_SDL)
libtcod.sys_set_fps(30)

libtcod.console_map_ascii_codes_to_font(256   , 32, 0, 5)  #map all characters in 1st row
libtcod.console_map_ascii_codes_to_font(256+32, 32, 0, 6)  #map all characters in 2nd row

mouse = libtcod.Mouse()
key = libtcod.Key()  

#initialize population

#enter game loop and check for user input
while not libtcod.console_is_window_closed():
	libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

	if key.vk == libtcod.KEY_ESCAPE:
		break
	if key.vk == libtcod.KEY_TAB:
		world.init_world()
	if key.vk == libtcod.KEY_UP:
		speed-=inc
	if key.vk ==libtcod.KEY_DOWN:
		speed+=inc
	if key.vk == libtcod.KEY_RIGHT:
		inc+=.05
	if key.vk ==libtcod.KEY_LEFT:
		inc-=.05

	#display world
	con_world = world.get_world()
	libtcod.console_blit(con_world, 0, 0, nwidth, nheight, 0, 0, 0)
	libtcod.console_flush()
	#waitkey = libtcod.console_wait_for_keypress(True)
	
	#check rules and create new population
	#replace old population with new one
	time.sleep(speed)
	world.update()



def draw_world(world):
	for y in range(data.CAMERA_HEIGHT):
		for x in range(data.CAMERA_WIDTH):
			(map_x, map_y) = (Game.camera_x + x, Game.camera_y + y)
			visible = libtcod.map_is_in_fov(Game.player.fighter.fov, map_x, map_y)
			wall = Game.map[Game.dungeon_levelname].block_sight(map_x, map_y)

			if data.ASCIIMODE:
				thewallchar  = data.WALL_CHAR
				thegroundchar = data.GROUND_CHAR
			else:
				thewallchar  = data.TILE_WALL
				thegroundchar = data.TILE_GROUND

			#thegroundchar = data.GROUND_CHAR
			if not visible:
				#tile not visible
				if wall:
					color_wall_ground = data.COLOR_DARK_WALL
					char_wall_ground = thewallchar
				else:
					color_wall_ground = data.COLOR_DARK_GROUND
					char_wall_ground = thegroundchar
				fov_wall_ground = libtcod.grey
			else:
				#tile is visible
				Game.map[Game.dungeon_levelname].set_explored(map_x, map_y)
				if wall:
					color_wall_ground = data.COLOR_LIGHT_WALL
					char_wall_ground = thewallchar
				else:
					color_wall_ground = data.COLOR_LIGHT_GROUND
					char_wall_ground = thegroundchar
				fov_wall_ground = libtcod.white

			if Game.map[Game.dungeon_levelname].explored(map_x, map_y):
				libtcod.console_put_char_ex(Game.con, x, y, char_wall_ground, fov_wall_ground, color_wall_ground)
			

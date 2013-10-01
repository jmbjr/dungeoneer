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
		self.population =[]

		self.con = libtcod.console_new(self.nwidth,self.nheight)

		self.init_world()

	def init_world(self):
		self.population = [[ flip_coin()
		for yy in range(self.nheight) ]
			for xx in range(self.nwidth) ]

	def get_world(self):
		libtcod.console_clear(self.con)
		for yy in range(self.nheight):		
			for xx in range(self.nwidth):
				my_color=self.random_color()	
				libtcod.console_set_default_foreground(self.con, my_color)
				libtcod.console_print_ex(self.con, xx, yy, libtcod.BKGND_NONE, libtcod.LEFT, self.get_entity(self.population[xx][yy]))
		return self.con

	def get_entity(self, entity):

		if entity == 0:
			return ' '
		elif entity < 10:
			return '.'
		elif entity >=10 and entity < 20:
			return ','
		elif entity >=20 and entity < 30:
			return '_'
		elif entity >=30 and entity < 40:
			return '-'
		elif entity >=40 and entity < 50:
			return '|'
		elif entity >=50 and entity < 60:
			return '+'
		elif entity >=60 and entity < 70:
			return 'x'
		elif entity >=70 and entity < 80:
			return '='
		elif entity >=80 and entity < 90:
			return '#'
		elif entity >=90 and entity < 100:
			return 'o'
		else:
			return '@'

	def update(self):
		new_population = []
		new_population = [[ 0
			for yy in range(self.nheight) ]
				for xx in range(self.nwidth) ]

		for yy in range(self.nheight):		
			for xx in range(self.nwidth):	

				if self.isalive(self.population[xx][yy]):
					state = self.alive
				else:
					state = self.dead

				num_neighbors = self.neighbors(xx,yy)
				#print str(xx) + '/' + str(yy) + ':' + str(state) + '\t' + str(num_neighbors)
				if state == self.alive:
					#check rules 1 & 3 (rule 2, nothing happens)
					if num_neighbors <2 or num_neighbors >3:
						#rule 1: #neighbors < 2, alive->dead
						#rule 3: #neighbors = 4, alive->dead
						new_population[xx][yy] = 0
						#print '!!! DEATH !!!'
					else:
						new_population[xx][yy] = self.population[xx][yy]+1
						#print 'STAYIN ALIVE!'
				else: #dead
					#check rule 4
					if num_neighbors == 3:
						#rule 4: #neighbors = 3 alive, dead->alive
						new_population[xx][yy] = self.population[xx][yy]+1
						#print '??? BACK FROM DEATH ???'

		self.population = new_population
			
	def random_cell(self):
		if flip_coin() == 0:
			return self.dead
		else:
			return self.alive

	def random_color(self):
		rr = libtcod.random_get_int(0,0,255)
		gg = libtcod.random_get_int(0,0,255)
		bb = libtcod.random_get_int(0,0,255)
		return libtcod.Color(rr,gg,bb)

	def isalive(self,entity):
		if entity > 0:
			return True
		else:
			return False

	def neighbors(self, xx,yy):
		num_neighbors=0

		if xx != 0: #not far left
			if self.isalive(self.population[xx-1][yy]):
				num_neighbors+=1

		if xx !=self.nwidth-1: #not far right
			if self.isalive(self.population[xx+1][yy]):
				num_neighbors+=1			

		if yy != 0: #not far bottom
			if self.isalive(self.population[xx][yy-1]):
				num_neighbors+=1

		if yy != self.nheight-1: #not far top
			if self.isalive(self.population[xx][yy+1]):
				num_neighbors+=1

		if xx != 0 and yy != 0: #not bottom left
			if self.isalive(self.population[xx-1][yy-1]):
				num_neighbors+=1

		if xx != 0 and yy != self.nheight-1: #not top left
			if self.isalive(self.population[xx-1][yy+1]):
				num_neighbors+=1

		if xx != nwidth-1 and yy != 0: #not bottom right
			if self.isalive(self.population[xx+1][yy-1]):
				num_neighbors+=1

		if xx != nwidth-1 and yy != nheight-1: #not top right
			if self.isalive(self.population[xx+1][yy+1]):
				num_neighbors+=1

		return num_neighbors



	def __str__(self):
		ret=''
		for yy in range(self.nheight):	
			ret= ret + '|'		
			for xx in range(self.nwidth):
				ret= ret + str(self.population[xx][yy])
			ret= ret + '|\n'
		return(ret)


#create world
nwidth = 100
nheight = 60
alivechar = '+'
deadchar = ' '
speed = .1
inc = 0.01

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

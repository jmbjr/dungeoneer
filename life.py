import libtcod
import data
import gamedata
import cursesx
from gamestuff import *
import entitydata
import time
import math
import keys
import guistuff

class World(object):
    def __init__(self, nwidth, nheight, alivechar, deadchar, char_option, rndgen, gui):
        
        self.nwidth = nwidth
        self.nheight = nheight 
        self.alive = alivechar
        self.dead = deadchar
        self.char_option = char_option
        self.population =[]
        self.generation = 0
        self.rndgen = rndgen
        self.gui = gui
        self.con = self.gui.console(self.nwidth, self.nheight)

        self.init_world()

    def init_world(self):
        self.generation = 0
        self.population = [[ flip_coin(self.rndgen)
        for yy in range(self.nheight) ]
            for xx in range(self.nwidth) ]

    def check_stable(self):
        MAX_POP = 125
        num_unstable=0
        for yy in range(self.nheight):
            for xx in range(self.nwidth):
                if self.population[xx][yy] > 2 and self.population[xx][yy] <=MAX_POP:
                    num_unstable+=1

        if num_unstable < 5 and self.generation >500:
            self.init_world()    

    def get_world(self):
        self.gui.clear(self.con)

        for yy in range(self.nheight):        
            for xx in range(self.nwidth):
                #my_color=self.random_color()
                my_color = self.get_color(self.population[xx][yy])
                self.gui.printstr(self.con, xx, yy, self.get_entity(self.population[xx][yy], self.char_option), my_color)

        return self.con

    def get_entity(self, entity, option):
        Max_ASCII = 125
        ASCII_offset = 23

        if option is 'symbol':

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
        elif option is 'ascii':
            if entity == 0:
                thechar = ' '
            elif entity < 10:
                thechar = entity
            elif entity >=10 and entity <= Max_ASCII - ASCII_offset:
                thechar =  chr(entity + ASCII_offset)
            else:
                thechar = chr(Max_ASCII + 1)

            return str(thechar)

    def update(self):
        self.generation+=1
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
            
    def get_color(self, code):
#TODO: set up some graphics options and set them in data
#TODO: then have an options menu on startup to choose the GRAPHICSMODE and sub-options for that graphics mode
#TODO: i.e. rgb, 7 color mode, etc
#TODO: then in this function, just call the guistuff.colorcode(option) or something
        #left this block of gamedata.GRAPHICSMODE since it's specialized to life.py
        if gamedata.GRAPHICSMODE == 'libtcod':
	    rr = 8
	    gg = 8 + code*2
	    bb = 8

	    if gg > 255:
	        rr = 128
	        gg = 255
	        bb = 128

	    return libtcod.Color(rr,gg,bb)
        elif gamedata.GRAPHICSMODE == 'curses':
            fg = round(code/16) + 1
            themod = code%16 
            if fg <=0:
                fg = 0
            elif fg >=8:
                fg = 7
                return cursesx.color_pair(int(fg)) | cursesx.A_STANDOUT            
            if themod <= 8:
                return cursesx.color_pair(int(fg))
            else:
                return cursesx.color_pair(int(fg)) | cursesx.A_BOLD
        else: 
            print('error in get_color. Wrong GRAPHICSMODE')
       
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

        if xx != self.nwidth-1 and yy != 0: #not bottom right
            if self.isalive(self.population[xx+1][yy-1]):
                num_neighbors+=1

        if xx != self.nwidth-1 and yy != self.nheight-1: #not top right
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

def life(stdscr):
    if gamedata.GRAPHICSMODE == 'curses':
        for col in range(1,8):
            cursesx.init_pair(col, col, cursesx.COLOR_BLACK)
       
    gui = guistuff.Guistuff(gamedata.GRAPHICSMODE)
 
#TODO make these settable in an options window
    #create world
    nwidth = 100 
    nheight = 60
    alivechar = '+'
    deadchar = ' '
    char_option = 'ascii'
    speed = .1
    inc = 0.01

    # default generator
    default = libtcod.random_get_instance()
    # another random generator
    my_random = libtcod.random_new()
    # a random generator with a specific seed
    my_determinist_random = libtcod.random_new_from_seed(0xdeadbeef)

    world = World(nwidth,nheight, alivechar, deadchar, char_option, my_determinist_random, gui)
    mouse,key = gui.prep_console(world.con, world.nwidth, world.nheight)

    #initialize population

    #enter game loop and check for user input
    while not gui.isgameover():
        thekey = gui.getkey(world.con, mouse, key)
    
#TODO add some enums here or find ones that work
        if thekey == keys.TAB:
            world.init_world()
        elif thekey == keys.UP:
            speed-=inc
        elif thekey ==keys.DOWN:
            speed+=inc
        elif thekey == keys.RIGHT:
            inc+=.01
        elif thekey ==keys.LEFT:
            inc-=.01
        elif thekey == keys.ESC:
                break             

        if speed <0:
            speed = .001
        #display world
        current_world = world.get_world()
        gui.con_blit(current_world, 0, 0, world.nwidth, world.nheight, 0, 0, 0)
        gui.flush(current_world)
    
        #check rules and create new population
        #replace old population with new one
        time.sleep(speed)
        world.update()
        world.check_stable()

def main():
    if gamedata.GRAPHICSMODE == 'libtcod':
        life(None)
    elif gamedata.GRAPHICSMODE == 'curses':
        cursesx.wrapper(life)
    else:
        print('Error in __name__. wrong GRAPHICSMODE')


import gamedata
import sys

class Jumptable(object):
    def play_dungeoneer_gfx(self):
        print('Playing Dungeoneer!!!')
        gamedata.ASCIIMODE = False

    def play_dungeoneer_ascii(self):
        print('Playing Dungeoneer!!!')
        gamedata.ASCIIMODE = True

    def play_life(self):
        print('Going to play life! Press a key!')
        gamedata.ASCIIMODE = True
        import life
        life.main()

    def jump(self,cmd):
        self.jump_table[cmd](self)

    jump_table = {'1':play_dungeoneer_gfx, '2':play_dungeoneer_ascii, '3':play_life}

goodchoice = False

if sys.platform == 'darwin':
   gamedata.GRAPHICSMODE = 'libtcod'
elif sys.platform == 'linux2':
   gamedata.GRAPHICSMODE = 'curses'
elif sys.platform == 'win32':
   gamedata.GRAPHICSMODE = 'libtcod'
else:
    raise ImportError('unknown os', sys.platform)

print('Dungoneer! by johnstein')
print('-----------------------')
while not goodchoice:
    print('    Play!               ')
    print('1. Dungeoneer (graphics)')
    print('2. Dungeoneer (ASCII)   ')
    print('3. Rogue-Life           ')
    choice = raw_input()

    if choice in ['1', '2', '3']:
        goodchoice = True
        j = Jumptable()
        j.jump(choice)


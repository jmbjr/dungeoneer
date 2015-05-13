import gamedata

class Jumptable(object):
    def play_dungeoneer(self):
        print('Playing Dungeoneer!!!')

    def play_life(self):
        print('Going to play life! Press a key!')
        import life
        life.main()

    def jump(self,cmd):
        self.jump_table[cmd](self)

    jump_table = {'1':play_dungeoneer, '2':play_life}


goodchoice = False
graphicsmode  = {'1':'libtcod', '2':'curses'}
asciimode     = {'1':True,      '2':False}

print('Dungoneer! by johnstein')
print('-----------------------')
while not goodchoice:
    print('    Options Setup:     ')
    print('1. libtcod (graphical)')
    print('2. curses  (terminal) ')
    choice = raw_input()

    if choice == '1' or choice == '2':
        goodchoice = True
        gamedata.GRAPHICSMODE = graphicsmode[choice]

goodchoice = False
if choice == '1': #libtcod
    while not goodchoice:
        print('    libtcod Mode:     ')
        print('1. ASCII Mode         ')
        print('2. Graphics Mode      ')
        choice = raw_input()

        if choice == '1' or choice == '2':
            goodchoice = True
            gamedata.ASCIIMODE = asciimode[choice]

goodchoice = False
while not goodchoice:
    print('    Play!             ')
    print('1. Dungeoneer         ')
    print('2. Rogue-Life         ')
    choice = raw_input()

    if choice == '1' or choice == '2':
        goodchoice = True
        j = Jumptable()
        j.jump(choice)


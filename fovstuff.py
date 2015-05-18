import libtcod
import gamedata

class Fovstuff(object):
    def __init__(self, fovmode):
        self.fovmode = fovmode

    def fovmap(self, nwidth, nheight):
        if self.fovmode == 'libtcod':
            return libtcod.map_new(nwidth, nheight)
        else:
            self.err_fovmode('fovmap')

    def set_map_properties(self, fovmap, xx, yy, block_sight, blocked):
        if self.fovmode == 'libtcod':
            libtcod.map_set_properties(fovmap, xx, yy, block_sight, blocked)
        else:
            self.err_fovmode('fovmap')


    def err_fovmode(self, func):
        print('Error in guistuff.' + func + '. wrong FOVMODE: ' + self.fovmode)            
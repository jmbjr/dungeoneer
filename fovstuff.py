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

    def map_set_properties(self, fovmap, xx, yy, block_sight, blocked):
        if self.fovmode == 'libtcod':
            libtcod.map_set_properties(fovmap, xx, yy, block_sight, blocked)
        else:
            self.err_fovmode('set_map_properties')

    def map_is_in_fov(self, fovmap, xx, yy):
        if self.fovmode == 'libtcod':
            return libtcod.map_is_in_fov(fovmap, xx, yy)
        else:
            self.err_fovmode('map_is_in_fov')

    def map_compute_fov(self, fovmap, xx, yy, radius, light_walls, algo):
        if self.fovmode == 'libtcod':
            return libtcod.map_compute_fov(fovmap, xx, yy, radius, light_walls, algo)
        else:
            self.err_fovmode('map_compute_fov')


    def err_fovmode(self, func):
        print('Error in guistuff.' + func + '. wrong FOVMODE: ' + self.fovmode)            
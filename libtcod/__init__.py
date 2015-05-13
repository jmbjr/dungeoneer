import sys

if sys.platform == 'darwin':
    from libtcod.osx import *
elif sys.platform == 'linux2':
    from libtcod.linux import *
elif sys.platform == 'windows':
    from libtcod.windows import *
else:
    raise ImportError('unknown os', sys.platform)


import gamedata

if gamedata.GRAPHICSMODE == 'curses':
    try:
        from curses import *
    except:
        print('Error importing curses!')
        raise ImportError('curses module not available!')


import gamedata

if gamedata.GRAPHICSMODE == 'curses':
    try:
        from curses import *
        import curses.ascii as ascii
    except:
        print('Error importing curses!')
        raise ImportError('curses module not available!')


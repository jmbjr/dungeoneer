def is_blocked(x, y, Game):
    #first test the map tile
    if Game.map[x][y].blocked:
        return True

    #now check for any blocking objects
    for object in Game.objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False
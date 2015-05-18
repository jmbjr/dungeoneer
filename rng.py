import libtcod

def flip_coin(rndgen=False):
    if not rndgen:
        rndgen = 0
    return (random_int(rndgen,0,1))

def random_choice(chances_dict):
    #choose one option from dict of chances and return key
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]

def random_int(seed, min, max):
    return libtcod.random_get_int(seed, min, max)

def random_choice_index(chances): #choose one option from list of chances. return index
    #the dice will land on some number between 1 and sum of the chances
    dice = random_int(0, 1, sum(chances))

    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds with this choice
        if dice <= running_sum:
            return choice
        choice +=1
        
def roll_dice(dicelist):
    dice=[]
    for [die_low, die_high] in dicelist:
        roll = random_int(0,die_low,die_high)
        dice.append(roll)

    return [sum(dice), dice]

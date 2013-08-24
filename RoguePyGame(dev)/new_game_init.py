# new game initialization

def player():
    player = Object("player", int((((screensize[0])/2)/32)-1), int((((screensize[1])/2)/32)-1), image.player)
    '''print player.xcoord, player.ycoord'''
    player.fighter = Fighter(player, 50, 1, 1, 1, 0)
    
    return player
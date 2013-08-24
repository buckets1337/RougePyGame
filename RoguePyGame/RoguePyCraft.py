#! c:\Python27
#! requires Python v2.7 and PyGame installed

#import modules and libraries
import sys, pygame, pygame.mixer, time, random
from pygame.locals import *
import libtcodpy as libtcod
import CONFIG




## Color Definitions

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (100,100,100)
YELLOW = (255,255,0)
RED = (255,0,0)
DARK_RED = (128,0,0)
BLUE = (0,0,255)
DARK_BLUE = (0,0,70)
GREEN = (0,160,40)
DARK_GREEN = (0,70,20)
BRIGHT_GREEN = (0,255,0)
PAPYRUS = (207,175,59)
DIRT = (80, 70, 20)


## initializes pygame

pygame.init()
#sets key repeat to on
pygame.key.set_repeat(200, 100)

# sets screen size and creates global timer
screensize = width, height = CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT
clock = pygame.time.Clock()

# creates the screen and sets the base display font
screen = pygame.display.set_mode(screensize)
BASE_FONT = pygame.font.Font(None, 12)


## Image Prep definitions
def image_prep_alpha(img):
    image = pygame.image.load(img)
    image = pygame.Surface.convert_alpha(image)
    image = pygame.transform.scale(image, (32,32))
    return image
    
def image_prep(img):
    image = pygame.image.load(img).convert()
    image = pygame.transform.scale(image, (32, 32))
    return image
    
class Generic(object):
    pass
    
# creates a generic container for images called at image.<filename>
image = Generic()
image.player = image_prep_alpha("img\Player.png")
image.playercorpse = image_prep_alpha("img\PlayerCorpse.png")
image.snake = image_prep_alpha("img\Snake.png")
image.snakecorpse = image_prep_alpha("img\SnakeCorpse.png")

image.wall = image_prep("img\Wall.png")
image.exploredwall = image_prep_alpha("img\ExploredWall.png")
image.floor = image_prep("img\Floor.png")
image.exploredfloor = image_prep_alpha("img\ExploredFloor.png")





## Load sounds and streamed music to the mixer
bumpsound = pygame.mixer.Sound('bump.wav')
metaltinksound = pygame.mixer.Sound('swordHit.wav')
attacksound = pygame.mixer.Sound('punch.wav')



## global variable init

ScreenMode = "window"
GameState = "playing"
death_message = False




## data structures init

Objects = []
Monsters = []
CurrentMap = []
MapList = []
Messages = []



## class definitions

class Object:       # An Object is a thing that draws to the map, may or may not move
    def __init__(self, name, xcoord, ycoord, img, blocked=False, block_sight=False, fighter=None, ai=None):
        self.x = 32*xcoord
        self.xcoord = xcoord
        self.y = 32*ycoord
        self.ycoord = ycoord
        self.img = img
        self.blocked = blocked
        self.block_sight = block_sight
        self.fighter = fighter
        self.ai = ai
        self.name = name

        
        Objects.append(self)
        
        '''print Objects'''

    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.xcoord, self.ycoord):
            screen.blit(self.img, (self.x, self.y))
        elif CurrentMap[self.xcoord][self.ycoord].explored == True:
            if CurrentMap[self.xcoord][self.ycoord].terrain == "wall":
                screen.blit(image.exploredwall, (self.x, self.y))
            if CurrentMap[self.xcoord][self.ycoord].terrain == "floor":
                screen.blit(image.exploredfloor, (self.x, self.y))

        
    def move(self, xmovement, ymovement):
        global Objects, fov_map, fov_recompute
    
        if is_blocked((self.xcoord+xmovement),(self.ycoord+ymovement)):
            #print "blocked"
            if self == player:
                for object in Objects:
                    if object.xcoord == (self.xcoord+xmovement) and object.ycoord == (self.ycoord+ymovement):
                        #print object.ai
                        if object.ai is not None:
                            player.fighter.attack(object)
                        else:
                            if object.blocked == True:
                                #message("blocked at "+(str(self.xcoord+xmovement))+","+(str(self.ycoord+ymovement)), YELLOW)
                                bumpsound.play()
                                #player.fighter.hp -= 1
                                #message("Ouch! Bumped for 1 damage", RED)
            else:
                #print "init"
                flag = True
                while flag == True:
                    direction = random.randint(0,4)
                    if direction == 0:
                        #print 0
                        if not is_blocked(self.xcoord, self.ycoord - 1):
                            self.move(0, -1)
                            flag = False
                    elif direction == 1:
                        #print 1
                        if not is_blocked(self.xcoord + 1, self.ycoord):
                            self.move(1, 0)
                            flag = False
                    elif direction == 2:
                        #print 2
                        if not is_blocked(self.xcoord, self.ycoord + 1):
                            self.move(0, 1)
                            flag = False
                    elif direction == 3:
                        #print 3
                        if not is_blocked(self.xcoord -1, self.ycoord):
                            self.move(-1, 0)
                            flag = False
        else:                               # not blocked
        
            CurrentMap[self.xcoord][self.ycoord].objects.remove(self)
            self.xcoord += xmovement
            if self == player:
                for object in Objects:
                    if object != player:
                        object.x -= 32 * xmovement
            else:
                self.x += 32 * xmovement
                
            self.ycoord += ymovement
            if self == player:
                for object in Objects:
                    if object != player:
                        object.y -= 32 *ymovement
            else:
                self.y += 32 * ymovement
                
            CurrentMap[self.xcoord][self.ycoord].objects.append(self)
            CurrentMap[self.xcoord][self.ycoord].update()
            
                
            if self.xcoord <=0:
                self.xcoord = 0
                if self == player:
                    bumpsound.play()
            elif self.xcoord >= CONFIG.MAP_WIDTH:
                self.xcoord = CONFIG.MAP_WIDTH
                if self == player:
                    bumpsound.play()
            if self.ycoord <=0:
                self.ycoord = 0
                if self == player:
                    bumpsound.play()
            elif self.ycoord >= CONFIG.MAP_HEIGHT:
                self.ycoord = CONFIG.MAP_HEIGHT
                if self == player:
                    bumpsound.play()
                    
        fov_recompute = True
        for object in Objects:
            if libtcod.map_is_in_fov(fov_map, object.xcoord, object.ycoord):
                CurrentMap[object.xcoord][object.ycoord].explored = True
                #print(str(object.xcoord) + "," + str(object.ycoord)+ " explored")
            
            '''print "player("+str(self.xcoord)+","+str(self.ycoord)+")"'''

class Rectangle:    # A definition of a generic rectangle on the map with helpful functions
    def __init__(self, xpos, ypos, width, height):
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        self.x2 = xpos + width
        self.y2 = ypos + height
        self.xcenter = self.xpos + round(width/2)
        self.ycenter = self.ypos + round(height/2)
        
    def centercoords(self):
        centercoords = int(self.xcenter), int(self.ycenter)
        return centercoords
        
    def is_intersecting(self, other):
        return(self.xpos <= other.x2 and self.x2 >= other.xpos and self.ypos <= other.y2 and self.y2 >= other.ypos)

class Tile:         # A Tile is a placeholder for information about a map tile (terrain, etc)
    def __init__(self, xcoord, ycoord, terrain=None, block_sight=False, blocked=False, explored=False):
        self.xcoord = xcoord
        self.ycoord = ycoord
        self.terrain = terrain
        self.block_sight = block_sight
        self.blocked = blocked
        self.explored = explored
        self.objects = []
        
        for object in self.objects:
            if object.block_sight == True:
                self.block_sight = True
                
        for object in self.objects:
            if object.blocked == True:
                self.blocked == True
                
    def update(self):
        for object in self.objects:
            if object.block_sight == True:
                self.block_sight = True
                
        for object in self.objects:
            if object.blocked == True:
                self.blocked == True

class Map:          # A map is an array of tiles with a name.  Is always saved to MapList

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height

    def make_dungeon_map(self, num_rooms, width, height):     # makes a new underground map
    
        def create_h_tunnel(x1,x2,y):   # creates horizontal segment of hallway
            global CurrentMap
            for x in range(min(x1,x2), max(x1,x2)+1):
                '''print "{"+str(x)+","+str(y)+"}"'''
                '''print CurrentMap[x][y]'''
                CurrentMap[x][y].terrain = "floor"

        def create_v_tunnel(y1,y2,x):   # creates vertical segment of hallway
            global CurrentMap
            for y in range(min(y1,y2), max(y1,y2)+1):
                '''print "{"+str(x)+","+str(y)+"}"'''
                '''print CurrentMap[x][y]'''
                CurrentMap[x][y].terrain = "floor"
                
        def generate_monsters(rect, number_monsters):       #generates the monsters in a room
            global Monsters
            xpos = random.randint(rect.xpos, rect.xpos+rect.width-1)
            ypos = random.randint(rect.ypos, rect.ypos+rect.height-1)
            
            
            for i in range(0, number_monsters):
                monster = Object("snake", xpos, ypos, image.snake, blocked=True)
                monster.fighter = Fighter(monster, 6, 0, 0, 1, 100)
                monster.ai = MonsterAI(monster)
                
            Monsters.append(monster)
            CurrentMap[xpos][ypos].objects.append(monster)
            CurrentMap[xpos][ypos].update()
                
        global CurrentMap, MapList
        
        # creates CurrentMap, an array of arrays that describes the map to be drawn, 
        # and fills it with tiles that describe a single tile's traits
        x=0
        y=0
        rooms = []
        room_intersects = 0
        
        CurrentMap = [[None for y in range(0, height)] for x in range(0, width)]
        
        for x in range(0, width):
            for y in range(0, height):
                tile = Tile(x,y)
                CurrentMap[x][y] = tile
                

        # fills the map with solid walls
        for x in range(0, width):
            for y in range(0, height):
                CurrentMap[x][y].terrain = "wall"
        
        # removes wall tiles to create rooms
        for i in range(0, num_rooms):
            # generates dimensions for the room
            w = random.randrange(CONFIG.ROOM_MIN_SIZE,CONFIG.ROOM_MAX_SIZE)
            h = random.randrange(CONFIG.ROOM_MIN_SIZE,CONFIG.ROOM_MAX_SIZE)
            xpos = random.randrange(1, (CONFIG.MAP_WIDTH)-w-1)
            ypos = random.randrange(1, (CONFIG.MAP_HEIGHT)-h-1)

            # defines the shape of the room
            room = Rectangle(xpos, ypos, w, h)
            center = room.centercoords()
            
            for other_room in rooms:
                if room.is_intersecting(other_room):
                    room_intersects +=1
                    if room_intersects >= CONFIG.MAX_ROOM_INTERSECTS:
                        failed = True
                        pass
            
            # sets wall tiles to clear floor in the defined room
            for x in range(xpos, xpos+w):
                for y in range(ypos, ypos+h):
                    CurrentMap[x][y].terrain = "floor"
                    
                    
            if i == 0:
                if not is_blocked(center[0], center[1]):
                    # moves the player to the center of the first room
                    player.xcoord = center[0]
                    # player.x = (center[0]*32)
                    player.ycoord = center[1]
                    # player.y = (center[1]*32)
                    '''print player.xcoord, player.ycoord'''
                elif not is_blocked(center[0]+1, center[1]):
                    # moves the player to the center of the first room
                    player.xcoord = center[0]+1
                    # player.x = (center[0]*32)
                    player.ycoord = center[1]
                    # player.y = (center[1]*32)
                elif not is_blocked(center[0], center[1]+1):
                    # moves the player to the center of the first room
                    player.xcoord = center[0]
                    # player.x = (center[0]*32)
                    player.ycoord = center[1]+1
                    # player.y = (center[1]*32)
                
            else:
                # carve a hallway connecting this room to the last room
                flip = random.randint(0,1)

                if flip:
                    # horizontal first
                    create_h_tunnel(old_center[0], center[0], old_center[1])
                    
                    # then vertical
                    create_v_tunnel(old_center[1], center[1], center[0])
                    
                else:
                    # vertical first
                    create_v_tunnel(old_center[1], center[1], old_center[0])
                    
                    # then horizontal
                    create_h_tunnel(old_center[0], center[0], center[1])
                    
                
            flip = random.randint(0,1)
            if flip == 1:
                generate_monsters(room, 1)
            old_center = center
            rooms.append(room)
        
        # after all the rooms are carved, adds terrain to the object list so it will draw and can be interacted with
        for x in range(0, width):
            for y in range(0, height):
                if CurrentMap[x][y].terrain == "wall":
                    wall = (Object("wall", CurrentMap[x][y].xcoord, CurrentMap[x][y].ycoord, image.wall, blocked=True, block_sight=True))
                    CurrentMap[x][y].objects.append(wall)
                    CurrentMap[x][y].update()
                elif CurrentMap[x][y].terrain == "floor":
                    floor = (Object("floor", CurrentMap[x][y].xcoord, CurrentMap[x][y].ycoord, image.floor))
                    CurrentMap[x][y].objects.append(floor)
                    CurrentMap[x][y].update()

        # sets the map's TileList to CurrentMap
        self.TileList = CurrentMap
        
        # appends the map to the MapList
        MapList.append(self)

class Fighter:      # Constructor holding the traits for anything that engages in combat
    def __init__(self, owner, hp, power, defense, speed, xp):
        self.hp = hp
        self.max_hp = hp
        self.power = power
        self.defense = defense
        self.speed = speed
        self.owner = owner
        self.xp = xp
        self.level = 0
        self.to_level = 200
        self.to_level = int(self.to_level * (1.0 + (self.level * 0.1)))
        
    def attack(self, other):
        attack_damage = self.power + (random.randint(0, self.speed))
        other.fighter.hp -= attack_damage
        message_string = self.owner.name + " attacks " + other.name + " for " + str(attack_damage) + " damage."
        if self.owner == player:
            message_color = WHITE
            attacksound.play()
        else:
            message_color = RED
        message(message_string, message_color)
        if other.fighter.hp <= 0:
            other.fighter.kill()
            
    def kill(self):     # kills off fighter.owner
        global GameState, Monsters, Objects
        if self.owner == player:
            player.img = image.playercorpse
            GameState = "dead"
        else:       #turns the img to corpse, removes ai, and grants xp
            self.owner.img = image.snakecorpse
            self.owner.ai = None
            player.fighter.xp += self.xp
            self.owner.blocked = False
            Monsters.remove(self.owner)
            Monsters.insert(0, self.owner)
            message("You killed a " + self.owner.name + ". +" + str(self.xp) + " exp", YELLOW)
            
    def level_up(self):
        self.to_level = int(self.to_level * (1.5 + (self.level * 0.1)))
        self.xp = 0
        self.level += 1
        #eventually this will enable choice at level up
        self.max_hp += 10
        self.hp += 10
        message("Congratulations! You are now level " + str(player.fighter.level), BRIGHT_GREEN)

class MonsterAI:    # Constructor that controls the behavior of a monster
    def __init__(self, owner):
        self.owner = owner
        
    def move(self):        # controls enemy movement
        for i in range(0, self.owner.fighter.speed):
            path = vector_to(self.owner, player)
            x_path = 0
            y_path = 0

            if path[0] > 0:
                x_path = 1
            elif path[0] < 0:
                x_path = -1
            elif path[0] == 0:
                x_path = 0
                
            if path[1] > 0:
                y_path = 1
            elif path[1] < 0:
                y_path = -1
            elif path[1] == 0:
                y_path = 0

            target = ((self.owner.xcoord + x_path),(self.owner.ycoord + y_path))
            if is_blocked(target[0], target[1]):
                flag = True
                while flag == True:
                    direction = random.randint(0,4)
                    if direction == 0:
                        #print 0
                        if not is_blocked(self.owner.xcoord, self.owner.ycoord - 1):
                            self.owner.move(0, -1)
                            flag = False
                    elif direction == 1:
                        #print 1
                        if not is_blocked(self.owner.xcoord + 1, self.owner.ycoord):
                            self.owner.move(1, 0)
                            flag = False
                    elif direction == 2:
                        #print 2
                        if not is_blocked(self.owner.xcoord, self.owner.ycoord + 1):
                            self.owner.move(0, 1)
                            flag = False
                    elif direction == 3:
                        #print 3
                        if not is_blocked(self.owner.xcoord -1, self.owner.ycoord):
                            self.owner.move(-1, 0)
                            flag = False
            if not is_blocked(target[0], target[1]) and (target[0] != player.xcoord or target[1] != player.ycoord):
                self.owner.move(x_path, y_path)
            elif target[0] == player.xcoord and target[1] == player.ycoord:           # is adjacent to the player
                self.owner.fighter.attack(player)

    def patrol(self):       # how an enemy moves when it is unaware of the player
        direction = random.randint(0,5)
        if direction == 0:
            self.owner.move(0,-1)
        elif direction == 1:
            self.owner.move(1,0)
        elif direction == 2:
            self.owner.move(0,1)
        elif direction == 3:
            self.owner.move(-1,0)
        else:
            pass
                
                
## helper functions

def is_blocked(xpos,ypos):      # returns the blocked trait of objects at xpos,ypos (boolean)
    blocked = False
    for i in range(0, len(Objects)):
        if xpos == Objects[i].xcoord and ypos == Objects[i].ycoord:
            object = Objects[i].blocked
            if object:
                blocked = object
                
    return blocked

def message(message, color):           # prints the message into the GUI messagebox console
    global Messages
    font = BASE_FONT
    messagetext = font.render(message, 1, color)
    Messages.insert(0, messagetext)

def percent_bar(label, label_color, x, y, width, height, base_attr, max_attr, base_color, max_color, is_labeled=True):       # renders a percent bar to the screen
    font = BASE_FONT
    label_string = font.render(label+": "+str(base_attr)+" / "+str(max_attr), 1, label_color)
    label_shadow = font.render(label+": "+str(base_attr)+" / "+str(max_attr), 1, BLACK)
    attr_max_bar = Rect(x, y, width, height)
    attr_bar_length = ((float(base_attr)/float(max_attr))*width)
    if attr_bar_length < 0:
        attr_bar_length = 0
    attr_current_bar = Rect(x, y, attr_bar_length, height)
    
    pygame.draw.rect(screen, max_color, attr_max_bar)
    pygame.draw.rect(screen, base_color, attr_current_bar)
    if is_labeled:
        screen.blit(label_shadow, (x+4, y+4))
        screen.blit(label_string, (x+3, y+3))

def vector_to(self, other):          # determines a vector (distance+direction) between coordinates of two entities
    x_vector = other.xcoord - self.xcoord
    y_vector = other.ycoord - self.ycoord
    return(x_vector, y_vector)

def turn_passed():                  # called when a turn has passed, runs the AI for non-player entitites
    for object in Objects:
        if object.ai is not None:
            if libtcod.map_is_in_fov(fov_map, object.xcoord, object.ycoord):
                object.ai.move()
            else:
                object.ai.patrol()


## handlers and engine components

def key_handler():              # handles keyboard input
    global ScreenMode, screen, GameState, done
    
    # event handlers
    if GameState == "playing":
        for event in pygame.event.get():
            # system controls
            #if event.type == pygame.QUIT: sys.exit()
            #if event.type == KEYDOWN and event.key == K_ESCAPE: done = True
            if event.type == KEYDOWN and event.key == K_PRINT:
                screenshot_label = "Screenshots\\"
                screenshot_label += time.asctime(time.localtime(time.time()))
                screenshot_label = screenshot_label.replace(":", " ")
                screenshot_label += ".png"
                pygame.image.save(screen, screenshot_label)
            elif event.type == KEYDOWN and event.key == K_F12:
                if ScreenMode == "window":
                    ScreenMode = "fullscreen"
                    screen = pygame.display.set_mode(screensize, pygame.FULLSCREEN)
                elif ScreenMode == "fullscreen":
                    ScreenMode = "window"
                    screen = pygame.display.set_mode(screensize)

            # movement controls
            elif event.type == KEYDOWN and event.key == K_w:
                player.move(0,-1)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_KP8:
                player.move(0,-1)               
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_a:
                player.move(-1,0)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_KP4:
                player.move(-1,0)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_s:
                player.move(0,1)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_KP2:
                player.move(0,1)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_d:
                player.move(1,0)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_KP6:
                player.move(1,0)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_KP7:
                player.move(-1,-1)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_KP9:
                player.move(1, -1)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_KP1:
                player.move(-1, 1)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_KP3:
                player.move(1, 1)
                turn_passed()
            elif event.type == KEYDOWN and event.key == K_KP5:
                message("You waste time.", YELLOW)
                turn_passed()


def render():                   # renders everything to the screen
    global fov_map, fov_recompute
    
    if fov_recompute:       #recomputes FOV if needed (player move, etc)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.xcoord, player.ycoord, CONFIG.TORCH_RADIUS, CONFIG.FOV_LIGHT_WALLS, CONFIG.FOV_ALGO)
        
                    
    # redraws the screen
    pygame.display.flip()
    color = BLACK
    screen.fill(color)
    
    # draws objects to the screen
    for object in Objects:
        object.draw()
    
    for monster in Monsters:
        if libtcod.map_is_in_fov(fov_map, monster.xcoord, monster.ycoord):
            monster.draw()
            

    
    player.draw()
    
    GUIrender()


def GUIrender():                # renders the GUI panel on top of the map

    def message_render():         # handles the console message box
        global Messages
        console_area = Rect(CONFIG.SCREEN_WIDTH - 400, CONFIG.SCREEN_HEIGHT - 90, 398, 88)
        border_area = Rect(CONFIG.SCREEN_WIDTH - 402, CONFIG.SCREEN_HEIGHT - 92, 402, 92)
        screen.fill(WHITE, rect=border_area)
        screen.fill(BLACK, rect=console_area)
        id = 0
        offset = 0
        while id <= 5:
            messagetext = Messages[id]
            message_location = CONFIG.SCREEN_HEIGHT - 80 + offset
            screen.blit(messagetext, (CONFIG.SCREEN_WIDTH - 390, message_location))
            offset += 12
            id += 1


    def status_render():        # handles the status display
        border_area = Rect(0, CONFIG.SCREEN_HEIGHT - 92, 240, 92)
        status_area = Rect(2, CONFIG.SCREEN_HEIGHT - 90, 236, 88)
        screen.fill(WHITE, rect=border_area)
        screen.fill(BLACK, rect=status_area)
        
        percent_bar("HP", WHITE, 12, CONFIG.SCREEN_HEIGHT - 80, 100, 12, player.fighter.hp, player.fighter.max_hp, RED, DARK_RED)
        percent_bar("XP", WHITE, 12, CONFIG.SCREEN_HEIGHT - 60, 100, 12, player.fighter.xp, player.fighter.to_level, GREEN, DARK_GREEN)


    def health_bar_render():    # handles rendering health bar when a fighter is damaged
        global Monsters
        
        for monster in Monsters:
            if monster.fighter.hp != monster.fighter.max_hp and monster.fighter.hp > 0:
                percent_bar("HP", WHITE, monster.x + 1, monster.y - 5, 30, 5, monster.fighter.hp, monster.fighter.max_hp, RED, DARK_RED, is_labeled=False)
        
        
    def minimap_render():       # handles the minimap display
        
        
        minimap = pygame.Surface((CONFIG.MAP_WIDTH*2, CONFIG.MAP_HEIGHT*2))
        #minimap_array = pygame.PixelArray(minimap)
        #surface = minimap_array
        #print surface
        
        x = 0
        y = 0
        pixel_color = PAPYRUS
        for x in range(0, CONFIG.MAP_WIDTH):
            for y in range(0, CONFIG.MAP_HEIGHT):
                if player.xcoord == x and player.ycoord == y:
                    pixel_color = BRIGHT_GREEN
                if CurrentMap[x][y].explored:
                    for object in CurrentMap[x][y].objects:
                        if object.ai is not None:
                            if libtcod.map_is_in_fov(fov_map, object.xcoord, object.ycoord):
                                pixel_color = RED
                            else:
                                pixel_color = GRAY
                        elif object.blocked:
                            pixel_color = BLACK
                        elif object.blocked == False and (player.xcoord != x or player.ycoord != y):
                            pixel_color = GRAY
                pixel = pygame.Surface((2,2))
                #print pixel_color
                pixel.fill(pixel_color)
                pixel_color = PAPYRUS
                minimap.blit(pixel, ((x*2),(y*2)))
                
        # del minimap_array
        # del surface

        border_area = pygame.Surface(((CONFIG.MAP_WIDTH*2)+5, (CONFIG.MAP_HEIGHT*2)+5))
        inner_shadow = pygame.Surface(((CONFIG.MAP_WIDTH*2)+1, (CONFIG.MAP_HEIGHT*2)+1))
        outer_shadow = pygame.Surface(((CONFIG.MAP_WIDTH*2)+3, (CONFIG.MAP_HEIGHT*2)+3))
        border_area.fill(WHITE)
        inner_shadow.fill(BLACK)
        outer_shadow.fill(BLACK)
        screen.blit(outer_shadow, (3,3))
        screen.blit(border_area, (0,0))
        screen.blit(inner_shadow, (2,2))
        screen.blit(minimap,(3, 3))
       
        
    #renders the GUI elements to the screen
    message_render()
    status_render()
    minimap_render()
    health_bar_render()
    

def initialize_fov():   #initialize the FOV
        global fov_recompute, fov_map
        fov_recompute = True
    
        ######## FOV
        fov_map = libtcod.map_new(CONFIG.MAP_WIDTH, CONFIG.MAP_HEIGHT)
        for y in range(CONFIG.MAP_HEIGHT):
            for x in range(CONFIG.MAP_WIDTH):
                libtcod.map_set_properties(fov_map, x, y, not CurrentMap[x][y].block_sight, not CurrentMap[x][y].blocked)
        


## intializes game components

# player init
player = Object("player", int((((screensize[0])/2)/32)-1), int((((screensize[1])/2)/32)-1), image.player)
'''print player.xcoord, player.ycoord'''
player.fighter = Fighter(player, 50, 1, 1, 1, 0)

# creates a dungeon map (may start outside later on though)
firstmap = Map("first", CONFIG.MAP_WIDTH, CONFIG.MAP_HEIGHT)
firstmap.make_dungeon_map(CONFIG.NUM_ROOMS, firstmap.width, firstmap.height)

# adds the player to tile objects for the tile player is on
CurrentMap[player.xcoord][player.ycoord].objects.append(player)
CurrentMap[player.xcoord][player.ycoord].update()



Objects.remove(player)      # not sure about this, allows individual control of player but removes player inclusion into operations for all objects

# moves the objects to adjust to player's new position in the middle of the screen
for object in Objects:
    if object != player:
        object.x -= 32 * (player.xcoord - int((((screensize[0])/2)/32)-1))
        object.y -= 32 * (player.ycoord - int((((screensize[1])/2)/32)-1))
        '''print object.name+" "+str(object.xcoord)+", "+str(object.ycoord)+" init movement= "+str(object.x)+", "+str(object.y)'''

'''print str(player.xcoord)+", "+str(player.ycoord)'''

initialize_fov()


# initial console text
message(" ", WHITE)
message(" ", WHITE)
message("Luckily, you are a penguin.", WHITE)
message("It is cold here.", WHITE)
message("You find yourself trapped in a strange land.", WHITE)
message("Welcome Adventurer!", WHITE)

###############
## main loop ##
###############


while 1:        # this runs until global done=True is sent, is main game loop with each loop through representing 1 frame of the game

    # sets framerate to 30fps
    clock.tick(30)
    
    # handles key presses and mouse clicks
    key_handler()
    
    # renders the screen
    render()
    
    if GameState == "dead":
        if death_message == False:
            message("You died!", DARK_RED)
            death_message = True
        else:
            pass
            
    if player.fighter.xp >= player.fighter.to_level:
        player.fighter.level_up()


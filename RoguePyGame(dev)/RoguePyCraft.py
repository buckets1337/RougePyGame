#! c:\Python27
#! requires Python v2.7 and PyGame installed
# libtcodpy, libtcod-VS.dll, and zlib1.dll must be in game folder

#import modules and libraries
import sys, pygame, pygame.mixer, time, random
from pygame.locals import *
import libtcodpy as libtcod

# import game config
import CONFIG

# import various dialogs
import dialogs.sys_dialog as sys_dialog

# import the new game init





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
HEADER_FONT = pygame.font.Font(None, 16)
SPECIAL_FONT = pygame.font.Font(None, 14)


## Image Prep definitions
def image_prep_alpha(img):      # prepares images with alpha transparency info
    image = pygame.image.load(img)
    image = pygame.Surface.convert_alpha(image)
    image = pygame.transform.scale(image, (32,32))
    return image
    
def image_prep_portrait(img):   # prepares images to be character portraits
    image = pygame.image.load(img)
    image = pygame.Surface.convert_alpha(image)
    image = pygame.transform.scale(image, (120,120))
    return image
    
def image_prep(img):            # prepares images
    image = pygame.image.load(img).convert()
    image = pygame.transform.scale(image, (32, 32))
    return image
    
class Generic(object):          # generic class for holding a group of related attributes
    pass
    
# creates a generic container for images called at image.<filename>
image = Generic()
image.player = image_prep_alpha("img\Player.png")
image.playercorpse = image_prep_alpha("img\PlayerCorpse.png")
image.snake = image_prep_alpha("img\Snake.png")
image.snakecorpse = image_prep_alpha("img\SnakeCorpse.png")

image.wall = image_prep("img\Wall.png")
image.exploredwall = image_prep("img\ExploredWall.png")
image.floor = image_prep("img\Floor.png")
image.exploredfloor = image_prep("img\ExploredFloor.png")

image.testportraitimg = image_prep_portrait("img\TestPortrait.png")



## Load sounds and streamed music to the mixer
bumpsound = pygame.mixer.Sound('bump.wav')
metaltinksound = pygame.mixer.Sound('swordHit.wav')
attacksound = pygame.mixer.Sound('punch.wav')




## global variable init

ScreenMode = "window"
GameState = "playing"
death_message = False
dialog_box_message = ""
dialog_option_selection = 0
next_message = False
choice = None




## data structures init

Objects = []
Monsters = []
CurrentMap = []
MapList = []
Messages = []
Inventory = []



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

    def draw(self):         # draws the object to the screen
        if libtcod.map_is_in_fov(fov_map, self.xcoord, self.ycoord):
            screen.blit(self.img, (self.x, self.y))
        elif CurrentMap[self.xcoord][self.ycoord].explored == True:
            if CurrentMap[self.xcoord][self.ycoord].terrain == "wall":
                screen.blit(image.exploredwall, (self.x, self.y))
            if CurrentMap[self.xcoord][self.ycoord].terrain == "floor":
                screen.blit(image.exploredfloor, (self.x, self.y))

        
    def move(self, xmovement, ymovement):       # move the object
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
        
    def centercoords(self):         # returns the center coordinates of the rectangle
        centercoords = int(self.xcenter), int(self.ycenter)
        return centercoords
        
    def is_intersecting(self, other):       # check if the rectangle is intersecting another rectangle
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
                
    def update(self):       # updates tile information based
        for object in self.objects:
            if object.block_sight == True:
                self.block_sight = True
            if object.blocked == True:
                self.blocked == True

class Map:          # A map is an array of tiles with a name.  Is always saved to MapList

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height

    def make_dungeon_map(self, num_rooms, width, height):     # makes a new underground map by defining a room, then connecting it to previous room
    
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
        
    def attack(self, other):        # attack another object
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
            
    def level_up(self):     # run when the player gains a level
        
        self.to_level = int(self.to_level * (1.5 + (self.level * 0.1)))
        self.xp = 0
        self.level += 1
        
        # eventually this will enable choice at level up

        level_up_actions = [dialog_actions.level_up_health, dialog_actions.level_up_power, dialog_actions.level_up_defense, dialog_actions.level_up_speed, dialog_actions.level_up_random]
        dialog_box(sys_dialog.level_up_message, "You Gained a Level!", None, sys_dialog.level_up_options, rect.central_small, 3, 5, level_up_actions)
        
        # applies the choice to the fighter's stats
        # if choice == "It is unclear.":
            # result = random.randint(1, 5)
            # if result == 1:
                # self.max_hp += 10
                # self.hp += 10
            # if result == 2:
                # self.power += 1
            # if result == 3:
                # self.defense += 1
            # if result == 4:
                # self.speed += 1
        # elif choice == "I feel more vital.":
            # self.max_hp += 10
            # self.hp += 10
            # choice = ""
        # elif choice == "I feel stronger.":
            # self.power += 1
            # choice = ""
        # elif choice == "I feel tougher.":
            # self.defense += 1
            # choice = ""
        # elif choice == "I feel faster.":
            # self.speed += 1
            # choice = ""
        
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

def dialog_box(message, speaker, speaker_portrait, option_list, rect, num_lines, num_options, option_action_list):      # creates a pop-up message box, with player options if provided.  Pauses game.
    global GameState, dialog_box_message, dialog_option_selection
    
    GameState = "message"
    dialog_box_message = (message, speaker, speaker_portrait, option_list, rect, num_lines, num_options, option_action_list)

    pygame.event.wait()
    
def choice_checker():               # handles choices with dialog boxes
    global choice, dialog_box_message

    if choice == dialog_box_message[3][0]:
        dialog_box_message[7][0]
        print dialog_box_message[7][0]
    if choice == dialog_box_message[3][1]:
        dialog_box_message[7][1]
        print dialog_box_message[7][1]
    if choice == dialog_box_message[3][2]:
        dialog_box_message[7][2]
        print dialog_box_message[7][2]
    if choice == dialog_box_message[3][3]:
        dialog_box_message[7][3]
        print dialog_box_message[7][3]
    if choice == dialog_box_message[3][4]:
        dialog_box_message[7][4]
        print dialog_box_message[7][4]
        
    choice = ""
    print "choice checker ran"
    
    
## handlers and engine components

def key_handler():              # handles keyboard input
    global ScreenMode, screen, GameState, done, next_message, dialog_option_selection, choice
    
    # event handlers
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

        if GameState == "playing":
            # movement controls
            if event.type == KEYDOWN and event.key == K_w:
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
                if choice is not None:
                    print "choice: " +  choice
                else:
                    print "choice: None"
                
            elif event.type == KEYDOWN and event.key == K_m:
                top = Rect(97, 8, CONFIG.SCREEN_WIDTH - 100, 100)
                options2 = [None]
                options3 = ["hi", "lo"]
                options4 = ["alakazam", "yo", "antidisestablishmentarianism", "qwerty", "bean"]
                options = ["yes", "no", "maybe"]
                test_greeting = "Hello Penguin, Good Buddy!"
                test_repeat = "Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! "
                test_numbers = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127 128 129 130 131 132 133 134 135 136 137 138 139 140 141 142 143 144 145 146 147 148 149 150 151 152 153 154 155 156 157 158 159 160 161 162 163 164 165 166 167 168 169 170 171 172 173 174 175 176 177 178 179 180 181 182 183 184 185 186 187 188 189 190 191 192 193 194 195 196 197 198 199 200 201 202 203 204 205 206 207 208 209 210 211 212 213 214 215 216 217 218 219 220 221 222 223 224 225 226 227 228 229 230 231 232 233 234 235 236 237 238 239 240 241 242 243 244 245 246 247 248 249 250 251 252 253 254 255 256 257 258 259 260 261 262 263 264 265 266 267 268 269 270 271 272 273 274 275 276 277 278 279 280 281 282 283 284 285 286 287 288 289 290 291 292 293 294 295 296 297 298 299 300 301 302 303 304 305 306 307 308 309 310 311 312 313 314 315 316 317 318 319 320 321 322 323 324 325 326 327 328 329 330 331 332 333 334 335 336 337 338 339 340 341 342 343 344 345 346 347 348 349 350 351 352 353 354 355 356 357 358 359 360 361 362 363 364 365 366 367 368 369 370 371 372 373 374 375 376 377 378 379 380 381 382 383 384 385 386 387 388 389 390 391 392 393 394 395 396 397 398 399 400"
                testmsg = dialog_box(test_repeat, "Mr. Test", image.testportraitimg, options, rect.top, 3, 3, sys_dialog.dialog_box_test_actions)
                # print testmsg
                
            elif event.type == KEYDOWN and event.key == K_t:
                central_big = Rect(90, 50, CONFIG.SCREEN_WIDTH - 150, CONFIG.SCREEN_HEIGHT - 200)
                options2 = [None]
                options3 = ["hi", "lo"]
                options4 = ["alakazam", "yo", "antidisestablishmentarianism", "qwerty", "bean"]
                options = ["yes", "no", "maybe"]
                test_greeting = "Hello Penguin, Good Buddy!"
                test_repeat = "Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! Hello Penguin, Good Buddy! "
                test_numbers = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127 128 129 130 131 132 133 134 135 136 137 138 139 140 141 142 143 144 145 146 147 148 149 150 151 152 153 154 155 156 157 158 159 160 161 162 163 164 165 166 167 168 169 170 171 172 173 174 175 176 177 178 179 180 181 182 183 184 185 186 187 188 189 190 191 192 193 194 195 196 197 198 199 200 201 202 203 204 205 206 207 208 209 210 211 212 213 214 215 216 217 218 219 220 221 222 223 224 225 226 227 228 229 230 231 232 233 234 235 236 237 238 239 240 241 242 243 244 245 246 247 248 249 250 251 252 253 254 255 256 257 258 259 260 261 262 263 264 265 266 267 268 269 270 271 272 273 274 275 276 277 278 279 280 281 282 283 284 285 286 287 288 289 290 291 292 293 294 295 296 297 298 299 300 301 302 303 304 305 306 307 308 309 310 311 312 313 314 315 316 317 318 319 320 321 322 323 324 325 326 327 328 329 330 331 332 333 334 335 336 337 338 339 340 341 342 343 344 345 346 347 348 349 350 351 352 353 354 355 356 357 358 359 360 361 362 363 364 365 366 367 368 369 370 371 372 373 374 375 376 377 378 379 380 381 382 383 384 385 386 387 388 389 390 391 392 393 394 395 396 397 398 399 400"
                testmsg = dialog_box(test_numbers, "Mr. Test", image.testportraitimg, options4, rect.central_big, 16, 5, sys_dialog.dialog_box_test_actions4)
                # print testmsg
                
        if GameState == "message":
        
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                GameState = "playing"
                next_message = False
            elif event.type == KEYDOWN and event.key == K_SPACE:
                next_message = True
                pygame.event.wait()
            elif event.type == KEYDOWN and event.key == K_DOWN:
                dialog_option_selection += 1
                pygame.event.wait()
            elif event.type == KEYDOWN and event.key == K_UP:
                dialog_option_selection -= 1
                pygame.event.wait()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                choice = dialog_box_message[3][dialog_option_selection]
                choice_checker()
                dialog_option_selection = 0
                next_message = False
                GameState = "playing"
            else:
                pygame.event.wait()


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
        
        minimap_area = Rect(3, 3, CONFIG.MAP_WIDTH*2, CONFIG.MAP_HEIGHT*2)
        box_with_shadow(minimap_area, minimap, WHITE)


    #renders the GUI elements to the screen
    message_render()
    status_render()
    minimap_render()
    health_bar_render()


def dialog_box_render():    # renders message boxes
    global next_message, dialog_option_selection, choice, GameState

    if GameState == "message":
        # defines the message box area
        box = pygame.Surface((dialog_box_message[4][2], dialog_box_message[4][3]))
        box.fill(DARK_BLUE)
        box_area = Rect(dialog_box_message[4][0], dialog_box_message[4][1], dialog_box_message[4][2], dialog_box_message[4][3])
        
        box_with_shadow(box_area, box, WHITE)
        
        # writes the text in the box
        font = BASE_FONT
        header = HEADER_FONT
        special = SPECIAL_FONT
        
        speaker_title = header.render(dialog_box_message[1], 1, WHITE)
        speaker_title_shadow = header.render(dialog_box_message[1], 1, BLACK)
        
        #renders the message text into properly formatted lines in the message box
        char_index = 74
        result_found = False
        slice_position = None
        print_remainder = False
        # text = []
        dy = dialog_box_message[4][1] + 22
        i = 0
        for i in range(0,dialog_box_message[5]):
            while result_found == False:
                #print char_index + 1
                #print (dialog_box_message[0][None:100])
                if char_index < len(dialog_box_message[0]):
                    if dialog_box_message[0][char_index] == ' ':
                    
                        line_of_text = font.render(dialog_box_message[0][slice_position:(char_index+1)], 1, WHITE)
                        screen.blit(line_of_text, (dialog_box_message[4][0]+20, dy))
                        #print text
                        if i != 0:
                            index_change = (char_index+1) - slice_position + 1
                        else:
                            index_change = (char_index+1)
                        
                        slice_position = char_index + 1
                        char_index += index_change 
                        dy += 12
                        
                        result_found = True
                    else:
                        char_index -= 1
                else:
                    result_found = True
                    print_remainder = True

            result_found = False
                
                
        remainder_dialog = dialog_box_message[0][slice_position:]
        if print_remainder:
            line_of_text = font.render(remainder_dialog, 1, WHITE)
            screen.blit(line_of_text, (dialog_box_message[4][0] + 28, dy))
        else:
            if len(remainder_dialog) < 80:
                more_tag_shadow = special.render("[more]", 1, WHITE)
                #more_tag = special.render("[more]", 1, GRAY)
                
                screen.blit(more_tag_shadow, (dialog_box_message[4][0] + 350, dialog_box_message[4][1] + dialog_box_message[4][3] - 30))
                #screen.blit(more_tag, (CONFIG.SCREEN_WIDTH - 201, 67))
                if next_message == True:
                    dialog_box(remainder_dialog, dialog_box_message[1], dialog_box_message[2], dialog_box_message[3], dialog_box_message[4], dialog_box_message[5], dialog_box_message[6])
                    next_message == False
        screen.blit(speaker_title_shadow, (dialog_box_message[4][0] + 15, dialog_box_message[4][1] + 6))
        screen.blit(speaker_title, (dialog_box_message[4][0] + 13, dialog_box_message[4][1] + 4))

        # screen.blit(text[1], (125, 42))
        # screen.blit(text[2], (125, 54))
        
        # handles the display of the "more" tag and advancing to the next screen of long messages
        if dialog_box_message[0][300:] is not None:
            is_space = True
            for character in dialog_box_message[0][char_index:]:
                if character != ' ':
                    is_space = False
            if is_space == False:
                more_tag_shadow = special.render("[more]", 1, WHITE)
                #more_tag = special.render("[more]", 1, GRAY)
                
                screen.blit(more_tag_shadow, (dialog_box_message[4][0]+ 353, dialog_box_message[4][1]+dialog_box_message[4][3] - 40))
                #screen.blit(more_tag, (CONFIG.SCREEN_WIDTH - 201, 67))
                
                if next_message:
                    next_message = False
                    dialog_box(remainder_dialog, dialog_box_message[1], dialog_box_message[2], dialog_box_message[3], dialog_box_message[4], dialog_box_message[5], dialog_box_message[6])
            else:
                if dialog_box_message[3][0] is None:
                    if next_message:
                        next_message = False
                        GameState = "playing"
                    
                    
            # creates the options in options list
            
            if dialog_option_selection <0:
                dialog_option_selection = 0
            if dialog_option_selection > len(dialog_box_message[3])-1:
                dialog_option_selection = len(dialog_box_message[3])-1
                
            y = 40
            for i in range(0,len(dialog_box_message[3])):
                selection_width = ((len(dialog_box_message[3][i])) * 6) + 10
                selection_box = pygame.Surface((selection_width, 12))
                selection_box.fill(GRAY)
                ymod = (dialog_box_message[6] - 3) * 12
                if dialog_box_message[3][0] is not None:
                    if dialog_option_selection == i:
                        screen.blit(selection_box, (dialog_box_message[4][0] + 43, dialog_box_message[4][1] + dialog_box_message[4][3] - y - ymod))
                    y -= 12


            y = dialog_box_message[4][1] + dialog_box_message[4][3] - 38 - (12 * (len(dialog_box_message[3])-3))
            for option in dialog_box_message[3]:
                if option is not None:
                    option_text = font.render(option, 1, WHITE)
                    screen.blit(option_text, (dialog_box_message[4][0] + 50, y))
                    y += 12
            
            
            # renders the character portrait
            if dialog_box_message[2] is not None:
                portrait_area = Rect(dialog_box_message[4][0] + dialog_box_message[4][2] - 130, dialog_box_message[4][1] - 5, 120, 120)
                portrait = pygame.Surface((120, 120))
                portrait.blit(dialog_box_message[2], (0, 0))
                box_with_shadow(portrait_area, portrait, WHITE)


def initialize_fov():   #initialize the FOV
        global fov_recompute, fov_map
        fov_recompute = True
    
        ######## FOV
        fov_map = libtcod.map_new(CONFIG.MAP_WIDTH, CONFIG.MAP_HEIGHT)
        for y in range(CONFIG.MAP_HEIGHT):
            for x in range(CONFIG.MAP_WIDTH):
                libtcod.map_set_properties(fov_map, x, y, not CurrentMap[x][y].block_sight, not CurrentMap[x][y].blocked)


def box_with_shadow(rect, surface, border_color):   # renders a surface in a box with a shadow
        border_area = pygame.Surface((rect[2] + 5, rect[3] + 5))
        inner_shadow = pygame.Surface((rect[2] + 1, rect[3] + 1))
        outer_shadow = pygame.Surface((rect[2] + 3, rect[3] + 3))
        
        border_area.fill(border_color)
        
        screen.blit(outer_shadow, (rect[0], rect[1]))
        screen.blit(border_area, (rect[0] - 3, rect[1] - 3))
        screen.blit(inner_shadow, (rect[0] - 1, rect[1] - 1))
        screen.blit(surface, (rect[0], rect[1]))


# player init
player = Object("player", int((((screensize[0])/2)/32)-1), int((((screensize[1])/2)/32)-1), image.player)
'''print player.xcoord, player.ycoord'''
player.fighter = Fighter(player, 50, 1, 1, 1, 0)
        
## dialog action definitions
dialog_actions = Generic()
def level_up_health(self):
    self.fighter.hp += 10
    self.fighter.max_hp += 10
    print "health gained"
    
def level_up_power(self):
    self.fighter.power += 1
    
def level_up_defense(self):
    self.fighter.defense += 1
    
def level_up_speed(self):
    self.fighter.speed += 1
    
def level_up_random(self):
    result = random.randint(1, 5)
    if result == 1:
        level_up_health(self)
    if result == 2:
        level_up_power(self)
    if result == 3:
        level_up_defense(self)
    if result == 4:
        level_up_speed(self)
        
dialog_actions.level_up_health = level_up_health(player)
dialog_actions.level_up_power = level_up_power(player)
dialog_actions.level_up_defense = level_up_defense(player)
dialog_actions.level_up_speed = level_up_speed(player)
dialog_actions.level_up_random = level_up_random(player)

## Screen Location Definitions
rect = Generic()
rect.central_big = Rect(90, 50, CONFIG.SCREEN_WIDTH - 150, CONFIG.SCREEN_HEIGHT - 200)
rect.central_small = Rect(120, 120, CONFIG.SCREEN_WIDTH - 270, CONFIG.SCREEN_HEIGHT - 340)
rect.top = Rect(97, 8, CONFIG.SCREEN_WIDTH - 100, 100)
        
## intializes game components



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

# initializes the player's field of view
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

while 1:        # this runs until game is quit, is main game loop with each loop through representing 1 frame of the game

    # sets framerate to 30fps
    clock.tick(30)
    
    # handles key presses and mouse clicks
    key_handler()
    
    # renders the screen
    render()
    
    # if the player died this turn, print a message to the console
    if GameState == "dead":
        if death_message == False:
            message("You died!", DARK_RED)
            death_message = True
        else:
            pass
            
    # if the player is engaged in a dialog, draw the dialog box
    if GameState == "message":
        dialog_box_render()
        
    # level up the player if the xp is high enough
    if player.fighter.xp >= player.fighter.to_level:
        player.fighter.level_up()


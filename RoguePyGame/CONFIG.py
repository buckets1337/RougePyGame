## Config Variables, used to tweak game

NUM_ROOMS = 30                  # number of rooms in the map
ROOM_MIN_SIZE = 3               # minimum dimension for a room
ROOM_MAX_SIZE = 10              # max dimension for a room
MAX_ROOM_INTERSECTS = 3         # max number of rooms that may intersect to form one room.  Extra rooms above this are thrown out.
MAP_WIDTH = 50                  # width of the map
MAP_HEIGHT = 50                 # height of the map

SCREEN_WIDTH = 640              # width of the screen the game runs in
SCREEN_HEIGHT = 480             # height of the screen the game runs in

TORCH_RADIUS = 7                # fov render distance
FOV_LIGHT_WALLS = True          # whether the FOV extends to visible wall tiles
FOV_ALGO = 1                    # fov algo to use
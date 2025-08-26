"""
constants.py - Game constants, colors, and configuration
"""

# Window settings
WIN_WIDTH = 1200
WIN_HEIGHT = 700
GROUND_HEIGHT = 50
FPS = 60

# Slingshot settings
SLINGSHOT_X = 150
SLINGSHOT_Y = WIN_HEIGHT - 125
MAX_STRETCH = 150
LAUNCH_POWER = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
LIGHTBLUE = (173, 216, 230)
GRASS_COLOR = (34, 139, 34)
GROUND_COLOR = (101, 67, 33)
WOOD_COLOR = (139, 90, 43)
STONE_COLOR = (105, 105, 105)
ICE_COLOR = (176, 224, 230)
METAL_COLOR = (70, 70, 70)
PIG_COLOR = (144, 238, 144)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GOLD = (255, 215, 0)

# Game settings
MAX_BIRDS = 5
BIRD_TYPES = ["red", "yellow", "blue"]

# Score values
SCORE_PIG_HIT = 10
SCORE_PIG_ELIMINATED = 500
SCORE_BLOCK_HIT = 5
SCORE_BLOCK_DESTROYED = 100
SCORE_PIG_CRUSHED = 300

# Level configurations
LEVEL_CONFIGS = {
    1: {
        "name": "Getting Started",
        "birds": ["red", "red", "red"],
        "castle_type": "simple"
    },
    2: {
        "name": "Ice Palace",
        "birds": ["red", "yellow", "red", "blue"],
        "castle_type": "ice_fortress"
    },
    3: {
        "name": "Stone Stronghold",
        "birds": ["red", "yellow", "yellow", "red", "blue"],
        "castle_type": "stone_castle"
    }
}
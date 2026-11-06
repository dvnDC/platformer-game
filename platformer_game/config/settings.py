import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration settings for the game

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Audio settings
BACKGROUND_MUSIC_PATH = os.path.join(BASE_DIR, 'assets', 'sounds', 'latenight.ogg')

MUSIC_VOLUME = 0.20

# Game settings
TPS_MAX = 100  # Set maximum ticks per second
FALL_LIMIT_Y = 800  # Player top below this is under every tile, so the player fell out of the level
PLAYER_LIVES = 3
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
FPS_MAX = 60  # Set maximum rendered frames per second
MAX_TICKS_PER_FRAME = 25  # Catch-up limit: time behind by more than this is dropped
ATTACK_FRAME_TICKS = 5  # Ticks each attack animation frame is shown
ATTACK_TICKS = 45  # Attack length: 9 frames, the other images are unused
RUN_FRAME_TICKS = 5  # Ticks each run animation frame is shown
RUN_CYCLE_TICKS = 33  # 7 frames, the last one shorter. Close to the old cycle of 20 drawn frames at 60 FPS
FALL_LIMIT_Y = 800  # Player top below this is under every tile, so the player fell out of the level
PLAYER_LIVES = 3
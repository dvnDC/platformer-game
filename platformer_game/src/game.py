import sys
import pygame
from pygame.math import Vector2
from src.core.collision_manager import CollisionManager
from src.entities.enemy import Enemy
from src.core.game_engine import GameEngine
from src.core.asset_loader import AssetLoader
from src.entities.projectile import Projectile
from src.world.game_map import GameMap
from src.ui.menu import Menu
from src.core.physics_engine import PhysicsEngine
from src.world.platform_manager import PlatformManager
from src.entities.player import Player
from src.ui.sprite_manager import SpriteManager
from src.entities.weapon import Weapon
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_MUSIC_PATH, MUSIC_VOLUME, TPS_MAX

pygame.display.set_caption("dvn's game")

WIDTH = 1280
HEIGHT = 720

"""Game class for managing the overall game state and interactions.
This class initializes all game components, handles the game loop,
and manages game state updates and rendering."""
class Game:

    def __init__(self):
        self.initialize_audio()
        self.initialize_screen()
        self.initialize_game_components()

    def initialize_audio(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
            pygame.mixer.music.play(-1)  # -1 oznacza zapętlenie
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
        except pygame.error as e:
            print(f"Error initializing audio: {e}")

    def initialize_screen(self):
        self.tps_max = TPS_MAX  # Set maximum ticks per second

        # Initialize the game screen with specified resolution
        pygame.init()
        self.resolution = (self.screen_width, self.screen_height) = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(self.resolution)

        self.tps_clock = pygame.time.Clock()
        self.tps_delta = 0.0
        self.scroll = Vector2(0, 0)

    def initialize_game_components(self):
        self.sprite = SpriteManager(self)
        self.map = GameMap(self)
        self.player = Player(self)
        self.enemy = Enemy(self)
        self.weapon = Weapon(self)
        self.fire = Projectile(self)
        self.physics = PhysicsEngine(self)
        self.platforms = PlatformManager(self)
        self.collision = CollisionManager(self)
        self.menu = Menu(self)
        self.file_loader = AssetLoader(self)
        self.engine = GameEngine(self)

    """The main game loop."""
    def run(self):
        try:
            while True:
                # Events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit(0)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  ############# klik i cos sie dzieje raz
                        sys.exit(0)

                # Fixed time step for game logic updates
                self.tps_delta += self.tps_clock.tick() / 1000.0
                while self.tps_delta > 1 / self.tps_max:
                    self.tick()  # Update game logic
                    self.tps_delta -= 1 / self.tps_max

                # Rendering
                self.render()  # Render the game state
        except Exception as e:
            print(f"An error occurred during the game loop: {e}")

    def tick(self):
        self.player.tick()
        self.weapon.tick()
        self.fire.tick()
        self.enemy.tick()
        self.physics.tick()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.draw()
        self.engine.display_fps()
        pygame.display.flip()

    def draw(self):
        # self.menu.draw()
        self.map.draw()
        self.player.draw()
        self.enemy.draw()
        self.weapon.draw()
        self.fire.draw()

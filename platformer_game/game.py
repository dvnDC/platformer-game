import sys
import pygame
from pygame.math import Vector2

from collision import Collision
from enemy import Enemy
from engine import Engine
from file_loader import FileLoader
from fire import Fire
from map import Map
from menu import Menu
from physics import Physics
from platforms import Platforms
from player import Player
from sprite import Sprite
from weapon import Weapon
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_MUSIC_PATH, MUSIC_VOLUME, TPS_MAX

pygame.display.set_caption("dvn's game")

WIDTH = 1280
HEIGHT = 720


class Game:
    """
    Game class for managing the overall game state and interactions.

    This class initializes all game components, handles the game loop,
    and manages game state updates and rendering.
    """

    def __init__(self):
        self.initialize_audio()
        self.initialize_screen()
        self.initialize_game_components()

    def initialize_audio(self):
        """
        Initializes the game audio settings.
        """
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
            pygame.mixer.music.play(0, 0.0, 5000)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
        except pygame.error as e:
            print(f"Error initializing audio: {e}")

    def initialize_screen(self):
        """
        Initializes the game screen with specified resolution.
        """


        self.tps_max = TPS_MAX  # Set maximum ticks per second

        # Initialize the game screen with specified resolution
        pygame.init()
        self.resolution = (self.screen_width, self.screen_height) = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(self.resolution)

        self.tps_clock = pygame.time.Clock()
        self.tps_delta = 0.0
        self.scroll = Vector2(0, 0)

    def initialize_game_components(self):
        """
        Creates and initializes all major game components like map, player, enemies, etc.
        """
        self.map = Map(self)
        self.player = Player(self)
        self.enemy = Enemy(self)
        self.weapon = Weapon(self)
        self.fire = Fire(self)
        self.physics = Physics(self)
        self.platforms = Platforms(self)
        self.collision = Collision(self)
        self.sprite = Sprite(self)
        self.menu = Menu(self)
        self.file_loader = FileLoader(self)
        self.engine = Engine(self)

    def run(self):
        """
            The main game loop.

            Handles event processing, updates the game state, and renders the game.
            Continuously runs until an exit event is triggered.
            """
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
        """
        Update game logic here.
        This method runs at a fixed time step.
        """
        self.player.tick()
        self.weapon.tick()
        self.fire.tick()
        self.enemy.tick()
        self.physics.tick()

    def render(self):
        """
        Render the game state to the screen.
        This method runs as fast as the hardware allows.
        """
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

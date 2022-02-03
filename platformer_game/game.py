import pygame, sys
import os
from player import Player
from map import Map
from enemy import Enemy
from weapon import Weapon
from fire import Fire
from collision import Collision
from physics import Physics
from platforms import Platforms
from sprite import Sprite
from menu import Menu
from file_loader import FileLoader
from font import Font


from pygame.math import Vector2

pygame.display.set_caption("dvn's game")


class Game(object):

    def __init__(self):
        # Settings
        self.WIDTH = 320
        self.HEIGHT = 180
        self.SCALE = 3

        # Sound settings
        pygame.mixer.init()
        pygame.mixer.music.load('latenight.ogg')
        pygame.mixer.music.play(0)

        # Config
        self.tps_max = 100

        # Initialization
        pygame.init()
        self.resolution = (self.screen_width, self.screen_height) = (self.WIDTH, self.HEIGHT)
        self.screen = pygame.display.set_mode((self.screen_width * self.SCALE, self.screen_height * self.SCALE), pygame.RESIZABLE)

        self.tps_clock = pygame.time.Clock()
        self.tps_delta = 0.0
        self.scroll = Vector2(0,0)

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
        self.font = Font(self)

        self.sprite.load_images()
        self.sprite.load_icon()
        while True:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    sys.exit(0)
                elif event.type == pygame.VIDEORESIZE:
                    pass
                elif event.type == pygame.VIDEOEXPOSE:
                    pass


            # Ticking
            self.tps_delta += self.tps_clock.tick() / 1000.0  # convert milliseconds to seconds; 1000 ms = 1 s
            while self.tps_delta > 1 / self.tps_max:
                self.tick()
                self.tps_delta -= 1 / self.tps_max

            # Rendering/Drawing
            self.screen.fill((0, 0, 0))
            self.draw()
            pygame.display.update()

    def tick(self):
        self.player.tick()
        self.weapon.tick()
        self.fire.tick()
        self.enemy.tick()
        self.physics.tick()

    def draw(self):
        pass
        # self.menu.draw()
        self.map.draw()
        self.player.draw()
        # self.enemy.draw()
        # self.weapon.draw()
        self.font.draw()


if __name__ == "__main__":
    Game()

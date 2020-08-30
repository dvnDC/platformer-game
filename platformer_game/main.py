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

from pygame.math import Vector2


WIDTH = 1280
HEIGHT = 720

class Game(object):

    def __init__(self):



        # Config
        self.tps_max = 120.0

        # Initialization
        pygame.init()
        self.resolution = (self.screen_width, self.screen_height) = (WIDTH, HEIGHT)
        self.screen = pygame.display.set_mode(self.resolution)


        self.tps_clock = pygame.time.Clock()
        self.tps_delta = 0.0
        self.scroll = Vector2(0,0)


        self.map = Map(self)
        self.player = Player(self)  # przy inicjalizacji przekazuje playerowi wszystko Player(self)
        self.enemy = Enemy(self)
        self.weapon = Weapon(self)
        self.fire = Fire(self)
        self.physics = Physics(self)
        self.platforms = Platforms(self)
        self.collision = Collision(self)
        self.sprite = Sprite(self)


        while True:

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  ############# klik i cos sie dzieje raz
                    sys.exit(0)

            # Ticking
            self.tps_delta += self.tps_clock.tick() / 1000.0  # zamieniam MS na sekundy
            while self.tps_delta > 1 / self.tps_max:
                self.tick()
                self.tps_delta -= 1 / self.tps_max

            # Rendering/Drawing
            self.screen.fill((0, 0, 0))

            self.draw()
            pygame.display.flip()

    def tick(self):
        self.player.tick()
        self.weapon.tick()
        self.fire.tick()
        self.enemy.tick()
        self.physics.tick()

    def draw(self):
        self.map.draw()
        self.player.draw()
        self.enemy.draw()
        self.weapon.draw()
        self.fire.draw()




if __name__ == "__main__":
    Game()

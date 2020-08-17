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


class Game(object):

    def __init__(self):



        # Config
        self.tps_max = 60.0

        # Initialization
        pygame.init()
        self.resolution = (self.screen_width, self.screen_height) = (1280, 720)
        self.screen = pygame.display.set_mode(self.resolution)


        self.tps_clock = pygame.time.Clock()
        self.tps_delta = 0.0

        self.map = Map(self)
        self.player = Player(self)  # przy inicjalizacji przekazuje playerowi wszystko Player(self)
        self.enemy = Enemy(self)
        self.weapon = Weapon(self)
        self.fire = Fire(self)
        self.physics = Physics(self)
        self.platforms = Platforms(self)
        self.collision = Collision(self)
        self.sprite = Sprite(self)

        # images
        self.backgroundImage = pygame.image.load("images/bg3.jpg")
        self.playerImage = pygame.image.load("images/hero2.png")
        self.enemyImage = pygame.image.load("images/enemy2.png")
        self.platformImage = pygame.image.load("images/platform.png")




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
            self.screen.blit(self.backgroundImage, (0, 0)) ##################
            self.draw()
            pygame.display.flip()

    def tick(self):
        # Input
        self.player.tick()
        self.collision.player_collision()
        self.weapon.tick()
        self.fire.tick()
        self.enemy.tick()
        self.collision.enemy_collision()




    def draw(self):
        self.player.draw()
        self.map.draw()
        self.enemy.draw()
        self.weapon.draw()
        self.fire.draw()



if __name__ == "__main__":
    Game()

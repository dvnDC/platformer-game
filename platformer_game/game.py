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


from pygame.math import Vector2

pygame.display.set_caption("dvn's game")


class Game(object):

    def __init__(self):

        # Settings

        pygame.mixer.init()

        pygame.mixer.music.load('latenight.ogg')
        pygame.mixer.music.play(0)

        self.WIDTH = 1280
        self.HEIGHT = 720

        # Config
        self.tps_max = 100

        # Initialization
        pygame.init()
        font = pygame.font.SysFont("Arial", 18)
        self.resolution = (self.screen_width, self.screen_height) = (self.WIDTH, self.HEIGHT)
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
        self.menu = Menu(self)
        self.file_loader = FileLoader(self)

        self.sprite.load_images()

        def create_fonts(font_sizes_list):
            "Creates different fonts with one list"
            fonts = []
            for size in font_sizes_list:
                fonts.append(
                    pygame.font.SysFont("Arial", size))
            return fonts

        def render(fnt, what, color, where):
            "Renders the fonts as passed from display_fps"
            text_to_show = fnt.render(what, 0, pygame.Color(color))
            self.screen.blit(text_to_show, where)

        def display_fps():
            "Data that will be rendered and blitted in _display"
            render(
                fonts[0],
                what=str(int(self.tps_clock.get_fps())),
                color="white",
                where=(0, 0))

        fonts = create_fonts([32, 16, 14, 8])
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
            display_fps()
            pygame.display.flip()

    def tick(self):
        self.player.tick()
        self.weapon.tick()
        self.fire.tick()
        self.enemy.tick()
        self.physics.tick()

    def draw(self):
        # self.menu.draw()
        self.map.draw()
        self.player.draw()
        self.enemy.draw()
        self.weapon.draw()
        self.fire.draw()




if __name__ == "__main__":
    Game()

import pygame
from pygame.math import Vector2
from numpy import *

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

class Platforms(object):
    def __init__(self, game):
        self.game = game
        self.pos = Vector2(0, 0)
        # self.pos4 = Vector2(self.game.screen_width - 700, self.game.height - 300)
        # self.pos5 = Vector2(self.game.screen_width - 900, self.game.height - 400)

        self.pos.x = 0
        self.pos.y = 0
        self.width = 0
        self.height = 0
        self.x_min = {}
        self.x_max = {}
        self.y_min = {}
        self.y_max = {}
        self.platform_position = {}
        self.true_scroll = Vector2(0, 0)


        self.platformPOS = zeros((10,4), float_)


        self.scroll = Vector2(0, 0)

        # Colors
        self.WHITE = (255,250,250)
        self.GREEN = (0, 150, 50)






    def draw_platform(self, x, y, width, height, letter):
        self.pos.x = x - self.scroll[0]
        self.pos.y = y
        self.width = width
        self.height = height


        rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)  ##szerokosc,wysokosc
        pygame.draw.rect(self.game.screen, (self.WHITE), rect)
        platformImageScaled = pygame.transform.scale(self.game.sprite.platformImage, (width, height))
        self.game.screen.blit(platformImageScaled, (self.pos.x, self.pos.y))
       # self.platform_pos(letter) ### przechowuje wartosci x1,x2,y1,y2 platform w tabeli z kluczami



    def platformList(self):
        n = 3
        x = 400
        y = 275
        width = 150
        height = 15
        letter = 0
        changer = 60
        while n > 0:
            self.platformPOS[letter][0] = x
            self.platformPOS[letter][1] = x + width
            self.platformPOS[letter][2] = y
            self.platformPOS[letter][3] = y + height
            n -= 1
            # self.draw_platform(x, y, width, height, letter)
            self.draw_platform(x, y, width, height, letter)
            x += 350
            y -= changer
            changer *= -1

            letter += 1

    def draw(self):
        self.platformList()










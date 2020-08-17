import pygame
from pygame.math import Vector2



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

        # Colors
        self.WHITE = (255,250,250)
        self.GREEN = (0, 150, 50)



    def draw_platform(self, x, y, width, height, letter):
        self.pos.x = x
        self.pos.y = y
        self.width = width
        self.height = height

        self.platform_pos(letter) ### przechowuje wartosci x1,x2,y1,y2 platform w tabeli z kluczami

        rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)  ##szerokosc,wysokosc
        pygame.draw.rect(self.game.screen, (self.WHITE), rect)

    def draw(self):
        self.draw_platform(780,630,500,200, 'a')
        platformImageScaled = pygame.transform.scale(self.game.platformImage,(100,200))
        self.game.screen.blit(platformImageScaled, (780, 630))
        self.draw_platform(880,590,500,100, 'b')
        platformImageScaled = pygame.transform.scale(self.game.platformImage, (500, 200))
        self.game.screen.blit(platformImageScaled, (880, 590))
        self.draw_platform(980,500,500,15, 'c')
        platformImageScaled = pygame.transform.scale(self.game.platformImage, (500, 15))
        self.game.screen.blit(platformImageScaled, (980, 500))
        self.draw_platform(0,220,500,15, 'd')
        platformImageScaled = pygame.transform.scale(self.game.platformImage, (500, 15))
        self.game.screen.blit(platformImageScaled, (0, 220))
        self.draw_platform(580,420,300,15, 'e')
        platformImageScaled = pygame.transform.scale(self.game.platformImage, (300, 15))
        self.game.screen.blit(platformImageScaled, (580, 420))
        self.draw_platform(400,320,300,15, 'f')
        platformImageScaled = pygame.transform.scale(self.game.platformImage, (300, 15))
        self.game.screen.blit(platformImageScaled, (400, 320))
        self.draw_platform(800,250,300,15, 'g')
        platformImageScaled = pygame.transform.scale(self.game.platformImage, (300, 15))
        self.game.screen.blit(platformImageScaled, (800, 250))


    def platform_pos(self, letter):
        self.x_min[letter] = self.pos.x
        self.y_min[letter] = self.pos.y
        self.x_max[letter] = self.pos.x + self.width
        self.y_max[letter] = self.pos.y + self.height
        self.platform_position[letter] = self.pos.x, self.pos.x + self.width, self.pos.y, self.pos.y + self.height





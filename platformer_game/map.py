import pygame
from pygame.math import Vector2



class Map(object):
    def __init__(self, game):
        self.game = game
        self.pos = Vector2(0,0)
        self.platform_pos = {}
        # self.pos.x = (0, 0)
        # self.pos.y = (0, 0)



    def draw(self):
        self.game.platforms.draw()
        self.position()

    def position(self):
        self.platform_pos = self.game.platforms.platform_position




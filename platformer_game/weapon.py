import pygame
from pygame.math import Vector2


class Weapon(object):

    def __init__(self, game):
        self.game = game

        self.pos = Vector2(0, 0)
        self.pos.x = 1200
        self.pos.y = 400

        self.picked_up = False
        self.fire = False

    def tick(self):
        if self.pos.x-30 <= self.game.player.pos.x <= self.pos.x+30 and self.pos.y-30 <= self.game.player.pos.y <= self.pos.y+30:
            self.picked_up = True
        # got a weapon && weapon input
        if self.picked_up == True:
            self.game.player.got_weapon = True



    def draw(self):
        if self.picked_up == False:
            pygame.draw.circle(self.game.screen, (200, 200, 20), (int(self.pos.x), int(self.pos.y)), 20)



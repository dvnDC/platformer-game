import pygame
from pygame.math import Vector2


class Weapon(object):
    def __init__(self, game):
        self.game = game

        self.pos = Vector2(0, 0)
        self.pos.x = 0
        self.pos.y = 0
        self.position = (0,0,0,0) #xxyy
        self.scroll = Vector2(0, 0)
        # self.picked_up = True
        self.fire = False

    def tick(self):
        self.pos.y = self.game.player.pos.y-50
        self.position = (self.pos.x,self.pos.x+100,self.pos.y,self.pos.y+100)

    def draw(self):

        # melee range
        self.rect_weapon = pygame.Rect(self.game.player.pos.x - self.scroll.x + 30, self.game.player.pos.y - 50, 100, 100)

        if self.game.player.vel.x >= 0:
            self.rect_weapon.x = self.game.player.pos.x - self.scroll.x + 30
            self.pos.x = self.game.player.pos.x + 30
        if self.game.player.vel.x < 0:
            self.rect_weapon.x = self.game.player.pos.x - self.scroll.x - 100
            self.pos.x = self.game.player.pos.x - 100

        # Show attack hitbox
        # pygame.draw.rect(self.game.screen, (0, 150, 200), self.rect_weapon)



import pygame
from pygame.math import Vector2

class Fire(object):

    def __init__(self, game):
        self.game = game
        self.speed = 30

        self.pos = Vector2(0, 0)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.start_ticks = pygame.time.get_ticks()
        #self.seconds = 0.0
        self.projectileRight = False
        self.projectileLeft = False


    def add_force(self, force):
        self.acc += force

    def tick(self):

        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        if self.game.weapon.fire == True:
             self.draw()
             # self.seconds = (pygame.time.get_ticks()-self.start_ticks)/1000
             # if self.seconds > 5.0:
             #    self.game.weapon.fire = False
             #    self.seconds = 0
        if self.game.weapon.fire == True:
            if self.projectileRight == True:
                self.projectileLeft == False
            else:
                self.projectileRight == False
            if self.game.player.vel.x > 0 and self.projectileRight == False and self.projectileLeft == False:
                self.add_force(Vector2(self.speed, 0))
                self.projectileRight = True
            if self.game.player.vel.x < 0 and self.projectileLeft == False and self.projectileRight == False:
                self.add_force(Vector2(-self.speed, 0))
                self.projectileLeft = True
                #self.bullet_distance = self.pos.x - self.game.player.pos_weapon.x
        if self.pos.x > 1280 or self.pos.x < 0: #do zmiany! poki co szybkosc ataku sie zwieksza przy krawedziach
                self.vel *= 0.0
                self.projectileRight = False
                self.projectileLeft= False
                self.game.weapon.fire = False


    def draw(self):
        if self.game.weapon.fire == True:                                ### podwojne strzaly ...
            if self.projectileRight == True and self.projectileLeft == False:
                pygame.draw.circle(self.game.screen, (200, 200, 20), (int(self.pos.x + 35), int(self.pos.y + 15)), 5, 5)
            if self.projectileLeft == True and self.projectileRight == False:
                pygame.draw.circle(self.game.screen, (200, 200, 20), (int(self.pos.x - 15), int(self.pos.y + 15)), 5, 5)
        else:
            self.pos.x = -100
            self.pos.y = -100

                # self.pos.x = self.game.player.rect_weapon.x
                # self.pos.y = self.game.player.rect_weapon.y

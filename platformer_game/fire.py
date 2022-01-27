import pygame
from pygame.math import Vector2
import time


time0 = time.time()

class Fire:

    def __init__(self, game):
        self.game = game
        self.speed = 8

        self.pos = Vector2(0, 0)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.start_ticks = pygame.time.get_ticks()
        #self.seconds = 0.0
        self.projectileRight = False
        self.projectileLeft = False

        self.scroll = Vector2(0, 0)
        self.bullet_distance = Vector2(0, 0)

        self.seconds = 0.0

    def add_force(self, force):
        self.acc += force

    def tick(self):
        # Time for animations
        global time0
        self.time1 = time.time()
        self.dt = self.time1 - time0

        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0
        if pygame.key.get_pressed()[pygame.K_r] and self.game.player.has_weapon is True and self.game.weapon.fire is False:
            time0 = self.time1

        if self.game.weapon.fire is True:
            self.seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000 ###############
            self.draw()

            if self.game.player.vel.x >= 0 and self.projectileRight is False and self.projectileLeft is False:
                # self.add_force(Vector2(self.speed, 0))
                self.vel.x += self.speed
                self.projectileRight = True
            if self.game.player.vel.x < 0 and self.projectileLeft is False and self.projectileRight is False:
                self.add_force(Vector2(-self.speed, 0))
                self.projectileLeft = True

    def draw(self):
        if self.game.weapon.fire is True:

            if self.projectileRight is True and self.projectileLeft is False:
                cooldown = int(self.dt*3)
                if cooldown > 5:
                    cooldown = int(self.dt)-4
                self.game.screen.blit(self.game.sprite.img_fireball[cooldown], (self.pos.x - self.scroll[0] - 40, self.pos.y - 60))
                if self.dt >= 5:
                    self.game.weapon.fire = False
                    self.projectileRight = False
                    self.projectileLeft = False
                    self.vel.x = 0
                    global time0
                    time0 = self.time1
            if self.projectileLeft is True and self.projectileRight is False:
                cooldown = int(self.dt*3)
                if cooldown > 5:
                    cooldown = int(self.dt)-4
                self.game.screen.blit(self.game.sprite.img_fireball_flip[cooldown], (self.pos.x - self.scroll[0] - 120, self.pos.y - 60))
                if self.dt > 5:
                    self.game.weapon.fire = False
                    self.projectileRight = False
                    self.projectileLeft = False
                    self.vel.x = 0
                    time0 = self.time1
        else:
            self.pos.x = -1000
            self.pos.y = -1000

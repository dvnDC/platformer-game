import pygame
from pygame.math import Vector2
import time

time0 = time.time()

class Enemy(object):
    def __init__(self, game):
        self.game = game
        self.speed = -1
        self.gravity = 0.9

        self.pos = Vector2(0, 0)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.pos.x = 1400
        self.pos.y = 100

        self.width = 50
        self.height = 50

        self.scroll = Vector2(0,0)

        self.position = (0,0,0,0) # x0 x1 y0 y1

        self.live = True
        self.newSpawn = False

        self.counter = 1

    def add_force(self, force):
        #self.acc += force
        self.pos += force

    def tick(self):
        # Time for animations
        global time0
        self.time1 = time.time()
        self.dt = self.time1 - time0
        #
        if self.live == True:
            self.game.physics.standing()
            self.vel *= 0.85
            self.vel -= Vector2(0,-self.gravity)  # grawitacjaself.add_force(Vector2(0, self.gravity))
            self.add_force(Vector2(self.speed, 0))
            self.vel += self.acc
            self.pos += self.vel
            self.acc *= 0

            # Actual position
            self.position = (self.pos.x, (self.pos.x + self.width), self.pos.y, (self.pos.y + self.height))

            # Collision
            self.game.collision.bullet_collision()
            # self.game.collision.enemy_collision()
            for n in range(self.game.map.GRID_boxes_coll_number):
                self.pos.x,self.pos.y,self.vel = self.game.collision.object_collision_check(self.pos.x, (self.pos.x + self.width), self.pos.y, (self.pos.y + self.height), self.vel,self.game.map.GRID_boxes_coll[n])
        else:
             self.counter += 1
             self.pos.x = self.game.player.pos.x + 1280
             self.pos.y = 100
             self.live = True
        if self.game.player.pos.x - self.pos.x > 1000:
            self.live = False


             # self.speed = 1
             # self.newSpawn = True

    def draw(self):
        if self.live == True:
            # rect = pygame.Rect(self.pos.x-self.scroll[0], self.pos.y, self.width, self.height) ##szerokosc,wysokosc
            # pygame.draw.rect(self.game.screen, (150, 20, 20), rect)
            self.game.screen.blit(self.game.sprite.imageEnemyRunning[0], (self.pos.x - 8 - self.scroll[0], self.pos.y - 10))
        # else:
        #     self.pos.x = 1280 * self.counter

# class Enemy(object):
#
#     def __init__(self, game):
#         self.game = game
#         self.speed = 1
#         self.gravity = 0.9
#
#         self.pos = Vector2(0, 0)
#         self.vel = Vector2(0, 0)
#         self.acc = Vector2(0, 0)
#
#         self.pos.x = 100
#         self.pos.y = 670
#
#         self.width = 20
#         self.height = 80
#
#         self.scroll = Vector2(0,0)
#
#         self.position = (0,0,0,0) # x0 x1 y0 y1
#
#         self.live = True
#         self.newSpawn = False
#
#         self.counter += 1
#
#
#     def add_force(self, force):
#         #self.acc += force
#         self.pos += force
#
#
#     def tick(self):
#         if self.live == True:
#             self.game.physics.standing()
#             # if self.game.physics.isStanding == True:
#             #     self.gravity = 0
#             # else:
#             #     self.gravity = 0.9
#             # if self.newSpawn == True and self.game.physics.isStanding == True:
#             # self.speed *= 1
#             #     self.newSpawn = False
#             self.vel *= 0.85
#             self.vel -= Vector2(0,-self.gravity)  # grawitacjaself.add_force(Vector2(0, self.gravity))
#             self.add_force(Vector2(self.speed, 0))
#             self.vel += self.acc
#             self.pos += self.vel
#             self.acc *= 0
#
#             # Actual position
#             self.position = (self.pos.x, (self.pos.x + self.width), self.pos.y, (self.pos.y + self.height))
#
#             # Collision
#             self.game.collision.bullet_collision()
#             # self.game.collision.enemy_collision()
#             for n in range(self.game.map.GRID_boxes_coll_number):
#                 self.pos.x,self.pos.y,self.vel = self.game.collision.object_collision_check(self.pos.x, (self.pos.x + self.width), self.pos.y, (self.pos.y + self.height), self.vel,self.game.map.GRID_boxes_coll[n])
#         else:
#              self.counter += 1
#              self.pos.x = 1280 * self.counter
#              self.pos.y = 670
#              self.live = True
#
#
#              self.speed = 1
#              # self.newSpawn = True
#
#
#
#
#
#     def draw(self):
#         if self.live == True:
#             # rect = pygame.Rect(self.pos.x-self.scroll[0], self.pos.y, self.width, self.height) ##szerokosc,wysokosc
#             # pygame.draw.rect(self.game.screen, (150, 20, 20), rect)
#             self.game.screen.blit(self.game.sprite.enemyImage, (self.pos.x - 50- self.scroll[0], self.pos.y - 40))
#         else:
#             self.pos.x = 1280 * self.counter
#

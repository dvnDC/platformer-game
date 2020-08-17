import pygame
from pygame.math import Vector2


class Enemy(object):

    def __init__(self, game):
        self.game = game
        self.speed = 3
        self.gravity = 0.9

        self.pos = Vector2(0, 0)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.pos.x = 100
        self.pos.y = 670
        self.width = 20
        self.height = 80

        self.position = (0,0,0,0) # x0 x1 y0 y1

        self.live = True
        self.newSpawn = False

    def add_force(self, force):
        #self.acc += force
        self.pos += force


    def tick(self):
        if self.live == True:
            self.game.physics.standing()
            # if self.game.physics.isStanding == True:
            #     self.gravity = 0
            # else:
            #     self.gravity = 0.9
            if self.newSpawn == True and self.game.physics.isStanding == True:
                self.speed = 3
                self.newSpawn == False
            self.vel *= 0.85
            self.vel -= Vector2(0,-self.gravity)  # grawitacjaself.add_force(Vector2(0, self.gravity))
            self.add_force(Vector2(self.speed, 0))
            self.vel += self.acc
            self.pos += self.vel
            self.acc *= 0


            # Collision
            self.game.collision.bullet_collision()
            self.game.collision.enemy_collision()


        else:
             self.live = True 
             self.pos.x = 105
             self.pos.y = 10

             #self.speed = 0
             self.newSpawn = True

        # Actual position
        self.position = (self.pos.x, (self.pos.x + self.width), self.pos.y, (self.pos.y + self.height))



    def draw(self):
        if self.live == True:
            rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height) ##szerokosc,wysokosc
            #pygame.draw.rect(self.game.screen, (150, 20, 20), rect)
            self.game.screen.blit(self.game.enemyImage, (self.pos.x - 50, self.pos.y - 40))  ##################
        else:
            self.pos.x = 10
            self.pos.y = 10
        # if self.live == False:
        #     rect = pygame.Rect(0, 0, 20, 50) ##szerokosc,wysokosc
        #     pygame.draw.rect(self.game.screen, (150, 20, 20), rect)
        #     self.live = True

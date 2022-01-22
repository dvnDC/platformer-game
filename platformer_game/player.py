import pygame
from pygame.math import Vector2
import time


time0 = time.time()

class Player(object):

    def __init__(self, game):
        self.game = game

        self.speed = 0.55
        self.gravity = 0.7

        self.is_jumping = False
        self.has_weapon = False

        #self.pos = pygame.math.Vector2(0,0)
        self.pos = Vector2(0,0)
        self.vel = Vector2(0,0)
        self.acc = Vector2(0,0)

        self.vel.x = 0.1
        self.pos.x = 320
        self.pos.y = 170
        self.width = 20
        self.height = 60

        self.scroll = Vector2(0,0)

        self.time1 = 0
        self.dt = 0

        self.position = (0,0,0,0) # x0 x1 y0 y1

        self.isAttacking = False
        self.isRunning = False
        self.runCount = 0
        self.rect_weapon = pygame.Rect(self.pos.x-self.scroll.x+30, self.pos.y-50, 100, 100)

    def add_force(self, force):
        self.acc += force

    def animations_time(self):
        global time0
        self.time1 = time.time()
        self.dt = self.time1 - time0

    def input(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_a]:
            self.add_force(Vector2(-self.speed,0))
            self.isRunning = True
        elif pressed[pygame.K_d]:
            self.add_force(Vector2(self.speed,0))
            self.isRunning = True
        else:
            self.isRunning = False
            self.runCount = 0

        if pressed[pygame.K_SPACE] and self.is_jumping == False and self.vel.y == 0:        #
            self.is_jumping = True
            jump = -20.0
            while self.is_jumping == True:
                self.add_force(Vector2(0, jump))
                if self.vel.y == 0:
                    self.is_jumping = False
                    self.gravity = self.game.physics.gravity

        if pressed[pygame.K_r] and self.has_weapon == True and self.game.weapon.fire == False:
            self.game.weapon.fire = True
            self.game.fire.pos.x = self.pos.x
            self.game.fire.pos.y = self.pos.y

        if pressed[pygame.K_e] and self.isAttacking == False:
            time0 = self.time1
            self.isAttacking = True
            self.game.collision.collision((self.game.weapon.position),(self.game.enemy.position))
            if self.game.collision.isCollision == True:
                self.game.enemy.live = False

    def physic_vel(self):
        self.vel *= 0.85
        self.vel -= Vector2(0,-self.gravity)

        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

    def actual_postion(self):
        self.position = (self.pos.x, (self.pos.x + self.width), self.pos.y, (self.pos.y + self.height))


    def tick(self):
        self.animations_time()
        self.input()
        self.physic_vel()
        self.actual_postion()

        self.game.collision.player_collision() # collision with playforms, borders

        # self.game.map.grid()
        for n in range(self.game.map.GRID_boxes_coll_number):
            self.game.collision.player_collision_check(self.game.map.GRID_boxes_coll[n])

        self.game.collision.player_enemy_collision()

        # Player animation
        if self.runCount + 1 >= 21:
            self.runCount = 0


    def draw(self):
        # base model
        # rect_player = pygame.Rect(self.pos.x -self.scroll.x, self.pos.y, self.width, self.height)
        # pygame.draw.rect(self.game.screen, (0, 150, 200), rect_player)

        if self.isRunning == False and self.isAttacking == False:
            if self.vel.x == 0:
                self.game.screen.blit(self.game.sprite.imagePlayerStand,(self.pos.x - self.scroll.x - 70, self.pos.y - 70))
            if self.vel.x > 0:
                self.game.screen.blit(self.game.sprite.imagePlayerStand, (self.pos.x - self.scroll.x - 70, self.pos.y - 70))
                # self.rect_weapon.x = self.pos.x - self.scroll.x +30
            if self.vel.x < 0:
                hero_flip = pygame.transform.flip(self.game.sprite.imagePlayerStand, True, False)
                self.game.screen.blit(hero_flip, (self.pos.x - self.scroll.x - 70, self.pos.y - 70))
                # self.rect_weapon.x = self.pos.x - self.scroll.x -100

        elif self.isRunning == True and self.isAttacking == False:
            if self.vel.x > 0:
                self.game.screen.blit(self.game.sprite.imagePlayerRun[self.runCount//3], (self.pos.x - self.scroll.x - 70, self.pos.y - 70))
                self.runCount += 1
            elif self.vel.x < 0:
                self.game.screen.blit(self.game.sprite.imagePlayerRunFlip[self.runCount//3], (self.pos.x - self.scroll.x - 70, self.pos.y - 70))
                self.runCount += 1

        elif self.isAttacking:
            animate_speed = self.dt * 20
            if not int(animate_speed) >= 9:
                if self.vel.x >= 0:
                    self.game.screen.blit(self.game.sprite.imagePlayerAttack[int(animate_speed)],(self.pos.x - self.scroll.x - 70, self.pos.y - 70))
                    self.game.screen.blit(self.game.sprite.imageAttackEffect[int(animate_speed)],(self.game.weapon.pos.x - self.scroll.x, self.game.weapon.pos.y))
                elif self.vel.x < 0:
                    self.game.screen.blit(self.game.sprite.imagePlayerAttackFlip[int(animate_speed)],(self.pos.x - self.scroll.x - 70, self.pos.y - 70))
                    self.game.screen.blit(self.game.sprite.imageAttackEffect[int(animate_speed)],(self.game.weapon.pos.x - self.scroll.x, self.game.weapon.pos.y))
            if self.dt >= 2 or int(animate_speed) >= 9:
                global time0
                time0 = self.time1
                self.isAttacking = False

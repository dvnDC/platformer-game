import pygame
from pygame.math import Vector2


class Player(object):

    def __init__(self, game):
        self.game = game
        self.speed = 1.2
        self.gravity = 0.9
        self.isJump = False
        self.got_weapon = False

        #self.pos = pygame.math.Vector2(0,0)
        self.pos = Vector2(0,0)
        self.vel = Vector2(0,0)
        self.acc = Vector2(0,0)

        self.pos.x = 300
        self.pos.y = 170
        self.width = 20
        self.height = 60

        self.position = (0,0,0,0) # x0 x1 y0 y1

        self.pos_weapon = self.pos



    def add_force(self, force):
        self.acc += force

    def tick(self):


        # Input
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_a]:
            self.add_force(Vector2(-self.speed,0))
        if pressed[pygame.K_d]:
            self.add_force(Vector2(self.speed,0))

        if pressed[pygame.K_SPACE] and self.isJump == False and self.vel.y == 0:        #
            self.isJump = True
            jump = -30.0
            while self.isJump == True:
                self.add_force(Vector2(0, jump))
                jump *= self.gravity
                if self.vel.y == 0:
                    self.isJump = False
        if pressed[pygame.K_r] and self.got_weapon == True and self.game.weapon.fire == False:
            self.game.weapon.fire = True
            self.game.fire.pos.x = self.pos_weapon.x
            self.game.fire.pos.y = self.pos_weapon.y


            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  ############# klik i cos sie dzieje raz

        # Physics
        self.vel *= 0.85
        self.vel -= Vector2(0,-self.gravity)  # grawitacja

        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        # Actual position
        self.position = (self.pos.x, (self.pos.x + self.width), self.pos.y, (self.pos.y + self.height))

        # Collision with playforms, borders
        self.game.collision.player_collision()

        # Collision with enemy
        self.game.collision.player_enemy_collision()



    def draw(self):
        # base model
        rect_player = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height) ##szerokosc,wysokosc
        #pygame.draw.rect(self.game.screen, (0, 150, 200), rect_player)
        self.game.screen.blit(self.game.playerImage, (self.pos.x - 40, self.pos.y - 30))  ##################
        # self.rect_weapon = pygame.Rect(self.pos.x+30, self.pos.y+10,10,10)
        if self.vel.x > 0:
            self.game.screen.blit(self.game.playerImage, (self.pos.x - 40, self.pos.y - 30))
        #     self.rect_weapon.x = self.pos.x+30
        if self.vel.x < 0:
            hero_flip = pygame.transform.flip(self.game.playerImage, True, False)
            self.game.screen.blit(hero_flip, (self.pos.x - 40, self.pos.y - 30))
        #     self.rect_weapon.x = self.pos.x-20
        # if self.got_weapon == True:
        #     pygame.draw.rect(self.game.screen, (0, 150, 200), self.rect_weapon)
        #angle = self.vel.angle_to(Vector2(1,0))
        #self.pos.rotate(angle)




import pygame
from pygame.math import Vector2



class Map(object):
    def __init__(self, game):
        self.game = game
        self.pos = Vector2(0,0)
        self.platform_pos = {}
        self.scroll = Vector2(0,0)

        self.chunk = 1

        #self.imgPosX = 0


    def draw(self):
        self.background()
        self.game.platforms.draw()
        self.stone()
        # self.position()
        # self.bird()

    # def position(self):
    #     self.platform_pos = self.game.platforms.platform_position

    def background(self):


        #reszta tla

        # layer background
        n = 3
        imgPosX2 = -1280
        while n > 0:
            n -= 1
            self.game.screen.blit(self.game.sprite.backgroundImage, (imgPosX2 - self.scroll.x / 30, 0))
            imgPosX2 += 1280

        # layer back
        n = 60
        imgPosX2 = -1280
        while n > 0:
            n -= 1
            self.game.screen.blit(self.game.sprite.backgroundImage2, (imgPosX2 - self.scroll.x / 6, 0))
            imgPosX2 += 300

        # layer front

        n = 20
        imgPosX = -1280
        # if self.game.player.pos.x > self.chunk * 1280:
        #     self.chunk += 1
        #     self.imgPosX += 1280
        #     print("test")
        # elif self.game.player.pos.x < (self.chunk-1) * 1280:
        #     self.chunk -= 1
        #     self.imgPosX -= 1280
        #     print("test_powrot")
        while n > 0:
            n -= 1
            self.game.screen.blit(self.game.sprite.backgroundImage3, (imgPosX - self.scroll.x, 0))
            imgPosX += 1280


        # self.game.screen.blit(self.game.sprite.backgroundImage3, (0-self.scroll.x,0))
        # self.game.screen.blit(self.game.sprite.backgroundImage3, (1280-self.scroll.x,0))
        # self.game.screen.blit(self.game.sprite.backgroundImage3, (2560-self.scroll.x,0))
        # self.game.screen.blit(self.game.sprite.backgroundImage3, (3840-self.scroll.x,0))
        #self.game.screen.blit(self.game.sprite.backgroundImage3, (380,0))


        #self.game.screen.blit(imageScaled, (self.pos.x-1000, self.pos.y+20))
        #self.game.screen.blit(imageScaled, (self.pos.x-1000, self.pos.y+20))

    def bird(self):
        imageScaled = pygame.transform.scale(self.game.sprite.shipImage, (75, 40))
        self.game.screen.blit(imageScaled, (self.pos.x - 1000, self.pos.y + 20))
        self.pos.x += 1
        if self.pos.x == 3000:
            self.pos.x = -1000
    def stone(self):
        self.game.screen.blit(self.game.sprite.stone, (-234-self.scroll.x,self.game.screen_height-220))





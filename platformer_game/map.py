import pygame
from pygame.math import Vector2
import numpy as np

position_multiplayer = 0
imgPosX = 1280

class Map(object):
    def __init__(self, game):
        self.game = game
        self.pos = Vector2(0,0)
        self.platform_pos = {}
        self.scroll = Vector2(0,0)
        self.player_checkpoint = 0
        self.checkpoint_bg = 0
        self.checkpoint_bgg = 0

        self.row = 10        # screen/displayed size 9
        self.colum = 80     #   16
        self.GRID = np.zeros((self.row, self.colum), int)
        self.GRID_pos_x_for_colli = np.zeros((1, self.colum), float)
        # 0 free space  1 collision invisible 2 dirt box 3 grass box
        self.GRID = [[7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.GRID_position = []

        self.GRID_boxes_coll_number = 0
        self.GRID_boxes_coll = []
        self.GRID_boxes_coll = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def bird(self):
        imageScaled = pygame.transform.scale(self.game.sprite.shipImage, (75, 40))
        self.game.screen.blit(imageScaled, (self.pos.x - 1000, self.pos.y + 20))
        self.pos.x += 1
        if self.pos.x == 3000:
            self.pos.x = -1000

    def stone(self):
        self.game.screen.blit(self.game.sprite.stone, (0 - self.scroll.x + (3840 * (self.player_checkpoint)),self.game.screen_height-220))
        self.game.screen.blit(self.game.sprite.stone, (1280 - self.scroll.x + (3840 * (self.player_checkpoint)),self.game.screen_height-220))

    def background_vanilla(self):
        n = 3
        imgPosX2 = -1280
        while n > 0:
            n -= 1
            self.game.screen.blit(self.game.sprite.backgroundImage, (imgPosX2 - self.scroll.x / 30, 0))
            imgPosX2 += 1280
        n = 28
        imgPosX2 = -1280
        while n > 0:
            n -= 1
            self.game.screen.blit(self.game.sprite.backgroundImage2, (imgPosX2 - self.scroll.x / 6, 0))
            imgPosX2 += 300

    def background(self):
        if self.game.player.pos.x > (1280 * (self.checkpoint_bgg + 4)):  ## 640 - player starting point
            self.checkpoint_bgg += 1
        elif self.game.player.pos.x < (1280 * (self.checkpoint_bgg+4)):
            self.checkpoint_bgg -= 1
        pos = 1280
        self.game.screen.blit(self.game.sprite.backgroundImage, (pos - self.scroll.x / 30 + (1280 * (self.checkpoint_bgg-1)),0))
        self.game.screen.blit(self.game.sprite.backgroundImage, (pos + 1280 - self.scroll.x / 30 + (1280 * (self.checkpoint_bgg)),0))

        if self.game.player.pos.x >= (1500 * (self.player_checkpoint + 2)):  ## 640 - player starting point
            self.checkpoint_bg += 1
        elif self.game.player.pos.x < (1500 * (self.player_checkpoint)):
            self.checkpoint_bg -= 1
        for n in range(-1,4):
            pos = 300
            pos = pos * n
            self.game.screen.blit(self.game.sprite.backgroundImage2, (pos - self.scroll.x / 6 + (1500 * (self.checkpoint_bg)),0))
            self.game.screen.blit(self.game.sprite.backgroundImage2, (pos - self.scroll.x / 6 + (1500 * (self.checkpoint_bg+1)),0))

    def grid(self):
        if self.game.player.pos.x > (3840 * (self.player_checkpoint+1) - 1280): ## 640 - player starting point
            self.player_checkpoint += 1
        elif self.game.player.pos.x < (3840 * (self.player_checkpoint-1)) + 2560:
            self.player_checkpoint -= 1

        posX = 80
        posY = 80
        box_size = 80  # x 16      y 9
        self.GRID_boxes_coll_number = 0
        checkpoint = (3840 * (self.player_checkpoint)) - 2560

        for row in range(self.row):
            for column in range(self.colum):
                box = pygame.Rect(posX*column + checkpoint, posY*row, posX*row+box_size + checkpoint, posY*row+box_size)
                if self.GRID[row][column] == 1:
                    self.game.screen.blit(self.game.sprite.imageGrid1, ((posX * column - self.scroll.x) + checkpoint, posY * row))
                    positionbox = (posX * column) + checkpoint, (posX * column + box_size) + checkpoint, posY * row, posY * row + box_size

                    self.GRID_position.append(positionbox)
                    self.GRID_boxes_coll[self.GRID_boxes_coll_number] = positionbox
                    self.GRID_boxes_coll_number += 1
                if self.GRID[row][column] == 7:
                    self.game.screen.blit(self.game.sprite.backgroundImage3, ((posX * column - self.scroll.x) + checkpoint, posY * row))
                    positionbox = (posX * column) + checkpoint, (posX * column + box_size) + checkpoint, posY * row, posY * row + box_size

                    self.GRID_position.append(positionbox)
                else:
                    self.GRID_position.append((posX * column, posX * column + box_size, posY * row, posY * row + box_size))

    def grid_static(self):
        posX = 80
        posY = 80
        box_size = 80  # x 16      y 9
        self.GRID_boxes_coll_number = 0

        for row in range(self.row):
            for column in range(self.colum):
                box = pygame.Rect(posX*column, posY*row, posX*row+box_size, posY*row+box_size)
                if self.GRID[row][column] == 1:
                    self.game.screen.blit(self.game.sprite.imageGrid1, ((posX * column - self.scroll.x), posY * row))
                    positionbox = (posX * column), (posX * column + box_size), posY * row, posY * row + box_size
                    self.GRID_position.append(positionbox)
                    self.GRID_boxes_coll[self.GRID_boxes_coll_number] = positionbox
                    self.GRID_boxes_coll_number += 1
                if self.GRID[row][column] == 7:
                    self.game.screen.blit(self.game.sprite.backgroundImage3, ((posX * column - self.scroll.x), posY * row))
                    positionbox = (posX * column), (posX * column + box_size), posY * row, posY * row + box_size
                    # self.game.collision.player_collision_check(positionbox)
                    # self.game.collision.player_collision_check(self.GRID_position[gridNr])
                    self.GRID_position.append(positionbox)
                else:
                    self.GRID_position.append((posX * column, posX * column + box_size, posY * row, posY * row + box_size))

    def draw(self):
        # self.background()
        self.background_vanilla()
        self.stone()
        self.game.platforms.draw()
        self.grid()
        # self.grid_static()
        # self.position()
        # self.bird()





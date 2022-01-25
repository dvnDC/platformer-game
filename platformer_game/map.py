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
        # 0 free space  1 collision invisible 2 dirt box 3 grass box                                                    # STARTING
        self.GRID = [[7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.GRID_position = []

        self.GRID_boxes_coll_number = 0
        self.GRID_boxes_coll = []
        self.GRID_boxes_coll = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def stone(self):
        self.game.screen.blit(self.game.sprite.img_stone, (0 - self.scroll.x + (3840 * (self.player_checkpoint)), self.game.screen_height / 2 + 50))
        self.game.screen.blit(self.game.sprite.img_stone, (1280 - self.scroll.x + (3840 * (self.player_checkpoint)), self.game.screen_height / 2 - 100100))

    def background_vanilla(self):
        # layer background
        starting_pos = -320 * self.game.SCALE
        for n in range(3): # number of images
            self.game.screen.blit(self.game.sprite.img_background, (starting_pos - self.scroll.x / 30, 0))
            starting_pos += 320 * self.game.SCALE
        # layer back
        imgPosX2 = -900
        for n in range(12): # number of images
            self.game.screen.blit(self.game.sprite.img_background2, (imgPosX2 - self.scroll.x / 6, 0))
            imgPosX2 += 225
        # # layer front
        starting_pos = -320 * self.game.SCALE
        for n in range(3): # number of images
            self.game.screen.blit(self.game.sprite.img_background3, (starting_pos - self.scroll.x, 0))
            starting_pos += 320 * self.game.SCALE

    def background(self):
        if self.game.player.pos.x > (1280 * (self.checkpoint_bgg + 4)):  ## 640 - player starting point
            self.checkpoint_bgg += 1
        elif self.game.player.pos.x < (1280 * (self.checkpoint_bgg+4)):
            self.checkpoint_bgg -= 1
        if self.game.player.pos.x >= (1500 * (self.player_checkpoint + 2)):  ## 640 - player starting point
            self.checkpoint_bg += 1
        elif self.game.player.pos.x < (1500 * (self.player_checkpoint)):
            self.checkpoint_bg -= 1
        for n in range(-1,4):
            pos = 300
            pos = pos * n
    def grid(self):
        if self.game.player.pos.x > (3840 * (self.player_checkpoint+1) - 1280): ## 640 - player starting point
            self.player_checkpoint += 1
        elif self.game.player.pos.x < (3840 * (self.player_checkpoint-1)) + 2560:
            self.player_checkpoint -= 1

        posX = 40
        posY = 40
        box_size = 40  # x 16      y 9
        self.GRID_boxes_coll_number = 0
        checkpoint = (3840 * (self.player_checkpoint)) - 2560

        for row in range(self.row):
            for column in range(self.colum):
                if self.GRID[row][column] == 1:
                    self.game.screen.blit(self.game.sprite.imageGrid1, ((posX * column - self.scroll.x) + checkpoint, posY * row))

    def grid_static(self):
        def grid_draw_hitbox():
            box = pygame.Rect(posX*column, posY*row, posX*row+box_size, posY*row+box_size)
            pygame.draw.rect(self.game.screen, (0, 150, 200), box)
        posX = 80
        posY = 80
        box_size = 80  # x 16      y 9
        self.GRID_boxes_coll_number = 0

        for row in range(self.row):
            for column in range(self.colum):
                if self.GRID[row][column] == 1:
                    grid_draw_hitbox()
                    self.game.screen.blit(self.game.sprite.imageGrid1, ((posX * column - self.scroll.x), posY * row))
                    positionbox = (posX * column), (posX * column + box_size), posY * row, posY * row + box_size
                if self.GRID[row][column] == 7:
                    grid_draw_hitbox()
                    self.game.screen.blit(self.game.sprite.img_background3, ((posX * column - self.scroll.x), posY * row))
                else:
                    self.GRID_position.append((posX * column, posX * column + box_size, posY * row, posY * row + box_size))

    def draw_map_hitbox(self):
        rect_map = pygame.Rect(0 - self.scroll.x, 0, 320, 180)
        pygame.draw.rect(self.game.screen, (0, 0, 0), rect_map)

    def draw(self):
        # self.background()
        self.background_vanilla()
        self.stone()
        # self.game.aplatforms.draw()
        # self.grid()
        self.grid_static()
        self.draw_map_hitbox()

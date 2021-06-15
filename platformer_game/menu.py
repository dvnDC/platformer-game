import pygame
from pygame.math import Vector2
import numpy as np

position_multiplayer = 0
imgPosX = 1280




class Menu(object):
    def __init__(self, game):
        self.game = game
        self.pos = Vector2(0,0)
        self.platform_pos = {}
        self.scroll = Vector2(0,0)
        self.player_checkpoint = 0
        # self.checkpoint_bg = 0
        # self.checkpoint_bgg = 0
        #
        #
        self.row = 10        # screen/displayed size 9
        self.colum = 16     #   16
        self.GRID = np.zeros((self.row, self.colum), int)
        # self.GRID_pos_x_for_colli = np.zeros((1, self.colum), float)
        # # 0 free space  1 collision invisible 2 dirt box 3 grass box
        self.GRID = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.GRID_position = []

        self.GRID_boxes_coll_number = 0
        self.GRID_boxes_coll = []
        self.GRID_boxes_coll = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.mouse = pygame.mouse.get_pos()
        self.click = pygame.mouse.get_pressed()

    def button(self, x, y, w, h, action=None):
        if x + w > self.mouse[0] > x and y + h > self.mouse[1] > y:
            pygame.draw.rect(gameDisplay, (210, 210, 210), (x, y, w, h))
            if self.click[0] == 1 and action != None:
                action()

    def background(self):
        self.game.screen.blit(self.game.sprite.backgroundImage,(0,0))

    def text_objects(text, font):
        textSurface = font.render(text, True, randomcolor)
        return textSurface, textSurface.get_rect()

    def grid_static(self):

        posX = 80
        posY = 80
        box_size = 80  # x 16      y 9
        self.GRID_boxes_coll_number = 0


        for row in range(self.row):
            for column in range(self.colum):
                # box = pygame.Rect(posX*column, posY*row, posX*column+box_size, posY*row+box_size)
                if self.GRID[row][column] == 1:
                    # pygame.draw.rect(self.game.screen, (255, 150, 200), box)
                #     self.game.screen.blit(self.game.sprite.backgroundImage,((posX * column - self.scroll.x/30.0) + checkpoint, posY * row))
                #     self.game.screen.blit(self.game.sprite.backgroundImage3,((posX * column - self.scroll.x) + checkpoint, posY * row))
                    self.game.screen.blit(self.game.sprite.imageMenuGrid1, ((posX * column, posY * row)))
                    positionbox = (posX * column), (posX * column + box_size), posY * row, posY * row + box_size
                    # self.game.collision.player_collision_check(positionbox)
                    # self.game.collision.player_collision_check(self.GRID_position[gridNr])

                    self.GRID_position.append(positionbox)
                    # self.GRID_position[self.GRID_boxes_coll_number] = (positionbox)
                    self.GRID_boxes_coll[self.GRID_boxes_coll_number] = positionbox
                    self.GRID_boxes_coll_number += 1


                    self.button(posX*column, posY*row, posX*column+box_size, posY*row+box_size)

                if self.GRID[row][column] == 7:
                    pygame.draw.rect(self.game.screen, (0, 150, 200), box)
                    self.game.screen.blit(self.game.sprite.backgroundImage3, ((posX * column), posY * row))
                    positionbox = (posX * column), (posX * column + box_size), posY * row, posY * row + box_size
                    # self.game.collision.player_collision_check(positionbox)
                    # self.game.collision.player_collision_check(self.GRID_position[gridNr])

                    self.GRID_position.append(positionbox)
                else:
                    self.GRID_position.append((posX * column, posX * column + box_size, posY * row, posY * row + box_size))



        # for gridNr in range(143):
        #     self.game.collision.player_collision_check(self.GRID_position[gridNr])

    def draw(self):
        self.background()
        self.grid_static()








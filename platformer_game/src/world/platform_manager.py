import pygame
from pygame.math import Vector2
from numpy import zeros


class PlatformManager(object):
    def __init__(self, game):
        self.game = game
        self.pos = Vector2(0, 0)
        self.width = 0
        self.height = 0
        self.platform_positions = zeros((10, 4), float)
        self.scroll = Vector2(0, 0)

        # Colors
        self.WHITE = (255, 250, 250)
        self.GREEN = (0, 150, 50)

    def draw_platform(self, x, y, width, height, index):
        self.pos.x = x - self.scroll[0]
        self.pos.y = y
        self.width = width
        self.height = height

        rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        pygame.draw.rect(self.game.screen, self.WHITE, rect)

        platformImageScaled = pygame.transform.scale(self.game.sprite.platformImage, (width, height))
        self.game.screen.blit(platformImageScaled, (self.pos.x, self.pos.y))

        # Store platform positions
        self.platform_positions[index] = [x, x + width, y, y + height]

    def create_platform_list(self):
        num_platforms = 3
        x = 800
        y = 550
        width = 300
        height = 30
        index = 0
        y_offset = 120
        for _ in range(num_platforms):
            self.draw_platform(x, y, width, height, index)
            x += 350
            y -= y_offset
            y_offset *= -1
            index += 1

    def draw(self):
        self.create_platform_list()

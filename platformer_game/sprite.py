import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
    ###############        sprite    sheet     #################
    # def draw(self, surface, cellindex, x, y, handle = 0):
    #     pygame.surface.blit(self.sheet, (x + self.handle[handle][0], y+ self.handle[handle][1],self.cells[cellindex]))

    # def test(self, filename, cols, rows):
        # W,H = 1280,720
        # HW, HH = W/2, H/2
        # AREA = W * H
        # CLOCK = pygame.display.set_mode((W,H))
        # pygame.display.set_caption("code.Pylet - Sprite Sheets")
        #
        # self.sheet = pygame.image.load(filename)  # 512x576 8x9
        # self.cols = cols
        # self.rows = rows
        # self.totalCellCount = cols * rows
        #
        # self.rect = self.sheet.get_rect()
        # w = self.cellWidth = self.rect.width / cols
        # h = self.cellHeight = self.rect.height / rows
        # hw, hh = self.cellCenter = (w / 2, h / 2)
        #
        # self.cels = list([(index % cols * w, index / cols * h) for index in range(self.totalCellCount)])
        # self.handle = list([
        #     (0, 0), (-hw, 0), (-w, 0),
        #     (0, -hh), (-hw, -hh), (-w, -hh),
        #     (0, -h), (-hw, -h), (-w, -h), ])
        # CENTER_HANDLE = 4
        # index = 0
        # self.draw(self.game.resolution,index % self.totalCellCount, HW, HH, CENTER_HANDLE)
        # index += 1




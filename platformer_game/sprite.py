import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game

        self.left = False
        self.right = False
        self.walkCount = 0

        # player
        ### standing
        self.imagePlayerStand = pygame.image.load("images/hero/Knight/Stand/0.png")
        self.imagePlayerStand = pygame.transform.scale(self.imagePlayerStand, (160, 160))

        # self.playerImage = pygame.transform.scale(self.playerImage, (20, 60))
        ### running right
        self.imagePlayerRun = [
            pygame.image.load('images/hero/Knight/Run/0.png'),
            pygame.image.load('images/hero/Knight/Run/1.png'),
            pygame.image.load('images/hero/Knight/Run/2.png'),
            pygame.image.load('images/hero/Knight/Run/3.png'),
            pygame.image.load('images/hero/Knight/Run/4.png'),
            pygame.image.load('images/hero/Knight/Run/5.png'),
            pygame.image.load('images/hero/Knight/Run/6.png'),
            pygame.image.load('images/hero/Knight/Run/7.png'),
            pygame.image.load('images/hero/Knight/Run/8.png'),
            pygame.image.load('images/hero/Knight/Run/9.png')]
        n = 0
        while n < 10:
            self.imagePlayerRun[n] = pygame.transform.scale(self.imagePlayerRun[n], (160, 160))
            n += 1
        ### running left
        self.imagePlayerRunFlip = [
            pygame.image.load('images/hero/Knight/Run/0.png'),
            pygame.image.load('images/hero/Knight/Run/1.png'),
            pygame.image.load('images/hero/Knight/Run/2.png'),
            pygame.image.load('images/hero/Knight/Run/3.png'),
            pygame.image.load('images/hero/Knight/Run/4.png'),
            pygame.image.load('images/hero/Knight/Run/5.png'),
            pygame.image.load('images/hero/Knight/Run/6.png'),
            pygame.image.load('images/hero/Knight/Run/7.png'),
            pygame.image.load('images/hero/Knight/Run/8.png'),
            pygame.image.load('images/hero/Knight/Run/9.png')]
        n = 0
        while n < 10:
            self.imagePlayerRunFlip[n] = pygame.transform.scale(self.imagePlayerRunFlip[n], (160, 160))
            self.imagePlayerRunFlip[n] = pygame.transform.flip(self.imagePlayerRunFlip[n], True, False)
            n += 1
        ### attack right
        self.imagePlayerAttack = [
            pygame.image.load('images/hero/Knight/Attack1H/0.png'),
            pygame.image.load('images/hero/Knight/Attack1H/1.png'),
            pygame.image.load('images/hero/Knight/Attack1H/2.png'),
            pygame.image.load('images/hero/Knight/Attack1H/3.png'),
            pygame.image.load('images/hero/Knight/Attack1H/4.png'),
            pygame.image.load('images/hero/Knight/Attack1H/5.png'),
            pygame.image.load('images/hero/Knight/Attack1H/6.png'),
            pygame.image.load('images/hero/Knight/Attack1H/7.png'),
            pygame.image.load('images/hero/Knight/Attack1H/8.png'),
            pygame.image.load('images/hero/Knight/Attack1H/9.png')]
        n = 0
        while n < 10:
            self.imagePlayerAttack[n] = pygame.transform.scale(self.imagePlayerAttack[n], (160, 160))
            n += 1
        ### attack right
        self.imagePlayerAttackFlip = [
            pygame.image.load('images/hero/Knight/Attack1H/0.png'),
            pygame.image.load('images/hero/Knight/Attack1H/1.png'),
            pygame.image.load('images/hero/Knight/Attack1H/2.png'),
            pygame.image.load('images/hero/Knight/Attack1H/3.png'),
            pygame.image.load('images/hero/Knight/Attack1H/4.png'),
            pygame.image.load('images/hero/Knight/Attack1H/5.png'),
            pygame.image.load('images/hero/Knight/Attack1H/6.png'),
            pygame.image.load('images/hero/Knight/Attack1H/7.png'),
            pygame.image.load('images/hero/Knight/Attack1H/8.png'),
            pygame.image.load('images/hero/Knight/Attack1H/9.png')]
        n = 0
        while n < 10:
            self.imagePlayerAttackFlip[n] = pygame.transform.scale(self.imagePlayerAttackFlip[n], (160, 160))
            self.imagePlayerAttackFlip[n] = pygame.transform.flip(self.imagePlayerAttackFlip[n], True, False)
            n += 1
        # effects
        ### fireball
        self.imageFireball = [
            pygame.image.load('images/effects/1.png'),
            pygame.image.load('images/effects/2.png'),
            pygame.image.load('images/effects/3.png'),
            pygame.image.load('images/effects/4.png'),
            pygame.image.load('images/effects/5.png'),
            pygame.image.load('images/effects/6.png')]
        n = 0
        n = 0
        while n < 6:
            self.imageFireball[n] = pygame.transform.scale(self.imageFireball[n], (256, 100))
            self.imageFireball[n] = pygame.transform.flip(self.imageFireball[n], True, False)
            n += 1
        ### fireball left
        self.imageFireballLeft = [
            pygame.image.load('images/effects/1.png'),
            pygame.image.load('images/effects/2.png'),
            pygame.image.load('images/effects/3.png'),
            pygame.image.load('images/effects/4.png'),
            pygame.image.load('images/effects/5.png'),
            pygame.image.load('images/effects/6.png')]
        n = 0
        while n < 6:
            self.imageFireballLeft[n] = pygame.transform.scale(self.imageFireballLeft[n], (256, 100))
            n += 1
        ### melee attack
        self.temp = pygame.image.load("images/effects/attack/2.png")
        self.temp = pygame.transform.scale(self.temp, (400, 400))
        n = 0
        m = 0
        width = 100
        height = 100
        k = 0
        l = 0
        number = 0
        self.imageAttackEffect=[0,0,0,0,0,0,0,0,0,0,0,0]
        while n < 3:
            while m < 4:
                self.imageAttackEffect[number] = self.get_image(0+k, 0+l, width, height, self.temp)
                m += 1
                k += 100
                number += 1
            k = 0
            m = 0
            l += 100
            n += 1

        # enemy running
        self.imageEnemyRunning = [
            pygame.image.load('images/enemy/0/w_000.png'),
            pygame.image.load('images/enemy/0/w_001.png'),
            pygame.image.load('images/enemy/0/w_002.png'),
            pygame.image.load('images/enemy/0/w_003.png'),
            pygame.image.load('images/enemy/0/w_004.png'),
            pygame.image.load('images/enemy/0/w_005.png'),
            pygame.image.load('images/enemy/0/w_006.png'),
            pygame.image.load('images/enemy/0/w_007.png'),
            pygame.image.load('images/enemy/0/w_008.png'),
            pygame.image.load('images/enemy/0/w_009.png')]
        n = 0
        while n < 10:
            self.imageEnemyRunning[n] = pygame.transform.scale(self.imageEnemyRunning[n], (60, 60))
            n += 1
        ###
        self.imageEnemyRunningFlip = [
            pygame.image.load('images/enemy/0/w_000.png'),
            pygame.image.load('images/enemy/0/w_001.png'),
            pygame.image.load('images/enemy/0/w_002.png'),
            pygame.image.load('images/enemy/0/w_003.png'),
            pygame.image.load('images/enemy/0/w_004.png'),
            pygame.image.load('images/enemy/0/w_005.png'),
            pygame.image.load('images/enemy/0/w_006.png'),
            pygame.image.load('images/enemy/0/w_007.png'),
            pygame.image.load('images/enemy/0/w_008.png'),
            pygame.image.load('images/enemy/0/w_009.png')]
        n = 0
        while n < 10:
            self.imageEnemyRunningFlip[n] = pygame.transform.scale(self.imageEnemyRunningFlip[n], (60, 60))
            self.imageEnemyRunningFlip[n] = pygame.transform.flip(self.imageEnemyRunningFlip[n], True, False)
            n += 1

        # images
        self.backgroundImage = pygame.image.load("images/layers/country-platform-back.png")
        self.backgroundImage2 = pygame.image.load("images/layers/country-platform-forest.png")
        self.backgroundImage3 = pygame.image.load("images/layers/country-platform-tiles-example.png")

        self.backgroundImage = pygame.transform.scale(self.backgroundImage, (1280, 720))
        self.backgroundImage2 = pygame.transform.scale(self.backgroundImage2, (300, 720))
        self.backgroundImage3 = pygame.transform.scale(self.backgroundImage3, (1280, 720))

        self.stone = pygame.image.load("images/objects/stone.png")
        self.stone = pygame.transform.scale(self.stone, (234, 200))

        self.enemyImage = pygame.image.load("images/enemy2.png")
        self.platformImage = pygame.image.load("images/platform.png")
        self.platformImage = pygame.transform.scale(self.platformImage, (300, 30))

        self.weaponPickupImage = pygame.image.load("images/weapon.png")
        self.shipImage = pygame.image.load("images/spaceship")

        self.imageGrid0 = pygame.image.load("images/grid0.png")
        self.imageGrid0 = pygame.transform.scale(self.imageGrid0, (80, 80))

        self.imageGrid1 = pygame.image.load("images/grid1.png")
        self.imageGrid1 = pygame.transform.scale(self.imageGrid1, (80, 80))

        # self.imageMenuGrid1 = pygame.image.load("images/menu/grid1.png")
        # self.imageMenuGrid1 = pygame.transform.scale(self.imageMenuGrid1, (80, 80))

    def get_image(self, posx, posy, width, height, sprite_sheet):
        image = pygame.Surface([width, height])
        image.blit(sprite_sheet, (0, 0), (posx, posy, width, height))
        image.set_colorkey((0,0,0))

        return image

    # def spirtesheet(self, filename, cols, rows):
    #     self.sheet = pygame.image.load(filename)
    #     self.cols = cols
    #     self.rows = rows
    #     self.totalCellCount = cols * rows
    #
    #     self.rect = self.sheet.get_rect()
    #     w = self.cellWidth = self.rect.width / cols
    #     h = self.cellHeight = self.rect.height / rows
    #     hw, hh = self.cellCenter = (w / 2, h / 2)
    #
    #     self.cells = list([(index % cols * w, index // cols * h, w, h) for index in range(self.totalCellCount)]) #2048x2048
    #     self.handle = list([
    #         (0,0),(-hw,0),(-w,0),
    #         (0,-hh),(-hw,-hh),(-w,-hh),
    #         (0,-h),(-hw,-h),(-w,-h),])
    #
    # def draw(self, cellIndex, x, y, handle = 0):
    #     self.game.screen.blit(self.sheet,(x + self.handle[handle][0], y + self.handle[handle][1]), self.cells[cellIndex])




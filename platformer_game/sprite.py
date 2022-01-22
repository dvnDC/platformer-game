import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game

        self.left = False
        self.right = False
        self.walkCount = 0

        # player
        # standing
        self.imagePlayerStand = pygame.image.load("images/hero/Knight/Stand/0.png")
        self.imagePlayerStand = pygame.transform.scale(self.imagePlayerStand, (160, 160))


        # self.playerImage = pygame.transform.scale(self.playerImage, (20, 60))

        self.backgroundImage = 0
        self.backgroundImage2 = 0
        self.backgroundImage3 = 0
        self.stone = 0
        self.imagePlayerRun = []            # player knight running right
        self.imagePlayerRunFlip = []        # player knight running left
        self.imageEnemyRunning = []         # enemy blob running right
        self.imageEnemyRunningFlip = []     # enemy blob running left
        self.imageFireball = []
        self.imageFireballFlip = []
        self.imagePlayerAttack = []
        self.imagePlayerAttackFlip = []
        self.imageAttackEffect=[]

        self.enemyImage = pygame.image.load("images/enemy2.png") # NOT USED
        self.weaponPickupImage = pygame.image.load("images/weapon.png") # NOT USED


    def tmp_melee_attack(self):
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

    def load_image(self, image_path):
        return self.game.file_loader.get_image(image_path)

    # number: number of images in folder
    def load_folder(self, folder_path, number):
        return self.game.file_loader.get_image_folder(folder_path, number)

    def transform(self, image, scale=(0,0)):
        return pygame.transform.scale(image, scale)

    def transform_array(self, images, scale=(0, 0)):
        array = []
        for i in range(len(images)):
            array.append(pygame.transform.scale(images[i], scale))
        return array

    def flip_image(self, image):
        return pygame.transform.flip(image, True, False)

    def flip_array(self, images):
        array = []
        for i in range(len(images)):
            array.append(pygame.transform.flip(images[i], True, False))
        return array

    def load_icon(self):
        icon = self.load_image("images/icon.png") # 32x32 file
        pygame.display.set_icon(icon)

    def load_images(self):
        self.imagePlayerRun = self.transform_array(self.load_folder("images/hero/Knight/Run/", 10), (160, 160))
        self.imagePlayerRunFlip = self.flip_array(self.imagePlayerRun)

        self.backgroundImage = self.transform(self.load_image("images/layers/country-platform-back.png"), (640, 360))
        self.backgroundImage2 = self.transform(self.load_image("images/layers/country-platform-forest.png"), (150, 360))
        self.backgroundImage3 = self.transform(self.load_image("images/layers/country-platform-tiles-example.png"), (640, 360))


        self.platformImage = self.transform(self.load_image("images/platform.png"), (30, 30))
        self.stone = self.transform(self.load_image("images/objects/stone.png"), (117, 100))

        self.imageGrid0 = self.transform(self.load_image("images/grid/0.png"), (40, 40))
        self.imageGrid1 = self.transform(self.load_image("images/grid/1.png"), (40, 40))

        self.imageEnemyRunning = self.transform_array(self.load_folder("images/enemy/blob/", 10), (60, 60))
        self.imageEnemyRunningFlip = self.flip_array(self.imageEnemyRunning)

        self.imageFireball = self.transform_array(self.load_folder("images/effects/fireball/", 6), (128, 50))
        self.imageFireballFlip = self.flip_array(self.imagePlayerRun)

        self.imagePlayerAttack = self.transform_array(self.load_folder("images/hero/Knight/Attack1H/", 10), (160, 160))
        self.imagePlayerAttackFlip = self.flip_array(self.imagePlayerRun)

        self.tmp_melee_attack()

    def get_image(self, posx, posy, width, height, sprite_sheet):
        image = pygame.Surface([width, height])
        image.blit(sprite_sheet, (0, 0), (posx, posy, width, height))
        image.set_colorkey((0,0,0))

        return image

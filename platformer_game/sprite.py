import pygame
from file_loader import FileLoader


class Sprite(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self.file_loader = FileLoader(game)

        self.left = False
        self.right = False
        self.walkCount = 0

        self.load_player_images()
        self.load_effect_images()
        self.load_enemy_images()
        self.load_background_and_object_images()
        self.load_attack_effect_images()

    def load_player_images(self):
        """Load player images."""
        self.imagePlayerStand = self.file_loader.get_image("images/hero/Knight/Stand/0.png")
        self.imagePlayerStand = pygame.transform.scale(self.imagePlayerStand, (160, 160))

        self.imagePlayerRun = self.file_loader.get_image_folder('images/hero/Knight/Run/', 10)
        self.imagePlayerRun = [pygame.transform.scale(img, (160, 160)) for img in self.imagePlayerRun]

        self.imagePlayerRunFlip = [pygame.transform.flip(img, True, False) for img in self.imagePlayerRun]

        self.imagePlayerAttack = self.file_loader.get_image_folder('images/hero/Knight/Attack1H/', 10)
        self.imagePlayerAttack = [pygame.transform.scale(img, (160, 160)) for img in self.imagePlayerAttack]

        self.imagePlayerAttackFlip = [pygame.transform.flip(img, True, False) for img in self.imagePlayerAttack]

    def load_effect_images(self):
        """Load effect images."""
        self.imageFireball = self.file_loader.get_image_folder('images/effects/', 6)
        self.imageFireball = [pygame.transform.scale(img, (256, 100)) for img in self.imageFireball]
        self.imageFireball = [pygame.transform.flip(img, True, False) for img in self.imageFireball]

        self.imageFireballLeft = [pygame.transform.scale(img, (256, 100)) for img in self.imageFireball]

    def load_attack_effect_images(self):
        self.temp = pygame.image.load("images/effects/attack/2.png")
        self.temp = pygame.transform.scale(self.temp, (400, 400))
        n = 0
        m = 0
        width = 100
        height = 100
        k = 0
        l = 0
        number = 0
        self.imageAttackEffect = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        while n < 3:
            while m < 4:
                self.imageAttackEffect[number] = self.get_image(0 + k, 0 + l, width, height, self.temp)
                m += 1
                k += 100
                number += 1
            k = 0
            m = 0
            l += 100
            n += 1

    def get_image(self, posx, posy, width, height, sprite_sheet):
        image = pygame.Surface([width, height])
        image.blit(sprite_sheet, (0, 0), (posx, posy, width, height))
        image.set_colorkey((0,0,0))

        return image
    def load_enemy_images(self):
        """Load enemy images."""
        self.imageEnemyRunning = self.file_loader.get_image_folder('images/enemy/0/w_', 10)
        self.imageEnemyRunning = [pygame.transform.scale(img, (60, 60)) for img in self.imageEnemyRunning]

        self.imageEnemyRunningFlip = self.file_loader.get_image_folder('images/enemy/0/w_', 10)
        self.imageEnemyRunningFlip = [pygame.transform.scale(img, (60, 60)) for img in self.imageEnemyRunningFlip]
        self.imageEnemyRunningFlip = [pygame.transform.flip(img, True, False) for img in self.imageEnemyRunningFlip]

    def load_background_and_object_images(self):
        """Load background and object images."""
        self.backgroundImage = pygame.image.load("images/layers/country-platform-back.png")
        self.backgroundImage2 = pygame.image.load("images/layers/country-platform-forest.png")
        self.backgroundImage3 = pygame.image.load("images/layers/country-platform-tiles-example.png")

        self.backgroundImage = pygame.transform.scale(self.backgroundImage, (1280, 720))
        self.backgroundImage2 = pygame.transform.scale(self.backgroundImage2, (300, 720))
        self.backgroundImage3 = pygame.transform.scale(self.backgroundImage3, (1280, 720))

        self.imageGrid0 = pygame.image.load("images/grid0.png")
        self.imageGrid1 = pygame.image.load("images/grid1.png")

        self.stone = pygame.image.load("images/objects/stone.png")
        self.stone = pygame.transform.scale(self.stone, (234, 200))

        self.enemyImage = pygame.image.load("images/enemy2.png")
        self.platformImage = pygame.image.load("images/platform.png")
        self.platformImage = pygame.transform.scale(self.platformImage, (300, 30))

        self.weaponPickupImage = self.file_loader.get_image("images/weapon.png")
        self.weaponPickupImage = pygame.transform.scale(self.weaponPickupImage, (50, 50))
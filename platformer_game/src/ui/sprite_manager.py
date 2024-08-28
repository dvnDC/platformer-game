import pygame
from src.core.asset_loader import AssetLoader

class SpriteManager(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self.file_loader = AssetLoader(game)
        self.left = False
        self.right = False
        self.walkCount = 0

        self.load_images()

    def load_images(self):
        self.load_player_images()
        self.load_enemy_images()
        self.load_background_and_object_images()
        self.load_effect_images()
        self.load_attack_effect_images()

    def load_player_images(self):
        """Load player images."""
        self.imagePlayerStand = self.scale_image("assets/images/hero/Knight/Stand/0.png", (160, 160))
        self.imagePlayerRun = self.scale_images_folder('assets/images/hero/Knight/Run/', (160, 160), 10)
        self.imagePlayerRunFlip = self.flip_images(self.imagePlayerRun)
        self.imagePlayerAttack = self.scale_images_folder('assets/images/hero/Knight/Attack1H/', (160, 160), 10)
        self.imagePlayerAttackFlip = self.flip_images(self.imagePlayerAttack)

    def load_enemy_images(self):
        """Load enemy images."""
        self.imageEnemyRunning = self.scale_images_folder('assets/images/enemy/0/w_', (60, 60), 10)
        self.imageEnemyRunningFlip = self.flip_images(self.imageEnemyRunning)

    def load_background_and_object_images(self):
        """Load background and object images."""
        self.backgroundImage = self.scale_image("assets/images/layers/country-platform-back.png", (1280, 720))
        self.backgroundImage2 = self.scale_image("assets/images/layers/country-platform-forest.png", (300, 720))
        self.backgroundImage3 = self.scale_image("assets/images/layers/country-platform-tiles-example.png", (1280, 720))
        self.imageGrid0 = pygame.image.load("assets/images/grid0.png")
        self.imageGrid1 = pygame.image.load("assets/images/grid1.png")
        self.stone = self.scale_image("assets/images/objects/stone.png", (234, 200))
        self.enemyImage = pygame.image.load("assets/images/enemy2.png")
        self.platformImage = self.scale_image("assets/images/platform.png", (300, 30))
        self.weaponPickupImage = self.scale_image("assets/images/weapon.png", (50, 50))

    def load_effect_images(self):
        """Load effect images."""
        self.imageFireball = self.scale_images_folder('assets/images/effects/', (256, 100), 6)
        self.imageFireballLeft = self.imageFireball.copy()

    def load_attack_effect_images(self):
        sprite_sheet = self.scale_image("assets/images/effects/attack/2.png", (400, 400))
        self.imageAttackEffect = self.slice_sprite_sheet(sprite_sheet, 3, 4, (100, 100))

    def scale_image(self, path, size):
        return pygame.transform.scale(pygame.image.load(path), size)

    def scale_images_folder(self, folder, size, count):
        return [self.scale_image(f'{folder}{i}.png', size) for i in range(count)]

    def flip_images(self, images):
        return [pygame.transform.flip(img, True, False) for img in images]

    def slice_sprite_sheet(self, sprite_sheet, rows, cols, cell_size):
        images = []
        for row in range(rows):
            for col in range(cols):
                x = col * cell_size[0]
                y = row * cell_size[1]
                images.append(self.get_image(x, y, cell_size[0], cell_size[1], sprite_sheet))
        return images

    def get_image(self, posx, posy, width, height, sprite_sheet):
        image = pygame.Surface([width, height], pygame.SRCALPHA)
        image.blit(sprite_sheet, (0, 0), (posx, posy, width, height))
        return image

    # def load_attack_effect_images(self):
    #     self.temp = pygame.image.load("images/effects/attack/2.png")
    #     self.temp = pygame.transform.scale(self.temp, (400, 400))
    #     n = 0
    #     m = 0
    #     width = 100
    #     height = 100
    #     k = 0
    #     l = 0
    #     number = 0
    #     self.imageAttackEffect = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     while n < 3:
    #         while m < 4:
    #             self.imageAttackEffect[number] = self.get_image(0 + k, 0 + l, width, height, self.temp)
    #             m += 1
    #             k += 100
    #             number += 1
    #         k = 0
    #         m = 0
    #         l += 100
    #         n += 1

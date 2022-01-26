import pygame

class Sprite(pygame.sprite.Sprite):

    def __init__(self, game):
        self.game = game

        "Scale"
        # (width, height)
        self.display_scale = self.scale_image(320, 180) # background, background3

        self.background_scale = self.display_scale # background, background3
        self.background3_scale = self.display_scale # background, background3
        self.background2_scale = self.scale_image(75, 180)
        self.platform_scale = self.scale_image(15, 15)
        self.stone_scale = self.scale_image(57, 50)
        self.grid_scale = self.scale_image(40, 40)

        self.player_scale = self.scale_image(40, 40)
        self.player_effect_scale = self.scale_image(400, 400) # vanilla 400, 400

        self.fireball_scale = self.scale_image(64, 25)
        self.enemy_scale = self.scale_image(30, 30)

        "Images"
        # Map
        self.img_background = 0
        self.img_background2 = 0
        self.img_background3 = 0
        self.img_stone = 0
        self.img_platform = 0
        self.imageGrid0 = 0
        self.imageGrid1 = 0

        # Player
        self.img_player_idle = 0
        self.img_player_running = []
        self.img_player_running_flip = []
        self.img_player_attacking = []
        self.img_player_attacking_flip = []
        self.img_attack_effect=[]

        # Effects
        self.img_fireball = []
        self.img_fireball_flip = []

        # Enemies
        self.img_enemy_running = []
        self.img_enemy_running_flip = []

        # Not used
        self.enemyImage = pygame.image.load("images/enemy2.png")
        self.weaponPickupImage = pygame.image.load("images/weapon.png")

    def scale_image(self, width, height):
        return width * self.game.SCALE, height * self.game.SCALE

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
        
    def img_tmp_melee_attack(self): # TODO: Simple refactoring
        def get_image(posx, posy, width, height, sprite_sheet):
            image = pygame.Surface([width, height])
            image.blit(sprite_sheet, (0, 0), (posx, posy, width, height))
            image.set_colorkey((0, 0, 0))
            return image

        temp = self.transform(self.load_image("images/effects/attack/2.png"), self.player_effect_scale)
        n = 0
        m = 0
        width = 100
        height = 100
        k = 0
        l = 0
        number = 0
        self.img_attack_effect=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        while n < 3:
            while m < 4:
                self.img_attack_effect[number] = get_image(0 + k, 0 + l, width, height, temp)
                m += 1
                k += 100
                number += 1
            k = 0
            m = 0
            l += 100
            n += 1

    "After adding new sprite - ADD it also to images.py"
    def load_images(self):
        # Map
        self.img_background = self.transform(self.load_image("images/layers/country-platform-back.png"), self.background_scale)
        self.img_background2 = self.transform(self.load_image("images/layers/country-platform-forest.png"), self.background2_scale)
        self.img_background3 = self.transform(self.load_image("images/layers/country-platform-tiles-example.png"), self.background3_scale)
        self.img_platform = self.transform(self.load_image("images/platform.png"), self.platform_scale)
        self.img_stone = self.transform(self.load_image("images/objects/stone.png"), self.stone_scale)
        self.imageGrid0 = self.transform(self.load_image("images/grid/0.png"), self.grid_scale)
        self.imageGrid1 = self.transform(self.load_image("images/grid/1.png"), self.grid_scale)

        # Player
        self.img_player_running = self.transform_array(self.load_folder("images/hero/Knight/Run/", 10), self.player_scale)
        self.img_player_running_flip = self.flip_array(self.img_player_running)
        self.img_player_attacking = self.transform_array(self.load_folder("images/hero/Knight/Attack1H/", 10), self.player_scale)
        self.img_player_attacking_flip = self.flip_array(self.img_player_attacking)
        self.img_player_idle = self.transform(self.load_image("images/hero/Knight/Stand/0.png"), self.player_scale)
        self.img_tmp_melee_attack()

        # Effects
        self.img_fireball = self.transform_array(self.load_folder("images/effects/fireball/", 6), self.fireball_scale)
        self.img_fireball_flip = self.flip_array(self.img_fireball)

        # Enemies
        self.img_enemy_running = self.transform_array(self.load_folder("images/enemy/blob/", 10), self.enemy_scale)
        self.img_enemy_running_flip = self.flip_array(self.img_enemy_running)


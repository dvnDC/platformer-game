import pygame


class FileLoader(object):

    def __init__(self, game):
        self.game = game

    def get_image(self, key):
        image_cache = {}
        if not key in image_cache:
            image_cache[key] = pygame.image.load(key)
        return image_cache[key]

    # Image file index starts from 0. Example: 2 images: 0.png 1.png
    def get_image_folder(self, folder_path, number):
        images = []
        for i in range(number):
            path = folder_path + str(i) + '.png'
            images.append(self.get_image(path))
        return images


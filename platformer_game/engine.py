import pygame


class Engine(object):
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont("Arial", 18)
        self.fonts = self.create_fonts([32, 16, 14, 8])

    def create_fonts(self, font_sizes_list):
        """
        Creates different fonts with one list
        """
        self.fonts = []
        for size in font_sizes_list:
            self.fonts.append(
                pygame.font.SysFont("Arial", size))
        return self.fonts

    def render(self, fnt, what, color, where):
        """
        Renders the fonts as passed from display_fps
        """
        text_to_show = fnt.render(what, 0, pygame.Color(color))
        self.game.screen.blit(text_to_show, where)

    def display_fps(self):
        """
        Data that will be rendered and blitted in _display
        """
        self.render(
            self.fonts[0],
            what=str(int(self.game.tps_clock.get_fps())),
            color="white",
            where=(0, 0))

"""Checks that images are converted to the display format once, after the display
mode is set, without changing how they look (roadmap task R-32). Runs headlessly
in-process, so real-window speed isn't covered. Run from the repository root with:

    venv/bin/python -B -m unittest discover -s tests -v
"""
import collections
import os
import sys
import unittest
from unittest import mock

GAME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platformer_game")
# PNG files with no alpha channel. Every other image has real transparency.
OPAQUE_IMAGES = {"backgroundImage", "imageGrid0", "imageGrid1", "platformImage"}
BACKGROUND_COLOR = (90, 160, 40)

environment_patch = mock.patch.dict(
    os.environ,
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    PYGAME_HIDE_SUPPORT_PROMPT="1",
)
original_directory = os.getcwd()
pygame = None
Game = None
SpriteManager = None
AssetLoader = None


def setUpModule():
    global pygame, Game, SpriteManager, AssetLoader
    environment_patch.start()
    # Imports and sprite paths both resolve against platformer_game/.
    os.chdir(GAME_DIR)
    sys.path.insert(0, GAME_DIR)
    import pygame
    from src.core.asset_loader import AssetLoader
    from src.game import Game
    from src.ui.sprite_manager import SpriteManager


def tearDownModule():
    pygame.quit()
    sys.path.remove(GAME_DIR)
    os.chdir(original_directory)
    environment_patch.stop()


def game_images(sprite):
    """Every surface a SpriteManager holds, as (name, surface) pairs."""
    images = []
    for name, value in sorted(vars(sprite).items()):
        if isinstance(value, pygame.Surface):
            images.append((name, value))
        elif isinstance(value, list):
            images.extend((f"{name}[{index}]", frame) for index, frame in enumerate(value))
    return images


def base_name(image_name):
    return image_name.split("[")[0]


def unconverted_game():
    with mock.patch.object(SpriteManager, "optimize", lambda self, surface: surface):
        return Game()


def has_per_pixel_alpha(surface):
    return bool(surface.get_flags() & pygame.SRCALPHA)


class SurfaceConversionTestCase(unittest.TestCase):
    def setUp(self):
        self.keys = collections.defaultdict(bool)
        patcher = mock.patch("pygame.key.get_pressed", lambda: self.keys)
        patcher.start()
        self.addCleanup(patcher.stop)


class DisplayOrderTests(SurfaceConversionTestCase):
    def test_conversion_without_a_display_mode_fails_loudly(self):
        Game()
        pygame.display.quit()
        self.addCleanup(pygame.display.init)
        with self.assertRaises(pygame.error):
            SpriteManager(mock.Mock())

    def test_game_sets_the_display_mode_before_loading_images(self):
        pygame.display.quit()
        self.addCleanup(pygame.display.init)
        surfaces_at_load = []

        def recording_sprite_manager(game):
            surfaces_at_load.append(pygame.display.get_surface())
            return SpriteManager(game)

        with mock.patch("src.game.SpriteManager", recording_sprite_manager):
            game = Game()
        self.assertEqual(len(surfaces_at_load), 1)
        self.assertIs(surfaces_at_load[0], game.screen)


class ClassificationTests(SurfaceConversionTestCase):
    def setUp(self):
        super().setUp()
        self.game = Game()
        self.images = game_images(self.game.sprite)

    def test_the_test_finds_all_the_images(self):
        self.assertGreater(len(self.images), 90)

    def test_only_opaque_images_lose_the_alpha_channel(self):
        for name, surface in self.images:
            with self.subTest(image=name):
                self.assertEqual(has_per_pixel_alpha(surface), base_name(name) not in OPAQUE_IMAGES)

    def test_opaque_images_match_the_display_format(self):
        for name, surface in self.images:
            if base_name(name) in OPAQUE_IMAGES:
                with self.subTest(image=name):
                    self.assertEqual(surface.get_masks(), self.game.screen.get_masks())
                    self.assertEqual(surface.get_bitsize(), self.game.screen.get_bitsize())

    def test_scaled_and_flipped_copies_keep_the_converted_format(self):
        sprite = self.game.sprite
        flipped = pygame.transform.flip(sprite.imagePlayerStand, True, False)
        self.assertEqual(flipped.get_masks(), sprite.imagePlayerStand.get_masks())
        scaled = pygame.transform.scale(sprite.platformImage, (300, 30))
        self.assertEqual(scaled.get_masks(), self.game.screen.get_masks())


class OptimizeTests(SurfaceConversionTestCase):
    def setUp(self):
        super().setUp()
        self.sprite = Game().sprite

    def test_surface_with_no_alpha_becomes_opaque_display_format(self):
        surface = pygame.Surface((4, 4), depth=24)
        self.assertFalse(has_per_pixel_alpha(self.sprite.optimize(surface)))

    def test_surface_with_alpha_keeps_partial_transparency(self):
        surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        surface.fill((10, 20, 30, 128))
        converted = self.sprite.optimize(surface)
        self.assertTrue(has_per_pixel_alpha(converted))
        self.assertEqual(tuple(converted.get_at((0, 0))), (10, 20, 30, 128))

    def test_surface_with_a_colorkey_stays_transparent(self):
        surface = pygame.Surface((2, 1), depth=24)
        surface.fill((255, 0, 255))
        surface.set_at((1, 0), (1, 2, 3))
        surface.set_colorkey((255, 0, 255))
        converted = self.sprite.optimize(surface)
        self.assertEqual(converted.get_at((0, 0))[3], 0)
        self.assertEqual(tuple(converted.get_at((1, 0))), (1, 2, 3, 255))


class AppearanceTests(SurfaceConversionTestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = dict(game_images(unconverted_game().sprite))

    def setUp(self):
        super().setUp()
        self.game = Game()
        self.after = dict(game_images(self.game.sprite))

    def on_background(self, surface):
        canvas = pygame.Surface(surface.get_size()).convert(self.game.screen)
        canvas.fill(BACKGROUND_COLOR)
        canvas.blit(surface, (0, 0))
        return pygame.image.tobytes(canvas, "RGB")

    def test_conversion_keeps_size_and_every_pixel(self):
        self.assertEqual(self.after.keys(), self.before.keys())
        for name, surface in self.after.items():
            with self.subTest(image=name):
                self.assertEqual(surface.get_size(), self.before[name].get_size())
                self.assertEqual(pygame.image.tobytes(surface, "RGBA"),
                                 pygame.image.tobytes(self.before[name], "RGBA"))

    def test_conversion_blits_the_same_over_a_background(self):
        for name in ("imagePlayerStand", "imagePlayerRun[3]", "imageEnemyRunning[0]", "stone",
                     "imageAttackEffect[5]", "imageFireball[2]", "backgroundImage2", "platformImage"):
            with self.subTest(image=name):
                self.assertEqual(self.on_background(self.after[name]), self.on_background(self.before[name]))

    def test_a_rendered_frame_looks_the_same(self):
        def frame(game):
            game.engine.display_fps = lambda: None
            game.render()
            return pygame.image.tobytes(game.screen, "RGB")

        self.assertEqual(frame(self.game), frame(unconverted_game()))


class RepeatedWorkTests(SurfaceConversionTestCase):
    def test_each_file_loads_once_at_startup(self):
        loads = collections.Counter()
        original_load = pygame.image.load

        def counting_load(path):
            loads[path] += 1
            return original_load(path)

        with mock.patch("pygame.image.load", counting_load):
            Game()
        self.assertGreater(len(loads), 0)
        self.assertEqual({path: count for path, count in loads.items() if count > 1}, {})

    def test_playing_does_not_load_or_convert_again(self):
        game = Game()
        before = game_images(game.sprite)
        self.keys[pygame.K_a] = True
        with mock.patch("pygame.image.load") as load, \
                mock.patch.object(SpriteManager, "optimize") as optimize, \
                mock.patch.object(AssetLoader, "get_image") as get_image:
            for _ in range(20):
                game.tick()
                game.render()
        load.assert_not_called()
        optimize.assert_not_called()
        get_image.assert_not_called()
        for (name, surface), (_, same_surface) in zip(before, game_images(game.sprite)):
            self.assertIs(surface, same_surface, name)


if __name__ == "__main__":
    unittest.main()

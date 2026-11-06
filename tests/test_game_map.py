"""Regression checks for GameMap: no per-frame leak (roadmap task R-01) and
unchanged map structure and collision behaviour. Runs headlessly in-process.
Run from the repository root with:

    venv/bin/python -B -m unittest discover -s tests -v
"""
import collections
import gc
import os
import sys
import tracemalloc
import unittest
from unittest import mock

GAME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platformer_game")
GAME_MAP_FILE = os.path.join(GAME_DIR, "src", "world", "game_map.py")
TILE = 80
FLOOR_TOP = 640
GAP_COLUMNS = (27, 42)
# One grid() call used to retain about 155 KB, so 100 calls leaked about 16 MB.
RETAINED_LIMIT_BYTES = 16 * 1024

environment_patch = mock.patch.dict(
    os.environ,
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    PYGAME_HIDE_SUPPORT_PROMPT="1",
)
original_directory = os.getcwd()
pygame = None
Game = None


def setUpModule():
    global pygame, Game
    environment_patch.start()
    # Imports and sprite paths both resolve against platformer_game/.
    os.chdir(GAME_DIR)
    sys.path.insert(0, GAME_DIR)
    import pygame
    from src.game import Game


def tearDownModule():
    pygame.quit()
    sys.path.remove(GAME_DIR)
    os.chdir(original_directory)
    environment_patch.stop()


def solid_tiles():
    floor = [(8, column) for column in range(80) if column not in GAP_COLUMNS]
    return floor + [(9, 53), (9, 54)]


def expected_boxes(checkpoint_offset):
    return [
        (TILE * column + checkpoint_offset, TILE * column + TILE + checkpoint_offset, TILE * row, TILE * row + TILE)
        for row, column in solid_tiles()
    ]


def boxes(game_map):
    return game_map.GRID_boxes_coll[:game_map.GRID_boxes_coll_number]


class RecordingScreen:
    def __init__(self):
        self.blits = []

    def blit(self, image, position):
        self.blits.append((image, position))


class GameMapTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.map = self.game.map


class GridPositionLeakTests(GameMapTestCase):
    def test_repeated_grid_calls_do_not_grow_grid_position(self):
        self.map.grid()
        length_after_first_call = len(getattr(self.map, "GRID_position", ()))
        for _ in range(50):
            self.map.grid()
        self.assertEqual(len(getattr(self.map, "GRID_position", ())), length_after_first_call)

    # Catches the same leak under any attribute name, unlike the length check.
    def test_repeated_grid_calls_retain_no_memory(self):
        tracemalloc.start()
        self.addCleanup(tracemalloc.stop)
        file_filter = [tracemalloc.Filter(True, GAME_MAP_FILE)]

        # Traced from the first call, so replaced boxes do not count as growth.
        self.map.grid()
        gc.collect()
        before = tracemalloc.take_snapshot().filter_traces(file_filter)
        for _ in range(100):
            self.map.grid()
        gc.collect()
        after = tracemalloc.take_snapshot().filter_traces(file_filter)

        retained = sum(stat.size_diff for stat in after.compare_to(before, "lineno"))
        self.assertLess(retained, RETAINED_LIMIT_BYTES)

    def test_grid_position_is_gone(self):
        self.assertFalse(hasattr(self.map, "GRID_position"))
        self.map.grid()
        self.map.grid_static()
        self.assertFalse(hasattr(self.map, "GRID_position"))


class MapStructureTests(GameMapTestCase):
    def test_grid_dimensions(self):
        self.assertEqual(len(self.map.GRID), 10)
        self.assertTrue(all(len(row) == 80 for row in self.map.GRID))

    def test_tile_layout(self):
        tiles = collections.defaultdict(list)
        for row, values in enumerate(self.map.GRID):
            for column, value in enumerate(values):
                tiles[value].append((row, column))

        self.assertEqual(set(tiles), {0, 1, 7})
        self.assertEqual(tiles[1], solid_tiles())
        self.assertEqual(tiles[7], [(0, column) for column in (0, 16, 32, 48, 64)])

    def test_no_collision_boxes_before_the_first_grid_call(self):
        self.assertEqual(self.map.GRID_boxes_coll_number, 0)

    def test_only_solid_tiles_get_collision_boxes(self):
        self.map.grid()
        self.assertEqual(self.map.GRID_boxes_coll_number, 80)
        self.assertEqual(boxes(self.map), expected_boxes(-2560))

    def test_floor_gaps_keep_their_world_position(self):
        self.map.grid()
        floor = [box for box in boxes(self.map) if box[2] == FLOOR_TOP]
        covered = {box[0] for box in floor}
        self.assertNotIn(-400, covered)
        self.assertNotIn(800, covered)
        self.assertIn(-480, covered)
        self.assertIn(880, covered)

    def test_repeated_grid_calls_rebuild_the_same_boxes(self):
        self.map.grid()
        first_boxes = boxes(self.map)
        for _ in range(5):
            self.map.grid()
        self.assertEqual(boxes(self.map), first_boxes)

    def test_collision_boxes_are_in_world_coordinates(self):
        self.map.scroll.x = 500
        self.map.grid()
        self.assertEqual(boxes(self.map), expected_boxes(-2560))

    def test_collision_boxes_follow_the_player_checkpoint(self):
        for player_x, checkpoint in ((3000, 1), (7000, 2)):
            self.game.player.pos.x = player_x
            self.map.grid()
            self.assertEqual(self.map.player_checkpoint, checkpoint)
            self.assertEqual(boxes(self.map), expected_boxes(3840 * checkpoint - 2560))

    def test_collision_boxes_follow_the_player_checkpoint_backwards(self):
        self.game.player.pos.x = -2000
        self.map.grid()
        self.assertEqual(self.map.player_checkpoint, -1)
        self.assertEqual(boxes(self.map), expected_boxes(-3840 - 2560))

    def test_tiles_are_drawn_at_scrolled_positions(self):
        self.map.scroll.x = 100
        self.game.screen = RecordingScreen()
        self.map.grid()

        def drawn(image):
            return [position for blitted, position in self.game.screen.blits if blitted is image]

        offset = -2560 - 100
        self.assertEqual(
            drawn(self.game.sprite.imageGrid1),
            [(TILE * column + offset, TILE * row) for row, column in solid_tiles()],
        )
        self.assertEqual(
            drawn(self.game.sprite.backgroundImage3),
            [(TILE * column + offset, 0) for column in (0, 16, 32, 48, 64)],
        )
        self.assertEqual(len(self.game.screen.blits), 85)

    def test_grid_static_fills_boxes_without_a_checkpoint_offset(self):
        self.map.grid_static()
        self.assertEqual(boxes(self.map), expected_boxes(0))


class CollisionBehaviourTests(GameMapTestCase):
    def setUp(self):
        super().setUp()
        patcher = mock.patch("pygame.key.get_pressed", lambda: collections.defaultdict(bool))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.game.engine.display_fps = lambda: None

    def advance(self, steps):
        for _ in range(steps):
            self.game.render()
            self.game.tick()

    def test_player_lands_on_the_floor_and_stays(self):
        self.advance(200)
        y = self.game.player.pos.y
        self.assertAlmostEqual(y + self.game.player.height, FLOOR_TOP, delta=12)
        self.assertEqual(self.game.player.vel.y, 0)
        self.advance(50)
        self.assertEqual(self.game.player.pos.y, y)

    def test_player_falls_through_a_floor_gap(self):
        # Starts below the platform that spans the gap at x = 800.
        self.game.player.pos.update(830, 600)
        self.game.player.vel.update(0, 0)
        self.advance(35)  # Below the floor, but not yet past the fall limit (R-02)
        self.assertGreater(self.game.player.pos.y, FLOOR_TOP + TILE)

    def test_player_rests_on_the_platform_above_a_floor_gap(self):
        self.game.player.pos.update(830, 500)
        self.game.player.vel.update(0, 0)
        self.advance(200)
        self.assertEqual(self.game.player.pos.y, 500)
        self.assertEqual(self.game.player.vel.y, 0)

    def test_enemy_lands_on_the_floor(self):
        self.advance(250)
        self.assertTrue(self.game.enemy.live)
        self.assertAlmostEqual(self.game.enemy.pos.y + self.game.enemy.height, FLOOR_TOP, delta=12)
        self.assertEqual(self.game.enemy.vel.y, 0)

    def test_removing_collision_boxes_lets_the_player_fall(self):
        self.advance(200)
        self.game.map.grid = lambda: None
        self.game.map.GRID_boxes_coll_number = 0
        self.advance(50)
        self.assertGreater(self.game.player.pos.y + self.game.player.height, FLOOR_TOP + TILE)


if __name__ == "__main__":
    unittest.main()

"""Checks of the run animation, which advances with ticks rather than draws
(roadmap task R-08). Runs headlessly in-process, so how it looks in a real window
isn't covered. Run from the repository root with:

    venv/bin/python -B -m unittest discover -s tests -v
"""
import collections
import os
import sys
import unittest
from unittest import mock

GAME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platformer_game")
FLOOR_STANDING_Y = 579
OLD_CYCLE_SECONDS = 20 / 60  # 20 drawn frames at the 60 FPS cap, before the counter moved to tick()
FRAMES_IN_USE = 7

environment_patch = mock.patch.dict(
    os.environ,
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    PYGAME_HIDE_SUPPORT_PROMPT="1",
)
original_directory = os.getcwd()
pygame = None
Game = None
RUN_CYCLE_TICKS = None
RUN_FRAME_TICKS = None
TPS_MAX = None


def setUpModule():
    global pygame, Game, RUN_CYCLE_TICKS, RUN_FRAME_TICKS, TPS_MAX
    environment_patch.start()
    # Imports and sprite paths both resolve against platformer_game/.
    os.chdir(GAME_DIR)
    sys.path.insert(0, GAME_DIR)
    import pygame
    from src.game import Game
    from config.settings import RUN_CYCLE_TICKS, RUN_FRAME_TICKS, TPS_MAX


def tearDownModule():
    pygame.quit()
    sys.path.remove(GAME_DIR)
    os.chdir(original_directory)
    environment_patch.stop()


class RecordingFrames(list):
    """A list of animation frames that remembers which indexes were drawn."""

    def __init__(self, frames):
        super().__init__(frames)
        self.drawn = []

    def __getitem__(self, index):
        self.drawn.append(index)
        return super().__getitem__(index)


class RunAnimationTestCase(unittest.TestCase):
    def setUp(self):
        self.keys = collections.defaultdict(bool)
        patcher = mock.patch("pygame.key.get_pressed", lambda: self.keys)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.game = Game()
        self.game.engine.display_fps = lambda: None
        self.player = self.game.player
        self.game.render()  # Fills collision data
        self.player.pos.update(640, FLOOR_STANDING_Y)
        self.player.vel.update(0, 0)

    def record_frames(self):
        sprite = self.game.sprite
        sprite.imagePlayerRun = RecordingFrames(sprite.imagePlayerRun)
        sprite.imagePlayerRunFlip = RecordingFrames(sprite.imagePlayerRunFlip)

    def run_ticks(self, ticks, key=None):
        self.keys[key or pygame.K_a] = True
        for _ in range(ticks):
            self.game.tick()


class RenderingDoesNotAdvanceTests(RunAnimationTestCase):
    def test_repeated_draws_do_not_advance_run_count(self):
        self.run_ticks(7)
        count = self.player.runCount
        self.assertGreater(count, 0)
        for _ in range(50):
            self.player.draw()
        self.assertEqual(self.player.runCount, count)

    def test_repeated_renders_do_not_advance_run_count(self):
        self.run_ticks(7)
        count = self.player.runCount
        for _ in range(5):
            self.game.render()
        self.assertEqual(self.player.runCount, count)

    def test_repeated_draws_keep_the_same_frame(self):
        self.record_frames()
        self.run_ticks(7)
        for _ in range(10):
            self.player.draw()
        self.assertEqual(len(set(self.game.sprite.imagePlayerRunFlip.drawn)), 1)


class TickProgressionTests(RunAnimationTestCase):
    def test_each_running_tick_advances_by_one(self):
        self.run_ticks(5)
        count = self.player.runCount
        self.run_ticks(1)
        self.assertEqual(self.player.runCount, count + 1)

    def test_standing_does_not_advance(self):
        for _ in range(10):
            self.game.tick()
        self.assertEqual(self.player.runCount, 0)

    def test_releasing_the_key_resets_the_animation(self):
        self.run_ticks(7)
        self.keys.clear()
        self.game.tick()
        self.assertEqual(self.player.runCount, 0)

    def test_attacking_pauses_the_animation(self):
        self.run_ticks(7)
        count = self.player.runCount
        self.player.isAttacking = True
        self.run_ticks(5)
        self.assertEqual(self.player.runCount, count)

    def test_progression_does_not_depend_on_how_often_it_is_drawn(self):
        def progress(draw_every_ticks, draws):
            self.setUp()
            self.keys[pygame.K_a] = True
            counts = []
            for tick_number in range(120):
                self.game.tick()
                counts.append(self.player.runCount)
                if tick_number % draw_every_ticks == 0:
                    for _ in range(draws):
                        self.game.render()
            return counts

        reference = progress(draw_every_ticks=1, draws=1)
        self.assertEqual(progress(draw_every_ticks=4, draws=1), reference)
        self.assertEqual(progress(draw_every_ticks=1, draws=3), reference)


class AnimationSpeedTests(RunAnimationTestCase):
    def test_cycle_length_stays_close_to_the_old_speed(self):
        self.assertAlmostEqual(RUN_CYCLE_TICKS / TPS_MAX, OLD_CYCLE_SECONDS, delta=0.01)

    def test_a_cycle_shows_the_seven_frames_with_the_same_timing_as_before(self):
        self.record_frames()
        self.player.runCount = 0
        self.keys[pygame.K_a] = True
        for _ in range(RUN_CYCLE_TICKS):
            self.game.tick()
            self.player.draw()
        # 3 drawn frames each and 2 for the last, as it was at 60 FPS and 100 ticks per second.
        ticks_per_frame = collections.Counter(self.game.sprite.imagePlayerRunFlip.drawn)
        self.assertEqual(ticks_per_frame, {0: 5, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 3})
        self.assertEqual(self.player.runCount, 0)


class FrameIndexTests(RunAnimationTestCase):
    def assert_indexes_are_in_use(self, frames):
        self.assertEqual(set(frames.drawn), set(range(FRAMES_IN_USE)))

    def test_running_left_stays_within_the_frames_in_use(self):
        self.record_frames()
        self.keys[pygame.K_a] = True
        for _ in range(RUN_CYCLE_TICKS * 3):
            self.game.tick()
            self.player.draw()
        self.assert_indexes_are_in_use(self.game.sprite.imagePlayerRunFlip)

    def test_running_right_stays_within_the_frames_in_use(self):
        self.record_frames()
        self.player.pos.x = 1000  # The floor gap at x = 800 is behind the player
        self.keys[pygame.K_d] = True
        for _ in range(RUN_CYCLE_TICKS * 3):
            self.game.tick()
            self.player.draw()
        self.assert_indexes_are_in_use(self.game.sprite.imagePlayerRun)

    # Before, draws advanced the counter and only a tick wrapped it. 12 draws in a row
    # after a tick reached index 10 of the 10 frames and crashed with an IndexError.
    def test_many_draws_from_any_count_do_not_leave_the_frame_list(self):
        self.record_frames()
        self.player.isRunning = True
        self.player.vel.x = -1
        for count in range(RUN_CYCLE_TICKS):
            self.player.runCount = count
            for _ in range(40):
                self.player.draw()
        self.assert_indexes_are_in_use(self.game.sprite.imagePlayerRunFlip)

    def test_a_long_run_never_leaves_the_frame_list(self):
        self.keys[pygame.K_a] = True
        seen = set()
        for _ in range(2000):
            self.player.pos.update(640, FLOOR_STANDING_Y)  # Stays away from the gaps
            self.player.tick()
            seen.add(self.player.runCount)
        self.assertEqual(seen, set(range(RUN_CYCLE_TICKS)))


if __name__ == "__main__":
    unittest.main()

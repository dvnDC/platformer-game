"""Checks of the game loop's frame cap and catch-up limit (roadmap task R-08).

Most tests replace the clock, so frame times are exact and a stall takes no real
time. Runs headlessly in-process, so real-window behaviour isn't covered. Run from
the repository root with:

    venv/bin/python -B -m unittest discover -s tests -v
"""
import collections
import os
import sys
import time
import unittest
from unittest import mock

GAME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platformer_game")
FLOOR_TOP = 640
STALL_MS = 60000
LOADING_MS = 5000

environment_patch = mock.patch.dict(
    os.environ,
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    PYGAME_HIDE_SUPPORT_PROMPT="1",
)
original_directory = os.getcwd()
pygame = None
Game = None
FPS_MAX = None
MAX_TICKS_PER_FRAME = None
PLAYER_LIVES = None
TPS_MAX = None


def setUpModule():
    global pygame, Game, FPS_MAX, MAX_TICKS_PER_FRAME, PLAYER_LIVES, TPS_MAX
    environment_patch.start()
    # Imports and sprite paths both resolve against platformer_game/.
    os.chdir(GAME_DIR)
    sys.path.insert(0, GAME_DIR)
    import pygame
    from src.game import Game
    from config.settings import FPS_MAX, MAX_TICKS_PER_FRAME, PLAYER_LIVES, TPS_MAX


def tearDownModule():
    pygame.quit()
    sys.path.remove(GAME_DIR)
    os.chdir(original_directory)
    environment_patch.stop()


class FakeClock:
    """Reports the given frame times. The first call is the reset before the loop,
    and the last one ends the frame that posts the quit event."""

    def __init__(self, frame_times_ms):
        self.results = iter([LOADING_MS] + list(frame_times_ms) + [0])
        self.framerates = []

    def tick(self, framerate=0):
        self.framerates.append(framerate)
        return next(self.results)

    def get_fps(self):
        return 0.0


class GameLoopTestCase(unittest.TestCase):
    def setUp(self):
        self.keys = collections.defaultdict(bool)
        patcher = mock.patch("pygame.key.get_pressed", lambda: self.keys)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.game = Game()
        self.game.engine.display_fps = lambda: None

    def run_frames(self, frame_times_ms, on_tick=lambda tick_number: None):
        """Runs Game.run for one frame per given time, plus the first frame, which
        has no time before it. Returns the number of ticks before each render."""
        self.game.tps_clock = FakeClock(frame_times_ms)
        original_tick = self.game.tick
        original_render = self.game.render
        ticks_per_frame = []
        ticks = [0, 0]  # total, since the last render

        def tick():
            on_tick(ticks[0])
            original_tick()
            ticks[0] += 1
            ticks[1] += 1

        def render():
            original_render()
            ticks_per_frame.append(ticks[1])
            ticks[1] = 0
            if len(ticks_per_frame) == len(frame_times_ms) + 1:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

        self.game.tick = tick
        self.game.render = render
        with self.assertRaises(SystemExit) as stopped:
            self.game.run()
        self.assertEqual(stopped.exception.code, 0)
        return ticks_per_frame


class NormalSpeedTests(GameLoopTestCase):
    def assert_game_time_matches(self, frame_ms, frames):
        total_ticks = sum(self.run_frames([frame_ms] * frames))
        self.assertAlmostEqual(total_ticks, frame_ms * frames * TPS_MAX / 1000, delta=1)

    def test_game_time_follows_real_time_at_the_frame_cap(self):
        self.assert_game_time_matches(frame_ms=16, frames=125)

    def test_game_time_follows_real_time_on_a_slow_frame_rate(self):
        self.assert_game_time_matches(frame_ms=100, frames=20)

    def test_game_time_follows_real_time_faster_than_the_tick_rate(self):
        self.assert_game_time_matches(frame_ms=3, frames=100)

    def test_a_frame_just_under_the_limit_loses_no_time(self):
        almost_limit_ms = (MAX_TICKS_PER_FRAME - 1) * 1000 // TPS_MAX
        self.assert_game_time_matches(frame_ms=almost_limit_ms, frames=8)

    def test_player_path_does_not_depend_on_the_frame_rate(self):
        def path_at(frame_ms, ticks=200):
            self.setUp()

            def script(tick_number):
                self.keys.clear()
                self.keys[pygame.K_a] = 100 <= tick_number < 170
                self.keys[pygame.K_SPACE] = 130 <= tick_number < 135
                self.keys[pygame.K_e] = 110 <= tick_number < 112
                self.keys[pygame.K_d] = tick_number >= 180
                player = self.game.player
                path.append((player.pos.x, player.pos.y, player.vel.x, player.vel.y, player.runCount,
                             player.isAttacking, player.attack_ticks))

            path = []
            self.run_frames([frame_ms] * (ticks * 10 // frame_ms + 1), on_tick=script)
            return path[:ticks]

        reference = path_at(10)
        self.assertEqual(len(reference), 200)
        self.assertLess(reference[-1][0], 640, "the script never moved the player")
        self.assertEqual(path_at(16), reference)
        self.assertEqual(path_at(100), reference)


class CatchUpLimitTests(GameLoopTestCase):
    def test_a_stall_runs_at_most_the_limit_of_ticks(self):
        ticks_per_frame = self.run_frames([16, STALL_MS, 16])
        self.assertEqual(ticks_per_frame[0], 0)
        self.assertLessEqual(ticks_per_frame[2], MAX_TICKS_PER_FRAME)
        self.assertGreaterEqual(ticks_per_frame[2], MAX_TICKS_PER_FRAME - 1)

    def test_time_above_the_limit_is_not_carried_to_later_frames(self):
        ticks_per_frame = self.run_frames([STALL_MS, 16, 16, 16])
        self.assertLessEqual(max(ticks_per_frame[2:]), 2)

    def test_stalling_on_every_frame_stays_at_the_limit(self):
        ticks_per_frame = self.run_frames([STALL_MS] * 10)
        self.assertLessEqual(max(ticks_per_frame), MAX_TICKS_PER_FRAME)

    def test_a_stall_does_not_drop_the_player_through_the_floor(self):
        self.run_frames([16] * 110 + [STALL_MS] * 5 + [16] * 5)
        self.assertEqual(self.game.player.lives, PLAYER_LIVES)
        self.assertLess(self.game.player.pos.y, FLOOR_TOP)

    # A respawn from another map repetition leaves stale collision boxes until the next render.
    def test_a_stall_after_a_far_fall_does_not_cost_another_life(self):
        self.game.player.pos.update(4670, 790)
        self.game.player.vel.update(0, 0)
        self.run_frames([STALL_MS] * 10)
        self.assertEqual(self.game.player.lives, PLAYER_LIVES - 1)
        self.assertLess(self.game.player.pos.y, FLOOR_TOP)


class FirstFrameTests(GameLoopTestCase):
    def test_loading_time_and_the_first_frame_run_no_ticks(self):
        ticks_per_frame = self.run_frames([16, 16])
        self.assertEqual(ticks_per_frame[0], 0)


class FrameCapTests(GameLoopTestCase):
    def test_every_frame_passes_the_cap_to_the_clock(self):
        self.run_frames([16] * 5)
        self.assertEqual(self.game.tps_clock.framerates, [0] + [FPS_MAX] * 6)

    def test_real_clock_caps_frames_and_keeps_the_tick_rate(self):
        seconds = 1.5
        counts = collections.Counter()
        original_tick = self.game.tick
        self.game.render()  # Fills collision data. Later frames draw nothing, so only the cap can slow them
        started = []

        def tick():
            original_tick()
            counts["ticks"] += 1

        def render():
            counts["frames"] += 1
            if not started:
                started.append(time.perf_counter())
            elif time.perf_counter() - started[0] >= seconds:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

        self.game.tick = tick
        self.game.render = render
        with self.assertRaises(SystemExit):
            self.game.run()
        self.assertLessEqual(counts["frames"], seconds * FPS_MAX * 1.1)
        self.assertGreater(counts["frames"], 0)
        self.assertAlmostEqual(counts["ticks"], seconds * TPS_MAX, delta=seconds * TPS_MAX * 0.15)


if __name__ == "__main__":
    unittest.main()

"""Checks of falling out of the level, losing a life and respawning (roadmap
task R-02). Runs headlessly in-process. Run from the repository root with:

    venv/bin/python -B -m unittest discover -s tests -v
"""
import collections
import os
import sys
import time
import unittest
from unittest import mock

GAME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platformer_game")
SPAWN = (640, 170)
FLOOR_TOP = 640
FALL_TICKS = 80  # Enough to get from a floor gap to the fall limit at any gravity

environment_patch = mock.patch.dict(
    os.environ,
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    PYGAME_HIDE_SUPPORT_PROMPT="1",
)
original_directory = os.getcwd()
pygame = None
Game = None
FALL_LIMIT_Y = None
PLAYER_LIVES = None


def setUpModule():
    global pygame, Game, FALL_LIMIT_Y, PLAYER_LIVES
    environment_patch.start()
    # Imports and sprite paths both resolve against platformer_game/.
    os.chdir(GAME_DIR)
    sys.path.insert(0, GAME_DIR)
    import pygame
    from src.game import Game
    from config.settings import FALL_LIMIT_Y, PLAYER_LIVES


def tearDownModule():
    pygame.quit()
    sys.path.remove(GAME_DIR)
    os.chdir(original_directory)
    environment_patch.stop()


class RespawnTestCase(unittest.TestCase):
    def setUp(self):
        self.keys = collections.defaultdict(bool)
        patcher = mock.patch("pygame.key.get_pressed", lambda: self.keys)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.game = Game()
        self.game.engine.display_fps = lambda: None
        self.player = self.game.player

    def advance(self, steps):
        for _ in range(steps):
            self.game.render()
            self.game.tick()

    def place_in_gap(self, x=830):
        # Below the platform that spans the gap at x = 800.
        self.player.pos.update(x, 600)
        self.player.vel.update(0, 0)

    def fall_until_respawn(self):
        lives = self.player.lives
        for tick in range(FALL_TICKS):
            self.advance(1)
            if self.player.lives != lives or tuple(self.player.pos) == SPAWN:
                return tick
        self.fail(f"no respawn within {FALL_TICKS} ticks, y = {self.player.pos.y}")


class FallDetectionTests(RespawnTestCase):
    def test_standing_on_the_floor_is_not_a_fall(self):
        self.advance(400)
        self.assertEqual(self.player.lives, PLAYER_LIVES)
        self.assertAlmostEqual(self.player.pos.y + self.player.height, FLOOR_TOP, delta=12)

    def test_player_is_not_respawned_above_the_limit(self):
        self.game.render()
        self.player.pos.update(830, FALL_LIMIT_Y - 50)
        self.player.vel.update(0, 0)
        self.player.tick()
        self.assertEqual(self.player.lives, PLAYER_LIVES)
        self.assertGreater(self.player.pos.y, FALL_LIMIT_Y - 50)

    def test_player_is_respawned_below_the_limit(self):
        self.game.render()
        self.player.pos.update(830, FALL_LIMIT_Y + 1)
        self.player.tick()
        self.assertEqual(self.player.lives, PLAYER_LIVES - 1)
        self.assertEqual(tuple(self.player.pos), SPAWN)

    def test_every_kind_of_gap_is_detected(self):
        for name, x, checkpoint in (("right", 830, 0), ("left", -370, 0), ("next map repeat", 4670, 1)):
            with self.subTest(name):
                self.setUp()
                self.game.map.player_checkpoint = checkpoint
                self.place_in_gap(x)
                self.fall_until_respawn()
                self.assertEqual(self.player.lives, PLAYER_LIVES - 1)
                self.assertEqual(tuple(self.player.pos), SPAWN)

    def test_running_into_the_first_gap_from_the_start(self):
        self.advance(150)
        self.keys[pygame.K_d] = True
        deepest = 0
        for _ in range(300):
            self.advance(1)
            deepest = max(deepest, self.player.pos.y)
            if self.player.lives != PLAYER_LIVES:
                break
        self.assertEqual(self.player.lives, PLAYER_LIVES - 1)
        self.assertLessEqual(deepest, FALL_LIMIT_Y)
        self.assertGreater(deepest, FLOOR_TOP)


class LivesTests(RespawnTestCase):
    def test_one_fall_takes_exactly_one_life(self):
        self.place_in_gap()
        self.fall_until_respawn()
        self.assertEqual(self.player.lives, PLAYER_LIVES - 1)
        self.advance(300)
        self.assertEqual(self.player.lives, PLAYER_LIVES - 1)

    def test_each_new_fall_takes_another_life(self):
        for fall in range(1, PLAYER_LIVES + 1):
            self.place_in_gap()
            self.fall_until_respawn()
            self.assertEqual(self.player.lives, PLAYER_LIVES - fall)

    def test_no_lives_left_still_respawns_and_stays_at_zero(self):
        self.player.lives = 0
        self.place_in_gap()
        self.fall_until_respawn()
        self.assertEqual(self.player.lives, 0)
        self.assertEqual(tuple(self.player.pos), SPAWN)
        self.advance(200)
        self.assertAlmostEqual(self.player.pos.y + self.player.height, FLOOR_TOP, delta=12)


class RespawnStateTests(RespawnTestCase):
    def test_player_state_is_reset(self):
        self.game.render()
        self.player.pos.update(830, FALL_LIMIT_Y + 1)
        self.player.vel.update(3, 6)
        self.player.isRunning = True
        self.player.isAttacking = True
        self.player.runCount = 15
        self.player.attack_ticks = 30

        self.player.tick()

        self.assertEqual(tuple(self.player.pos), SPAWN)
        self.assertEqual(tuple(self.player.vel), (0, 0))
        self.assertEqual(tuple(self.player.acc), (0, 0))
        self.assertEqual(self.player.position, (640, 660, 170, 230))
        self.assertFalse(self.player.isJump)
        self.assertFalse(self.player.isRunning)
        self.assertFalse(self.player.isAttacking)
        self.assertEqual(self.player.runCount, 0)
        self.assertEqual(self.player.attack_ticks, 0)

    def test_collision_flags_are_cleared_after_touching_an_enemy_while_falling(self):
        self.game.render()
        self.player.pos.update(830, FALL_LIMIT_Y + 1)
        self.player.position = (830, 850, FALL_LIMIT_Y + 1, FALL_LIMIT_Y + 61)
        self.game.enemy.position = (825, 875, FALL_LIMIT_Y + 50, FALL_LIMIT_Y + 100)

        self.player.tick()

        collision = self.game.collision
        for name in [name for name in vars(collision) if name.startswith("is")]:
            self.assertFalse(getattr(collision, name), name)
        self.assertEqual(self.player.lives, PLAYER_LIVES - 1)

    def test_gravity_keeps_its_value(self):
        for gravity in (0.7, 0.9):
            with self.subTest(gravity=gravity):
                self.setUp()
                self.player.gravity = gravity
                self.place_in_gap()
                self.fall_until_respawn()
                self.assertEqual(self.player.gravity, gravity)

    def test_camera_returns_to_the_spawn_immediately(self):
        self.game.map.player_checkpoint = 1
        self.game.physics.true_scroll[0] = 4000
        self.place_in_gap(4670)
        self.fall_until_respawn()
        self.assertEqual(tuple(self.player.scroll), (0, 0))
        self.assertEqual(tuple(self.game.map.scroll), (0, 0))

    def test_falling_far_from_the_spawn_lands_back_on_the_floor(self):
        far_checkpoint = 100
        self.game.map.player_checkpoint = far_checkpoint
        self.place_in_gap(3840 * far_checkpoint + 830)
        self.fall_until_respawn()
        self.assertEqual(self.game.map.player_checkpoint, 0)

        self.advance(200)
        self.assertEqual(self.player.lives, PLAYER_LIVES - 1)
        self.assertEqual(self.game.map.player_checkpoint, 0)
        self.assertEqual(self.player.vel.y, 0)
        self.assertAlmostEqual(self.player.pos.y + self.player.height, FLOOR_TOP, delta=12)

    def test_movement_and_jump_work_after_respawn(self):
        self.place_in_gap()
        self.fall_until_respawn()
        self.advance(200)
        start_x = self.player.pos.x

        self.keys[pygame.K_a] = True
        self.advance(30)
        self.assertLess(self.player.pos.x, start_x)
        self.keys[pygame.K_a] = False

        self.advance(50)
        self.assertEqual(self.player.vel.y, 0)
        y_before_jump = self.player.pos.y
        self.keys[pygame.K_SPACE] = True
        self.advance(10)
        self.keys[pygame.K_SPACE] = False
        self.assertLess(self.player.pos.y, y_before_jump - 50)

    def test_holding_jump_through_the_respawn_costs_one_life(self):
        self.place_in_gap()
        self.advance(2)  # Already falling, so the key cannot start a jump in the gap
        self.keys[pygame.K_SPACE] = True
        self.fall_until_respawn()
        self.advance(5)
        self.keys[pygame.K_SPACE] = False
        self.advance(300)
        self.assertEqual(self.player.lives, PLAYER_LIVES - 1)
        self.assertAlmostEqual(self.player.pos.y + self.player.height, FLOOR_TOP, delta=12)


class SlowStartTests(RespawnTestCase):
    def run_loop_for_frames(self, frames):
        original_render = self.game.render
        counts = {"frames": 0, "ticks_before_first_render": 0}
        original_tick = self.game.tick

        def tick():
            if counts["frames"] == 0:
                counts["ticks_before_first_render"] += 1
            original_tick()

        def render():
            original_render()
            counts["frames"] += 1
            if counts["frames"] == frames:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

        self.game.tick = tick
        self.game.render = render
        with self.assertRaises(SystemExit):
            self.game.run()
        return counts

    # Without the clock reset this delay meant 160 ticks with no floor: below the limit before the first frame.
    def test_slow_loading_does_not_cost_a_life(self):
        time.sleep(1.6)
        counts = self.run_loop_for_frames(10)
        self.assertLessEqual(counts["ticks_before_first_render"], 2)
        self.assertEqual(self.player.lives, PLAYER_LIVES)
        self.assertLess(self.player.pos.y, FLOOR_TOP)


if __name__ == "__main__":
    unittest.main()

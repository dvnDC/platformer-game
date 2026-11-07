"""Checks that attack timing and completion follow ticks, not drawing (roadmap task
R-09). Runs headlessly in-process, so how it looks in a real window isn't covered.
Run from the repository root with:

    venv/bin/python -B -m unittest discover -s tests -v
"""
import collections
import os
import sys
import unittest
from unittest import mock

GAME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platformer_game")
FLOOR_STANDING_Y = 579
FAR_AWAY = 100000
OLD_ATTACK_FRAMES = list(range(9))
EXPECTED_FRAME_BY_TICK = [frame for frame in OLD_ATTACK_FRAMES for _ in range(5)]

environment_patch = mock.patch.dict(
    os.environ,
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    PYGAME_HIDE_SUPPORT_PROMPT="1",
)
original_directory = os.getcwd()
pygame = None
Game = None
ATTACK_FRAME_TICKS = None
ATTACK_TICKS = None


def setUpModule():
    global pygame, Game, ATTACK_FRAME_TICKS, ATTACK_TICKS
    environment_patch.start()
    # Imports and sprite paths both resolve against platformer_game/.
    os.chdir(GAME_DIR)
    sys.path.insert(0, GAME_DIR)
    import pygame
    from src.game import Game
    from config.settings import ATTACK_FRAME_TICKS, ATTACK_TICKS


def tearDownModule():
    pygame.quit()
    sys.path.remove(GAME_DIR)
    os.chdir(original_directory)
    environment_patch.stop()


class RecordingScreen:
    """Stands in for the screen and remembers which surfaces were blitted."""

    def __init__(self, screen):
        self.screen = screen
        self.blitted = []

    def blit(self, surface, *args):
        self.blitted.append(surface)

    def __getattr__(self, name):
        return getattr(self.screen, name)


class AttackTestCase(unittest.TestCase):
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
        self.game.enemy.pos.x = FAR_AWAY
        self.sprite_names = self.name_sprites()

    def name_sprites(self):
        sprite = self.game.sprite
        names = {id(sprite.imagePlayerStand): ("stand", 0)}
        for kind, frames in (("attack", sprite.imagePlayerAttack), ("attack_flip", sprite.imagePlayerAttackFlip),
                             ("effect", sprite.imageAttackEffect), ("run", sprite.imagePlayerRun),
                             ("run_flip", sprite.imagePlayerRunFlip)):
            names.update({id(frame): (kind, index) for index, frame in enumerate(frames)})
        return names

    def drawn(self):
        """Draws the player and returns the (kind, frame) of each blitted sprite."""
        real_screen = self.game.screen
        self.game.screen = RecordingScreen(real_screen)
        self.player.draw()
        blitted = self.game.screen.blitted
        self.game.screen = real_screen
        return [self.sprite_names.get(id(surface)) for surface in blitted]

    def press_for_one_tick(self, key=None):
        self.keys[key or pygame.K_e] = True
        self.game.tick()
        self.keys[key or pygame.K_e] = False

    def tick(self, count=1):
        for _ in range(count):
            self.game.tick()


class ProgressionTests(AttackTestCase):
    def test_constants_keep_the_old_length_and_frames(self):
        self.assertEqual(ATTACK_TICKS, 45)
        self.assertEqual(ATTACK_FRAME_TICKS, 5)

    def test_each_frame_lasts_five_ticks_in_order(self):
        self.press_for_one_tick()
        shown = []
        effects = []
        for _ in range(ATTACK_TICKS):
            sprites = dict(self.drawn())
            shown.append(sprites["attack"])
            effects.append(sprites["effect"])
            self.tick()
        self.assertEqual(shown, EXPECTED_FRAME_BY_TICK)
        self.assertEqual(effects, EXPECTED_FRAME_BY_TICK)

    def test_attack_lasts_the_full_length(self):
        self.press_for_one_tick()
        attacking_ticks = 1
        while self.player.isAttacking and attacking_ticks < 200:
            self.tick()
            attacking_ticks += self.player.isAttacking
        self.assertEqual(attacking_ticks, ATTACK_TICKS)

    # BUG-04: the timer kept running between attacks, so this attack lasted 1 tick and drew nothing.
    def test_first_attack_after_a_long_wait_plays_from_the_first_frame(self):
        self.tick(200)
        self.press_for_one_tick()
        self.assertEqual(self.player.attack_ticks, 0)
        self.assertIn(("attack", 0), self.drawn())
        self.tick(44)
        self.assertTrue(self.player.isAttacking)

    def test_timer_does_not_run_without_an_attack(self):
        self.tick(30)
        self.assertEqual(self.player.attack_ticks, 0)

    # Before, the draw that ended the attack showed no player sprite at all.
    def test_player_stays_visible_when_the_attack_ends(self):
        self.press_for_one_tick()
        for _ in range(ATTACK_TICKS + 2):
            self.assertTrue(self.drawn())
            self.tick()
        self.assertEqual(self.drawn(), [("stand", 0)])


class RenderingDoesNotChangeTheAttackTests(AttackTestCase):
    def test_repeated_draws_do_not_advance_the_attack(self):
        self.press_for_one_tick()
        self.tick(12)
        ticks = self.player.attack_ticks
        first = self.drawn()
        for _ in range(100):
            self.assertEqual(self.drawn(), first)
        self.assertEqual(self.player.attack_ticks, ticks)
        self.assertTrue(self.player.isAttacking)

    def test_repeated_renders_do_not_advance_the_attack(self):
        self.press_for_one_tick()
        self.tick(12)
        ticks = self.player.attack_ticks
        for _ in range(5):
            self.game.render()
        self.assertEqual(self.player.attack_ticks, ticks)

    def test_draws_cannot_complete_an_attack(self):
        self.press_for_one_tick()
        self.tick(ATTACK_TICKS - 1)
        self.assertEqual(self.player.attack_ticks, ATTACK_TICKS - 1)
        for _ in range(100):
            self.player.draw()
        self.assertTrue(self.player.isAttacking)


class NoRenderingTests(AttackTestCase):
    def test_attack_completes_with_no_drawing(self):
        self.press_for_one_tick()
        self.tick(ATTACK_TICKS)
        self.assertFalse(self.player.isAttacking)

    def test_a_new_attack_can_start_with_no_drawing(self):
        self.press_for_one_tick()
        self.tick(ATTACK_TICKS)
        self.press_for_one_tick()
        self.assertTrue(self.player.isAttacking)
        self.assertEqual(self.player.attack_ticks, 0)

    def test_a_drawing_pause_shows_the_frame_for_the_ticks_that_passed(self):
        self.press_for_one_tick()
        self.tick(23)
        self.assertIn(("attack", 4), self.drawn())


class RenderingFrequencyTests(AttackTestCase):
    def attack_states(self, draw_every_ticks, draws_per_time):
        self.setUp()
        states = []
        self.press_for_one_tick()
        for tick_number in range(60):
            self.tick()
            states.append((self.player.isAttacking, self.player.attack_ticks))
            if draw_every_ticks and tick_number % draw_every_ticks == 0:
                for _ in range(draws_per_time):
                    self.game.render()
        return states

    def test_timing_is_the_same_at_any_drawing_rate(self):
        reference = self.attack_states(draw_every_ticks=1, draws_per_time=1)
        self.assertEqual(self.attack_states(draw_every_ticks=4, draws_per_time=1), reference)
        self.assertEqual(self.attack_states(draw_every_ticks=1, draws_per_time=3), reference)
        self.assertEqual(self.attack_states(draw_every_ticks=0, draws_per_time=0), reference)

    def test_a_sparse_draw_shows_the_frame_for_the_current_tick(self):
        self.press_for_one_tick()
        for _ in range(4):
            self.tick(7)
            self.assertIn(("attack", self.player.attack_ticks // 5), self.drawn())


class RunningJumpingAndFacingTests(AttackTestCase):
    def x_after_running(self, attack):
        self.setUp()
        self.keys[pygame.K_a] = True
        self.tick(10)
        self.keys[pygame.K_e] = attack
        self.tick(30)
        return self.player.pos.x

    def test_attacking_does_not_change_the_running_speed(self):
        self.assertEqual(self.x_after_running(attack=True), self.x_after_running(attack=False))

    def test_running_animation_waits_for_the_attack_and_then_continues(self):
        self.keys[pygame.K_a] = True
        self.tick(7)
        count = self.player.runCount
        self.press_for_one_tick()
        self.assertEqual(self.player.runCount, count)
        self.tick(ATTACK_TICKS - 1)
        self.assertEqual(self.player.runCount, count)
        self.assertTrue(self.player.isAttacking)
        self.assertIn(("attack_flip", 8), self.drawn())
        self.tick(1)
        self.assertFalse(self.player.isAttacking)
        self.assertEqual(self.drawn()[0][0], "run_flip")
        self.assertEqual(self.player.runCount, count + 1)

    def test_attacking_in_the_air_leaves_the_jump_unchanged(self):
        def jump_heights(attack):
            self.setUp()
            self.tick(5)
            self.keys[pygame.K_SPACE] = True
            self.tick(1)
            self.keys[pygame.K_SPACE] = False
            self.keys[pygame.K_e] = attack
            heights = []
            for _ in range(50):
                self.tick()
                heights.append(self.player.pos.y)
            return heights

        self.assertEqual(jump_heights(attack=True), jump_heights(attack=False))

    def test_attack_plays_in_the_air(self):
        self.keys[pygame.K_SPACE] = True
        self.tick(1)
        self.keys[pygame.K_SPACE] = False
        self.assertNotEqual(self.player.vel.y, 0)
        self.press_for_one_tick()
        self.assertEqual(self.player.attack_ticks, 0)
        self.assertTrue(self.player.isAttacking)

    def test_moving_right_or_standing_uses_the_right_facing_frames(self):
        self.press_for_one_tick()
        self.assertIn(("attack", 0), self.drawn())
        self.player.vel.x = 2
        self.assertIn(("attack", 0), self.drawn())

    def test_moving_left_uses_the_left_facing_frames(self):
        self.press_for_one_tick()
        self.player.vel.x = -2
        self.assertIn(("attack_flip", 0), self.drawn())

    def test_changing_direction_keeps_the_attack_going(self):
        self.press_for_one_tick()
        self.tick(12)
        self.player.vel.x = 2
        self.assertIn(("attack", 2), self.drawn())
        self.player.vel.x = -2
        self.assertIn(("attack_flip", 2), self.drawn())
        self.assertEqual(self.player.attack_ticks, 12)


class AttackInputTests(AttackTestCase):
    def count_attack_starts(self, ticks, keys_at_tick):
        starts = []
        original = self.player.handle_attack

        def counting_attack():
            starts.append(tick_number)
            original()

        self.player.handle_attack = counting_attack
        for tick_number in range(ticks):
            self.keys[pygame.K_e] = keys_at_tick(tick_number)
            self.game.tick()
        return starts

    def test_pressing_during_an_attack_does_not_restart_it(self):
        self.press_for_one_tick()
        self.tick(9)
        self.press_for_one_tick()
        self.assertEqual(self.player.attack_ticks, 10)

    def test_a_short_press_starts_one_attack(self):
        self.assertEqual(self.count_attack_starts(100, lambda tick: tick < 3), [0])

    def test_holding_repeats_attacks_with_no_gap(self):
        self.assertEqual(self.count_attack_starts(100, lambda tick: True), [0, 45, 90])
        self.assertTrue(self.player.isAttacking)

    def test_holding_keeps_the_player_visible_through_the_repeat(self):
        self.keys[pygame.K_e] = True
        for _ in range(100):
            self.game.tick()
            self.assertTrue(self.drawn())

    def test_pressing_right_when_an_attack_ends_starts_the_next_one(self):
        starts = self.count_attack_starts(50, lambda tick: tick in (0, 45))
        self.assertEqual(starts, [0, 45])

    def test_pressing_just_before_it_ends_is_ignored(self):
        starts = self.count_attack_starts(50, lambda tick: tick in (0, 44))
        self.assertEqual(starts, [0])

    # Only the start of an attack checks for a hit, as before.
    def test_a_hit_is_checked_once_per_attack(self):
        weapon_checks = []
        original_collision = self.game.collision.collision

        def collision(box, other_box):
            if box is self.game.weapon.position:
                weapon_checks.append(other_box)
            original_collision(box, other_box)

        self.game.collision.collision = collision
        self.press_for_one_tick()
        self.tick(ATTACK_TICKS - 1)
        self.assertEqual(len(weapon_checks), 1)
        self.press_for_one_tick()
        self.assertEqual(len(weapon_checks), 2)


class FrameIndexTests(AttackTestCase):
    def test_every_tick_of_an_attack_has_a_valid_frame_in_both_directions(self):
        sprite = self.game.sprite
        self.player.isAttacking = True
        for ticks in range(ATTACK_TICKS):
            self.player.attack_ticks = ticks
            self.assertLess(ticks // ATTACK_FRAME_TICKS, len(sprite.imagePlayerAttack))
            self.assertLess(ticks // ATTACK_FRAME_TICKS, len(sprite.imageAttackEffect))
            for velocity in (1, 0, -1):
                self.player.vel.x = velocity
                self.player.draw()

    def test_holding_for_a_long_time_stays_within_the_nine_frames(self):
        self.keys[pygame.K_e] = True
        frames = set()
        for _ in range(500):
            self.game.tick()
            self.player.pos.update(640, FLOOR_STANDING_Y)
            for kind, frame in self.drawn():
                if kind in ("attack", "effect"):
                    frames.add(frame)
        self.assertEqual(frames, set(OLD_ATTACK_FRAMES))


if __name__ == "__main__":
    unittest.main()

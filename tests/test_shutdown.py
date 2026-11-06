"""End-to-end checks of how the game process exits (roadmap task R-03).

Each scenario runs the game in its own subprocess, so the exit codes asserted
here are real process exit codes. Run from the repository root with:

    venv/bin/python -B -m unittest discover -s tests -v
"""
import os
import subprocess
import sys
import time
import unittest

GAME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "platformer_game")
TIMEOUT_SECONDS = 60
TRIGGER_FRAME = 3

# Runs the real entry point, src.main.main(), and fires the scenario once the
# game loop has rendered a few frames. Passed to the interpreter with -c.
DRIVER = """
import sys
import pygame
from src.game import Game
from src.main import main

scenario = sys.argv[1]
frames = 0
original_render = Game.render
original_tick = Game.tick
tick_should_fail = False


def trigger(game):
    global tick_should_fail
    print("TRIGGERED", flush=True)
    if scenario == "escape":
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    elif scenario == "window_close":
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    elif scenario == "other_key":
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q))
    elif scenario == "render_error":
        raise RuntimeError("injected render failure")
    elif scenario == "tick_error":
        tick_should_fail = True
    elif scenario == "real_game_error":
        game.menu.draw()


def render(game):
    global frames
    original_render(game)
    frames += 1
    if frames == """ + str(TRIGGER_FRAME) + """:
        trigger(game)
    elif scenario == "other_key" and frames == """ + str(TRIGGER_FRAME + 5) + """:
        print("STILL_RUNNING", flush=True)
        pygame.event.post(pygame.event.Event(pygame.QUIT))


def tick(game):
    if tick_should_fail:
        raise ValueError("injected tick failure")
    original_tick(game)


Game.render = render
Game.tick = tick
main()
"""


def game_environment():
    return dict(
        os.environ,
        SDL_VIDEODRIVER="dummy",
        SDL_AUDIODRIVER="dummy",
        PYTHONDONTWRITEBYTECODE="1",
        PYGAME_HIDE_SUPPORT_PROMPT="1",
    )


def run_scenario(scenario):
    return subprocess.run(
        [sys.executable, "-c", DRIVER, scenario],
        cwd=GAME_DIR,
        env=game_environment(),
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
    )


class NormalShutdownTests(unittest.TestCase):
    def assert_clean_exit(self, result):
        self.assertIn("TRIGGERED", result.stdout, "the game loop never reached the scenario")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("An error occurred", result.stdout + result.stderr)

    def test_escape_exits_with_code_0(self):
        self.assert_clean_exit(run_scenario("escape"))

    def test_window_close_exits_with_code_0(self):
        self.assert_clean_exit(run_scenario("window_close"))

    def test_other_keys_do_not_exit(self):
        result = run_scenario("other_key")
        self.assert_clean_exit(result)
        self.assertIn("STILL_RUNNING", result.stdout)


class UnexpectedErrorTests(unittest.TestCase):
    def assert_crash_is_reported(self, result, error_line, source_file):
        self.assertIn("TRIGGERED", result.stdout, "the game loop never reached the scenario")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Traceback (most recent call last):", result.stderr)
        self.assertIn(error_line, result.stderr)
        self.assertIn(source_file, result.stderr)

    def test_error_during_render_reports_traceback_and_exits_with_code_1(self):
        result = run_scenario("render_error")
        self.assert_crash_is_reported(result, "RuntimeError: injected render failure", "in render")

    def test_error_during_tick_reports_traceback_and_exits_with_code_1(self):
        result = run_scenario("tick_error")
        self.assert_crash_is_reported(result, "ValueError: injected tick failure", "in tick")

    def test_real_game_error_points_at_the_failing_line(self):
        result = run_scenario("real_game_error")
        self.assert_crash_is_reported(result, "imageMenuGrid1", os.path.join("src", "ui", "menu.py"))
        self.assertIn("AttributeError", result.stderr)


class EntryPointTests(unittest.TestCase):
    def test_documented_launch_command_keeps_running(self):
        process = subprocess.Popen(
            [sys.executable, "-m", "src.main"],
            cwd=GAME_DIR,
            env=game_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            time.sleep(2)
            self.assertIsNone(process.poll(), "the game exited on its own")
        finally:
            process.kill()
            process.communicate()


if __name__ == "__main__":
    unittest.main()

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

The game must be run as a module from `platformer_game/`. Imports (`from src...`, `from config...`) and sprite paths (`assets/images/...`) both resolve against that directory, so `python src/main.py` or running from the repo root fails.

```bash
cd platformer_game
../venv/bin/python -m src.main
```

To smoke-test without a window or audio device, set `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy`. The loop runs until killed, so stop it after a few seconds.

Dependencies are `pygame` and `numpy`. The working `venv/` (gitignored) is Python 3.12 with pygame 2.5.2, while the `Pipfile` still pins Python 3.8 and `platformer_game/requirements.txt` is empty. The venv has `include-system-site-packages = true`, so packages from the base asdf Python (such as `matplotlib` and `PIL`) are importable and a missing dependency can go unnoticed.

There are no tests, linter, or build config. `src/main.spec` (PyInstaller) is stale: it has a hardcoded Linux path and bundles no assets.

## Architecture

`Game` (`src/game.py`) is a service locator. It constructs one instance of each component, and every component receives `game` and reaches its collaborators through it (`self.game.player`, `self.game.collision`, ...). There is only one player, one enemy, and one projectile; they are not sprite groups.

- **Init order matters** (`Game.initialize_game_components`): `SpriteManager` loads all images first, and `CollisionManager.__init__` reads `game.player`, so it must come after `Player`.
- **Loop:** a fixed-timestep `tick()` at `TPS_MAX` (100/s), with an uncapped `render()` once per outer iteration.

### Non-obvious coupling

- **Collision data is produced by the draw pass.** `GameMap.grid()` fills `GRID_boxes_coll` and `PlatformManager.draw_platform()` fills `platform_positions` while rendering; `Player.tick()` and `Enemy.tick()` read them. Disabling a `draw` call also removes its collision, and collision geometry is empty before the first render.
- **Scroll is pushed, not read.** `PhysicsEngine.set_scroll` writes the camera offset into a hardcoded list of objects, so a new world object with a `scroll` attribute must be added there. Positions are in world coordinates and drawing subtracts `scroll`.
- **Bounding boxes are `(x0, x1, y0, y1)`,** not pygame's `(x, y, w, h)`. All `CollisionManager` methods and the `position` attributes use this order.
- **`CollisionManager` keeps per-call state on itself.** Its `pos`, `vel`, and `is*Collision` flags are overwritten on each check, and the side flags must be reset afterwards. `collision()` only clears `isCollision` when the x-axis test fails, so a stale `True` can survive a y-axis miss.
- **The map repeats.** `GameMap.grid()` shifts the 80-column grid by `player_checkpoint` multiples of 3840px as the player advances, so the grid has no fixed world position. Tiles are 80px; value `1` is a solid tile and `7` is a decoration that draws a full 1280×720 overlay image (grass, path, tree) and has no collision.

### Dead or broken code

Check these before building on them:

- `GameMap` defines `grid()` twice, and only the second definition is live.
- `Menu` is constructed but its `draw()` call is commented out. Calling it would crash with an `AttributeError` at `src/ui/menu.py:71`, because `SpriteManager` has no `imageMenuGrid1`. The file also uses the undefined names `gameDisplay` and `randomcolor`, but `draw()` fails before reaching them.
- `GameMap.bird()` is also disabled and uses the undefined `shipImage`.
- `Player.got_weapon` is never set to `True`, so the `R` ranged attack and `Projectile` firing are unreachable in play.
- `Player.state` (`PlayerState`) is unused; the live flags are attributes on `Player` itself.
- `AssetLoader.get_image` rebuilds its cache on every call, and `SpriteManager` calls `pygame.image.load` directly for all images.
- `config/settings.py` is the source for screen size, audio, and tick rate, but `Game` also has unused `WIDTH`/`HEIGHT` constants. Gravity is defined separately on `Player` (0.7), `Enemy` (0.9), and `PhysicsEngine` (0.9). The player's first jump permanently replaces `Player.gravity` with the `PhysicsEngine` value, so terminal fall speed changes from about 4.67 to 6 px/tick.

### Error visibility

`Game.run` catches every `Exception` in the loop, prints a single line without a traceback, and exits normally. To debug a crash, temporarily remove that handler or call `traceback.print_exc()` in it.

### Known runtime issues

- **`GRID_position` leaks memory.** The live `GameMap.grid()` appends 880 tuples per rendered frame (about 160 KB) to this list, never clears it, and nothing reads it. Memory use grows for as long as the game runs, and faster with higher FPS.
- **Surfaces are never converted.** No image gets `convert()` or `convert_alpha()`, and blitting them dominates render time. In a headless test, converting them in memory cut `render()` from about 16 ms to 2.5 ms. Fix the leak and the FPS-dependent `runCount` animation first, because a higher frame rate makes both worse.
- **Gaps in the level have no recovery.** The floor has gaps at `x = -400` and `x = 800`, repeating every 3840px. A player who falls in normally keeps falling with `pos.y` growing without limit: there is no respawn, death, or game over, jumping stops working because `vel.y` stays nonzero, and drawing ignores `scroll.y`, so the player is off-screen. In practice the only way out is to quit. The one known exception is accidental: contact with an enemy falling through the same gap can zero `vel.y` and allow a jump back (3 of 320 headless timing runs with Space held).

## Repository notes

- `.gitignore` doesn't cover `__pycache__`, and some old `.pyc` files under `platformer_game/__pycache__/` are tracked. Avoid staging generated `__pycache__` directories.
- Some comments are in Polish.

## Project Documentation

The `docs/` directory contains the project's technical documentation, architecture analysis, gameplay description, audit findings, and development roadmap.

These documents are an important source of project context and should be consulted before making significant changes. They are written in Polish; keep them in Polish when updating them.

### Available Documentation

- `docs/PROJECT_OVERVIEW.md` — Project overview, purpose, technologies, current implementation status, and project structure.
- `docs/ARCHITECTURE.md` — Software architecture, classes, responsibilities, dependencies, initialization order, and component interactions.
- `docs/GAMEPLAY.md` — Existing gameplay mechanics, player controls, physics, collisions, enemies, projectiles, maps, and progression.
- `docs/TECHNICAL_AUDIT.md` — Technical audit, identified bugs, architectural weaknesses, technical debt, performance issues, and stability assessment.
- `docs/ROADMAP.md` — Prioritized development tasks, recommended improvements, implementation order, and outstanding design decisions.

### Instructions for Claude Code

1. Before performing significant development work, read the documentation relevant to the task.
2. Before architectural changes or refactoring, read `ARCHITECTURE.md` and `TECHNICAL_AUDIT.md`.
3. Before modifying gameplay mechanics, read `GAMEPLAY.md`.
4. Before selecting the next development task, consult `ROADMAP.md`.
5. Treat documentation as a description of the analyzed project state, not as unquestionable truth. Always verify important assumptions against the current source code.
6. If implementation changes make the documentation outdated, update the relevant documentation files.
7. Do not silently ignore known issues or architectural constraints documented in the audit.
8. Do not implement multiple unrelated roadmap tasks in a single change unless explicitly requested.

### Documentation and Source Code Priority

The current source code is the authoritative reference for actual implementation behavior.

Documentation describes the intended and previously analyzed state of the project. If documentation conflicts with the current source code, investigate the discrepancy before making changes.

Keep documentation consistent with the actual implementation.

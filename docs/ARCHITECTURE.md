# Architektura

> Opis stanu faktycznego (commit `2d51b48`, gałąź `dev`, uzupełniony o zmiany R-03, R-01 i R-02), a nie stanu docelowego. Docelowe zmiany są w [ROADMAP.md](ROADMAP.md). Ścieżki są podawane względem `platformer_game/`. Znaczniki `[KOD]`, `[TEST]` itd. objaśnia [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md).

## 1. Obraz ogólny

Architektura opiera się na jednym obiekcie centralnym `Game`, który działa jak **service locator**. Tworzy po jednej instancji każdego komponentu i przekazuje im samego siebie. Komponenty komunikują się, sięgając przez ten obiekt po inne komponenty i zmieniając ich pola bezpośrednio:

```python
self.game.player.pos.x = self.pos.x       # CollisionManager zmienia pozycję gracza
self.game.enemy.live = False              # Player zabija przeciwnika
self.game.weapon.fire = True              # Player uruchamia pocisk
```

Nie ma zdarzeń, interfejsów ani wyraźnego właściciela stanu. Istnieje dokładnie jeden gracz, jeden przeciwnik i jeden pocisk. Nie używają one `pygame.sprite.Group` `[KOD]`.

```text
                        ┌────────────────────────┐
   main.py ──────────▶  │          Game          │  pętla, tick, render
                        └───────────┬────────────┘
         tworzy i udostępnia wszystkim przez self.game
  ┌──────────┬───────────┬──────────┼──────────┬───────────┬───────────┐
Sprite     GameMap     Player     Enemy      Weapon     Projectile  PhysicsEngine
Manager    (+grid)                                                  (kamera)
  │           │           │          │          │           │            │
  │     Platform      Collision  ◀───┘          │           │            │
  │     Manager       Manager  ◀────────────────┘           │            │
  └─ grafiki dla wszystkich          Menu, AssetLoader: nieużywane       │
                                     GameEngine: licznik FPS             │
```

## 2. Punkt wejścia i importy

1. `python -m src.main` importuje najpierw `src/__init__.py`, który wykonuje `from .core import *` i podobnie dla `entities`, `ui`, `world`. Oznacza to załadowanie niemal całego kodu.
2. `src/game.py` przy imporcie woła `pygame.display.set_caption(...)` (linia 19), czyli ma efekt uboczny jeszcze przed `pygame.init()`. W pygame 2.5.2 działa to bez błędu `[TEST]`.
3. `main()` tworzy `Game()` i woła `game.run()`.

`config/` nie ma `__init__.py`. Działa jako *namespace package* tylko dlatego, że bieżący katalog to `platformer_game/` `[KOD]`.

### Zależności importów między modułami

| Moduł | Importuje z projektu |
|---|---|
| `src/game.py` | wszystkie komponenty, `config.settings` |
| `src/ui/sprite_manager.py` | `src.core.asset_loader` (obiekt tworzony, nigdy nieużywany) |
| `src/entities/player.py` | `src.entities.player_state` (obiekt tworzony, nigdy nieużywany) |
| `src/entities/enemy.py` | `src.core.asset_loader` (import nieużywany) |
| pozostałe | tylko `pygame`, ewentualnie `numpy` |

Importy wyglądają na luźne, bo prawdziwe zależności ukrywają się w czasie działania za `self.game`.

### Rzeczywiste zależności w czasie działania

Liczba odwołań `self.game.X` w module `[TEST]` (analiza AST):

| Moduł | Komponenty, których używa |
|---|---|
| `Player` | `screen` 9, `sprite` 9, `weapon` 7, `collision` 6, `enemy` 2, `map` 3, `fire` 2, `physics` 2, `tps_max` 1 |
| `CollisionManager` | `player` 22, `enemy` 15, `fire` 2, `platforms` 2, `screen_width`, `screen_height` |
| `GameMap` | `sprite` 15, `screen` 15, `player` 4, `screen_height` 2, `platforms` 1 |
| `Enemy` | `collision` 2, `map` 2, `player` 2, `physics` 1, `screen` 1, `sprite` 1 |
| `Projectile` | `weapon` 5, `player` 3, `screen` 2, `sprite` 2 |
| `Weapon` | `player` 9 |
| `PhysicsEngine` | `collision` 3, `player` 3, `map`, `platforms`, `enemy`, `fire`, `weapon` po 1 |
| `PlatformManager` | `screen` 2, `sprite` 1 |
| `GameEngine` | `screen` 1, `tps_clock` 1 |
| `Menu` | `screen` 4, `sprite` 3 |

Występują cykle logiczne: `Player → CollisionManager → Player`, `Player → Enemy → Player`, `Enemy → PhysicsEngine → CollisionManager → Enemy`.

## 3. Kolejność inicjalizacji

`Game.__init__` wykonuje kolejno `initialize_audio()`, `initialize_screen()` i `initialize_game_components()`. Mikser startuje więc przed `pygame.init()`.

Komponenty powstają w tej kolejności (`src/game.py:55-67`):

| # | Pole | Klasa | Dlaczego kolejność ma znaczenie |
|---|---|---|---|
| 1 | `sprite` | `SpriteManager` | Ładuje grafiki w konstruktorze. Inne komponenty korzystają z nich dopiero przy rysowaniu. |
| 2 | `map` | `GameMap` | Bez wymagań w konstruktorze. |
| 3 | `player` | `Player` | Musi istnieć przed `CollisionManager`. |
| 4 | `enemy` | `Enemy` | |
| 5 | `weapon` | `Weapon` | |
| 6 | `fire` | `Projectile` | Nazwa pola myląca: `game.fire` to pocisk, a `weapon.fire` to flaga logiczna. |
| 7 | `physics` | `PhysicsEngine` | Czyta komponenty dopiero w `set_scroll`. |
| 8 | `platforms` | `PlatformManager` | |
| 9 | `collision` | `CollisionManager` | **Konstruktor czyta `game.player.position`** (linia 18), więc musi być po `Player`. Czyta też rozmiar ekranu. |
| 10 | `menu` | `Menu` | Tworzone, nigdy nierysowane. |
| 11 | `file_loader` | `AssetLoader` | Tworzone, nigdy nieużywane. |
| 12 | `engine` | `GameEngine` | Tworzy czcionki przez `pygame.font.SysFont`, więc wymaga `pygame.init()`. |

## 4. Pętla gry

`Game.run()` (`src/game.py:70-90`):

```text
wyzeruj zegar                      # czas ładowania nie jest nadrabiany
dopóki True:
    obsłuż zdarzenia (QUIT, Esc -> sys.exit(0))
    tps_delta += czas od ostatniego obiegu
    dopóki tps_delta > 1/100 s:    # stały krok, bez limitu nadrabiania
        tick()
    render()                       # bez limitu FPS
```

Cechy tej pętli:

- **Logika** ma stały krok 100 ticków na sekundę (`TPS_MAX`). Bez okna zmierzono 100 TPS przy ~63 FPS `[TEST]`.
- **Rysowanie** nie ma limitu w kodzie i zajmuje cały dostępny czas `[KOD]`. `clock.tick()` jest wołane bez argumentu, a kod nie włącza vsync. Zachowania w prawdziwym oknie nie sprawdzono `[NIEZWERYFIKOWANE]`.
- **Nadrabianie** nie ma górnego limitu, więc po długim zatrzymaniu procesu wykona się wiele ticków naraz `[KOD]`.
- **Wyjątki:** cała pętla jest w `try/except Exception`. Po błędzie `logging.exception` drukuje pełny ślad stosu na stderr, a proces kończy się kodem 1 `[TEST]`. `Esc` i zamknięcie okna wołają `sys.exit(0)`, a `SystemExit` nie jest przechwytywany przez ten blok, więc dają kod 0 `[TEST]`.

### Kolejność w jednym ticku

```text
Game.tick()
├─ Player.tick()
│   ├─ handle_input()        klawisze, skok, atak (test trafienia)
│   ├─ całkowanie prędkości i pozycji
│   ├─ position = (x0, x1, y0, y1)
│   ├─ collision.player_collision()         3 platformy
│   ├─ collision.player_collision_check()   każdy kafelek stały (80)
│   ├─ collision.player_enemy_collision()
│   └─ respawn_after_fall(), jeśli y > FALL_LIMIT_Y
├─ Weapon.tick()             y i box (x pochodzi z poprzedniego draw)
├─ Projectile.tick()         ruch pocisku, może też rysować
├─ Enemy.tick()
│   ├─ physics.standing()    czyta nieaktualną flagę, wynik nieużywany
│   ├─ całkowanie
│   ├─ collision.bullet_collision()
│   ├─ collision.object_collision_check()   każdy kafelek stały (80)
│   └─ odrodzenie, jeśli martwy lub daleko za graczem
└─ PhysicsEngine.tick()      aktualizacja kamery, rozesłanie scroll
```

### Kolejność rysowania

```text
Game.render()
├─ screen.fill(czarny)
├─ GameMap.draw()
│   ├─ background_vanilla()   3 × góry (1280×720), 28 × las (300×720)
│   ├─ stone()                2 kamienie
│   ├─ PlatformManager.draw() prostokąt + skalowana grafika; ZAPISUJE pozycje platform
│   └─ grid()                 5 × obraz terenu 1280×720 + 80 kafelków; ZAPISUJE kolizje
├─ Player.draw()              ZMIENIA runCount, animation_timer, isAttacking
├─ Enemy.draw()
├─ Weapon.draw()              nic nie rysuje; ZAPISUJE weapon.pos.x
├─ Projectile.draw()          ZMIENIA weapon.fire, pos i time0
├─ GameEngine.display_fps()
└─ pygame.display.flip()
```

Warstwa `grid()` rysuje się po platformach. Dlatego dolna część platform na poziomie trawy jest zasłonięta przez trawę z obrazu terenu `[TEST]` (zrzut ekranu).

## 5. Klasy i odpowiedzialności

| Klasa | Plik | Faktyczna rola | Uwagi |
|---|---|---|---|
| `Game` | `src/game.py` | Inicjalizacja, pętla, kontener usług | Nieużywane: `WIDTH`, `HEIGHT`, `scroll`, `file_loader`, `menu` |
| `Player` | `src/entities/player.py` | Wejście, fizyka, kolizje, animacja, atak | Zbyt wiele ról. `state`, `time1`, `dt`, `rect_weapon` są nieużywane |
| `PlayerState` | `src/entities/player_state.py` | Nieużywana kopia flag gracza | Martwa |
| `Enemy` | `src/entities/enemy.py` | Ruch w lewo, grawitacja, odrodzenie | 91 z 166 linii to komentarze |
| `Weapon` | `src/entities/weapon.py` | Pozycja strefy ataku i flaga `fire` | Nie rysuje niczego |
| `Projectile` | `src/entities/projectile.py` | Ruch i animacja kuli ognia | Nieosiągalny, po włączeniu niestabilny |
| `CollisionManager` | `src/core/collision_manager.py` | Test AABB i reakcja, stan w polach | 3 prawie identyczne bloki reakcji i 1 wariant |
| `PhysicsEngine` | `src/core/physics_engine.py` | W praktyce **kamera** | Nazwa myląca, większość pól nieużywana |
| `GameEngine` | `src/core/game_engine.py` | Czcionki i licznik FPS | Nazwa myląca |
| `AssetLoader` | `src/core/asset_loader.py` | Nieużywany loader | Cache odtwarzany przy każdym wywołaniu |
| `SpriteManager` | `src/ui/sprite_manager.py` | Rzeczywiste ładowanie grafik | Dziedziczy po `pygame.sprite.Sprite` bez potrzeby, nie używa `AssetLoader` |
| `Menu` | `src/ui/menu.py` | Porzucone menu | Crash przy wywołaniu. Ma własną listę `GRID_position`, której R-01 nie zmieniło. Gra nie wywołuje `draw()`, a wywołanie ręczne dopisuje 43 krotki przed crashem `[TEST]` |
| `GameMap` | `src/world/game_map.py` | Dane siatki, tło, kamienie, kolizje kafelków | Dwie definicje `grid()`, ok. 800 nieużywanych `Rect` na klatkę (R-33). Zbędne gromadzenie krotek w `GRID_position` usunięto w R-01, a generowanie mapy i kolizje się nie zmieniły (sprawdzone bez okna) `[TEST]` |
| `PlatformManager` | `src/world/platform_manager.py` | Trzy stałe platformy | Pozycje zapisywane podczas rysowania |

## 6. Ukryte zależności

To najważniejsza sekcja przed wprowadzaniem zmian.

### 6.1. Dane kolizji powstają w rysowaniu

`GameMap.grid()` wypełnia `GRID_boxes_coll`, a `PlatformManager.draw_platform()` wypełnia `platform_positions`. Czytają je później `Player.tick()` i `Enemy.tick()`.

Skutki:

- Wyłączenie rysowania usuwa kolizje.
- Przed pierwszym renderem kolizji nie ma (`GRID_boxes_coll_number == 0`, platformy to same zera). Dlatego `Game.run` zeruje zegar tuż przed pętlą (R-02).
- `player_checkpoint` też zmienia się tylko w `grid()`, czyli najwyżej raz na klatkę.

### 6.2. Inne dane logiczne zmieniane w rysowaniu

| Pole | Gdzie zmieniane | Kto czyta |
|---|---|---|
| `Weapon.pos.x` | `Weapon.draw()` | `Weapon.tick()` przy budowie strefy ataku |
| `Player.runCount` | `Player.draw()`; zerowane w `tick()` | `Player.draw()` |
| `Player.isAttacking`, `animation_timer` | `Player.draw()` (koniec ataku) | `handle_input()` |
| `Projectile.pos`, `Weapon.fire`, `time0` | `Projectile.draw()` | logika pocisku |

W drugą stronę `Projectile.tick()` woła `self.draw()`, czyli rysuje w ticku `[KOD]`.

### 6.3. `CollisionManager` przechowuje stan wywołań

`pos`, `vel`, `position` i flagi `is*Collision` są polami obiektu nadpisywanymi przy każdym sprawdzeniu.

- `collision()` czyści `isCollision` tylko wtedy, gdy nie ma pokrycia w osi X. Pudło w osi Y zostawia poprzednią wartość (`collision_manager.py:35-40`).
- `player_enemy_collision()` nie zeruje żadnych flag na końcu, więc przechodzą one do następnego sprawdzenia, zwykle kolizji przeciwnika z kafelkiem lub następnego ticku `[KOD]`.
- `player_collision()` zeruje tylko 4 z 6 flag kierunkowych.

**Potwierdzone skutki `[TEST]`:** dotyczą platformy P3 (`x` 1500-1800), bo jest ostatnia w pętli i nic nie czyści po niej `isCollision`. Na P1 i P2 flagę czyści pudło w osi X przy następnej platformie.

- Gracz stojący na P3 jest odpychany przez przeciwnika idącego po ziemi pod nim, mimo że ich prostokąty się nie stykają.
- Atak wykonany z P3 zabija przeciwnika stojącego niżej, choć strefa ataku nie pokrywa go w pionie.

### 6.4. Przewinięcie jest rozsyłane, a nie odczytywane

`PhysicsEngine.set_scroll` wpisuje przesunięcie do zakodowanej listy: `map`, `player`, `platforms`, `enemy`, `fire`, `collision`, `weapon`. Nowy obiekt świata trzeba dopisać ręcznie.

- Współrzędne obiektów są światowe, a rysowanie odejmuje `scroll.x`.
- Kamera wylicza też `scroll.y`, który śledzi gracza co do piksela, ale **nikt go nie używa przy rysowaniu** `[KOD]`. Postać, która spadnie pod ekran, po prostu znika.

### 6.5. Siatka mapy nie ma stałej pozycji

Pozycja kolumny `c` zależy od indeksu `player_checkpoint`:

```text
x_świata = 80 · c + 3840 · player_checkpoint − 2560
```

Siatka ma 80 kolumn (6400 px), ale przesuwa się co 3840 px (48 kolumn). Przy normalnej grze zmiana nie jest widoczna, bo dziury i obraz terenu powtarzają się zgodnie z tym okresem: warstwa mapy miała 0 zmienionych pikseli przy tej samej kamerze na trzech granicach i trzech pozycjach kamery `[TEST]`. Teleportacja o więcej niż jeden okres na klatkę dałaby na chwilę błędne podłoże, bo indeks zmienia się o 1 na `grid()`.

### 6.6. Format prostokątów

`position` i prostokąty kolizji mają układ `(x0, x1, y0, y1)`, a nie pygame'owy `(x, y, w, h)`. Pomylenie ich nie daje błędu, tylko błędne kolizje.

### 6.7. Kierunek postaci wynika ze znaku prędkości

Nie ma pola „facing”. Kierunek rysowania postaci i strefy ataku wynika ze znaku `vel.x`. Działa to tylko dlatego, że wykładnicze tłumienie nie sprowadza prędkości do zera: po 6000 ticków bezczynności zostało `-1.5e-323` `[TEST]`.

## 7. Potok kolizji

Test pokrycia jest przedziałowy, z lewą krawędzią włączoną:

```text
a.x1 >= b.x0 and a.x0 < b.x1  and  a.y1 >= b.y0 and a.y0 < b.y1
```

Po wykryciu pokrycia `collision_side` ustala strony na podstawie **marginesu 12 px** odległości krawędzi, bez sprawdzania kierunku ruchu:

| Warunek | Flaga | Reakcja gracza |
|---|---|---|
| `abs(y1 − b.y0) ≤ 12` | dół | `pos.y -= vel.y; vel.y = 0` |
| `abs(y0 − b.y1) ≤ 12` | góra | `pos.y += vel.y + 5; vel.y = 0.1` |
| `abs(x1 − b.x0) ≤ 12` | prawo | `pos.x -= vel.x + 4; vel.x *= 0.1` (albo cofnięcie y, jeśli jest też dół) |
| `abs(x0 − b.x1) ≤ 12` | lewo | `pos.x += vel.x + 4; vel.x *= 0.1` (albo cofnięcie y, jeśli jest też dół) |

Ważne szczegóły:

- `position` nie jest przeliczane po korektach, więc kolejne sprawdzenia używają tej samej, starej wartości, choć `pos` już się zmienił.
- Reakcja to cofnięcie kroku, a nie dosunięcie do krawędzi. Gracz zatrzymuje się w zmiennej odległości od podłoża, na przykład przy `y` między 576 a 580 `[TEST]`.
- Gdy gracz porusza się w górę, a jego stopy znajdą się w marginesie od góry platformy, kod potraktuje to jako lądowanie `[TEST]`.
- Przy uderzeniu głową `vel.y` jest ujemne, więc `pos.y += vel.y + 5` przesuwa postać dalej w górę, w głąb platformy `[TEST]`.

Przeciwnik używa `object_collision_check`, kopii tej logiki dla kafelków. Nie koliduje z platformami. Przeciwnik i gracz sprawdzani są w `player_enemy_collision`, a wynik zmienia tylko gracza.

Liczba testów na tick to około 3 + 80 + 1 + 80. Mimo braku podziału przestrzeni cały `tick()` trwa ~0,084 ms `[TEST]`, więc nie jest wąskim gardłem.

## 8. Kamera i układy współrzędnych

```text
true_scroll.x += (gracz.x − true_scroll.x − 640) / 40     # miękkie podążanie
true_scroll.y += (gracz.y − true_scroll.y − 170)          # natychmiastowe, nieużywane
scroll = int(true_scroll)
ekran.x = świat.x − scroll.x                              # dla obiektów świata
ekran.y = świat.y                                         # brak kamery pionowej
```

Parallaksa: góry przesuwają się o `scroll.x / 30`, las o `scroll.x / 6`. Kopii tła jest skończenie wiele, więc tło kończy się po dłuższym biegu ([GAMEPLAY.md](GAMEPLAY.md#kamera-i-tło)).

## 9. Gdzie żyje stan gry

Stan jest rozproszony i nie ma jednej struktury opisującej „aktualną grę”.

| Stan | Miejsce |
|---|---|
| Pozycja i prędkość gracza | `Player.pos`, `Player.vel`, kopia prostokąta w `Player.position` |
| Flagi akcji | `Player.isRunning`, `isAttacking`, `isJump` |
| Licznik animacji | `Player.runCount`, `Player.animation_timer` |
| Czas w module | globalne `time0` w `player.py`, `enemy.py`, `projectile.py` |
| Przeciwnik | `Enemy.pos`, `vel`, `live`, `counter` |
| Pocisk | `Weapon.fire`, `Projectile.pos`, `vel`, `projectileRight`, `projectileLeft` |
| Mapa | `GameMap.player_checkpoint`, `GRID_boxes_coll` |
| Kamera | `PhysicsEngine.true_scroll` i 7 kopii `scroll` |
| Życie i odrodzenie | `Player.lives`, `Player.spawn_pos` |
| Wynik, tryb gry | brak |

## 10. Martwy kod

Ustalono czytaniem kodu oraz analizą AST nazw atrybutów i metod `[TEST]`.

| Kategoria | Elementy |
|---|---|
| Nadpisana metoda | Pierwsze `GameMap.grid()` (linie 112-133), a z nią `update_player_checkpoint` |
| Niewywoływane metody | `GameMap.bird`, `background`, `update_checkpoint`, `grid_static`; `Menu.draw` i metody pomocnicze; `CollisionManager.collision_enemy`; `AssetLoader.get_image`, `get_image_folder` |
| Bez efektu | `CollisionManager.enemy_collision` (zapisuje wartości same do siebie), `PhysicsEngine.standing` (wynik nigdy nieczytany), `GameEngine.font` |
| Pola zapisywane, nieczytane | `GREEN`, `bullet_distance`, `counter`, `enemyImage`, `file_loader`, `imageEnemyRunningFlip`, `imageGrid0`, `isCollisionEnemy`, `isStanding`, `left`, `right`, `newSpawn`, `platform_pos`, `seconds`, `state`, `true_scroll2`, `walkCount`, `weaponPickupImage`, `wide`, `window_position`, `Game.menu` |
| Nieużywane importy | `enemy.py`: `pygame`, `AssetLoader`; `game_map.py`: `numpy` |
| Zakomentowany kod | Stara klasa `Enemy` (`enemy.py:88-166`), `background_old`, stara wersja wycinania efektów w `sprite_manager.py` |

Lista dla pól opiera się na nazwach. Atrybut uznany za czytany w jednym miejscu mógłby pochodzić z innej klasy o tej samej nazwie, dlatego faktycznych nieużywanych pól może być więcej.

## 11. Jak bezpiecznie zmieniać kod dziś

| Chcę... | Na co uważać |
|---|---|
| Dodać obiekt świata z `scroll` | Dopisz go w `PhysicsEngine.set_scroll`. |
| Zmienić punkt odrodzenia | `respawn_after_fall` ustawia `player_checkpoint = 0`, co pasuje tylko do obecnego startu `(640, 170)`. |
| Wyłączyć rysowanie mapy lub platform | Zniknie kolizja. Najpierw wydziel budowę geometrii. |
| Zmienić wymiary gracza lub przeciwnika | Margines 12 px i przesunięcia sprite'ów są zakodowane na stałe. |
| Dodać drugiego przeciwnika | `Game`, `CollisionManager` i `set_scroll` zakładają jednego. |
| Włączyć kulę ognia | Najpierw napraw licznik czasu, inaczej gra się wywróci. |
| Przyspieszyć rysowanie | Najpierw napraw animacje zależne od FPS ([ROADMAP.md](ROADMAP.md)). Lista w `GameMap.grid()`, która rosła z każdą klatką, została usunięta w R-01. |
| Debugować crash | Przeczytaj ślad stosu na stderr. Kod wyjścia 1 oznacza nieoczekiwany błąd, a 0 normalne zamknięcie. |
| Uruchomić grę w testach | Ustaw katalog roboczy na `platformer_game/` oraz sterowniki `dummy`. Klawisze można podstawić przez `pygame.key.get_pressed`. |

## 12. Czy architektura wspiera rozbudowę

Dziś słabo. Dodanie drugiego przeciwnika, menu lub normalnego poziomu dotyka niemal wszystkich klas, a logika zależy od rysowania. Zalety to mały rozmiar kodu i prosty przepływ, dzięki czemu refaktoryzacja etapami jest wykonalna. Kierunek zmian: oddzielić `update` od `render`, wprowadzić bezstanowe kolizje, model świata, sceny i listy encji. Szczegóły w [ROADMAP.md](ROADMAP.md).

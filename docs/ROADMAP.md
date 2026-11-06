# Plan rozwoju

> Oparte na ustaleniach z [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md) (identyfikatory `BUG-xx`, `ARCH-xx`, `ENV-xx`). Złożoność i ryzyko to oceny szacunkowe, nie pomiary. Priorytet określa kolejność prac i może różnić się od wagi błędu w audycie, co pokazuje [TECHNICAL_AUDIT.md §10](TECHNICAL_AUDIT.md#10-powiązanie-z-planem-rozwoju). Żadne zadanie nie jest jeszcze wykonane. Ścieżki są względem `platformer_game/`, o ile nie zaznaczono inaczej.

## Główna decyzja

**Nie dodawać nowych funkcji przed zakończeniem Etapu 3.** Nie trzeba też przepisywać wszystkiego od zera, bo kodu jest mało, a zasoby i pętla są użyteczne. Najpierw trzeba usunąć krytyczne błędy, wprowadzić testy i rozdzielić logikę od rysowania.

## Kolejność wdrożenia

| Etap | Cel | Zadania | Warunek zakończenia |
|---|---|---|---|
| **0. Bezpieczeństwo prac** | Widzieć błędy, mieć czyste repozytorium | R-03, R-04, R-05 | Crash pokazuje ślad stosu, status git jest czysty, środowisko odtwarzalne |
| **1. Pilne naprawy** | Grę da się używać | R-01, R-02, R-06, R-07 | Pamięć stabilna, dziura nie kończy gry, testy dymne przechodzą |
| **2. Czas i animacje** | Zachowanie niezależne od FPS | R-08, R-09, R-32, R-10, R-11 | Tempo animacji i FPS są pod kontrolą, render szybszy (ok. 6× w pomiarze bez okna; sprawdzić także w prawdziwym oknie) |
| **3. Fundamenty** | Rozdzielone update i render, poprawne kolizje | R-12, R-13, R-17, R-14, R-15, R-16, R-19, a R-18 stopniowo przy okazji | `tick()` działa bez rysowania, możliwe wielu przeciwników i osobne sceny |
| **4. Rozgrywka** | Prawdziwa gra | R-20, R-21, R-22, R-23, R-24, R-25, R-26 | Da się przegrać, a walka ma sens |
| **5. Treść i funkcje** | Pełna pętla | R-27, R-28, R-29, R-30, R-31 | Menu → poziom → wynik → koniec |
| **6. Dystrybucja** | Paczka do pobrania | R-36, R-35, R-34, R-33, R-37, R-38, R-39 | Plik wykonywalny działa na czystym systemie |

Etap 6 można w części realizować wcześniej. R-36 warto wyjaśnić, zanim włoży się pracę w zasoby o niepewnej licencji, a R-38 (CI) ma sens, gdy tylko powstaną testy z R-07.

### Najważniejsze zależności

| Zadanie | Wymaga | Powód |
|---|---|---|
| R-32 `convert_alpha` | R-01, R-08 | Wyższy FPS bez nich zwiększy wyciek ok. 6,6× i przyspieszy animację biegu, a przy dalszych zyskach zbliży grę do `IndexError` |
| R-13 kolizje | R-07, R-12 | Bez testów trudno sprawdzić, czy ruch nie zmienił się niezamierzenie, a bez R-12 geometria jest zależna od renderu |
| R-14 model świata | R-12 | Dane mapy muszą być dostępne bez rysowania |
| R-15 encje | R-13 | Wielu przeciwników wymaga bezstanowych kolizji |
| R-16 sceny | R-12 | Menu nie może powodować utraty kolizji przez brak rysowania mapy |
| R-20 życie | R-02, R-13, R-16 | Śmierć potrzebuje ścieżki odrodzenia, poprawnego kontaktu z przeciwnikiem i ekranu końca |
| R-21 AI | R-13, R-15 | Wykrywanie krawędzi wymaga sensownych zapytań o kolizje |
| R-25 kula ognia | R-08, R-12, R-15 | Musi korzystać z licznika w tickach, nie rysować w logice i być na liście encji |
| R-28 poziomy | R-14, R-20 | Checkpoint potrzebuje danych poziomu i śmierci |
| R-37 PyInstaller | R-03, R-05, R-06 | Błędy muszą być widoczne, zależności jasne, a ścieżki poprawne |

Schemat uproszczony, pełna lista zależności jest przy każdym zadaniu:

```text
R-03 ─ R-04 ─ R-05 ─ R-07 ──────────┐
R-01 ──┬─ R-08 ─┬─ R-32             │
R-02   │        └─ R-09             ▼
R-06 ──┼────────────────────────── R-12 ─┬─ R-13 ─┬─ R-15 ─┬─ R-21
       │                                 ├─ R-14  │        └─ R-25
       │                                 ├─ R-16 ─┼─ R-20 ─ R-28
       │                                 └─ R-17  └─ R-23
       └─ R-37 (także R-03, R-05)
```

## A. Błędy krytyczne

### R-01 — Usunąć wyciek pamięci w `GameMap.grid()`

- **Problem:** `GRID_position` rośnie o 880 elementów na klatkę, ok. 10 MB/s w pomiarze bez okna (BUG-01).
- **Dlaczego ważne:** Każda dłuższa sesja wyczerpuje pamięć, a każdy zysk FPS przyspiesza wyciek.
- **Rozwiązanie:** Usunąć pole i wszystkie dopisywania. Nieużywany `box = pygame.Rect(...)` należy do R-33.
- **Pliki:** `src/world/game_map.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Krytyczny
- **Zależności:** Brak. Sprawdzenie: RSS stabilne przez 5 minut działania gry.

### R-02 — Dodać wyjście z dziury

- **Problem:** Gracz spada bez końca (BUG-02). Dzieje się to już po 0,84 s od rozpoczęcia biegu w prawo.
- **Dlaczego ważne:** To najszybszy sposób na zakończenie rozgrywki bez możliwości kontynuacji.
- **Rozwiązanie:** Po przekroczeniu `y > 800` przenieść gracza do ostatniego bezpiecznego miejsca na podłożu, wyzerować prędkość, ustawić kamerę. Punkt bezpieczny zapisywać, gdy gracz stoi na podłożu, nie blisko krawędzi. Sam warunek `vel.y == 0` nie wystarczy, bo pod P1 potrafi wystąpić w powietrzu, także nad dziurą (`x = 802`, `y = 520,8`) `[TEST]`, a odrodzenie tam kończyłoby się ponownym spadkiem. Po dodaniu R-20 dołożyć utratę życia.
- **Pliki:** `src/entities/player.py`, `src/core/physics_engine.py`, `config/settings.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Krytyczny
- **Zależności:** Brak, ale zachowanie zależy od decyzji autora nr 2 poniżej. Później zintegrować z R-20.

### R-03 — Pokazywać błędy zamiast je ukrywać

- **Problem:** `except Exception` drukuje jedną linię i kończy się kodem 0 (BUG-03).
- **Dlaczego ważne:** To warunek skutecznego usuwania wszystkich pozostałych błędów.
- **Rozwiązanie:** `logging.exception(...)` z pełnym śladem, następnie `sys.exit(1)`. W wersji spakowanej zapis do pliku logu.
- **Pliki:** `src/game.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Krytyczny
- **Zależności:** Brak. Wykonać jako pierwsze.

## B. Ważne usprawnienia techniczne

### R-04 — Uporządkować repozytorium

- **Problem:** `.gitignore` z szablonu JavaScript, 11 śledzonych `.pyc`, dwa katalogi `.idea`, `dev` za `main`, przestarzały `working` (ENV-05, ENV-07).
- **Dlaczego ważne:** Commity zaczną odzwierciedlać tylko faktyczne zmiany.
- **Rozwiązanie:** Dopisać `__pycache__/`, `*.pyc`, `venv/`, `dist/`, `build/`. Wykonać `git rm -r --cached` dla `.pyc` i `.idea`. Zmergować `main` do `dev`. Ocenić 2 commity z `working`, zanim gałąź zostanie usunięta. Dodać `CLAUDE.md` i `docs/` do repozytorium, bo `CLAUDE.md` odsyła do tych dokumentów.
- **Pliki:** `.gitignore`, `platformer_game/__pycache__/`, `.idea/`, `platformer_game/.idea/`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Wysoki
- **Zależności:** Brak.

### R-05 — Jedno źródło zależności

- **Problem:** `Pipfile`, lock, pusty `requirements.txt` i `venv` się nie zgadzają. `venv` widzi pakiety systemowe (ENV-01, ENV-02).
- **Dlaczego ważne:** Bez tego nie da się odtworzyć środowiska, zbudować paczki ani uruchomić CI.
- **Rozwiązanie:** Wybrać jeden mechanizm, np. `pyproject.toml` z przypiętymi wersjami dla Pythona 3.12. Usunąć pozostałe. Utworzyć izolowane środowisko bez dostępu do pakietów systemowych. Sprawdzić, czy gra uruchamia się bez nich.
- **Pliki:** katalog główny: `Pipfile`, `Pipfile.lock`; `platformer_game/requirements.txt`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Wysoki
- **Zależności:** Brak.

### R-06 — Niezależne od katalogu ścieżki zasobów

- **Problem:** Grafiki mają ścieżki względne, a muzyka bezwzględne (BUG-13).
- **Dlaczego ważne:** Warunek pakowania, testów i CI.
- **Rozwiązanie:** Funkcja `asset_path(*parts)` w `config/settings.py`, oparta na `BASE_DIR`, z uwzględnieniem `sys._MEIPASS`. Dodać `config/__init__.py`. Zastąpić wszystkie ścieżki w `SpriteManager`.
- **Pliki:** `config/settings.py`, `src/ui/sprite_manager.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Wysoki
- **Zależności:** Brak.

### R-07 — Testy i linter

- **Problem:** Brak zabezpieczenia przed regresją (ENV-06).
- **Dlaczego ważne:** Kolizje i animacje są splątane, a kolejne etapy będą je przebudowywać.
- **Rozwiązanie:** pytest z trybem `dummy`, podstawieniem klawiszy i sterowaniem przez `tick()`/`render()`. Pierwsze testy to wartości zmierzone w tym audycie:
    - uruchomienie gry i wykonanie 1000 ticków bez wyjątku,
    - lądowanie, prędkość biegu 3,67 px/tick, wysokość skoku ~157 px,
    - przejście P1 → P2 → P3,
    - zabicie przeciwnika atakiem z przodu i brak trafienia za plecami,
    - stabilna pamięć.
    Do tego `ruff` i prosty `ruff format`. Celowo nie utrwalać błędów testami, tylko oznaczać je `xfail`.
- **Pliki:** nowe: `tests/`, konfiguracja narzędzi
- **Złożoność:** Średnia · **Ryzyko regresji:** Niskie · **Priorytet:** Wysoki
- **Zależności:** R-05, R-06.

### R-08 — Limit FPS i animacje w tickach

- **Problem:** Render bez limitu, a `runCount` liczy rysowania (BUG-07). Bez limitu nadrabiania (BUG-16).
- **Dlaczego ważne:** Różny sprzęt daje różne tempo animacji, a skrajny FPS kończy się `IndexError`.
- **Rozwiązanie:** `clock.tick(60)` lub vsync. Liczniki przenieść do `tick()`, użyć 10 klatek z indeksem modulo. Ograniczyć `tps_delta` do np. 0,25 s.
- **Pliki:** `src/game.py`, `src/entities/player.py`, `config/settings.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Średnie · **Priorytet:** Wysoki
- **Zależności:** R-07 (zalecane).

### R-09 — Naprawić atak

- **Problem:** Animacja rzadko się odtwarza (BUG-04), a stan ataku kończy się w `draw`.
- **Dlaczego ważne:** To główna akcja walki w grze i obecnie wygląda jak błąd.
- **Rozwiązanie:** Pole `attack_ticks` zerowane przy naciśnięciu i zwiększane w `tick()`. Koniec ataku w `tick()`, `draw()` tylko odczytuje indeks klatki.
- **Pliki:** `src/entities/player.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Wysoki
- **Zależności:** R-08.

### R-10 — Usunąć martwy kod

- **Problem:** Zduplikowane `grid()`, stare metody, 21 nieużywanych pól, komentarze ze starym kodem (ARCH-11, ARCH-12, BUG-19).
- **Dlaczego ważne:** Utrudniają zrozumienie kodu i mylą przy zmianach.
- **Rozwiązanie:** Usuwać małymi commitami. Historia git zachowuje stare wersje. Także `PlayerState`, `AssetLoader` (do czasu R-19), `Menu` (do czasu R-29), nieużywane importy i `numpy` (ENV-03). Usunąć też efekty uboczne importu, `import *` oraz globalne `time0` tam, gdzie nie służy logice (ARCH-09).
- **Pliki:** niemal wszystkie, głównie `src/world/game_map.py`, `src/entities/enemy.py`, `src/ui/menu.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Średni
- **Zależności:** R-07.

### R-11 — Stałe w konfiguracji

- **Problem:** Magiczne liczby i trzy wartości grawitacji, a gracz zmienia swoją po pierwszym skoku (ARCH-07, BUG-14, BUG-15).
- **Dlaczego ważne:** Strojenie rozgrywki powinno być jedną zmianą.
- **Rozwiązanie:** `TILE_SIZE`, `GRAVITY`, `PLAYER_SPEED`, `JUMP_IMPULSE`, `MAP_PERIOD` itd. w `settings.py`. Przyjąć jedną grawitację i usunąć pętlę z `handle_jump`.
- **Pliki:** `config/settings.py`, `src/entities/`, `src/core/`, `src/world/`
- **Złożoność:** Niska · **Ryzyko regresji:** Średnie, bo zmienia odczucie spadania · **Priorytet:** Średni
- **Zależności:** R-07.

## C. Refaktoryzacja architektury

### R-12 — Rozdzielić `tick()` i `draw()`

- **Problem:** Geometria kolizji, `Weapon.pos.x`, `player_checkpoint`, stan pocisku powstają w rysowaniu, a pocisk rysuje w logice (ARCH-02).
- **Dlaczego ważne:** To źródło większości trudnych błędów i warunek testów, scen oraz menu.
- **Rozwiązanie:** Zasada: `draw()` nie zmienia stanu. Geometrię liczyć przy starcie i przy zmianie `player_checkpoint` w `tick()`. Weryfikacja: `tick()` działa poprawnie 1000 razy bez `render()`, a test porównuje `pos` z wersją z renderem.
- **Pliki:** `src/world/game_map.py`, `src/world/platform_manager.py`, `src/entities/weapon.py`, `src/entities/projectile.py`, `src/entities/player.py`
- **Złożoność:** Średnia · **Ryzyko regresji:** Średnie · **Priorytet:** Wysoki
- **Zależności:** R-07, R-08, R-09.

### R-13 — Nowe kolizje

- **Problem:** Stan w obiekcie, 4 kopie reakcji, brak kierunku (ARCH-03, BUG-05, BUG-06, BUG-18).
- **Dlaczego ważne:** Naprawia fałszywe odepchnięcia i trafienia, podwójny skok, wchodzenie w platformy i upraszcza przyszłe encje.
- **Rozwiązanie:** Czyste funkcje na `pygame.Rect` lub własnym typie. Ruch i korekta osobno na osi X i Y, z dosunięciem do krawędzi. Pole `on_ground`. Warunek skoku oparty o `on_ground`, a nie o `vel.y == 0`. Parametry ruchu ustalić tak, by zachować wysokość i zasięg zmierzone wcześniej, lub świadomie je zmienić.
- **Pliki:** `src/core/collision_manager.py`, `src/entities/player.py`, `src/entities/enemy.py`
- **Złożoność:** Wysoka · **Ryzyko regresji:** Wysokie · **Priorytet:** Wysoki
- **Zależności:** R-07, R-12.

### R-14 — Model świata oparty na danych

- **Problem:** Siatka w kodzie, algorytm platform, przesuwanie okna mapy (ARCH-06, BUG-11, BUG-12).
- **Dlaczego ważne:** Bez tego nie da się projektować poziomów.
- **Rozwiązanie:** Plik poziomu (najprościej JSON lub CSV, ewentualnie eksport z Tiled), stałe współrzędne światowe, platformy jako dane, tło liczone modulo. Decyzja projektowa: **skończone poziomy zamiast nieskończonego powtarzania**. To rekomendacja, bo upraszcza kod i daje naturalny cel gry, ale rozstrzyga autor.
- **Pliki:** `src/world/game_map.py`, `src/world/platform_manager.py`, `assets/levels/`
- **Złożoność:** Średnia lub wysoka · **Ryzyko regresji:** Wysokie · **Priorytet:** Wysoki
- **Zależności:** R-12, najlepiej także R-13.

### R-15 — Encje i listy obiektów

- **Problem:** Po jednej instancji, zależności na sztywno (ARCH-05).
- **Dlaczego ważne:** Warunek wielu przeciwników, pocisków i przedmiotów.
- **Rozwiązanie:** Prosta klasa bazowa `Entity` z `pos`, `vel`, `rect`, `tick()`, `draw()`. Listy `enemies`, `projectiles`, `pickups`. Bez wprowadzania ciężkiego systemu ECS.
- **Pliki:** `src/entities/`, `src/game.py`
- **Złożoność:** Średnia · **Ryzyko regresji:** Średnie · **Priorytet:** Średni
- **Zależności:** R-13.

### R-16 — Sceny i stany gry

- **Problem:** Istnieje tylko jeden tryb (ARCH-04).
- **Dlaczego ważne:** Menu, pauza, ekran końca i ładowanie poziomów tego wymagają.
- **Rozwiązanie:** Interfejs sceny z `handle_event`, `tick`, `draw`. `Game` tylko przełącza aktywną scenę. Zaczynać od `GameplayScene`, opakowując obecną logikę.
- **Pliki:** `src/game.py`, nowe `src/scenes/`
- **Złożoność:** Średnia · **Ryzyko regresji:** Średnie · **Priorytet:** Wysoki
- **Zależności:** R-12.

### R-17 — Klasa kamery

- **Problem:** Rozsyłanie `scroll` do 7 obiektów, nieużywane `scroll.y`, mylące `PhysicsEngine` (ARCH-08, ARCH-10).
- **Dlaczego ważne:** Upraszcza dodawanie obiektów i pozwala wprowadzić kamerę pionową.
- **Rozwiązanie:** `Camera.world_to_screen(pos)` odczytywane przez rysowanie, usunięcie `set_scroll`.
- **Pliki:** `src/core/physics_engine.py`, wszystkie metody `draw`
- **Złożoność:** Niska lub średnia · **Ryzyko regresji:** Średnie · **Priorytet:** Średni
- **Zależności:** R-12.

### R-18 — Ograniczyć service locator

- **Problem:** Każdy komponent ma dostęp do całej gry (ARCH-01).
- **Dlaczego ważne:** Luźniejsze zależności ułatwiają testy.
- **Rozwiązanie:** Stopniowo przekazywać tylko to, co potrzebne, np. `player.tick(input, world)`. Robić to przy okazji innych zmian, nie jako osobny duży projekt.
- **Pliki:** całe `src/`
- **Złożoność:** Średnia · **Ryzyko regresji:** Średnie · **Priorytet:** Niski
- **Zależności:** R-13, R-15, R-16.

### R-19 — Menedżer zasobów i animacji

- **Problem:** Dwa mechanizmy, ręczne ładowanie, brak wspólnej klasy animacji (§3 audytu).
- **Dlaczego ważne:** Ułatwia dodawanie postaci i zapobiega rozjazdom liczników.
- **Rozwiązanie:** Jeden loader z cache i `convert_alpha`. Klasa `Animation(frames, fps)` oparta na tickach. Odwrócone wersje przygotowywane przy ładowaniu.
- **Pliki:** `src/core/asset_loader.py`, `src/ui/sprite_manager.py`, encje
- **Złożoność:** Średnia · **Ryzyko regresji:** Niskie · **Priorytet:** Średni
- **Zależności:** R-06, R-08.

## D. Ulepszenia rozgrywki

### R-20 — Życie, obrażenia, śmierć

- **Problem:** Brak konsekwencji i przegranej (BUG-10).
- **Dlaczego ważne:** Bez ryzyka nie ma gry.
- **Rozwiązanie:** Licznik życia, chwilowa nietykalność, odrzut przez prędkość, ekran końca i restart.
- **Pliki:** `src/entities/player.py`, `src/core/collision_manager.py`, sceny, HUD
- **Złożoność:** Średnia · **Ryzyko regresji:** Niskie · **Priorytet:** Wysoki
- **Zależności:** R-02, R-13, R-16.

### R-21 — Prawdziwe zachowanie przeciwników

- **Problem:** Stały ruch w lewo, wpadanie w dziury, brak animacji (BUG-09).
- **Dlaczego ważne:** Obecny przeciwnik często w ogóle nie dochodzi do gracza.
- **Rozwiązanie:** Automat stanów: patrol, zawracanie na krawędzi i przy ścianie, opcjonalnie pościg w zasięgu. 10 klatek animacji i kierunek. Śmierć z krótką animacją. Pozycje z pliku poziomu.
- **Pliki:** `src/entities/enemy.py`
- **Złożoność:** Średnia · **Ryzyko regresji:** Niskie · **Priorytet:** Wysoki
- **Zależności:** R-13, R-15.

### R-22 — Lepsza walka wręcz

- **Problem:** Trafienie tylko w 1 ticku, asymetryczna strefa, kierunek zależny od prędkości (BUG-17, BUG-18, BUG-20).
- **Dlaczego ważne:** Decyduje o odczuciu walki.
- **Rozwiązanie:** Pole `facing`, aktywne okno trafienia, symetryczna strefa, czas odnowienia, jedno trafienie na atak.
- **Pliki:** `src/entities/player.py`, `src/entities/weapon.py`
- **Złożoność:** Niska lub średnia · **Ryzyko regresji:** Niskie · **Priorytet:** Średni
- **Zależności:** R-09, R-12.

### R-23 — Odczucie ruchu

- **Problem:** Skok jest binarny, nie ma tolerancji krawędzi. Animacji skoku i spadania brak.
- **Dlaczego ważne:** Precyzja jest kluczowa w platformówce, tym bardziej że dziury kończą bieg.
- **Rozwiązanie:** Coyote time, bufor skoku, zmienna wysokość skoku, strzałki jako alternatywne klawisze. Parametry do strojenia ręcznego, bo tego nie da się ocenić w teście bez okna.
- **Pliki:** `src/entities/player.py`, `config/settings.py`
- **Złożoność:** Średnia · **Ryzyko regresji:** Średnie · **Priorytet:** Średni
- **Zależności:** R-13.

### R-24 — Czytelność świata

- **Problem:** Dziura wygląda jak roślinność, a trawa zakrywa platformy i wygląda jak przeszkoda (BUG-12).
- **Dlaczego ważne:** Gracz musi widzieć zagrożenie, zanim w nie wejdzie.
- **Rozwiązanie:** Prawdziwe kafelki z `country-platform-tileset.png`, poprawna kolejność warstw, wyraźne zagrożenie, ewentualnie kolizje dla kamieni.
- **Pliki:** `src/world/game_map.py`, `src/ui/sprite_manager.py`
- **Złożoność:** Niska lub średnia · **Ryzyko regresji:** Niskie · **Priorytet:** Średni
- **Zależności:** R-14.

### R-25 — Naprawiona kula ognia i broń do podniesienia

- **Problem:** Kod nieosiągalny i wywracający grę (BUG-08).
- **Dlaczego ważne:** Zasoby już są, a mechanika daje różnorodność.
- **Rozwiązanie:** Licznik w tickach na instancji, odwrócone klatki, kolizja z mapą, czas odnowienia, przedmiot do podniesienia z `weapon.png`.
- **Pliki:** `src/entities/projectile.py`, `src/entities/player.py`, `src/ui/sprite_manager.py`
- **Złożoność:** Średnia · **Ryzyko regresji:** Niskie · **Priorytet:** Średni
- **Zależności:** R-08, R-12, R-15.

### R-26 — Wykorzystać istniejące animacje

- **Problem:** Bezczynność i przeciwnik mają po jednej klatce, a pliki są.
- **Dlaczego ważne:** Duży zysk wizualny przy małym nakładzie.
- **Rozwiązanie:** Wczytać wszystkie klatki `Stand/`, użyć pełnego cyklu biegu i klatek przeciwnika.
- **Pliki:** `src/ui/sprite_manager.py`, `src/entities/player.py`, `src/entities/enemy.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Niski
- **Zależności:** R-08, najlepiej R-19.

## E. Nowe funkcje

| ID | Funkcja | Dlaczego | Rozwiązanie | Pliki | Złożoność | Ryzyko | Priorytet | Wymaga |
|---|---|---|---|---|---|---|---|---|
| R-27 | Wynik i HUD | Daje informację zwrotną | Punkty za przeciwników, pasek życia, FPS tylko w trybie debug. Użyć `FreeSansBold.ttf` | `src/core/game_engine.py`, nowy `src/ui/hud.py` | Niska | Niskie | Średni | R-16, R-20 |
| R-28 | Poziomy, checkpointy, koniec | Daje grze cel | Punkty kontrolne i meta z pliku poziomu, przejście do następnego | `src/world/`, sceny | Średnia | Średnie | Wysoki | R-14, R-20 |
| R-29 | Menu główne, pauza, ustawienia | Podstawa kompletnej gry | Nowe sceny zamiast obecnego `Menu`, głośność, klawisze | `src/scenes/`, `src/ui/` | Średnia | Niskie | Średni | R-16 |
| R-30 | Efekty dźwiękowe | Wzmacnia odczucie akcji | `pygame.mixer.Sound` dla skoku, ciosu, trafienia, z ustawieniem głośności | `src/core/`, encje | Niska | Niskie | Niski | R-19 |
| R-31 | Więcej treści | Dłuższa gra | Typy przeciwników, przedmioty, zapis postępu, kilka poziomów | Wiele | Wysoka | Średnie | Niski | R-15, R-21, R-28 |

## F. Optymalizacja wydajności

Wzrost wydajności nie jest teraz najpilniejszy, bo w pomiarze bez okna gra osiąga ~63 FPS, ale R-32 jest wyjątkowo tani. Płynności w prawdziwym oknie nie sprawdzono `[NIEZWERYFIKOWANE]`.

### R-32 — `convert_alpha()` dla wszystkich grafik

- **Problem:** Brak konwersji formatu. Render zajmuje 15,8 ms w pomiarze bez okna.
- **Dlaczego ważne:** Test w pamięci dał 2,37 ms, czyli 6,6× szybciej, co zapewnia zapas na treść. Wynik pochodzi ze sterownika `dummy` i w prawdziwym oknie może być inny.
- **Rozwiązanie:** Po `set_mode()` `convert_alpha()` przy ładowaniu i `convert()` dla obrazów bez alfa.
- **Pliki:** `src/ui/sprite_manager.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Wysoki
- **Zależności:** **Koniecznie po R-01 i R-08.**

### R-33 — Pomijanie rysowania poza ekranem i porządki

- **Problem:** 28 kopii lasu, 3 kopie gór i 5 obrazów terenu są rysowane niezależnie od widoczności. 800 nieużywanych `Rect` na klatkę. Odbicie sprite'a w każdej klatce. Skalowanie platform w każdej klatce.
- **Dlaczego ważne:** Drobny zysk, ale kod będzie prostszy. Skalowanie platform kosztuje tylko 0,03 ms, więc robić je dla czytelności, a nie szybkości.
- **Rozwiązanie:** Liczyć tylko widoczne kopie, gotowe odwrócone klatki, statyczne warstwy.
- **Pliki:** `src/world/game_map.py`, `src/world/platform_manager.py`, `src/entities/player.py`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Średni
- **Zależności:** R-32, R-14 dla warstw statycznych.

### R-34 — Mniejsze pliki graficzne

- **Problem:** Efekty 2048², bohater 512² skalowane do 400² i 160².
- **Dlaczego ważne:** Mniejsze repozytorium i paczka, ale czas ładowania nie jest obecnie problemem.
- **Rozwiązanie:** Przygotować zasoby w docelowych rozmiarach i usunąć ostrzeżenia iCCP, zachowując oryginały poza paczką.
- **Pliki:** `assets/images/`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Niski
- **Zależności:** R-35.

Świadomie **nie** ma tu podziału przestrzeni dla kolizji: `tick()` zajmuje 0,084 ms. Wróćmy do tego dopiero przy znacznie większych poziomach.

## G. Budowanie i dystrybucja

### R-35 — Porządki w zasobach

- **Problem:** Pliki bez rozszerzeń, nieużywane obrazy, duplikaty (§3 audytu).
- **Dlaczego ważne:** Mniejsza paczka i mniej niejasności licencyjnych.
- **Rozwiązanie:** Po ustaleniu planów usunąć lub przenieść do `assets/unused/`. Nie usuwać zasobów planowanych w innych zadaniach: `Stand/` i `enemy/` (R-26), `country-platform-tileset.png` (R-24), `weapon.png` i `effects/` (R-25), `FreeSansBold.ttf` (R-27).
- **Pliki:** `assets/`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Średni
- **Zależności:** R-36.

### R-36 — Wyjaśnić licencje

- **Problem:** Źródła postaci, muzyki i efektów są nieznane, a kod nie ma pliku licencji (ENV-08).
- **Dlaczego ważne:** Blokuje publiczną dystrybucję.
- **Rozwiązanie:** Plik `ASSETS.md` z autorem, źródłem i licencją każdego zestawu. Zastąpić to, czego nie da się potwierdzić. Wybrać licencję kodu.
- **Pliki:** nowe `ASSETS.md`, `LICENSE`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Wysoki przed publikacją
- **Zależności:** Brak.

### R-37 — Nowa konfiguracja PyInstallera

- **Problem:** Spec nie zadziała (§6 audytu).
- **Dlaczego ważne:** Umożliwi grę bez instalowania Pythona.
- **Rozwiązanie:** Przenieść spec do `platformer_game/`. Zacząć od `onedir` i `console=True`, dopiero po potwierdzeniu działania `console=False` z plikiem logu. Punkt wyjścia do sprawdzenia, nieprzetestowany:

    ```python
    a = Analysis(
        ["src/main.py"],
        pathex=["."],
        datas=[("assets", "assets")],
    )
    ```

    Testować na czystym systemie, osobno na macOS, Windows i Linuksie.
- **Pliki:** `src/main.spec`, `config/settings.py`
- **Złożoność:** Średnia · **Ryzyko regresji:** Niskie · **Priorytet:** Średni
- **Zależności:** R-03, R-05, R-06, a najlepiej też R-36.

### R-38 — Ciągła integracja

- **Problem:** Brak automatycznego sprawdzania.
- **Dlaczego ważne:** Wyłapuje regresje i pilnuje czystości środowiska.
- **Rozwiązanie:** GitHub Actions: instalacja zależności, `ruff`, pytest w trybie `dummy`. Później budowa paczek na trzech systemach.
- **Pliki:** nowe `.github/workflows/`
- **Złożoność:** Niska · **Ryzyko regresji:** Niskie · **Priorytet:** Średni
- **Zależności:** R-05, R-07.

### R-39 — Aktualizacja README

- **Problem:** README jest minimalne, a na `dev` link do GIF-a jest błędny.
- **Dlaczego ważne:** To pierwszy kontakt z projektem.
- **Rozwiązanie:** Instalacja, uruchamianie, sterowanie, odnośniki do `docs/`, stan projektu.
- **Pliki:** `README.md`
- **Złożoność:** Niska · **Ryzyko regresji:** Brak · **Priorytet:** Niski
- **Zależności:** R-04, R-05.

## Pierwsze kroki

Jeśli czas jest ograniczony, ten krótki zestaw daje największy zysk: **R-03, R-01, R-02, R-08, R-09, R-32**. Wszystkie mają niską złożoność, a gra powinna być po nich stabilniejsza i szybsza. Pozostałe problemy z audytu, w tym kolizje, zostają otwarte. W tej kolejności R-08 musi poprzedzać R-32.

## Decyzje do podjęcia przez autora

1. **Rodzaj gry:** skończone poziomy (rekomendacja) czy nieskończony bieg? Wpływa na R-14 i R-28.
2. **Dziura:** utrata życia z odrodzeniem (rekomendacja) czy natychmiastowy koniec gry? Wpływa na R-02 i R-20.
3. **Grawitacja:** 0,7 czy 0,9? Obecny skok działa przy 0,9, ale ostateczny wybór trzeba ocenić, grając ręcznie. Wpływa na R-11.
4. **Publikacja:** czy gra ma być docelowo publicznie dostępna? To decyduje o pilności R-36.
5. **Kula ognia:** zachować ją w grze czy porzucić? Wpływa na R-25.

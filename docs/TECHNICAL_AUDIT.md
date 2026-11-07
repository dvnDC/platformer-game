# Audyt techniczny

> Data: 2026-11-06. Zakres: gałąź `dev`, commit `2d51b48`, bez zmian w kodzie. Ścieżki są względem `platformer_game/`, o ile nie zaznaczono inaczej. Znaczniki objaśnia [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md).

## 1. Metodyka

1. Przeczytano cały kod źródłowy (21 plików), konfiguracje i deklaracje zależności.
2. Wykonano analizę statyczną AST: nieużywane importy, pola zapisywane i nieczytane, metody bez odwołań, zależności `self.game.X`.
3. Przeprowadzono eksperymenty bez okna skryptami poza repozytorium: `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`, wyłączone zapisywanie bytecode'u, klawisze podstawione przez zamianę `pygame.key.get_pressed`.
4. Obejrzano zrzuty ekranu wyrenderowane przez grę.

W niektórych testach, wyłącznie w pamięci procesu, zmieniano stan gry: teleportacja gracza lub przeciwnika, `got_weapon = True`, tymczasowy kafelek-ściana, wywołanie `convert_alpha()`. Pliki projektu nie zostały zmienione, a `git status` przed i po audycie (nie licząc `docs/`) jest taki sam.

**Ograniczenia:**

- Jeden komputer (macOS, Python 3.12.0, pygame 2.5.2), sterownik `dummy`. `display.flip()` nie ma tu realnego kosztu, więc FPS z prawdziwym oknem będzie inny `[NIEZWERYFIKOWANE]`.
- Nie grano ręcznie i nie oceniono „wyczucia” sterowania.
- Nie sprawdzono Windows, Linuksa ani budowania PyInstallerem.
- Wyciek pamięci obserwowano przez 30 s. Dłuższe wartości to ekstrapolacja. Dotyczy to stanu sprzed R-01.

## 2. Podsumowanie pomiarów

**Wszystkie liczby w tej sekcji pochodzą z pomiarów bez okna** (sterownik `dummy`, jeden komputer). Pokazują proporcje, a nie FPS gracza. Powtórny pomiar `render()` dał 16,2 ms bez konwersji i 2,45 ms po niej, czyli ten sam stosunek ok. 6,6×.

| Pomiar | Wynik |
|---|---|
| Render (FPS) w pętli, 30 s | ~63 FPS, stabilnie |
| Logika | 100 TPS |
| Czas `render()` | 15,8 ms |
| Czas `tick()` | 0,084 ms |
| Wzrost `GRID_position` | 880 krotek na klatkę, 1 658 800 po 30 s |
| Maksymalne RSS | 144 MB (5 s) → 399 MB (30 s), ok. 10 MB/s |
| Czas `render()` po `convert_alpha()` w pamięci | 2,37 ms (6,6× szybciej) |

Wiersze o `GRID_position` i RSS opisują stan sprzed R-01. Pomiary po naprawie są przy [BUG-01](#bug-01--nieograniczony-wyciek-pamięci-w-grid_position).

Szczegółowy czas części renderu:

| Element | Bez konwersji (ms) | Po `convert_alpha` (ms) |
|---|---|---|
| `background_vanilla` | 7,53 | 1,15 |
| `grid` | 7,52 | 1,03 |
| `stone` | 0,36 | 0,03 |
| `player.draw` | 0,20 | 0,02 |
| `platforms.draw` | 0,03 | 0,03 |
| `display_fps` | 0,003 | 0,003 |

**Wniosek z audytu:** koszt to prawie wyłącznie rysowanie dużych powierzchni bez konwersji formatu. Wbrew intuicji `transform.scale` w każdej klatce i brak podziału przestrzeni w kolizjach nie są dziś problemem wydajnościowym.

### Pomiary po R-32

Powyższe liczby opisują stan z audytu, a tabele niżej stan przed i po wprowadzeniu konwersji do `SpriteManager`, już z limitem FPS z R-08. Oba zestawy mierzono na tym samym komputerze (macOS), przy stojącym graczu i bez dźwięku.

**Bez okna** (sterownik `dummy`) `[TEST]`:

| Pomiar | Przed | Po |
|---|---|---|
| Mediana `render()` | 15,91 ms | 1,71 ms (9,3× szybciej) |
| Tło (`background_vanilla`) | 7,64 ms | 0,66 ms |
| `grid` | 7,55 ms | 0,91 ms |
| `stone` | 0,36 ms | 0,03 ms |
| `player.draw` | 0,20 ms | 0,02 ms |
| `tick()` | 0,085 ms | 0,085 ms |
| Pętla `Game.run`, 10 s | 60,4 FPS, 99,9 TPS, 100% rdzenia | 55,8 FPS, 99,9 TPS, 24% rdzenia |
| `Game()` przy starcie | 92 ms | 87 ms |
| Maksymalne RSS | 95,2 MB | 101,6 MB |

Spadek do 55,8 FPS wynika z tego, że proces naprawdę śpi w `clock.tick(60)`, a sen trwa dłużej, niż zamówiono. Tempo logiki się nie zmienia.

**Prawdziwe okno** (sterownik `cocoa`, pętla `Game.run`, 2 przebiegi po 8 s, pomiar skryptem, bez oceny wzrokowej i bez dźwięku):

| Pomiar | Przed | Po |
|---|---|---|
| Mediana `render()` z `flip()` | 17,3 ms | 3,9 ms (4,4× szybciej) |
| FPS | 56,8 i 57,1 | 59,0 i 59,4 |
| TPS | 100,0 i 100,1 | 100,1 i 100,0 |
| Użycie rdzenia | ok. 103% | ok. 28% |

**Zgodność obrazu:** 61 klatek ze skryptowego przebiegu (bieg, skok, cios, przeciwnik) było identycznych co do bajta przed i po konwersji, osobno bez okna i w prawdziwym oknie. Identyczne były też pozycje, prędkości i `runCount` w 1500 tickach. Pozostałe grafiki, np. kulę ognia, porównano pojedynczo tylko bez okna: rozmiar i wszystkie piksele RGBA się zgadzają `[TEST]`.

**Ograniczenia po R-32:**

- Bieg, walka i dłuższa gra nie były mierzone w prawdziwym oknie, a wynik pochodzi z jednego komputera. Inne ekrany i systemy mogą dać inne liczby `[NIEZWERYFIKOWANE]`.
- Format ekranu zależy od sterownika: `dummy` nie ma maski alfa, a `cocoa` ma. Po `convert()` powierzchnie w `cocoa` mają więc maskę alfa, ale pozostają nieprzezroczyste (`SRCALPHA` wyłączone, tryb mieszania 0, alfa 255). Testy automatyczne działają tylko na `dummy`.
- Plik RGBA bez żadnego przezroczystego piksela dostałby `convert_alpha()`, czyli bezpieczniejszą, ale wolniejszą ścieżkę. Teraz takich grafik nie ma `[TEST]`.
- Po `pygame.display.set_mode` z innym formatem grafiki trzeba by przekonwertować ponownie. Dziś tryb ustawiany jest raz `[KOD]`.

## 3. Grafika i zasoby

### Ładowanie

- Wszystko ładuje się raz, w `SpriteManager.__init__`, przez bezpośrednie `pygame.image.load` z **względnymi** ścieżkami `[KOD]`.
- Muzyka korzysta z bezwzględnego `BASE_DIR`. To niespójność, przez którą gra nie startuje poza `platformer_game/` `[TEST]`.
- `AssetLoader` nie jest używany, a jego cache tworzony jest od nowa w każdym wywołaniu (`asset_loader.py:9`) `[KOD]`.
- Od R-32 `SpriteManager.optimize` konwertuje każdą grafikę raz, zaraz po wczytaniu i skalowaniu. W audycie nie było `.convert()` ani `.convert_alpha()` w całym projekcie `[KOD]`.
- Przy starcie libpng drukuje ostrzeżenia `iCCP: known incorrect sRGB profile`, ok. 10 na uruchomienie. Chunk iCCP ma 17 plików PNG `[TEST]`.
- Pamięć po wczytaniu to szacunkowo ok. 14 MB `[WYLICZONE]`, więc wielkość zasobów w RAM nie jest problemem.

### Animacje

Animacje to listy `Surface` indeksowane licznikiem. Nie ma klasy animacji ani wspólnego zegara:

| Animacja | Zegar | Problem |
|---|---|---|
| Bieg gracza | Licznik `runCount` w tickach (od R-08) | Używane 7 z 10 klatek |
| Atak | `attack_ticks` w tickach, także koniec ataku (od R-09) | Używane 9 z 10 klatek |
| Efekt ataku | Ten sam timer | Używane 9 z 12 klatek |
| Kula ognia | `time.time()` i globalne `time0` | Błędny licznik, crash |
| Bezczynność | Brak | 1 z 10 klatek |
| Przeciwnik | Brak | 1 z 10 klatek |

### Inwentarz zasobów

Status „Wczytany” oznacza wywołanie w `SpriteManager`, a „Widoczny” oznacza rysowanie w osiągalnym kodzie `[KOD]`.

| Plik | Wymiary źródłowe | Wczytany | Widoczny | Uwagi |
|---|---|---|---|---|
| `hero/Knight/Stand/0.png` | 512² → 160² | Tak | Tak | |
| `hero/Knight/Stand/1-9.png` | 512² | **Nie** | Nie | Cały zestaw 0-9 to 5 unikatowych klatek i 5 duplikatów |
| `hero/Knight/Run/0-9.png` | 512² → 160² | Tak | 0-6 | Klatki 5-9 to duplikaty 4-0 |
| `hero/Knight/Attack1H/0-9.png` | 512² → 160² | Tak | 0-8 | 9 = duplikat 0 |
| `enemy/0/w_0.png` | 150² → 60² | Tak | Tak | |
| `enemy/0/w_1-9.png` | 150² | Tak | **Nie** | Oraz odwrócone kopie |
| `enemy2.png` | 120² | Tak | **Nie** | `enemyImage` nieczytane |
| `grid0.png` | 80² | Tak | **Nie** | |
| `grid1.png` | 80² | Tak | Tak | Bez kanału alfa |
| `layers/country-platform-back.png` | 384×224 → 1280×720 | Tak | Tak | |
| `layers/country-platform-forest.png` | 160×224 → 300×720 | Tak | Tak | |
| `layers/country-platform-tiles-example.png` | 384×224 → 1280×720 | Tak | Tak | Wartość `7` w siatce |
| `layers/country-platform-tileset.png` | 176×160 | **Nie** | Nie | |
| `objects/stone.png` | 700×600 → 234×200 | Tak | Tak | |
| `objects/stone` | 700×600 | **Nie** | Nie | PNG bez rozszerzenia, inny plik niż `stone.png` |
| `spaceship` | 969×422 | **Nie** | Nie | PNG bez rozszerzenia |
| `platform.png` | 500×50 → 300×30 | Tak | Tak | |
| `weapon.png` | 100² → 50² | Tak | **Nie** | Brak logiki podnoszenia |
| `effects/0-5.png` | 512×197 → 256×100 | Tak | **Nie** | Tylko kula ognia |
| `effects/attack/2.png` | 2048² → 400² | Tak | Tak | |
| `effects/attack/0-1.png` | 2048² | **Nie** | Nie | 760 KB łącznie |
| `fonts/FreeSansBold.ttf` | — | **Nie** | Nie | Gra używa systemowego Arial |
| `sounds/latenight.ogg` | — | Tak | n/d | 3,9 MB |
| `license.txt` | — | n/d | n/d | Nie wskazuje plików, których dotyczy |
| `preview.gif` (katalog główny) | 500×237 | n/d | n/d | Używany przez README na `main` |

Brakujących zasobów w osiągalnym kodzie nie ma. Martwy kod odwołuje się do nieistniejących pól `imageMenuGrid1` i `shipImage` `[TEST]`.

### Możliwości poprawy

Centralny menedżer zasobów z bezwzględnymi ścieżkami, `convert_alpha`, manifest z listą animacji, usunięcie duplikatów, przeskalowanie źródeł z 2048² i 512² do docelowych rozmiarów, używanie własnej czcionki.

## 4. Architektura i jakość kodu

| ID | Problem | Waga | Pliki | Skutki | Rozwiązanie |
|---|---|---|---|---|---|
| ARCH-01 | Service locator i wzajemne modyfikowanie pól, cykle `Player ↔ CollisionManager ↔ Enemy` ([zależności](ARCHITECTURE.md#rzeczywiste-zależności-w-czasie-działania)) `[TEST]` | Wysoka | Całe `src/`, zwłaszcza `src/game.py`, `src/entities/player.py` | Zmiana jednej klasy wpływa na inne, testy jednostkowe są trudne | R-18, stopniowo przekazywać jawne zależności |
| ARCH-02 | Logika w rysowaniu, a rysowanie w logice: geometria kolizji, `Weapon.pos.x`, `player_checkpoint`, `Projectile.tick → draw` `[KOD]` | Krytyczna dla rozwoju | `src/world/game_map.py`, `src/world/platform_manager.py`, `src/entities/weapon.py`, `src/entities/player.py`, `src/entities/projectile.py` | Wyłączenie rysowania zmienia fizykę, a menu lub pauza są utrudnione | R-12 |
| ARCH-03 | `CollisionManager` z ukrytym stanem, 4 kopiami reakcji i niestandardowym układem prostokątów `(x0, x1, y0, y1)` `[KOD]`, `[TEST]` | Wysoka | `src/core/collision_manager.py:81-100,126-145,172-191,216-237` | Błędy BUG-05, BUG-06, poprawki trzeba powielać | R-13 |
| ARCH-04 | Brak stanów gry i scen, `Game.run` zna tylko jeden tryb `[KOD]` | Wysoka | `src/game.py` | Brak miejsca na menu, pauzę i ekran końca | R-16 |
| ARCH-05 | Założenie jednej encji każdego typu, brak klasy bazowej `[KOD]` | Wysoka | `src/game.py`, `src/core/collision_manager.py`, `src/core/physics_engine.py`, `src/entities/` | Drugi przeciwnik wymaga zmian w wielu klasach | R-15 |
| ARCH-06 | Dane poziomu w kodzie: siatka jako literał bez stałej pozycji w świecie, platformy jako algorytm, kamienie jako wzór. Trzy osobne modele świata `[KOD]` | Wysoka | `src/world/game_map.py:25-37,46-48`, `src/world/platform_manager.py:34-47` | Projektowanie poziomów oznacza edycję kodu, a platformy się nie powtarzają | R-14 |
| ARCH-07 | Magiczne liczby: 3840, 2560, 1280, 640, 170, 80, 12, 70, a parametry fizyki poza `settings.py` `[KOD]` | Średnia | Całe `src/`, `config/settings.py` | Trudne strojenie, łatwo o rozjazd wartości | R-11 |
| ARCH-08 | Kamera rozsyłana do 7 obiektów, `scroll.y` liczony bez użycia `[KOD]` | Średnia | `src/core/physics_engine.py:23-37`, metody `draw` | Łatwo zapomnieć o nowym obiekcie, brak kamery pionowej | R-17 |
| ARCH-09 | Efekty uboczne importu (`set_caption`), `import *` w `src/__init__.py`, `config` bez `__init__.py`, globalne `time0` w 3 modułach `[KOD]` | Średnia | `src/game.py:19`, `src/__init__.py`, `src/entities/player.py:6`, `enemy.py:7`, `projectile.py:5` | Trudniejsze testy i pakowanie, ukryty stan globalny | R-06, R-10, R-25 |
| ARCH-10 | Mylące nazwy: `PhysicsEngine` (kamera), `GameEngine` (FPS), `game.fire` a `weapon.fire`, `pos` a `position`, `colum`, `position_multiplayer`; mieszane style nazw `[KOD]` | Średnia | `src/core/`, `src/entities/`, `src/ui/menu.py`, `src/world/game_map.py` | Kod wprowadza w błąd przy czytaniu | Zmieniać nazwy przy refaktoryzacji w R-12 do R-17 |
| ARCH-11 | 205 z ~1430 linii to komentarze, głównie stary kod. `enemy.py` ma ich 55% `[TEST]` | Niska | `src/entities/enemy.py:88-166`, `src/world/game_map.py:87-104`, `src/ui/sprite_manager.py:78-98` | Szum podczas czytania i wyszukiwania | R-10 |
| ARCH-12 | Zduplikowane fragmenty: `grid()` × 2, `grid_static` × 2, `collision`, `collision_grid`, `collision_enemy`, gałęzie prawo/lewo `[KOD]` | Średnia | `src/world/game_map.py`, `src/ui/menu.py`, `src/core/collision_manager.py`, `src/entities/player.py` | Niepewność, która wersja obowiązuje, poprawki w wielu miejscach | R-10, R-13 |

Mocne strony, które warto zachować: prosty przepływ, stały krok logiki, czytelny podział katalogów, niewielki rozmiar kodu, wspólny pomysł na `tick()`/`draw()`, działający parallax.

## 5. Błędy i ryzyka

Waga: **Krytyczna** blokuje normalne używanie, **Wysoka** wyraźnie psuje grę albo rozwój, **Średnia** to widoczna wada lub ukryte ryzyko, **Niska** to kosmetyka lub ryzyko odległe.

### BUG-01 — Nieograniczony wyciek pamięci w `GRID_position`

- **Status:** ✅ Naprawione w R-01 i zweryfikowane bez okna. Opis i skutki poniżej to historia z audytu, a nie obecny kod. Lista, jej wypełnianie i tworzone tylko dla niej krotki zostały usunięte. W porównaniu skryptowym 1690 kroków zgadzały się sumy kontrolne każdej klatki (bez licznika FPS), pola kolizji oraz stan gracza i przeciwnika `[TEST]`. W chwili naprawy przechodziło 26 testów `[TEST]`. Pomiary i ograniczenia są pod opisem błędu.
- **Opis:** `GameMap.grid()` dopisuje krotki do `GRID_position` w każdej klatce i nigdy nie czyści listy. Nic jej nie czyta. Kafelki `1` są dopisywane podwójnie, więc wychodzi 880 elementów na klatkę.
- **Waga:** Krytyczna `[TEST]`
- **Pliki i metody:** `src/world/game_map.py:23,154,161,163`, `GameMap.grid`
- **Skutki:** ok. 162 KB/klatkę, czyli ~10 MB/s przy 63 FPS. Przy tym tempie 8 GB pamięci wyczerpuje się w ok. 13 minut `[WYLICZONE]`. Co się stanie potem (swap, zabicie procesu), nie sprawdzano. Tempo rośnie z FPS.
- **Rozwiązanie:** Usunąć listę i wszystkie jej wypełnienia.

**Pomiar przed i po R-01** `[TEST]` (sterownik `dummy`, macOS, ten sam komputer, ok. 60 FPS w obu wersjach). Ponowny pomiar wersji sprzed naprawy potwierdził wynik audytu (146 → 388 MB wobec 144 → 399 MB).

| Pomiar | Przed | Po |
|---|---|---|
| Maksymalne RSS, 5 s | 146,2 MB | 94,4 MB |
| Maksymalne RSS, 30 s | 388,4 MB | 94,0 MB |
| Maksymalne RSS, 60 s ze sterowaniem | 677,3 MB | 93,2 MB |
| Maksymalne RSS, 300 s (18 011 klatek) | nie mierzono | 93,4 MB, bez zmian od 5. sekundy |
| Elementy `GRID_position` po 30 s | 1 589 280 | pole nie istnieje |
| Pamięć zatrzymana przez `grid()` (`tracemalloc`) | 155 776 B na wywołanie | 577 B łącznie po 6100 wywołaniach |

Stałe RSS nie oznacza, że cała pamięć jest stała. Te trzy kategorie trzeba rozróżniać:

- **Zatrzymana przez aplikację:** w 60-sekundowym przebiegu pełnej pętli przybyło 8,8 KB na 2603 klatki, bez samego skryptu pomiarowego. Większość to kompilacja filtrów `tracemalloc` (`_compiler`, `fnmatch`), a 3,4 KB przypada na `GameEngine.render`. W osobnym teście `display_fps()` wzrost wygasał (2,4 KB po 51 000 wywołań). Nie ma tu wzrostu zbliżonego do wycieku, ale nie wykazano też dokładnie zerowego przyrostu.
- **Tymczasowa:** `grid()` nadal tworzy w każdej klatce ok. 800 nieużywanych `Rect` (R-33), zwalnianych od razu, oraz 80 krotek kolizji, które zastępują krotki z poprzedniej klatki. Szczyt jednego wywołania to ok. 0,5 KB ponad stan początkowy. Te `Rect` mogą kosztować czas CPU, ale nie mierzono tego osobno.
- **Zarezerwowana przez Pythona, pygame i system:** z ok. 94 MB RSS areny alokatora Pythona zajmują 10 MiB (9,7 MB w użyciu). Pozostałe ok. 84 MB to pamięć poza tymi arenami, m.in. biblioteki i powierzchnie SDL. Nie rozdzielono jej dokładniej.

**Ograniczenia:**

- Nie sprawdzono prawdziwego okna, dźwięku ani ręcznej gry `[NIEZWERYFIKOWANE]`.
- Przebiegi 5-minutowe odbyły się bez okna i przy stojącym graczu. Ze sterowaniem skryptowym gra działała tylko 60 s.
- W tym 60-sekundowym przebiegu RSS spadło po ok. 42 s z 93,2 do 64,2 MB i już tak zostało. Przyczyny nie ustalono, więc nie jest to potwierdzona poprawa `[NIEZWERYFIKOWANE]`.
- `Menu.GRID_position` to osobna lista, której R-01 nie zmieniło. Jedyne wywołanie `Menu.draw()` w grze jest zakomentowane (`src/game.py:106`) `[KOD]`, a w 100 klatkach metoda nie została wywołana ani razu `[TEST]`, więc podczas gry lista nie rośnie. Wywołanie ręczne dopisuje 43 krotki i kończy się `AttributeError` `[TEST]`. Lista nie jest czyszczona, więc po naprawieniu i włączeniu menu rosłaby z każdą klatką `[KOD]`.

### BUG-02 — Wpadnięcie w dziurę kończy grę bez wyjścia

- **Status:** ✅ Naprawione w R-02, zweryfikowane bez okna i ręcznie w prawdziwym oknie. Opis i skutki poniżej to historia z audytu. Teraz po przekroczeniu `y > 800` gracz traci życie i wraca na start, a w grze bez spadków nic się nie zmieniło: 1360 kroków porównania z commitem `6bb0e6c` dało identyczne sumy kontrolne klatek (bez licznika FPS), pola kolizji i stan `[TEST]`. Ograniczenia są pod opisem błędu.
- **Opis:** Nie ma dolnej granicy świata, odrodzenia ani przegranej. Kamera pionowa nie działa.
- **Waga:** Krytyczna `[TEST]`
- **Pliki i metody:** `src/entities/player.py:102-134`, `src/core/physics_engine.py:32-37`
- **Skutki:** Bieg w prawo od startu kończy się spadkiem po 0,84 s. `y` rośnie bez końca, a w praktyce jedyne wyjście to zamknięcie gry. Jedyny znany wyjątek jest przypadkowy: kontakt z przeciwnikiem spadającym przez tę samą dziurę (3 z 320 prób z przytrzymaną spacją, szczegóły w [GAMEPLAY.md](GAMEPLAY.md#dziury)). Nie zmienia to wagi, bo gra nie ma żadnego mechanizmu wyjścia.
- **Rozwiązanie:** Linia śmierci, np. `y > 800`, z odrodzeniem w ostatnim bezpiecznym punkcie, a później obrażeniami i ekranem końca.

**Ograniczenia po R-02:**

- Ręczny test autora w prawdziwym oknie (gra uruchomiona z PyCharm) zakończył się powodzeniem, ale nie ma z niego pomiarów, np. FPS ani pamięci.
- Odrodzenie jest zawsze na starcie `(640, 170)`, a nie w ostatnim bezpiecznym punkcie, więc spadek daleko od startu cofa cały postęp. `player_checkpoint = 0` pasuje tylko do tej pozycji `[KOD]`.
- `Player.lives` nie jest wyświetlane. Przy 0 żyć gracz nadal się odradza, bo nie ma przegranej (R-20) `[TEST]`.
- Pierwszy tick po odrodzeniu ma `vel.y == 0`, więc przytrzymana spacja daje skok w powietrzu (do `y ≈ 13`), tak samo jak na starcie gry. Jeśli był to pierwszy skok, zmienia też grawitację (BUG-14) `[TEST]`.
- Przeciwnik nie jest przenoszony. Po spadku daleko od startu wraca sam dopiero wtedy, gdy znajdzie się ponad 1000 px za graczem: po 54 s przy spadku na `x = 4670`, po 206 s na `x = 19870` `[TEST]`.
- Pola kolizji odświeża dopiero render. Przed R-08 długi przestój po odrodzeniu z innego powtórzenia mapy kosztował kolejne życia. Od R-08 między rysowaniami jest najwyżej 25 ticków, więc w teście z przestojami po 60 s gracz traci tylko jedno życie `[TEST]`.

### BUG-03 — Wyjątki w pętli są połykane

- **Status:** ✅ Naprawione w R-03. Opis poniżej dotyczy stanu z audytu. Teraz `logging.exception` drukuje pełny ślad stosu na stderr, a proces kończy się kodem 1 `[TEST]`. Normalne wyjście (`Esc`, zdarzenie zamknięcia okna) nadal daje kod 0 `[TEST]`.
- **Opis:** `except Exception` drukuje jedną linię, bez typu i śladu stosu. Proces kończy się kodem 0.
- **Waga:** Wysoka `[TEST]`
- **Pliki i metody:** `src/game.py:88-90`, `Game.run`
- **Skutki:** Crash wygląda jak normalne zamknięcie. Po spakowaniu z `console=False` nie zostanie żaden ślad.
- **Rozwiązanie:** `traceback.print_exc()` lub `logging.exception`, potem kod wyjścia różny od 0. Plik logu w wersji spakowanej.

### BUG-04 — Animacja ataku zwykle się nie odtwarza

- **Status:** ✅ Naprawione w R-09, zweryfikowane bez okna. Opis i skutki poniżej to stan z audytu. Licznik `attack_ticks` zeruje się przy starcie ataku, a przebieg i koniec ataku należą do `tick()`. Każda klatka trwa 5 ticków, a cały atak 45 ticków `[TEST]`.
- **Opis:** `animation_timer` rośnie stale i zeruje się dopiero na końcu ataku. Gdy minęło ≥ 0,45 s, atak trwa 1 tick i nic nie rysuje.
- **Waga:** Wysoka `[TEST]`
- **Pliki i metody:** `src/entities/player.py:104,165-179`
- **Skutki:** Przeciwnik ginie bez widocznego ciosu. Przy E po 0,2 s animacja zaczyna się od środka.
- **Rozwiązanie:** Zerować licznik przy starcie ataku, koniec ataku obsługiwać w `tick()`.

**Weryfikacja kodu przed R-09** `[TEST]` (1 rysowanie na tick, chyba że podano inaczej). Sprostowanie do audytu: brak animacji dotyczył tylko naciśnięcia kończącego się przed następnym tickiem po rysowaniu. Przy dłuższym naciśnięciu, czyli prawdopodobnie przy większości zwykłych `[ZAŁOŻENIE]`, animacja startowała od razu po pustym ataku. Pomiar dodał też brak postaci w ostatnim rysowaniu i zawieszenie ataku bez rysowania:

| Sytuacja | Przed R-09 | Po R-09 |
|---|---|---|
| E na 1 tick po dłuższej przerwie | Atak 1 tick, jedno rysowanie bez postaci, brak animacji | 45 ticków, klatki 0-8 po 5 ticków |
| E przez 2 ticki po dłuższej przerwie | Atak 1 tick i rysowanie bez postaci, a od razu po nim pełna animacja: razem 46 ticków | 45 ticków, klatki 0-8 po 5 ticków |
| Drugie E po 0,2 s | Atak od klatki 4 | Zignorowane, bo pierwszy atak trwa |
| E przytrzymane | Atak 1 tick, potem cykle 45 ticków z 1 rysowaniem bez postaci, czas klatek 4, 6, 4, 5... | Cykle 45 ticków bez przerwy, po 5 ticków na klatkę |
| Brak rysowania | Atak nie kończy się nigdy (sprawdzone na 1000 ticków) | Kończy się po 45 tickach |
| Rysowanie co 4 ticki | Koniec zależy od rysowania | Ten sam przebieg stanu w każdym ticku |

**Celowe zmiany zachowania:**

- Każdy atak trwa pełne 0,45 s, także pierwszy po przerwie, nawet przy bardzo krótkim naciśnięciu. Przez ten czas kolejne E jest ignorowane. Dawniej pierwszy atak kończył się po 1 ticku, więc można było znów sprawdzić trafienie zaraz po nim.
- Bardzo krótkie naciśnięcie pokazuje teraz atak zamiast biegu, a licznik biegu czeka przez cały atak.
- E przytrzymane sprawdza trafienie co 45 ticków. Dawniej robiło to też w drugim ticku.
- Postać nie znika w ostatnim rysowaniu ataku.
- Klatki trwają równo po 5 ticków. Nierówny czas wynikał z błędów zaokrąglenia licznika zmiennoprzecinkowego.

**Bez zmian:** kolejność klatek, obraz efektu, sterowanie, sprawdzanie trafienia tylko przy starcie ataku, brak wpływu ataku na ruch i skok, wstrzymanie licznika biegu. Pozycje i prędkości gracza oraz przeciwnika przez 1500 ticków są identyczne, a z 61 porównanych klatek różni się tylko ta, na której dawniej brakowało postaci `[TEST]`.

**Ograniczenia po R-09:**

- `Weapon.pos.x` nadal powstaje w `Weapon.draw()`, więc strefa trafienia zależy od ostatniego rysowania (BUG-20, R-22) `[KOD]`.
- Kierunek ataku nadal wynika ze znaku `vel.x` (BUG-17, R-22) `[KOD]`.
- Stara wartość `isCollision` może nadal dawać fałszywe trafienie (BUG-05, R-13) `[KOD]`.

### BUG-05 — Przestarzałe flagi kolizji powodują fałszywe reakcje

- **Opis:** `collision()` nie czyści `isCollision` przy pudle w osi Y, a `player_enemy_collision` nie czyści flag kierunkowych.
- **Waga:** Wysoka `[TEST]`
- **Pliki i metody:** `src/core/collision_manager.py:35-40,157-201,203-242`; `src/entities/player.py:96-100`
- **Skutki:**
    - Gracz na platformie P3 (ostatnia w pętli, `x` 1500-1800) jest odpychany przez przeciwnika idącego po ziemi pod nim, bez dotykania: 11 razy w 170 tickach. Na P1 i P2 w tym samym scenariuszu nie było żadnego zdarzenia, bo kolejna platforma czyści flagę pudłem w osi X.
    - Z P3 można zabić przeciwnika stojącego niżej. W teście strefa ataku miała `y` 439-539, a przeciwnik 591-641, czyli bez pokrycia, a przeciwnik zginął.
    - Flagi pozostawione przez `player_enemy_collision` trafiają do pierwszego sprawdzenia kafelka przeciwnika `[KOD]`. W teście kontaktu na podłożu nie zmieniło to jego ruchu: zawsze −1 px/tick.
- **Rozwiązanie:** Bezstanowa funkcja `overlaps(a, b) -> bool`, flagi jako zmienne lokalne lub zwracany wynik.

### BUG-06 — Reakcja na kolizję ignoruje kierunek ruchu

- **Opis:** O stronie decyduje tylko odległość krawędzi, a znak w `pos.y += vel.y + 5` jest błędny przy ruchu w górę.
- **Waga:** Wysoka `[TEST]`
- **Pliki i metody:** `src/core/collision_manager.py:54-68,81-100,126-145,172-191`
- **Skutki:** Skok pod niską platformą urywa się po ~62 px, a przytrzymanie spacji daje podwójny skok do ~250 px. Głowa wchodzi w platformę (`y = 442` przy platformie 430-460). Stojąc pod niską platformą, postać zapada się ok. 3 px w podłoże.
- **Rozwiązanie:** Rozdzielenie osi: najpierw ruch i korekta X, potem Y, z użyciem kierunku prędkości i dosunięciem do krawędzi. Osobne pole `on_ground`.

### BUG-07 — Brak limitu FPS i animacja biegu zależna od FPS

- **Status:** ✅ Naprawione w R-08, zweryfikowane tylko bez okna. Opis i skutki poniżej to stan z audytu. Rysowanie ma limit `FPS_MAX = 60`. `runCount` rośnie w `Player.tick()`, a `draw()` tylko go odczytuje, więc tempo biegu nie zależy od FPS `[TEST]`. Indeks klatki to `runCount // 5` przy `runCount` od 0 do 32, czyli zawsze 0-6, i wielokrotne rysowanie go nie zmienia, więc `IndexError` nie ma już przyczyny `[TEST]`.
- **Sprostowanie do skutków:** tick zostawiał licznik najwyżej na 19, a wyjątek powstawał przy `runCount = 30`, czyli przy 12. rysowaniu bez ticku. 11 rysowań wystarczało tylko przy sztucznym starcie z `runCount = 20` `[TEST]`.
- **Opis:** `runCount` rośnie w `draw`, a resetuje się w `tick`. `clock.tick()` jest bez limitu.
- **Waga:** Wysoka `[TEST]`, `[KOD]`
- **Pliki i metody:** `src/entities/player.py:133-134,154-162`, `src/game.py:81`
- **Skutki:** Tempo animacji zależy od sprzętu. Render zajmuje cały dostępny czas `[KOD]`, co przy prawdziwym oknie powinno oznaczać duże obciążenie rdzenia `[ZAŁOŻENIE]`. Przy ≥ 11 rysowaniach na tick (ok. 1100 FPS) pojawia się `IndexError`, potwierdzony przez 11 kolejnych `render()`. Przy ~63 FPS zmierzonych bez okna to nierealne, ale po optymalizacji ryzyko rośnie.
- **Rozwiązanie:** Liczniki animacji w `tick()`, `clock.tick(60)` lub vsync.

**Pomiar przed i po R-08** `[TEST]` (sterownik `dummy`, macOS, ten sam komputer, pętla `Game.run`). Wiersze o cyklu biegu porównują stan tuż przed przeniesieniem `runCount`, czyli już z limitem FPS:

| Scenariusz | Przed | Po |
|---|---|---|
| Pełny render, 10 s | 60,4 FPS, 100,0 TPS, 100% rdzenia | 60,6 FPS, 100,0 TPS, 100% rdzenia |
| Render bez rysowania, 5 s | ok. 818 000 FPS, 100,2 TPS, 100% rdzenia | 54,7 FPS, 100,1 TPS, 4,7% rdzenia |
| Przestój 3 s | 302 ticki przed następnym rysowaniem | 24 ticki przed następnym rysowaniem |
| 900 ticków ze skryptowym sterowaniem (bieg, skok, cios) | punkt odniesienia | Identyczne pozycje i prędkości gracza oraz przeciwnika w każdym ticku |
| Cykl biegu w pętli, ok. 61 FPS | 20 rysowań, 327 ms | 33 ticki, ok. 332 ms |
| Czas klatek biegu 0-6 | 3, 3, 3, 3, 3, 3, 2 rysowania | 5, 5, 5, 5, 5, 5, 3 ticki |

**Ograniczenia po R-08:**

- Pełny render zajmował wtedy ok. 16 ms, czyli prawie cały budżet klatki, więc sam limit nie obniżył użycia procesora bez okna. Spadek przyniosło dopiero R-32, opisane w [§2](#2-podsumowanie-pomiarów).
- Limit nie jest dokładny: przy pustym renderze zmierzono 54,7 FPS, a przy pełnym 60,6 FPS. Prędkość gry od tego nie zależy, bo logika ma stały krok `[TEST]`.
- Tempo biegu jest teraz stałe, więc wygląda jak dawniej tylko przy ok. 60 FPS. Przy 30 FPS dawny cykl trwałby ok. 0,67 s, a teraz trwa 0,33 s `[WYLICZONE]`.
- `RUN_FRAME_TICKS` i `RUN_CYCLE_TICKS` są w tickach, więc zmiana `TPS_MAX` zmieni tempo biegu `[KOD]`.

### BUG-08 — Kula ognia wywraca grę po włączeniu

- **Opis:** `Projectile.tick` ma warunek zerowania czasu nieosiągalny przez kolejność ticków, a `cooldown` wychodzi poza listę.
- **Waga:** Średnia dziś, bo kod jest nieosiągalny; krytyczna po włączeniu `[TEST]`
- **Pliki i metody:** `src/entities/projectile.py:40-42,60-63,73-75`, `src/entities/player.py:88-91`
- **Skutki:** `IndexError` przy strzale, jeśli od startu lub końca poprzedniego strzału minęło ≥ 10 s. Strzał przerywany przy `dt` 5-10 s, błędne klatki przy 2-5 s. Lewa strona używa nieodwróconych grafik (`sprite_manager.py:49`).
- **Rozwiązanie:** Licznik w tickach na instancji pocisku, odwrócone klatki, rysowanie tylko w `draw`.

### BUG-09 — Przeciwnik wpada w dziury i nie dochodzi do gracza

- **Opis:** Przeciwnik nie sprawdza krawędzi. Pierwszy spawn wpada w dziurę na `x ≈ 800`, zanim dojdzie do startu gracza.
- **Waga:** Średnia `[TEST]`
- **Pliki i metody:** `src/entities/enemy.py:39-74`
- **Skutki:** Gracz stojący przy starcie nigdy nie spotka przeciwnika, a cykl powtarza się co ok. 23 s. Dodatkowo przeciwnik pozostaje niewidoczny pod mapą przez długi czas.
- **Rozwiązanie:** Wykrywanie krawędzi i zawracanie, usuwanie po spadnięciu.

### BUG-10 — Kontakt z przeciwnikiem nie ma konsekwencji

- **Opis:** Gracz jest odpychany i unoszony, ale nie traci życia, którego zresztą nie ma.
- **Waga:** Średnia `[TEST]`
- **Pliki i metody:** `src/core/collision_manager.py:203-242`
- **Skutki:** Przeciwnik pcha gracza bez końca (cofanie o 10 px co 10 ticków). Walka nie stanowi wyzwania.
- **Rozwiązanie:** System życia, nietykalność po trafieniu, kontrolowany odrzut przez prędkość, a nie przez pozycję.

### BUG-11 — Tło kończy się na dłuższym dystansie

- **Opis:** Stała liczba kopii warstw, a mapa jest nieskończona.
- **Waga:** Średnia `[TEST]`
- **Pliki i metody:** `src/world/game_map.py:50-62`
- **Skutki:** Las kończy się przy `scroll.x ≈ 35 040` i `≈ −7 680`, a góry przy `≈ ±38 400`. Wszystkie cztery końce potwierdzono próbkowaniem warstwy tła tuż przed i tuż za granicą. Za końcem gór widać czarny obszar.
- **Rozwiązanie:** Rysowanie kopii liczone modulo względem przesunięcia.

### BUG-12 — Czytelność świata: dziury, platformy, kamienie

- **Opis:** W dziurze widać wzór z obrazu terenu zamiast pustki. Warstwa `7` rysuje się po platformach, więc dolne platformy są częściowo zakryte trawą. Kamień wygląda jak przeszkoda, ale nie ma kolizji.
- **Waga:** Średnia `[TEST]` (zrzut ekranu)
- **Pliki i metody:** `src/world/game_map.py:50-62,189-194`, `src/world/platform_manager.py`
- **Skutki:** Gracz nie widzi zagrożenia.
- **Rozwiązanie:** Prawdziwe kafelki z tilesetu zamiast obrazu przykładowego, zmiana kolejności warstw.

### BUG-13 — Ścieżki zależne od katalogu roboczego

- **Opis:** Muzyka korzysta z `BASE_DIR`, grafiki ze ścieżek względnych.
- **Waga:** Średnia `[TEST]`
- **Pliki i metody:** `src/ui/sprite_manager.py:23-52`, `config/settings.py:4,13`
- **Skutki:** `FileNotFoundError` poza `platformer_game/`, a pakowanie jest niemożliwe bez zmian.
- **Rozwiązanie:** Funkcja `asset_path()` oparta na `BASE_DIR`.

### BUG-14 — Niespójna grawitacja

- **Opis:** Gracz ma 0,7, a po pierwszym skoku na stałe 0,9. Osobne wartości w trzech klasach.
- **Waga:** Niska `[TEST]`
- **Pliki i metody:** `src/entities/player.py:23,68` (`Player.__init__`, `handle_jump`), `src/entities/enemy.py:14`, `src/core/physics_engine.py:7`
- **Skutki:** Spadek przed pierwszym skokiem jest wolniejszy: ~4,67 px/tick wobec ~6 px/tick po nim `[TEST]`.
- **Rozwiązanie:** Jedna stała w `settings.py`, po usunięciu przypisania.

### BUG-15 — Pętla `while` w skoku może zawiesić grę

- **Opis:** Wyjście z pętli w `handle_jump` wymaga `vel.y == 0`, a pętla nie zmienia `vel.y`.
- **Waga:** Niska dziś, bo wywołanie jest strzeżone warunkiem; zawieszenie przy innym wywołaniu `[KOD]`
- **Pliki i metody:** `src/entities/player.py:58-68`, `Player.handle_jump`
- **Skutki:** Całkowite zawieszenie gry przy wywołaniu z `vel.y != 0`, na przykład przy dodawaniu podwójnego skoku albo buforowania skoku.
- **Rozwiązanie:** Zamienić na jednorazowe `add_force` bez pętli.

### BUG-16 — Brak limitu nadrabiania ticków

- **Status:** ✅ Naprawione w R-08, zweryfikowane tylko bez okna. Opis i skutki poniżej to historia z audytu. `tps_delta` jest teraz ograniczane do `MAX_TICKS_PER_FRAME / TPS_MAX`, czyli 0,25 s, więc między dwoma rysowaniami wykona się najwyżej 25 ticków, a starszy czas przepada. Gra działa więc w czasie rzeczywistym przy co najmniej 4 FPS, a poniżej tej wartości zwalnia zamiast przeskakiwać. Ponieważ pomiar czasu jest teraz na końcu klatki, przed pierwszym rysowaniem nie ma żadnego ticku `[TEST]`. Czas w `Projectile` nadal pochodzi z `time.time()` i nie podlega temu limitowi, ale kula ognia jest nieosiągalna `[KOD]`.
- **Opis:** `while tps_delta > 1 / tps_max` nie ma górnej granicy.
- **Waga:** Niska `[KOD]`
- **Pliki i metody:** `src/game.py:81-84`
- **Skutki:** Po 60 s zatrzymania ok. 6000 ticków naraz, czyli ok. 0,5 s zamrożenia przy obecnym koszcie `[WYLICZONE]`. Świat „przeskakuje” o 60 s bez rysowania i odświeżania danych zależnych od renderu.
- **Rozwiązanie:** Ograniczyć `tps_delta`, np. do 0,25 s.
- **Uzupełnienie z R-02:** zegar startował przed wczytaniem zasobów, więc czas ładowania był nadrabiany przed pierwszym renderem, gdy nie ma jeszcze kolizji. Zwykle były to tylko 6 ticków, ale przy ładowaniu trwającym ok. 1 s lub dłużej gracz przelatywał przez podłoże `[TEST]`. Naprawiono to, wywołując `tps_clock.tick()` tuż przed pętlą: nawet przy 4 s opóźnienia przed pierwszym renderem nie ma już ticków `[TEST]`. Brak limitu nadrabiania w trakcie gry usunęło dopiero R-08.

### BUG-17 — Kierunek postaci wynika ze znaku prędkości

- **Opis:** Nie ma pola `facing`. Gałąź `vel.x == 0` w `player.py:142` jest praktycznie nieosiągalna (`-1.5e-323` po 6000 ticków). Bieg z `vel.x == 0` niczego by nie narysował.
- **Waga:** Niska `[TEST]`
- **Pliki i metody:** `src/entities/player.py:141-176`, `src/entities/weapon.py:26-31`
- **Skutki:** Działa przypadkiem, kruche przy zmianach tłumienia.
- **Rozwiązanie:** Pole `facing` ustawiane z wejścia.

### BUG-18 — Asymetria reakcji i strefy ataku

- **Opis:** Reakcja z lewej to `+vel.x + 4`, co przy ujemnej prędkości daje mniejsze odepchnięcie niż z prawej. Strefa ataku zaczyna się 10 px od gracza tylko po prawej.
- **Waga:** Niska `[TEST]`
- **Pliki i metody:** `src/core/collision_manager.py:87-100`, `src/entities/weapon.py:27-31`
- **Skutki:** Różne drgania przy ścianie (5,4 px i 2,8 px), różny zasięg w obu kierunkach. Przenikania przez ścianę w testach nie stwierdzono.
- **Rozwiązanie:** Reakcję naprawić razem z BUG-06, a strefę ataku ustawić symetrycznie względem środka gracza.

### BUG-19 — Martwe funkcje, które wywrócą grę po włączeniu

- **Opis:** `Menu.draw`: `AttributeError` (`imageMenuGrid1`). `GameMap.bird`: `AttributeError` (`shipImage`). `Menu.text_objects`: brak `self`, `TypeError`. `Menu.button`: niezdefiniowane `gameDisplay`. `Menu.grid_static`: niezdefiniowane `box` dla wartości `7`. `GameMap.background`: `update_checkpoint` zmienia indeks co wywołanie (−4 po 4 wywołaniach).
- **Waga:** Niska, nieosiągalne `[TEST]`, `[KOD]`
- **Pliki i metody:** `src/ui/menu.py:45-56,58-89`, `src/world/game_map.py:39-44,64-85`
- **Skutki:** Dziś brak wpływu na grę. Włączenie „gotowego” menu zakończy grę od razu, a kod myli przy czytaniu.
- **Rozwiązanie:** Usunąć i napisać menu od nowa na bazie scen.

### BUG-20 — Atak działa tylko w pierwszym ticku, a pozycja broni jest opóźniona

- **Opis:** `Weapon.pos.x` powstaje w `draw`, a strefa w `tick`, więc jest opóźniona o klatkę. Sprawdzenie odbywa się tylko raz na atak.
- **Waga:** Niska `[KOD]`
- **Pliki i metody:** `src/entities/weapon.py:17-31` (`Weapon.tick`, `Weapon.draw`), `src/entities/player.py:96-100` (`Player.handle_attack`)
- **Skutki:** Atak może nie trafić przeciwnika, który wejdzie w zasięg podczas animacji. Przy obracaniu się strefa może być po starej stronie.
- **Rozwiązanie:** Aktywne okno ataku w tickach, strefa liczona w `tick`.

### Problemy środowiska i repozytorium

| ID | Opis | Waga | Skutki | Rozwiązanie |
|---|---|---|---|---|
| ENV-01 | `Pipfile` wymaga Pythona 3.8, lock ma pygame 2.1.2 i numpy 1.22.1, a `venv` to 3.12.0, 2.5.2 i 1.26.2. `requirements.txt` jest pusty `[TEST]` | Wysoka | Brak możliwości odtworzenia środowiska. Zgodność locka z Pythonem 3.12 jest wątpliwa `[ZAŁOŻENIE]` | Jedno źródło zależności dla 3.12 |
| ENV-02 | `venv/pyvenv.cfg`: `include-system-site-packages = true`. Widoczne są też matplotlib, pillow itp. z bazowego Pythona `[TEST]` | Średnia | Mogą ukryć się brakujące zależności | Nowe izolowane środowisko |
| ENV-03 | numpy tylko do `zeros((10, 4))` w `platform_manager.py`, nadpisanego pola w `menu.py` i nieużywanego importu `[KOD]` | Niska | Większy plik wynikowy | Usunąć zależność |
| ENV-04 | Spec PyInstallera nieaktualny (szczegóły w §6) | Średnia | Budowa nie zadziała | Nowy spec |
| ENV-05 | `.gitignore` to szablon JavaScript, uzupełniony w ramach R-04 o reguły dla Pythona. 11 plików `.pyc` z 3.8 nadal jest śledzonych w git. `.idea` śledzone w dwóch miejscach mimo wpisu w ignorowanych `[TEST]` | Średnia | Nowe pliki `__pycache__` są już ignorowane, ale śledzone pliki zostają w repozytorium | Reguły dodane. Pozostaje `git rm --cached`, po decyzji autora |
| ENV-06 | Brak lintera, formatera, CI i `pyproject.toml`. Testy obejmują kody wyjścia procesu (`tests/test_shutdown.py`), `GameMap`, kolizje podłoża i lądowanie (`tests/test_game_map.py`) spadek i odrodzenie (`tests/test_player_respawn.py`) limity pętli gry (`tests/test_game_loop.py`), animację biegu (`tests/test_run_animation.py`), animację ataku (`tests/test_attack_animation.py`) oraz konwersję grafik (`tests/test_surface_conversion.py`), ale parametrów biegu i skoku ani samej walki już nie `[KOD]` | Wysoka | Każda zmiana ryzykuje regresję | pytest, ruff, GitHub Actions |
| ENV-07 | README na `dev` linkuje do nieistniejącego GIF-a. `dev` jest 4 commity za `main`, a `working` jest przestarzały `[TEST]` | Niska | Bałagan w gałęziach | Zmergować `main` do `dev`, ocenić `working` |
| ENV-08 | Licencja: `license.txt` nie określa zakresu. Brak informacji o postaciach, muzyce, czcionce i brak licencji samego kodu `[NIEZWERYFIKOWANE]` | Średnia, wysoka przy publikacji | Ryzyko prawne przy dystrybucji | Spis źródeł, wymiana niepewnych zasobów, plik `LICENSE` |
| ENV-09 | Zasoby bez rozszerzeń, nieużywane i zduplikowane (§3) | Niska | Większe repozytorium i paczka | Porządki po potwierdzeniu |

## 6. Środowisko i uruchamianie

| Pytanie | Odpowiedź |
|---|---|
| Wersja Pythona w `venv` | 3.12.0 z asdf `[TEST]` |
| Zależności w `venv` | numpy 1.26.2, pygame 2.5.2 `[TEST]` |
| Czy deklaracje są kompletne i spójne | Nie (ENV-01) |
| Poprawne uruchomienie | `cd platformer_game && ../venv/bin/python -m src.main` `[TEST]` |
| Brakujące narzędzia | Testy, linter, formater, typowanie, CI, wersjonowanie paczek |

### Ocena `src/main.spec`

| Element | Problem |
|---|---|
| `pathex=['/home/dvn/PycharmProjects/platformer_game']` | Sztywna ścieżka z innego komputera `[KOD]` |
| `Analysis(['main.py'])` z `src/` | Skrypt importuje `src.game`, więc `platformer_game/` musi być na ścieżce. Bez poprawnego `pathex` analiza nie znajdzie pakietu `[ZAŁOŻENIE]` |
| `datas=[]` | Brak zasobów w paczce `[KOD]` |
| `console=False` | `Game.run` wypisuje błędy na stderr, więc bez konsoli i bez pliku logu pozostaną niewidoczne `[ZAŁOŻENIE]` |
| `upx=True` | UPX nie jest zainstalowany `[TEST]`; efekt przy budowie nie był sprawdzany |
| `block_cipher`, `cipher`, `win_*` | Parametry ze starych wersji PyInstallera, nowsze wersje mogą je odrzucać `[ZAŁOŻENIE]` |

### Możliwość zbudowania pliku wykonywalnego

Jest wykonalna, ale nie została przetestowana, bo PyInstaller nie jest zainstalowany, a audyt nie instaluje zależności. Pozytywne sygnały: pygame ma własny hook PyInstallera (`pygame/__pyinstaller/hook-pygame.py`, wpis `pyinstaller40` w metadanych) `[TEST]`, kod jest czystym Pythonem.

Warunki wstępne: ścieżki przez `BASE_DIR` (BUG-13), zasoby w `datas`, `pathex` względem spec, widoczne błędy (BUG-03), budowa osobno na każdym systemie. PyInstaller nie buduje krzyżowo, a macOS może wymagać podpisania aplikacji `[ZAŁOŻENIE]`.

## 7. Sprawdzenie zapisów z `CLAUDE.md`

Tabela pokazuje wynik sprawdzenia pierwotnej wersji `CLAUDE.md`. Prawie wszystkie jej zapisy były prawdziwe. Pozycje oznaczone 🟡 poprawiono już później w samym `CLAUDE.md`.

| Zapis | Wynik |
|---|---|
| Uruchamianie jako moduł z `platformer_game/` | ✅ Potwierdzone `[TEST]` |
| Test bez okna przez sterowniki `dummy` | ✅ Potwierdzone `[TEST]` |
| `venv`: Python 3.12, pygame 2.5.2; `Pipfile`: 3.8; pusty `requirements.txt` | ✅ `[TEST]` |
| Brak testów, lintera i aktualnego speca | ✅ `[KOD]` |
| `Game` to service locator, po jednej encji | ✅ `[KOD]` |
| Kolejność inicjalizacji | ✅ `[KOD]` |
| Pętla: stałe 100 TPS, render bez limitu | ✅ `[TEST]` |
| Geometria kolizji powstaje w rysowaniu | ✅ `[KOD]` |
| `set_scroll` z listą obiektów | ✅ `[KOD]` |
| Prostokąty `(x0, x1, y0, y1)` | ✅ `[KOD]` |
| Stan w `CollisionManager`, przestarzały `isCollision` | ✅ Potwierdzone, skutek zmierzony (BUG-05) `[TEST]` |
| Powtarzanie mapy, kafelki 80 px, `1` i `7` | ✅, doprecyzowanie: `7` rysuje cały obraz 1280×720 `[KOD]` |
| Podwójne `grid()` | ✅ `[KOD]` |
| `Menu.draw` wywraca grę przez `imageMenuGrid1`, `gameDisplay`, `randomcolor` | 🟡 Pierwszy błąd to `imageMenuGrid1`. Pozostałe są na ścieżkach nieosiąganych przed tym błędem `[TEST]` |
| `bird()` używa `shipImage` | ✅ `[TEST]` |
| `got_weapon` nigdy nie jest `True` | ✅ `[KOD]` |
| `Player.state` nieużywane | ✅ `[TEST]` |
| `get_image` odtwarza cache | ✅ `[KOD]` |
| `SpriteManager` używa `image.load` dla „większości” grafik | 🟡 W rzeczywistości dla **wszystkich**. `AssetLoader` nie jest w ogóle wywoływany `[TEST]` |
| `WIDTH`/`HEIGHT` nieużywane, trzy wartości grawitacji | ✅, dodatkowo gracz przejmuje 0,9 po pierwszym skoku `[TEST]` |
| `Game.run` łapie wyjątki i drukuje jedną linię | ✅, dodatkowo kod wyjścia to 0 `[TEST]` |
| `__pycache__` poza `.gitignore`, śledzone stare `.pyc` | ✅ 11 plików `[TEST]` |
| Polskie komentarze | ✅ `[KOD]` |

`CLAUDE.md` opisuje już także naprawiony wyciek `GRID_position`, konwersję powierzchni z R-32, `venv` z dostępem do pakietów systemowych, dziury z odrodzeniem po R-02 oraz zmianę grawitacji po pierwszym skoku.

## 8. Ocena ogólna

Oceny opisują stan z audytu (commit `2d51b48`) i nie były zmieniane po R-03, R-01 ani R-02. Uzasadnienia wspominające o połykaniu wyjątków, wycieku, soft-locku lub braku testów dotyczą tego stanu.

| Obszar | Ocena | Uzasadnienie |
|---|---|---|
| Architektura | **3/10** | Czytelny podział katalogów i stały krok logiki. Ale service locator, logika zależna od rysowania, brak scen i encji oraz cykle zależności. |
| Jakość kodu | **3/10** | Kod jest krótki i prosty do odczytania, ale ma 4 kopie reakcji na kolizję, podwójne metody, 14% komentarzy ze starym kodem, magiczne liczby, mylące nazwy i brak testów. |
| Rozgrywka | **3/10** | Ruch, skok, lądowanie, kamera i cios działają. Brakuje celu, życia, przegranej i AI, jest soft-lock przy pierwszej dziurze, a animacja ciosu rzadko się pojawia. |
| Wydajność | **4/10** | W pomiarach bez okna logika jest bardzo tania (0,084 ms), a render zajmuje 15,8 ms przez brak konwersji, co daje się łatwo poprawić 6,6×. Odejmują punkty: brak limitu FPS i wyciek zależny od klatek. |
| Stabilność | **3/10** | W testach bez okna normalne sterowanie nie wywołało crasha, ale długiej sesji w prawdziwym oknie nie sprawdzono. Ale wyciek rośnie bez ograniczeń, jest soft-lock, wyjątki są połykane, a ukryte ścieżki kończą się `IndexError`. |
| Łatwość utrzymania | **3/10** | Zmiana rysowania może zmienić fizykę, ukryty stan sprawia, że kolejność wywołań ma znaczenie, brak jakichkolwiek testów regresji. Pomaga mały rozmiar. |
| Potencjał rozwoju | **6/10** | Mały kod (~1430 linii), proste zależności, grafiki i muzyka już są, a pygame w zupełności wystarcza. Dużą część problemów naprawia się etapami. Potrzebna jest najpierw przebudowa fundamentów. |

## 9. Lista kontrolna ryzyk

| Kategoria | Elementy |
|---|---|
| Wycieki pamięci | BUG-01, jedyny stwierdzony, naprawiony w R-01. Osobna lista `Menu.GRID_position` nie rośnie podczas gry, bo menu nie jest wywoływane. Tymczasowe powierzchnie w `transform.scale` są zwalniane: pośrednio potwierdza to stałe RSS przez 5 minut bez okna `[TEST]` |
| Wąskie gardła | Rysowanie poza ekranem (5 × 1280×720, 28 × 300×720), 800 nieużywanych `Rect` na klatkę |
| Crash | kula ognia (BUG-08), martwe funkcje (BUG-19), brak pliku grafiki (ślad stosu, kod 1) `[TEST]` |
| Zawieszenie | `handle_jump` (BUG-15). Nadrabianie (BUG-16) ma limit od R-08 |
| Soft-lock | Dziura (BUG-02) naprawiona w R-02, innych nie stwierdzono |
| Nieoczekiwane zakończenie | Każdy wyjątek w pętli kończy grę, ale od R-03 ze śladem stosu i kodem 1 (BUG-03, naprawione) |
| Niespójności | Grawitacja, ścieżki, trzy modele świata, dwa loadery, dwa miejsca `WIDTH`/`HEIGHT` |

## 10. Powiązanie z planem rozwoju

Każde ustalenie ma zadanie w [ROADMAP.md](ROADMAP.md). Waga opisuje skutek problemu, a priorytet kolejność prac, dlatego mogą się różnić. Dotyczy to zwłaszcza warunków wstępnych dla innych zadań, jak R-03 i R-06, oraz brakujących podstaw rozgrywki, jak R-20 i R-21. Zadania dla `ARCH-xx` podaje tabela w §4.

| Ustalenie | Waga | Zadanie | Priorytet zadania |
|---|---|---|---|
| BUG-01 (naprawione) | Krytyczna | R-01 (wykonane) | Krytyczny |
| BUG-02 (naprawione) | Krytyczna | R-02 (wykonane), później R-20 | Krytyczny, Wysoki |
| BUG-03 (naprawione) | Wysoka | R-03 (wykonane) | Krytyczny |
| BUG-04 (naprawione) | Wysoka | R-09 (wykonane) | Wysoki |
| BUG-05, BUG-06 | Wysoka | R-13 | Wysoki |
| BUG-07 (naprawione) | Wysoka | R-08 (wykonane) | Wysoki |
| BUG-08 | Średnia | R-25 | Średni |
| BUG-09 | Średnia | R-21 | Wysoki |
| BUG-10 | Średnia | R-20 | Wysoki |
| BUG-11 | Średnia | R-14 | Wysoki |
| BUG-12 | Średnia | R-14, R-24 | Wysoki, Średni |
| BUG-13 | Średnia | R-06 | Wysoki |
| BUG-14, BUG-15 | Niska | R-11 | Średni |
| BUG-16 (naprawione) | Niska | R-08 (wykonane) | Wysoki |
| BUG-17, BUG-20 | Niska | R-22 | Średni |
| BUG-18 | Niska | R-13, R-22 | Wysoki, Średni |
| BUG-19 | Niska | R-10, R-29 | Średni |
| ENV-01, ENV-02 | Wysoka, Średnia | R-05 | Wysoki |
| ENV-03 | Niska | R-10 | Średni |
| ENV-04 | Średnia | R-37 | Średni |
| ENV-05 | Średnia | R-04 | Wysoki |
| ENV-06 | Wysoka | R-07, R-38 | Wysoki, Średni |
| ENV-07 | Niska | R-04, R-39 | Wysoki, Niski |
| ENV-08 | Średnia, wysoka przy publikacji | R-36 | Wysoki przed publikacją |
| ENV-09 | Niska | R-35 | Średni |
| Brak konwersji powierzchni (§2, naprawione) | Wysoka dla wydajności | R-32 (wykonane) | Wysoki |
| Rysowanie poza ekranem, nieużywane `Rect` (§9) | Niska | R-33 | Średni |
| Duże pliki, ostrzeżenia iCCP (§3) | Niska | R-34 | Niski |
| Rozproszone ładowanie i animacje (§3) | Średnia | R-19 | Średni |

Kolejność napraw i plan prac są w [ROADMAP.md](ROADMAP.md).

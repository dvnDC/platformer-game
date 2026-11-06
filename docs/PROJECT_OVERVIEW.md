# Przegląd projektu

> Stan na: 2026-11-06, gałąź `dev`, HEAD `9fb1337` („Fix R-01”, ale zawiera R-03). Kod i zasoby przeanalizowano w commicie `2d51b48` („Changing the structure of the application”, 2024-08-28), a `ec06314` dodał tylko `CLAUDE.md` i `docs/`. R-01 jest na razie tylko w katalogu roboczym.
> Dokument opisuje to, co faktycznie jest w kodzie. Szczegóły: [ARCHITECTURE.md](ARCHITECTURE.md), [GAMEPLAY.md](GAMEPLAY.md), [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md), [ROADMAP.md](ROADMAP.md).

## Oznaczenia wiarygodności

We wszystkich dokumentach stosowane są te same znaczniki:

| Znacznik | Znaczenie |
|---|---|
| `[KOD]` | Potwierdzone bezpośrednio przez czytanie kodu. |
| `[TEST]` | Potwierdzone eksperymentem bez okna (sterowniki `dummy`, sterowanie wstrzyknięte w pamięci). |
| `[WYLICZONE]` | Wynika z obliczeń lub ekstrapolacji pomiaru, nie zmierzone wprost. |
| `[ZAŁOŻENIE]` | Wniosek logiczny lub wiedza ogólna, niesprawdzone w tym projekcie. |
| `[NIEZWERYFIKOWANE]` | Nie dało się tego sprawdzić w ramach audytu. |

**Czego audyt nie sprawdził:** gry w prawdziwym oknie, prawdziwej klawiatury, realnego dźwięku, działania na Windows i Linux, budowania pliku wykonywalnego (PyInstaller nie jest zainstalowany). Liczby wydajnościowe pochodzą z jednego komputera (macOS) i sterownika `dummy`, więc pokazują proporcje, a nie gwarantowany FPS.

## Czym jest ta gra

Dwuwymiarowa platformówka z przewijaniem w poziomie, napisana w Pythonie i pygame. Gracz steruje rycerzem, który biega po powtarzającym się w nieskończoność terenie, skacze na platformy i uderza mieczem nadchodzącego przeciwnika. Tytuł okna to „dvn's game” (`src/game.py:19`).

Grywalny jest na razie tylko **prototyp ruchu i walki**. Gra nie ma celu, punktacji, życia, przegranej, wygranej ani menu `[KOD]`. Jedyny stan porażki to wpadnięcie w dziurę, po którym postać spada bez końca, a gry w praktyce nie da się kontynuować bez ponownego uruchomienia `[TEST]`. Rzadki, przypadkowy wyjątek opisuje [GAMEPLAY.md](GAMEPLAY.md#dziury).

W stanie początkowym ekran wygląda tak: rycerz stoi na trawie, nad nim są czerwonawe platformy, w tle parallaksa z gór i lasu, a w lewym górnym rogu licznik FPS.

## Technologie

| Element | Wersja w działającym `venv/` | Zadeklarowane | Uwagi |
|---|---|---|---|
| Python | 3.12.0 (asdf) | 3.8 (`Pipfile`, `Pipfile.lock`) | Rozbieżność |
| pygame | 2.5.2 | `*` (`Pipfile`), 2.1.2 (`Pipfile.lock`) | Rozbieżność |
| numpy | 1.26.2 | `*` (`Pipfile`), 1.22.1 (`Pipfile.lock`) | Realnie potrzebne tylko do jednego `zeros(...)` |
| `requirements.txt` | — | pusty plik | Nieprzydatny |
| Testy | `unittest` (biblioteka standardowa) | brak | Kody wyjścia procesu (`tests/test_shutdown.py`) oraz `GameMap`, kolizje podłoża i lądowanie (`tests/test_game_map.py`). Większość rozgrywki nie ma testów |
| Linter, CI | brak | brak | |
| PyInstaller | niezainstalowany | `src/main.spec` nieaktualny | Patrz [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md) |

Kod liczy około 1430 linii Pythona w 21 plikach. Z tego 205 linii (14%) to same komentarze, głównie wyłączony stary kod `[TEST]` (analiza AST).

## Jak uruchomić

Grę trzeba uruchamiać jako moduł z katalogu `platformer_game/`:

```bash
cd platformer_game
../venv/bin/python -m src.main
```

Ten wariant działa `[TEST]`. Pozostałe warianty zawodzą `[TEST]`:

| Polecenie | Wynik |
|---|---|
| `python src/main.py` (z `platformer_game/`) | `ModuleNotFoundError: No module named 'src'` |
| `python -m platformer_game.src.main` (z katalogu głównego repozytorium) | `ModuleNotFoundError: No module named 'src'` |
| `PYTHONPATH=platformer_game python -m src.main` (z katalogu głównego) | `FileNotFoundError` dla pierwszego obrazka, bo ścieżki grafik są względne |

Sterowanie: `A`/`D` ruch, `Spacja` skok, `E` atak mieczem, `Esc` wyjście. Klawisz `R` (kula ognia) jest w kodzie, ale nieosiągalny, bo gracz nigdy nie dostaje broni.

Uruchomienie bez okna, na przykład do szybkiego testu:

```bash
cd platformer_game
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m src.main
```

Pętla działa do przerwania, więc proces trzeba zakończyć ręcznie.

## Stan implementacji

| Obszar | Stan | Komentarz |
|---|---|---|
| Ruch poziomy | ✅ Działa | Przyspieszenie i tłumienie, przewidywalny `[TEST]` |
| Skok i grawitacja | 🟡 Częściowo | Działa, ale grawitacja zmienia się po pierwszym skoku, a pod niskimi platformami skok się urywa i można wykonać podwójny skok `[TEST]` |
| Kolizje z podłożem i platformami | 🟡 Częściowo | Lądowanie działa, reakcja od dołu i z boku ma błędy `[TEST]` |
| Kamera pozioma i parallaksa | 🟡 Częściowo | Działa, ale tło kończy się po przebyciu dłuższego dystansu `[TEST]` |
| Nieskończona mapa | 🟡 Częściowo | Podłoże i dziury się powtarzają, platformy występują tylko raz `[TEST]` |
| Atak mieczem | 🟡 Częściowo | Trafienie działa, animacja zwykle się nie odtwarza `[TEST]` |
| Przeciwnik | 🟡 Częściowo | Idzie w lewo, grawitacja i odrodzenie działają. Brak AI i animacji, wpada w dziury `[TEST]` |
| Muzyka | ✅ Działa w kodzie | Zapętlony utwór, realnego dźwięku nie sprawdzono `[NIEZWERYFIKOWANE]` |
| Licznik FPS | ✅ Działa | Jedyny element interfejsu `[KOD]` |
| Kula ognia | ❌ Nieosiągalna | Po włączeniu strzał wywraca grę, jeśli od startu lub poprzedniego strzału minęło co najmniej 10 s `[TEST]` |
| Menu | ❌ Zepsute | Wywołanie kończy się `AttributeError` `[TEST]` |
| Podnoszenie broni | ❌ Brak | Grafika jest ładowana, logiki nie ma `[KOD]` |
| Życie, obrażenia, śmierć, wynik | ❌ Brak | `[KOD]` |
| Prawdziwe checkpointy, poziomy, cel gry | ❌ Brak | `player_checkpoint` to tylko indeks przesunięcia mapy `[KOD]` |
| Stany gry, pauza, ekran końca | ❌ Brak | `[KOD]` |

## Struktura projektu

```text
platformer-game/
├── README.md                 Krótki opis i animowany podgląd
├── Pipfile, Pipfile.lock     Nieaktualne deklaracje zależności (Python 3.8)
├── preview.gif               Podgląd używany przez README na gałęzi main (3,9 MB)
├── CLAUDE.md                 Notatki techniczne dla asystenta
├── docs/                     Ta dokumentacja
├── tests/                    Testy kodów wyjścia i mapy (test_shutdown.py, test_game_map.py)
├── venv/                     Działające środowisko (ignorowane przez własny .gitignore)
├── .idea/                    Ustawienia PyCharm (śledzone mimo wpisu w .gitignore)
└── platformer_game/          Katalog roboczy gry
    ├── requirements.txt      Pusty
    ├── config/settings.py    Rozdzielczość, muzyka, liczba ticków na sekundę
    ├── assets/
    │   ├── fonts/            FreeSansBold.ttf (nieużywana)
    │   ├── sounds/           latenight.ogg (muzyka)
    │   └── images/           Postacie, efekty, tła, kafelki
    ├── __pycache__/          11 starych plików .pyc z Pythona 3.8, śledzonych w git
    ├── .idea/                Drugi zestaw ustawień PyCharm
    └── src/
        ├── main.py           Punkt wejścia
        ├── main.spec         Nieaktualna konfiguracja PyInstallera
        ├── game.py           Klasa Game: inicjalizacja, pętla, update, render
        ├── core/
        │   ├── asset_loader.py        Nieużywany loader z zepsutym cache
        │   ├── collision_manager.py   Testy i reakcja na kolizje
        │   ├── game_engine.py         Czcionki i licznik FPS
        │   └── physics_engine.py      Kamera i rozsyłanie przewinięcia
        ├── entities/
        │   ├── player.py              Sterowanie, fizyka, animacje gracza
        │   ├── player_state.py        Nieużywana klasa stanu
        │   ├── enemy.py               Przeciwnik
        │   ├── projectile.py          Kula ognia (nieosiągalna)
        │   └── weapon.py              Pozycja strefy ataku mieczem
        ├── ui/
        │   ├── sprite_manager.py      Ładowanie grafik
        │   └── menu.py                Zepsute, wyłączone menu
        └── world/
            ├── game_map.py            Siatka kafelków, tło, kamienie
            └── platform_manager.py    Trzy stałe platformy
```

## Zasoby w skrócie

`assets/` zajmuje 9 MB, z czego muzyka 3,9 MB. Z 59 plików PNG część nie jest wczytywana albo jest wczytywana i nieużywana. Dodatkowo dwa pliki (`objects/stone`, `spaceship`) to obrazy PNG bez rozszerzenia, a `Stand/`, `Run/` i `Attack1H/` zawierają zduplikowane klatki. Pełna tabela jest w [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md#3-grafika-i-zasoby).

Licencja: `assets/images/license.txt` mówi o CC0 i autorze Luisie Zuno (ansimuz), ale nie wskazuje, których plików to dotyczy. Pochodzenia pozostałych zasobów, w tym muzyki, nie da się potwierdzić na podstawie repozytorium `[NIEZWERYFIKOWANE]`. Ma to znaczenie przed publiczną dystrybucją.

## Stan repozytorium

- W commitach `dev` i `main` zawierają ten sam kod. `main` ma 4 commity, których nie ma `dev`, w tym merge'e, a `dev` ma 1 commit, którego nie ma `main` (`ec06314`, jeszcze niewypchnięty na `origin/dev`). Różnice w plikach to link do GIF-a w `README.md` oraz `CLAUDE.md` i `docs/`, obecne tylko na `dev`.
- README na `dev` wskazuje plik `Screen Recording 2023-06-05...gif`, którego nie ma w repozytorium. Na `main` link prowadzi do `preview.gif`.
- Gałąź `working` ma 2 commity, których nie ma w `dev`, i jest 18 commitów za `dev`.
- Niezapisane w commitach: implementacja R-01 (`src/world/game_map.py`, `tests/test_game_map.py`), związane z nią zmiany w `CLAUDE.md` i `docs/` oraz katalogi `__pycache__`. R-03 jest już w commicie `9fb1337`, mimo że jego tytuł brzmi „Fix R-01”. Kodu R-01 ten commit nie zawiera.
- Historia sięga 2020-08-17 i liczy 75 commitów na gałęzi `dev`. Ostatni commit kodu pochodzi z 2024-08-28.

## Najważniejsze wnioski

1. Podstawowa pętla gry działa i wygląda przyzwoicie, ale jest prototypem.
2. Natychmiastowej naprawy wymaga **brak wyjścia z dziury**, do której można wpaść w niecałą sekundę od wylądowania. Wyciek pamięci rzędu 10 MB/s (pomiar bez okna) w `GameMap.grid()` usunięto w R-01: RSS utrzymało się na ok. 93,4 MB przez 5 minut bez okna, przy stojącym graczu. W prawdziwym oknie jeszcze tego nie sprawdzono.
3. Logika jest splątana z rysowaniem, a kolizje mają ukryty stan. To największe przeszkody w rozbudowie, więc trzeba je usunąć przed dodawaniem funkcji.
4. Projekt jest mały, dlatego naprawa etapami jest realna i nie wymaga przepisywania wszystkiego od zera. Kolejność prac jest w [ROADMAP.md](ROADMAP.md).

## Od czego zacząć po dłuższej przerwie

1. Przeczytaj tabelę stanu powyżej.
2. Uruchom grę i przejdź po mapie, omijając dziurę na współrzędnej `x = 800`, czyli około 160 px w prawo od startu.
3. Przeczytaj `src/game.py` (109 linii), bo pokazuje cały przepływ.
4. W [ARCHITECTURE.md](ARCHITECTURE.md) zajrzyj do sekcji o ukrytych zależnościach, zanim cokolwiek zmienisz.
5. Wybierz następne zadanie z [ROADMAP.md](ROADMAP.md).

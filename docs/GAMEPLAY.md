# Mechaniki rozgrywki

> Opis zachowania gry na podstawie kodu (commit `2d51b48`, uzupełniony o R-02) i eksperymentów bez okna. Klawisze były podstawiane programowo, więc **odczucia z prawdziwego sterowania nie zostały ocenione** `[NIEZWERYFIKOWANE]`. Znaczniki objaśnia [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md).
>
> Jednostki: logika działa w 100 tickach na sekundę. 1 tick = 10 ms. Prędkości podane są w px/tick (mnożąc przez 100, dostajemy px/s).

## Podsumowanie stanu mechanik

| Mechanika | Stan | Główne ograniczenie |
|---|---|---|
| Ruch A/D | ✅ Działa | Brak klawiszy strzałek |
| Skok | 🟡 Częściowo | Podwójny skok pod niskimi platformami, urwany wznos |
| Grawitacja | 🟡 Częściowo | Zmienia wartość po pierwszym skoku |
| Lądowanie na podłożu i platformach | ✅ Działa | Nieregularna odległość od podłoża, kilka pikseli |
| Uderzenie głową i boki przeszkód | 🟡 Częściowo | Postać wchodzi w platformę, drży przy ścianie |
| Dziury | ✅ Działa | Spadek kosztuje życie i cofa na start. Potwierdzone też ręcznie w prawdziwym oknie |
| Kamera pozioma | ✅ Działa | Tło kończy się po długim biegu |
| Kamera pionowa | ❌ Brak efektu | Wartość liczona, nieużywana |
| Atak mieczem: trafienie | ✅ Działa | Sprawdzane tylko w pierwszym ticku |
| Atak mieczem: animacja | ✅ Działa | Pełna animacja przy każdym ataku (R-09). Nie sprawdzono w prawdziwym oknie |
| Przeciwnik | 🟡 Częściowo | Brak AI i animacji, wpada w dziury |
| Odepchnięcie przez przeciwnika | 🟡 Częściowo | Brak obrażeń, na platformie P3 działa też bez dotyku |
| Kula ognia | ❌ Nieosiągalna | Crash po włączeniu |
| Podnoszenie broni | ❌ Brak | |
| Życie, śmierć, wynik, cel gry | 🟡 Częściowo | Tylko niewidoczny licznik żyć przy spadku. Brak śmierci, wyniku i celu |
| Menu, pauza, ekran końca | ❌ Brak lub zepsute | |

## Sterowanie

Obsługa w `Player.handle_input` (`src/entities/player.py:70-94`) oraz `Game.run`.

| Klawisz | Działanie | Szczegóły |
|---|---|---|
| `A` | Bieg w lewo | Ma pierwszeństwo przed `D`, gdy oba są wciśnięte |
| `D` | Bieg w prawo | |
| `Spacja` | Skok | Tylko gdy `vel.y == 0`. Przytrzymanie daje ciągłe skakanie `[TEST]` |
| `E` | Atak mieczem | Nie blokuje ruchu |
| `R` | Kula ognia | Wymaga `got_weapon == True`, co nigdy nie zachodzi `[KOD]` |
| `Esc` | Wyjście | Natychmiast, bez potwierdzenia |
| Zamknięcie okna | Wyjście | |

Nie ma obsługi strzałek, gamepada ani zmiany klawiszy.

## Fizyka gracza

Parametry z `Player.__init__`:

| Parametr | Wartość | Uwagi |
|---|---|---|
| Hitbox | 20 × 60 px | Sprite ma 160 × 160 px |
| Start | `x = 640`, `y = 170` | Spada na podłoże, lądowanie po ~0,9 s `[TEST]` |
| Siła biegu | 0,55 na tick | |
| Tłumienie | `vel *= 0.85` na tick | Dotyczy też osi Y |
| Grawitacja | 0,7, potem 0,9 | Po pierwszym skoku na stałe bierze wartość z `PhysicsEngine` |
| Impuls skoku | −35 | |

Kolejność kroku (`player.py:112-117`):

```text
vel *= 0.85
vel.y += gravity
vel += acc        # bieg lub skok
pos += vel
acc = 0
```

Wynikające wartości:

| Wielkość | Wartość | Źródło |
|---|---|---|
| Maksymalna prędkość biegu | 0,55 / 0,15 ≈ 3,67 px/tick (~367 px/s) | `[WYLICZONE]`, zmierzono 3,67 `[TEST]` |
| Prędkość początkowa skoku | −34,1 px/tick | `[TEST]` |
| Wysokość skoku | 157 px | `[TEST]` |
| Czas lotu | ~45 ticków (0,45 s) | `[TEST]` |
| Zasięg skoku w biegu, od bezruchu | ~156 px | `[TEST]` |
| Prędkość graniczna spadania | ~4,67 px/tick przed pierwszym skokiem (grawitacja 0,7), ~6 px/tick po nim (grawitacja 0,9) | `[WYLICZONE]`, potwierdzone pomiarem `[TEST]` |

### Warunek skoku

Skok jest możliwy, gdy `vel.y == 0` dokładnie. Reakcja na kolizję od dołu ustawia zero, więc warunek działa jak „stoję na czymś”.

Niezamierzony skutek to **podwójny skok pod niskimi platformami**. Gdy gracz skacze pod platformą `y = 550`, jego stopy w trakcie wznoszenia trafiają w margines górnej krawędzi platformy. Kod uznaje to za lądowanie, zeruje `vel.y` w powietrzu i pozwala skoczyć ponownie. Pojedynczy skok urywa się po ~62 px. Z przytrzymaną spacją postać wznosi się na ~250 px, a nie zwykłe 157 px `[TEST]`.

`Player.handle_jump` zawiera pętlę `while self.isJump`, która kończy się tylko przy `vel.y == 0`. Obecnie warunek w `handle_input` gwarantuje to przed wywołaniem, ale wywołanie z innego miejsca zawiesiłoby grę `[KOD]`.

## Kolizje

Dokładny algorytm jest w [ARCHITECTURE.md](ARCHITECTURE.md#7-potok-kolizji). Z perspektywy rozgrywki:

| Sytuacja | Zachowanie | Źródło |
|---|---|---|
| Stanie na podłożu | Stabilne, `vel.y == 0` przez 1000 ze 1000 ticków po ustabilizowaniu | `[TEST]` |
| Lądowanie | Cofnięcie ostatniego kroku, postać może zatrzymać się do ok. 4 px nad podłożem i po chwili opaść | `[TEST]` |
| Stanie na platformie | Stabilne, `y ≈ 489-490` na niskiej platformie | `[TEST]` |
| Stanie pod niską platformą (y 550-580) | Postać jest przesunięta ~3 px w dół (`y = 582,97` zamiast ok. 580), bo głowa dotyka platformy | `[TEST]` |
| Uderzenie głową w wysoką platformę | Postać zostaje wypchnięta w górę, głową w środek platformy (`y = 442` przy platformie 430-460), potem spada | `[TEST]` |
| Ściana z prawej | Blokuje, drgania ok. 5,4 px | `[TEST]`, sztuczna ściana w pamięci |
| Ściana z lewej | Blokuje, drgania ok. 2,8 px, reakcja asymetryczna | `[TEST]`, sztuczna ściana w pamięci |
| Bok platformy | Odbicie i spadek, co może skończyć się dziurą | `[TEST]` |

Mapa nie ma obecnie żadnych ścian z kafelków, dlatego test ścian wymagał tymczasowego kafelka w pamięci.

## Mapa

Siatka ma 10 wierszy i 80 kolumn, a kafelek 80 × 80 px (`GameMap.initialize_grid`).

| Wartość | Znaczenie | Kolizja |
|---|---|---|
| `0` | Pusto | Nie |
| `1` | Kafelek ziemi (`grid1.png`) | Tak |
| `7` | Rysuje cały obraz `country-platform-tiles-example.png` 1280×720, od tej pozycji | Nie |

Wiersze i ich zawartość:

- Wiersz 0: wartość `7` w kolumnach 0, 16, 32, 48, 64, co daje jeden obraz co 1280 px. To z niego pochodzą trawa, ścieżka i drzewo.
- Wiersz 8 (`y` = 640-720): podłoże, z przerwami w kolumnach 27 i 42.
- Wiersz 9 (`y` = 720-800): dwa kafelki w kolumnach 53-54, poniżej krawędzi ekranu. Z dziur nie da się do nich dotrzeć, więc w praktyce nie mają znaczenia `[WYLICZONE]`.

### Mapa świata

Przekrój dla `player_checkpoint = 0`, z zachowaniem współrzędnych światowych, ale nie skali:

```text
 y
430                                             [ P2: 1150-1450 ]
550                             [ P1: 800-1100 ]                  [ P3: 1500-1800 ]
640  ████████ ░░ ██████████████ ░░ ████████████████████████████████████████████
              ▲         ▲       ▲
    dziura -400..-320   │     dziura 800..880
                   start x = 640
```

- Podłoże powtarza się z okresem 3840 px. Dziury są w `x = -400 + 3840·k` i `x = 800 + 3840·k`, czyli na przykład 3440 i 4640 dla `k = 1` `[TEST]`.
- Platformy to stałe współrzędne światowe. **Występują tylko raz**, w okolicy startu `[KOD]`. Na prawo od ~1800 px są tylko podłoże, dziury i dekoracje.
- Kamienie są dekoracją bez kolizji i rysują się w `x = 3840·k` oraz `x = 3840·k + 1280`.

### `player_checkpoint` to nie checkpoint

To tylko indeks przesunięcia siatki. Zmienia się przy przekraczaniu `x = 2560 + 3840·k`. Nie zapisuje postępu i nie jest punktem odrodzenia (odrodzenie tylko je zeruje). Przejście przez granicę nie zmienia podłoża pod nogami ani obrazu mapy `[TEST]`, a kolejna dziura pojawia się na 3440.

### Dziury

Dziury to najważniejsza mechanika wymagająca decyzji projektowej:

- Pierwsza prawa dziura znajduje się 160 px od startu. **Bieg w prawo od startu kończy się spadkiem już po 0,84 s** `[TEST]`.
- Nad nią wisi platforma P1. Wyskok z `x` około 700-780 w prawo prowadzi na platformę. Wcześniejszy wyskok (z 560-680) kończy się spadkiem do dziury, bo postać uderza w lewy bok P1 i opada `[TEST]`.
- Dziury dalej w świecie nie mają platform nad sobą. Startując z bezruchu, da się je przeskoczyć, odbijając się w ostatnich 80 px przed krawędzią `[TEST]`.
- **Spadek kończy się odrodzeniem (R-02).** Gdy `y` przekroczy 800 (`FALL_LIMIT_Y`), czyli gdy hitbox jest już poniżej wszystkich kafelków, gracz traci jedno życie i wraca na start `(640, 170)`, a kamera od razu wraca do niego. Zerują się prędkość, bieg i atak, a grawitacja zostaje taka, jaka była `[TEST]`. Gracz ma 3 życia (`PLAYER_LIVES`), których nie widać na ekranie. Przy 0 żyć nadal się odradza, bo gra nie ma przegranej `[TEST]`. Spacja przytrzymana w chwili odrodzenia daje skok w powietrzu, tak jak na starcie gry `[TEST]`. Przeciwnik nie jest przenoszony, więc po spadku daleko od startu wraca dopiero po pewnym czasie (54 s przy `x = 4670`) `[TEST]`. Autor potwierdził działanie odrodzenia ręcznie w prawdziwym oknie gry uruchomionej z PyCharm.
- **Rzadki, przypadkowy wyjątek (pomiar sprzed R-02).** Jeśli przeciwnik wpada do tej samej dziury razem z graczem, kontakt z nim może na chwilę wyzerować `vel.y`, a przytrzymana spacja pozwala wtedy wyskoczyć. Przy naturalnym dojściu do dziury wróciło tak 3 z 320 prób ze spacją, wszystkie po pierwszym skoku (grawitacja 0,9). Bez spacji powrotu nie było. Przy sztucznie ustawionym kontakcie od głębokości `y ≥ 760` skok nie wystarczał do powrotu. To skutek uboczny reakcji na kolizję, a nie mechanizm wyjścia. Przegląd czasów nie był wyczerpujący `[TEST]`.
- Dziura nie wygląda jak dziura. W tym miejscu widać dolną część obrazu terenu, czyli wzór przypominający roślinność `[TEST]` (zrzut ekranu).

Sprawdzono, że dalszy marsz po mapie jest możliwy: P1 → P2 → zejście na P3 → podłoże, aż do `x ≈ 2640` i dalej `[TEST]`.

## Kamera i tło

- Kamera pozioma dąży do `x_gracza − 640`, doganiając o 1/40 różnicy na tick. W biegu postać wyprzedza środek ekranu o ok. 150 px `[WYLICZONE]`.
- Kamera pionowa jest liczona, ale nieużywana. Skok nie przesuwa widoku, a to, co jest poniżej 720 px, jest niewidoczne.
- Parallaksa: góry 1/30 przesunięcia, las 1/6.
- Tło ma skończoną liczbę kopii `[KOD]`, a efekt potwierdzono `[TEST]`:

| Warstwa | Koniec w prawo | Koniec w lewo |
|---|---|---|
| Las | `scroll.x ≈ 35 040` | `scroll.x ≈ −7 680` |
| Góry | `scroll.x ≈ 38 400`, dalej czarne tło | `scroll.x ≈ −38 400` |

Przy ciągłym biegu odpowiada to ok. 95 s w prawo i ok. 21 s w lewo do końca lasu `[WYLICZONE]`.

## Animacje gracza

Sprite gracza ma 160 × 160 px i jest rysowany z przesunięciem `(-70, -70)` względem `pos`. Widoczna sylwetka to mniej więcej `x − 20 .. x + 44` oraz `y − 30 .. y + 66` `[TEST]`, a hitbox to `x .. x + 20` i `y .. y + 60`. Wizualnie jest to dobrze dopasowane, ale szerokość sprite'a jest większa od hitboxu.

| Stan | Klatki w plikach | Realnie używane | Zachowanie |
|---|---|---|---|
| Bezczynność | 10 (`Stand/`) | 1 | Brak animacji, tylko klatka 0 |
| Bieg | 10 (`Run/`) | 7 (indeksy 0-6) `[TEST]` | Licznik rośnie co tick: 5 ticków na klatkę, ostatnia 3, więc tempo nie zależy od FPS |
| Atak | 10 (`Attack1H/`) | 9 (indeksy 0-8) | 5 ticków na klatkę, czyli 20 klatek/s, na podstawie `attack_ticks` |
| Skok lub spadanie | Brak | Brak | Pokazuje bieg albo bezczynność |

Cykl biegu trwa 33 ticki, czyli 0,33 s, niezależnie od FPS `[TEST]`. Do R-08 licznik rósł co rysowanie, a podobne tempo dawało ok. 60 FPS `[TEST]`. Licznik rośnie tylko podczas biegu bez ataku i zeruje się po puszczeniu klawisza `[KOD]`. Indeks klatki nie wychodzi poza 0-6 `[TEST]`. Prędkość ruchu nie zależy od FPS, bo logika ma stały krok `[TEST]`.

## Atak mieczem

- Strefa ataku ma 100 × 100 px. Z prawej: `x + 30 .. x + 130`, z lewej: `x − 100 .. x`. Pionowo `y − 50 .. y + 50` (`weapon.py`). Po prawej jest więc 10 px przerwy między hitboxem gracza a strefą, a po lewej jej nie ma.
- Trafienie sprawdzane jest raz, w chwili naciśnięcia. Dalsza część animacji nie zadaje obrażeń `[KOD]`.
- Atak do przodu zabija, atak za plecami nie `[TEST]`.
- Trafienie to natychmiastowe odrodzenie przeciwnika 1280 px w prawo od gracza, na `y = 100`. Nie ma punktów ani animacji śmierci `[TEST]`.

**Czas ataku (od R-09).** Atak trwa 45 ticków, czyli 0,45 s. Klatki 0-8 postaci i efektu zmieniają się co 5 ticków `[TEST]`. Przebieg i koniec ataku należą do `tick()`, więc nie zależą od rysowania, a atak kończy się także wtedy, gdy nic nie jest rysowane `[TEST]`.

| Sytuacja | Zachowanie |
|---|---|
| Pojedyncze E, także po długiej przerwie | Pełna animacja, 45 ticków |
| E podczas ataku | Zignorowane, bez kolejkowania |
| E w ticku, w którym atak się kończy | Nowy atak od klatki 0 |
| E przytrzymane | Kolejne ataki co 45 ticków, bez przerwy |

Atak nie zmienia ruchu ani skoku i działa też w powietrzu. Podczas ataku licznik biegu czeka, a po ataku wraca `[TEST]`.

Ponieważ `collision()` zachowuje poprzednią wartość przy pudle w osi Y, atak wykonany z platformy P3 może zabić przeciwnika stojącego niżej. W teście strefa ataku miała `y` 439-539, a przeciwnik 591-641, więc nie pokrywały się w pionie, a przeciwnik zginął `[TEST]`.

## Przeciwnik

Parametry: hitbox 50 × 50 px, start `(1400, 100)`, prędkość `−1` px/tick (100 px/s), grawitacja 0,9.

| Aspekt | Zachowanie | Źródło |
|---|---|---|
| Ruch | Stały w lewo, bez reakcji na gracza | `[KOD]` |
| AI | Brak: nie patroluje, nie goni, nie zawraca | `[KOD]` |
| Animacja | Tylko klatka 0 z 10, klatki odwrócone nieużywane | `[KOD]` |
| Kolizje | Tylko kafelki. Przechodzi przez platformy | `[KOD]` |
| Obrażenia | Nie zadaje | `[KOD]` |
| Odrodzenie | Po śmierci lub gdy jest ponad 1000 px za graczem: `(x_gracza + 1280, 100)` | `[TEST]` |

**Przeciwnik nie dochodzi do gracza stojącego na starcie.** Idąc od `x = 1400`, wpada w dziurę na `x ≈ 800-830` około ticku 600. Dalej spada pod mapą, wciąż przesuwając się w lewo. Gdy znajdzie się 1000 px za graczem (tick 1760), odradza się na `x = 1921`, i cykl się powtarza co ok. 23 s. Najbliższa odległość pozioma to ok. 190 px `[TEST]`.

### Kontakt z graczem

`player_enemy_collision` reaguje tylko na gracza:

| Sytuacja | Efekt | Źródło |
|---|---|---|
| Przeciwnik dochodzi z boku na podłożu | Co 10 ticków gracz cofa się o 10 px i unosi o 8 px. Przeciwnik pcha go stale, bez obrażeń | `[TEST]` |
| Gracz spada na przeciwnika | Gracz może na nim stać, dopóki przeciwnik nie odejdzie. Nie ma „zdeptania” | `[TEST]` |
| Gracz na P3, przeciwnik na ziemi pod nim | **Niezamierzone odepchnięcie bez kontaktu**, 11 razy w 170 tickach. Na P1 i P2 w tym samym scenariuszu nie występuje | `[TEST]` |

## Kula ognia (nieosiągalna)

Żaden kod nie ustawia `got_weapon = True`, a grafika `weaponPickupImage` jest tylko wczytywana `[KOD]`. Żeby ocenić mechanikę, w teście ustawiono tę flagę w pamięci.

| Aspekt | Wynik | Źródło |
|---|---|---|
| Lot | 8 px/tick, poziomo, na wysokości gracza | `[TEST]` |
| Trafienie | Zabija przeciwnika, jeśli pocisk jest w `−50..+50` w poziomie i `−20..+60` w pionie względem jego pozycji | `[TEST]` |
| Kolizja z mapą | Brak | `[KOD]` |
| Liczba pocisków | Jeden, do 5 s | `[KOD]` |
| Lewy kierunek | Używa tych samych, nieodwróconych grafik | `[TEST]` |
| **Crash** | Strzał co najmniej 10 s po starcie lub po poprzednim strzale: `IndexError` | `[TEST]` |

Przyczyna crasha: `time0` powinno zerować się przy strzale, ale warunek w `Projectile.tick` jest fałszywy, bo `Player.tick` wykonany wcześniej ustawił już `weapon.fire = True`. Dlatego `dt` liczy czas od importu modułu albo od końca poprzedniego strzału, a `cooldown = int(dt) − 4` wychodzi poza listę 6 klatek.

| Wartość `dt` podczas lotu | Zachowanie |
|---|---|
| < 2 s | Kolejne klatki 0-5 `[WYLICZONE]` |
| 2-4 s | Ujemne indeksy, pokazuje klatki od końca `[WYLICZONE]` |
| 4-5 s | Stale klatka 0 `[WYLICZONE]` |
| 5-10 s | Strzał kończy się po pierwszym rysowaniu `[TEST]` |
| ≥ 10 s | Crash `[TEST]` |

## Punkty, postęp, stany gry

| Element | Stan |
|---|---|
| Punkty | Brak. `Enemy.counter` rośnie przy odrodzeniu, ale nikt go nie czyta |
| Życie gracza i obrażenia | Tylko `Player.lives`, zmniejszane przy spadku. Przeciwnik nie zadaje obrażeń |
| Śmierć i restart | Brak. Spadek daje odrodzenie na starcie także przy 0 żyć |
| Prawdziwe checkpointy | Brak |
| Koniec poziomu i wygrana | Brak |
| Menu główne | Klasa istnieje, `draw()` wyłączone. Po włączeniu: `AttributeError: imageMenuGrid1` `[TEST]` |
| Pauza | Brak |
| HUD | Tylko licznik FPS |

## Dźwięk

Jeden utwór, `assets/sounds/latenight.ogg`, zapętlony przy głośności 0,20. Brak efektów dźwiękowych. Błąd braku pliku muzyki jest obsłużony: gra drukuje komunikat i działa dalej `[KOD]`. Sam błąd ładowania potwierdzono jako `pygame.error` `[TEST]`. Realnego odtwarzania nie sprawdzano `[NIEZWERYFIKOWANE]`.

## Co dziś jest rzeczywistą pętlą rozgrywki

1. Gracz pojawia się w powietrzu i spada na podłoże.
2. Omija dziurę, wskakując na platformy, albo w nią wpada, co kosztuje życie i cofa go na start.
3. Biegnie w prawo, przeskakując dziury co 1200 i 2640 px na zmianę.
4. Spotyka przeciwnika, który go odpycha, i może go zabić jednym ciosem, a przeciwnik zaraz pojawia się znowu z prawej strony.
5. Gra nigdy się nie kończy sama, nie zapisuje wyniku i nie daje nagrody.

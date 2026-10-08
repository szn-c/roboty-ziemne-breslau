# Postęp prac (dziennik) – aktualizuj po każdym etapie

## Stan ogólny
- [x] Założenia bilansu uporządkowane: `USTALENIA.md`.
- [x] Repo zoptymalizowane przez użytkownika; mapa dokumentów i fakty z usuniętych plików: `prace/MAPA_DOKUMENTOW.md`, `prace/FAKTY_Z_USUNIETYCH_DOKUMENTOW.md`.
- [x] Zasady pracy z obrazami: `prace/OBRAZY_LIMIT_2000PX.md`.
- [x] T0: ścieżki dokumentów (`prace/MAPA_DOKUMENTOW.md`).
- [x] T1: wyciąg z dokumentacji → `prace/ekstrakt_dokumentacji.md`.
- [x] T2: weryfikacja ustaleń → `prace/WERYFIKACJA_raport.md`.
- [x] T3: odpowiedzi użytkownika (2 rundy pytań) zapisane w `USTALENIA.md` pkt 11–23 (i w `.kiro/steering/ustalenia.md`).
- [x] T4–T8: dane, strefy z wektorowego PZT, grunty przydatne, obliczenia A i B, arkusz Excel, podkład DXF v3, `wyniki/CZYTAJ_NAJPIERW.md`.
- [ ] Brak otwartych pytań – czekam na uwagi użytkownika do wyniku.

## Sesja 7.10.2026 (wieczór) – dokumentacja i weryfikacja
- Repo: `main` (35ad073) → gałąź `weryfikacja-dokumentacji`. `USTALENIA.md` = `.kiro/steering/ustalenia.md` (różni się tylko nagłówek). Obrazy w sesji: **1** (wycinek PZT, mało czytelny – dalej tylko analiza liczbowa).
- Przeczytane teksty: DGI (cały), karty 5.1–5.28, przekroje 6.1–6.12, tabela 8, mapy 4.x, PG, OG, PZT, przekroje terenowe, PW_*, F; z historii gita: ekstrakty rzutu zabezpieczenia i przekroju B-B.
- Odzyskane z gita do `prace/_odzyskane/` (w `.gitignore`): wektorowy PZT, PW_1A, mapa 4.3.
- Skrypty w `prace/weryfikacja/`:
  - `odczyt_kart_otworow.py` → `karty_otworow_odczyt.json` (profile 28 otworów wg położenia słów),
  - `geometria_kontrola.py` (pola, odległości, otwory w działce),
  - `pzt_raster_kontrola.py` (krzyże siatki na rastrze PZT),
  - `pzt_wektor_hale.py`, `pzt_wektor_hale_dopasowanie.py`, `pzt_wektor_granica_scianka.py`, `transformacja_uzytk_do_PZT.py` (porównanie z wektorowym PZT; wynik `transformacja_uzytk_do_PZT.json`),
  - `scianka_warianty_zamkniecia.json` (warianty a/b/c domknięcia ścianki).
- Główne wnioski (szczegóły w raporcie): pliki `*_checked` pomniejszone o 0,37% (po korekcie granica 25 289,84 m², hale 12 167,36 m²); odcinek zamykający ściankę przecina hale 7 i 8; dno 121,86 potwierdzone; 143 pogrubienia płyt (ok. 640 m³) + doły do 120,00; zieleń na stropie 3 975,11 (literówka w PZT); nasyp 5/17/20; otwór 12 E ≈ 6 433 688,2; brak w dokumentach: przestrzeni roboczej, skarp, spulchnienia, gęstości gleby i nasypu.

## Sesja 8.10.2026 – odpowiedzi użytkownika (T3) i obliczenia
- Odpowiedzi: (1) sprawdzić `siatka_10m_dz190_checked_v2.dxf` i użyć, jeśli OK (wolno skorygować i oddać nowy podkład DXF); (2) od południa brak ścianki – wykop ze skarpą 1:1,5; (3) dno 121,86 + fundamenty głębsze osobno; (4) przestrzeń robocza 1,0 m i skarpa 1:1,5 – tak; (5) zieleń – wszystkie grunty rodzime poza glebą i nasypem; nawierzchnie – przemarzanie 1,00 m, w strefie przemarzania grunt dowożony; (6) gęstości z tabeli 8, gleba 1,60, nasyp 1,80, spulchnienie jako pola informacyjne; (7a) zieleń na stropie sprawdzić na DXF v2; (7b–d) tak; tylko otwory 2–24 + CPTU 10, 12, 18, 21, 24.
- Kontrola v2 (`prace/weryfikacja/kontrola_dxf_v2.py`, `pzt_strefy_wektor.py`, `pzt_strefy_widoczne.py`): **hale, granica i ścianka w v2 są identyczne jak w v1 (różnice < 1 mm) – nie są poprawione**; zieleń na gruncie (23 polilinie) 6 264,04 m² (zawiera ok. 229 m² ogrodów deszczowych, brakuje ok. 358 m² zieleni z PZT); zieleń na stropie (38 polilinii) 3 572,61 m², brakuje ok. 369 m² (PZT: **3 979,48 m²** → potwierdza 3 975,11). Strefy biorę z wypełnień wektorowego PZT. Na PZT są 4 pochylnie (5 × 25 m) i zadaszone dojazdy poza obrysami hal (zieleń na stropie poza halami 396 m²). Obrazy w sesji: 2 (schemat stref – `_cache/schemat_strefy.png`).

- Fundamenty głębsze (`fundamenty_glebsze.py`, PW_* odzyskane do `prace/_odzyskane/`, obrazy 3–4: wycinki PW_1A): pogrubienia 3,40×4,40 (gr. 80 cm, d.k. −4,34, obrys skosu +0,50 m), w 2C także 4,40×6,54 (×6) i 2 szt. d.k. −4,54, w 4B/8B 4,40×6,59 (×2); rdzenie 7,48×8,57 (2C: 8,57×9,48) d.k. −4,34 z szybem windy d.k. −4,93; studzienki PF: d.k. −6,00 (2,00×3,00), −5,83 (1,80×1,455), −5,40 (1,50×1,80; tylko 1A, 4B, 6A, 8B).
- CPTU 10, 12, 18, 21, 24 odczytane (`odczyt_cptu.py` → `cptu_odczyt.json`). Nasyp z mapy 4.3 (`mapa43_nasyp.py`): strefy 759,3 m² (otw. 17, 20) i 350,3 m² (otw. 5).
- Wiaty (wypełnienie (152,152,152), 144,00 m² ≈ 143,15 z Bilansu) – to nie ściany pochylni. Pochylnie: 4 × 5,0×25,0 m (kreskowanie), z murami ok. 550 m² (Bilans 553,77).

- [x] T4: dane w `prace/dane/` (`prace/obliczenia_v2/dane.py`): geometria po korekcie do PZT, strefy z PZT wektorowego, 17 otworów + 5 CPTU, nasyp z mapy 4.3, teren (PZT + otwory), projekt (PZT).
- [x] T5–T7: silnik `prace/obliczenia_v2/silnik.py` (raster 0,25 m) → `wyniki.json`; wrażliwość `niepewnosc.py` → `niepewnosc.json`. Wyniki bazowe: humus 15 274 m³, nasyp 259 m³; wykop gruntu rodzimego A 33 899 m³, B 45 125 m³ (w tym spod hal 27 063 m³ – wywóz); fundamenty głębsze 1 294 m³; deficyt gruntu do zasypu ok. 11 735 m³ (A i B); grunt niewysadzinowy (strefa przemarzania) 2 660 m³.
- [x] T8: arkusz `wyniki/BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx` (`prace/obliczenia_v2/arkusz.py`: 156 formuł z zapisanymi wartościami; kontrola niezależna `kontrola_arkusza.py`: 36 pozycji, różnica 0,000 m³; kontrole bilansu = 0), podkład `wyniki/PODKLAD_dz190_v3.dxf` (`podklad_dxf.py`, audyt DXF bez błędów), `wyniki/CZYTAJ_NAJPIERW.md`. Obrazy w sesji: 5 (schematy stref i wykopów, 2 wycinki PW_1A).
- [x] Odpowiedzi na 5 pytań z `wyniki/CZYTAJ_NAJPIERW.md` – patrz sesja niżej.
- Odtworzenie wyników: `cd prace/obliczenia_v2 && python dane.py && python silnik.py && python niepewnosc.py && python arkusz.py && python podklad_dxf.py` (wymaga `prace/_odzyskane/` – skrypty w `prace/weryfikacja/` same odzyskują PZT z gita; PW_* i 4.3 – komenda w `prace/MAPA_DOKUMENTOW.md`).

## Sesja – trzecia runda odpowiedzi (ustalenia 18–23)
- Odpowiedzi: grunt spod hal przydatny → do zasypu; rampy i zadaszone dojazdy jak garaż – tak; ogrody deszczowe 0,30 m substratu; wymiana w strefie przemarzania pod drogą/chodnikiem/parkingiem; podnóże skarpy w B – zostaje; rozbieżność v2 (0,37%) i zieleń na stropie z PZT – OK. Pytanie użytkownika: jak liczony jest wariant A (załącznik „BILANS_ROBOT_ZIEMNYCH_wczesniej” przyszedł jako nieczytelne dane binarne, nie ma go w repo).
- Silnik: `wymiana_mrozu` (strefa U w obrysach `ciagi_pieszo_jezdne`, `ciagi_piesze`, `plac_uslugowy`, `geokrata_na_gruncie` – wykop do zp − 1,00 m, 471,81 m², 77,070 m³), `substrat_ogrod` = 0,30, cały wykop dostępny do zasypu, wykop A = najniższa z powierzchni dołów (hale 121,86 i rampy z własnym spodem). Rozkład wariantu A krok po kroku → `rozklad_wariantu_A.json` i arkusz WARIANT_A (poprzedni arkusz v1 „A (skarpy 1:1,5)” 29 234,555 m³ → 1d nowe dane 30 733,696 → dno 121,86 32 549,392 → wymiana 32 626,461 → południe otwarte 32 970,669 → zadaszone dojazdy 34 071,578 → rampy 34 264,887).
- Arkusz: nowe zakładki WARIANT_A, warunki wbudowania w GRUNTY; odwołania „ustalenie NN”; sumy w ROUND; licznik formuł poprawiony (160 komórek z formułą i wartością; wcześniej liczone podwójnie). Kontrole = 0, kontrola niezależna 36 pozycji, różnica 0,000.
- Wynik (A / B): wykop rodzimy 34 264,887 / 45 202,425 m³ (cały na odkład); ponowne wbudowanie 19 260,539 / 30 198,076; **wywóz razem 30 060,323 / 30 060,324 m³** (55 926,115 / 55 974,728 t); **dowóz 2 735,129 / 2 735,130 m³** (tylko grunt niewysadzinowy). Informacyjnie (poza ścianką, nie kopiemy): 24,015 m³ humusu w gruncie, 14,964 m³ w strefie przemarzania innych nawierzchni, 0,079 m³ konstrukcji.
- DXF v3: nowe warstwy `BILANS_WYMIANA_PRZEMARZANIE_A`/`_B`; opis dna A z rampami; audyt bez błędów.
- Obrazy w sesji: 0 nowych (łącznie 5/15).

## Uwagi
- Rzędne w warstwach DXF użytkownika są stare i wstępne – teren brać z tekstu PZT i otworów.
- Poprzednie wyniki (`prace/obliczenia_v1/`) obowiązywały przy innych założeniach.
- Strefy (T5) brać z wektorowego PZT (`prace/_odzyskane/PZT_wektorowy.pdf`) – legenda: obrys garażu (0,42; 0,04; 0,30) 0,85 pt; zieleń na gruncie – kreskowanie (0,22; 0,45; 0,18) 0,14 pt; transformacja strony PZT → PL-2000 jak w `wyciagnij_dane_z_pdf.py` (sprawdzona).

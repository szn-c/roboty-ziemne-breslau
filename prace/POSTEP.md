# Postęp prac (dziennik) – aktualizuj po każdym etapie

## Stan ogólny
- [x] Założenia bilansu uporządkowane: `USTALENIA.md`.
- [x] Repo zoptymalizowane przez użytkownika; mapa dokumentów i fakty z usuniętych plików: `prace/MAPA_DOKUMENTOW.md`, `prace/FAKTY_Z_USUNIETYCH_DOKUMENTOW.md`.
- [x] Zasady pracy z obrazami: `prace/OBRAZY_LIMIT_2000PX.md`.
- [x] T0: ścieżki dokumentów (`prace/MAPA_DOKUMENTOW.md`).
- [x] T1: wyciąg z dokumentacji → `prace/ekstrakt_dokumentacji.md`.
- [x] T2: weryfikacja ustaleń → `prace/WERYFIKACJA_raport.md`.
- [ ] **T3: czekam na odpowiedzi użytkownika (7 pytań w raporcie, sekcja 8).** Po odpowiedziach: zapisać decyzje w `USTALENIA.md` (i w `.kiro/steering/ustalenia.md`).
- [ ] T4–T8: dane (otwory, geometria po decyzji o korekcie), strefy z wektorowego PZT, grunty przydatne, obliczenia A i B, arkusz Excel (0,00 m², 0,000 m³), raport.

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
- [ ] T8: arkusz Excel `wyniki/BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx` (`prace/obliczenia_v2/arkusz.py`), podkład DXF `wyniki/PODKLAD_dz190_v3.dxf`, `wyniki/CZYTAJ_NAJPIERW.md`.

## Uwagi
- Rzędne w warstwach DXF użytkownika są stare i wstępne – teren brać z tekstu PZT i otworów.
- Poprzednie wyniki (`prace/obliczenia_v1/`) obowiązywały przy innych założeniach.
- Strefy (T5) brać z wektorowego PZT (`prace/_odzyskane/PZT_wektorowy.pdf`) – legenda: obrys garażu (0,42; 0,04; 0,30) 0,85 pt; zieleń na gruncie – kreskowanie (0,22; 0,45; 0,18) 0,14 pt; transformacja strony PZT → PL-2000 jak w `wyciagnij_dane_z_pdf.py` (sprawdzona).

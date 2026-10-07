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

## Uwagi
- Rzędne w warstwach DXF użytkownika są stare i wstępne – teren brać z tekstu PZT i otworów.
- Poprzednie wyniki (`prace/obliczenia_v1/`) obowiązywały przy innych założeniach.
- Strefy (T5) brać z wektorowego PZT (`prace/_odzyskane/PZT_wektorowy.pdf`) – legenda: obrys garażu (0,42; 0,04; 0,30) 0,85 pt; zieleń na gruncie – kreskowanie (0,22; 0,45; 0,18) 0,14 pt; transformacja strony PZT → PL-2000 jak w `wyciagnij_dane_z_pdf.py` (sprawdzona).

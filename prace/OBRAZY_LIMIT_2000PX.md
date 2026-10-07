# Limit 2000 px dla obrazów – dlaczego sesja się blokuje i jak tego uniknąć

## Co się stało
Błąd **„At least one of the image dimensions exceed max allowed size for many-image requests: 2000 pixels"** pochodzi z API modelu. Gdy w jednym żądaniu jest **więcej niż 20 obrazów**, każdy obraz musi mieć **najwyżej 2000 px na każdym boku** (przy 20 obrazach lub mniej limit wynosi 8000 px). Sesja wysyła całą historię przy każdej wiadomości, więc po obejrzeniu ok. 20 obrazów **jeden stary, duży obraz blokuje każdą następną wiadomość**. Historii nie da się naprawić – trzeba zacząć nową sesję (albo spróbować `/compact`, które usuwa stare obrazy z kontekstu).

## Dlaczego w tym repo tak łatwo o ten błąd
Duże rysunki mają strony rzędu 1700–4300 pt, a 1 pt to 1 px przy zoomie 1. Typowe „zoom 2" na PZT daje **8503 × 5181 px**. Część dokumentów to skany bez tekstu (mapa do celów projektowych, decyzja PRG), więc trzeba je oglądać. Do tego kart otworów jest 28, przekrojów 12, stron CPTU 40 – łatwo przekroczyć 20 obrazów.

## Zasady
1. **Najpierw tekst**: `prace/ekstrakty_tekstu/`, `wyciagnij_tekst_dokumentow.py`, dane wektorowe (PyMuPDF `get_cdrawings`). Obraz tylko wtedy, gdy tekstu/wektorów brak.
2. **Obrazy renderuj wyłącznie** skryptem `prace/obliczenia_v1/_skrypt/renderuj_pdf.py` (dłuższy bok 1500 px, nie przekroczy 2000 px). Nie wywołuj `get_pixmap(matrix=Matrix(2,2))` na dużych stronach.
3. **Przed wczytaniem dowolnego obrazu** sprawdź rozmiar: `python renderuj_pdf.py --sprawdz obraz.png`. Nie wczytuj obrazów > 1500 px.
4. Duży rysunek **tnij na wycinki** (`--wycinek` lub `--kafelki 3x2`) i oglądaj tylko potrzebne. Nie oglądaj dwa razy tego samego.
5. **Nie więcej niż ok. 15 obrazów w sesji.** Gdy zbliżasz się do limitu, zapisz postęp w `prace/POSTEP.md` i zaproponuj użytkownikowi nową sesję.
6. Po każdym etapie **zapisuj postęp do repo** (`prace/POSTEP.md`), żeby zablokowana sesja nie kosztowała pracy.

## Duże dokumenty w repo (rozmiar strony w pt = px przy zoomie 1)
Kolumna „bezpieczny zoom" daje dłuższy bok 1500 px. Dla skanów (bez tekstu) obraz jest jedyną drogą – oglądaj wycinkami.

| Dokument | Stron | Największa strona [pt] | Największy osadzony obraz [px] | Znaków tekstu | Bezpieczny zoom |
|---|---:|---:|---:|---:|---:|
| 6. PZT.pdf | 1 | 4252 | 202 | 39575 | 0.35 |
| 8. Przekroje terenowe z naniesionym średnim poziomem wody gruntowej.pdf | 1 | 4252 | 202 | 24858 | 0.35 |
| 1. MDCP.pdf | 1 | 3376 | 9379 | 0 | 0.44 |
| PW_1A-K-01_Rzut fundamentów .pdf | 1 | 2891 | 0 | 3226 | 0.52 |
| PW_3A-K-01_Rzut fundamentów .pdf | 1 | 2891 | 0 | 3126 | 0.52 |
| PW_4B-K-01_Rzut fundamentów.pdf | 1 | 2891 | 0 | 3293 | 0.52 |
| PW_5A-K-01_Rzut fundamentów .pdf | 1 | 2891 | 0 | 3124 | 0.52 |
| PW_6A-K-01_Rzut fundamentów .pdf | 1 | 2891 | 0 | 3306 | 0.52 |
| PW_7A-K-01_Rzut fundamentów .pdf | 1 | 2891 | 0 | 3126 | 0.52 |
| PW_8B-K-01_Rzut fundamentów .pdf | 1 | 2891 | 0 | 3295 | 0.52 |
| 7. PZT GARAŻE.pdf | 1 | 2835 | 204 | 21712 | 0.53 |
| PW_2C-K-01_Rzut fundamentów .pdf | 1 | 2324 | 0 | 2959 | 0.65 |
| 2. OPINIA GEOTECHNICZA_DBPG Wrocław ul. Lutosławskiego 1_90.pdf | 26 | 1191 | 4605 | 37372 | 1.26 |
| 4.1 Mapa sytuacyjno-wysokościowa.pdf | 1 | 1191 | 3070 | 751 | 1.26 |
| 4.2 Mapa gruntów słabonośnych.pdf | 1 | 1191 | 3070 | 728 | 1.26 |
| 4.3 Mapa gruntów antropogenicznych.pdf | 1 | 1191 | 3070 | 687 | 1.26 |
| 4.4 Mapa warunków budowlanych 5 m.pdf | 1 | 1191 | 3070 | 1089 | 1.26 |
| 4.5 Mapa poziomów wodonośnych.pdf | 1 | 1191 | 3070 | 1113 | 1.26 |
| 4.6 Mapa przepuszczalności gruntów na gł. 5 m ppt.pdf | 1 | 1191 | 3070 | 625 | 1.26 |
| 4.7 Mapa głębokości do podłoża nośnego.pdf | 1 | 1191 | 3070 | 615 | 1.26 |
| 4.8 Mapa osadów poniżej 1m ppt.pdf | 1 | 1191 | 3070 | 649 | 1.26 |
| 1 Mapa topograficzna.pdf | 1 | 842 | 2102 | 340 | 1.78 |
| 2 SMGP.pdf | 2 | 842 | 2100 | 585 | 1.78 |
| 3. PROJEKT GEOTECHNICZNY Lutoslawskiego 250410.pdf | 16 | 842 | 3959 | 30493 | 1.78 |
| A decyzja zatwierdzająca PRG.pdf | 4 | 842 | 2988 | 6 | 1.78 |
| 3 MGsP A.pdf | 2 | 841 | 2100 | 590 | 1.78 |

Pozostałe PDF-y (21) mają strony do 1500 pt i obrazy do 2000 px, ale i tak preferuj tekst.

## Przykłady
```
python renderuj_pdf.py "ścieżka/6. PZT.pdf"                       # cała strona, 1500 px
python renderuj_pdf.py "ścieżka/6. PZT.pdf" --wycinek 2400 480 3260 1140   # wycinek (pt)
python renderuj_pdf.py "ścieżka/1. MDCP.pdf" --kafelki 2x3           # 6 kafelków po ≤ 1500 px
python renderuj_pdf.py --sprawdz _obrazy/plik.png                     # kontrola przed wczytaniem
```

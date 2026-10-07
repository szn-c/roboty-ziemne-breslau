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

## Duże dokumenty w repo (stan po optymalizacji)
Rozmiar strony w pt = px przy zoomie 1. „Bezpieczny zoom" daje dłuższy bok 1500 px. **Uwaga: nowy `6. PZT.pdf` zawiera jeden osadzony obraz 8503×5181 px** – nigdy nie wyciągaj go ani nie renderuj ze zoomem; używaj `renderuj_pdf.py` i wycinków.

| Dokument | Stron | Największa strona [pt] | Największy osadzony obraz [px] | Znaków tekstu | Bezpieczny zoom |
|---|---:|---:|---:|---:|---:|
| 6. PZT.pdf | 1 | 4252 | 8503 | 39636 | 0.35 |
| 2. OPINIA GEOTECHNICZA_DBPG Wrocław ul. Lutosławskiego 1_90.pdf | 26 | 1191 | 4605 | 37372 | 1.26 |
| 8. Przekroje terenowe z naniesionym średnim poziomem wody gruntowej.pdf | 1 | 4252 | 202 | 24858 | 0.35 |
| 3. PROJEKT GEOTECHNICZNY Lutoslawskiego 250410.pdf | 16 | 842 | 3959 | 30493 | 1.78 |
| 4.1 Mapa sytuacyjno-wysokościowa.pdf | 1 | 1191 | 3070 | 751 | 1.26 |

Pozostałe PDF-y (14) mają strony do 1500 pt i obrazy do 2000 px, ale i tak preferuj tekst. Usunięte z repo duże pliki (MDCP, PZT garaże, mapy) są w historii gita – po odzyskaniu obowiązują te same zasady.

## Przykłady
```
python renderuj_pdf.py "ścieżka/6. PZT.pdf"                       # cała strona, 1500 px
python renderuj_pdf.py "ścieżka/6. PZT.pdf" --wycinek 2400 480 3260 1140   # wycinek (pt)
python renderuj_pdf.py "ścieżka/1. MDCP.pdf" --kafelki 2x3           # 6 kafelków po ≤ 1500 px
python renderuj_pdf.py --sprawdz _obrazy/plik.png                     # kontrola przed wczytaniem
```

# obliczenia_v1 – poprzednie obliczenia (NIEAKTUALNE założenia)

Powstały przy założeniach innych niż obecne (`USTALENIA.md`): jeden wariant naraz, bez podziału na strefy (hale / zieleń / nawierzchnie), wyniki zaokrąglane do 100 m³, pełny grunt z wykopu jako „przydatny".
**Nie używaj liczb z `00_WYNIKI/` jako wyników.** Pliki zachowano, bo zawierają użyteczne narzędzia i dane do weryfikacji.

## Do wykorzystania (po weryfikacji)
| Plik | Co robi |
|---|---|
| `_skrypt/wyciagnij_dane_z_pdf.py` | odtwarza rzędne z PZT; geometrię z rzutu zabezpieczenia tylko jeśli ten PDF jest w repo (teraz go nie ma) |
| `_skrypt/odczyt_dwg/` | czyta pliki DWG bez AutoCAD (LibreDWG w WebAssembly; wymaga Node: `env -u NODE_OPTIONS npm install`) |
| `_skrypt/renderuj_pdf.py` | bezpieczne renderowanie PDF do PNG (max 1500 px) |
| `_skrypt/wyciagnij_tekst_dokumentow.py` | tekst z PDF, DOC, DOCX |
| `_skrypt/eg_model.py` | model terenu istniejącego (pomiar z PZT + otwory + siatka 10 m po korekcie) |
| `_skrypt/oblicz_bilans.py` | silnik rastra 0,5 m: grubość humusu/nasypu z otworów, skład gruntu, warianty A/B |
| `_skrypt/generuj_pliki.py` | dane 17 otworów (słowniki `OTWORY` i `W`) – **wpisane ręcznie z kart, do sprawdzenia** |
| `_skrypt/generuj_wynik_prosty_xlsx.py` | wzorzec budowy arkusza Excel z żywymi formułami i zapisem wartości w komórkach (`wpisz_wartosci`) |
| `_skrypt/kontrola/` | niezależna weryfikacja formuł biblioteką `formulas` |
| `_skrypt/dane/` | geometria i rzędne odczytane z PDF (CSV, JSON) |
| `04_gstarcad_siatka/` | DXF z obrysami i siatką, pliki z wierzchołkami, skrypt `.scr`, LISP |

## Do przeróbki
`bilans_formuly.py`, `bilans_prosty.py`, `generuj_dane_dodatkowe_xlsx.py`, `generuj_dxf_geometria.py` – logika bilansu i arkusz trzeba przerobić na strefy, grunty przydatne/nieprzydatne i format 0,00 / 0,000.

## Wyniki wersji 1 (tylko dla porównania, inne założenia)
Wykop w całym obszarze ścianki (B): grunt z wykopu ok. 42 000 m³; w wariancie A ok. 29 300 m³; humus z całej działki ok. 15 400 m³; nasyp niekontrolowany ok. 1 300 m³.

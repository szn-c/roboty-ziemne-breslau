# Roboty ziemne – działka 1/90, Wojszyce (Wrocław)

Bilans mas ziemnych dla ośmiu podziemnych hal garażowych w ściance szczelnej.
**Repozytorium prywatne** (dokumenty inwestycji).

## Od czego zacząć (nowa sesja)
1. Przeczytaj `USTALENIA.md` (wiążące założenia i kolejność pracy).
2. Potem `ZADANIA_I_WERYFIKACJA.md` (plan prac i lista weryfikacji).
3. **Najpierw dokumentacja i weryfikacja ustaleń, dopiero potem obliczenia.**
   Pierwszą wiadomość do nowej sesji możesz skopiować z `PROMPT_DLA_NOWEJ_SESJI.md`.

## Struktura
(Pliki PDF są już w repo – wgrał je użytkownik; ta paczka ich nie zawiera.)
```
USTALENIA.md                      założenia (kopia .kiro/steering/ustalenia.md)
ZADANIA_I_WERYFIKACJA.md          plan prac + lista weryfikacji
PROMPT_DLA_NOWEJ_SESJI.md         gotowa pierwsza wiadomość
JAK_PRZESLAC_NA_GITHUB.md         instrukcja wgrania plików
.kiro/steering/ustalenia.md       czytane automatycznie przez asystenta
dokumentacja/
  01_geologiczno_inzynierska/     NAJWAŻNIEJSZE (pełna dokumentacja)
  02_projekt_geotechniczny/       pomocniczo
  03_opinia_geotechniczna/        pomocniczo
  04_projekt_zagospodarowania_i_architektura/   PZT, rzut garaży, przekrój
  05_rzedne_i_obrysy_fundamentow/ do uzupełnienia
  06_zabezpieczenie_wykopu/       rzut zabezpieczenia wykopu
  07_mapa_do_celow_projektowych/  granica działki i rzędne terenu
prace/
  dane_wejsciowe_uzytkownika/     pliki od użytkownika (szkic, wierzchołki granicy)
  ekstrakty_tekstu/               tekst wyciągnięty z dokumentów (szybkie czytanie)
  obliczenia_v1/                  poprzednie obliczenia i skrypty (inne założenia!)
archiwum/                         stary pakiet Civil 3D (nieaktualny)
```

## Stan prac
- Wersja 1 obliczeń (`prace/obliczenia_v1/`) powstała przy **innych założeniach** (jeden wariant, bez podziału na strefy, zaokrąglenia do 100 m³). Wyniki tej wersji są **nieaktualne**. Zachowano skrypty, które można wykorzystać: odtwarzanie geometrii z PDF, model terenu, silnik rastra.
- Nowe założenia (dwa warianty A i B, strefy hale / zieleń / nawierzchnie, grunty przydatne i nieprzydatne, decyzja o dowozie po stronie użytkownika, dokładność 0,00 m² i 0,000 m³): patrz `USTALENIA.md`.
- Dokumenty (PDF) użytkownik wgrał bezpośrednio do repo; nowa sesja ma je znaleźć i opisać w `prace/MAPA_DOKUMENTOW.md`.

## Narzędzia
- `prace/obliczenia_v1/_skrypt/wyciagnij_dane_z_pdf.py` – geometria (ścianka, hale, granica) i rzędne z PDF, w układzie PL-2000.
- `prace/obliczenia_v1/_skrypt/wyciagnij_tekst_dokumentow.py` – tekst z PDF, DOC i DOCX.
- Środowisko: `export PYENV_VERSION=3.12.13` i `python -m pip install -q numpy scipy shapely ezdxf openpyxl formulas pymupdf pillow olefile`.

# Roboty ziemne – działka 1/90, Wojszyce (Wrocław)

Bilans mas ziemnych dla ośmiu podziemnych hal garażowych w ściance szczelnej.
**Repozytorium prywatne** (dokumenty inwestycji).

## Od czego zacząć (nowa sesja)
1. Przeczytaj `USTALENIA.md` (wiążące założenia i kolejność pracy).
2. Potem `ZADANIA_I_WERYFIKACJA.md` (plan prac i lista weryfikacji).
3. **Najpierw dokumentacja i weryfikacja ustaleń, dopiero potem obliczenia.**
   Pierwszą wiadomość do nowej sesji przygotowuje użytkownik (zasady: dokumentacja → weryfikacja → obliczenia; patrz `USTALENIA.md`).

## Struktura
(Pliki PDF są już w repo – wgrał je użytkownik; ta paczka ich nie zawiera.)
```
USTALENIA.md                      założenia (kopia .kiro/steering/ustalenia.md)
ZADANIA_I_WERYFIKACJA.md          plan prac + lista weryfikacji
.kiro/steering/ustalenia.md       czytane automatycznie przez asystenta
dokumentacja/
  01_geologiczno_inzynierska/     NAJWAŻNIEJSZE (pełna dokumentacja)
  02_projekt_geotechniczny/       pomocniczo
  03_opinia_geotechniczna/        pomocniczo
  04_projekt_zagospodarowania_i_architektura/   PZT, rzut garaży, przekrój
  05_rzedne_i_obrysy_fundamentow/ do uzupełnienia
  06_zabezpieczenie_wykopu/       (pusty – usunięty)
  07_mapa_do_celow_projektowych/  granica działki i rzędne terenu
prace/
  dane_wejsciowe_uzytkownika/     obrysy użytkownika *_checked (hale, ścianka, granica) i DXF
  ekstrakty_tekstu/               tekst wyciągnięty z dokumentów (szybkie czytanie)
  obliczenia_v1/                  poprzednie obliczenia i skrypty (inne założenia!)
archiwum/                         stary pakiet Civil 3D (nieaktualny)
```

## Stan prac
- **8.10.2026: gotowy bilans v2** – `wyniki/BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx`, podkład `wyniki/PODKLAD_dz190_v3.dxf`, opis i pytania `wyniki/CZYTAJ_NAJPIERW.md`. Obliczenia: `prace/obliczenia_v2/`, dane: `prace/dane/`.
- Wersja 1 obliczeń (`prace/obliczenia_v1/`) powstała przy **innych założeniach** (jeden wariant, bez podziału na strefy, zaokrąglenia do 100 m³). Wyniki tej wersji są **nieaktualne**. Zachowano skrypty, które można wykorzystać: odtwarzanie geometrii z PDF, model terenu, silnik rastra.
- Nowe założenia (dwa warianty A i B, strefy hale / zieleń / nawierzchnie, grunty przydatne i nieprzydatne, decyzja o dowozie po stronie użytkownika, dokładność 0,00 m² i 0,000 m³): patrz `USTALENIA.md`.
- Dokumenty (PDF) użytkownik wgrał bezpośrednio do repo; nowa sesja ma je znaleźć i opisać w `prace/MAPA_DOKUMENTOW.md`. Teksty są w `prace/ekstrakty_tekstu/`.
- **Limit obrazów 2000 px zablokował jedną sesję** – przeczytaj `prace/OBRAZY_LIMIT_2000PX.md`. Postęp prac: `prace/POSTEP.md`.
- Obowiązująca geometria hal, ścianki i granicy: pliki `*_checked` użytkownika (`prace/dane_wejsciowe_uzytkownika/README.md`). Mapa dokumentów i fakty z usuniętych plików: `prace/MAPA_DOKUMENTOW.md`, `prace/FAKTY_Z_USUNIETYCH_DOKUMENTOW.md`.

## Narzędzia
- `prace/obliczenia_v1/_skrypt/wyciagnij_dane_z_pdf.py` – rzędne z tekstu PZT w układzie PL-2000 (geometria z rzutu zabezpieczenia: tylko jeśli PDF jest w repo).
- `prace/obliczenia_v1/_skrypt/renderuj_pdf.py` – bezpieczne renderowanie PDF do PNG (max 1500 px).
- `prace/obliczenia_v1/_skrypt/wyciagnij_tekst_dokumentow.py` – tekst z PDF, DOC i DOCX.
- Środowisko: `export PYENV_VERSION=3.12.13` i `python -m pip install -q numpy scipy shapely ezdxf openpyxl formulas pymupdf pillow olefile`.

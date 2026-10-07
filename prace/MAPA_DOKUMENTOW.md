# Mapa dokumentów w repo (stan po optymalizacji użytkownika)

Zasada: **nie trzymamy w sesji niepotrzebnych dużych plików**. Teksty wszystkich dokumentów (także usuniętych) są w `prace/ekstrakty_tekstu/` – czytaj najpierw je.
Usunięte pliki **nie zniknęły**: leżą w historii gita. Odzyskasz je tylko gdy naprawdę potrzebne:
Odzysk (w katalogu repo, wynik zapisz w katalogu roboczym, np. `prace/_odzyskane/`, nie w `/tmp`):
```
mkdir -p prace/_odzyskane
git show 851b25a:"dokumentacja/04_projekt_zagospodarowania_i_architektura/PW_4B-K-01_Rzut fundamentów.pdf" > "prace/_odzyskane/PW_4B.pdf"
```
Plik jest wektorowy – nie renderuj go dużym zoomem (użyj `renderuj_pdf.py`). Katalog `prace/_odzyskane/` jest w `.gitignore`.

## Dokumenty w repo (do czytania)
| Dokument | Rola | Tekst | Uwagi |
|---|---|---|---|
| `dokumentacja/01_geologiczno_inzynierska/DGI Wrocław Wojszyce.doc` | **dokumentacja geologiczno-inżynierska (priorytet 1)** | tak | DOC, tekst przez `wyciagnij_tekst_dokumentow.py` |
| `dokumentacja/01_geologiczno_inzynierska/załączniki graficzne/4.1 Mapa sytuacyjno-wysokościowa.pdf` | lokalizacja otworów, raster 1:1000 | prawie brak | 3070 px osadzonego obrazu – tylko wycinki |
| `dokumentacja/01_geologiczno_inzynierska/załączniki graficzne/5.1 - 5.28 Karty otworów geol-inż.pdf` | **profile 28 otworów (dane pierwotne)** | tak | |
| `dokumentacja/01_geologiczno_inzynierska/załączniki graficzne/8 Tabela parametrów geologiczno-inżynierskich.pdf` | parametry warstw (ρ, φ, c, M…) | tak | |
| `dokumentacja/01_geologiczno_inzynierska/załączniki graficzne/zał. 6 przekroje geologiczno - inżynierskie/6.1…6.12` | przekroje geologiczno-inżynierskie | tak | wektorowe |
| `dokumentacja/02_projekt_geotechniczny/3. PROJEKT GEOTECHNICZNY Lutoslawskiego 250410.pdf` | projekt geotechniczny (pomocniczo) | tak | |
| `03.../2. OPINIA GEOTECHNICZA…pdf` | opinia geotechniczna (pomocniczo) | tak | 206 obrazów osadzonych (do 4605 px) – nie renderować wprost |
| `dokumentacja/04_projekt_zagospodarowania_i_architektura/6. PZT.pdf` | PZT „wyniesienie" 1:250: rzędne, Bilans terenu | tak (39 637 zn.) | **spłaszczony do rastra** (jeden obraz 8503×5181 px, zero wektorów) |
| `dokumentacja/04_projekt_zagospodarowania_i_architektura/8. Przekroje terenowe z naniesionym średnim poziomem wody gruntowej.pdf` | rzędne i poziom wody | tak | wektorowy, strona 4252×1684 pt |
| `prace/dane_wejsciowe_uzytkownika/*_checked.txt` i `siatka_10m_dz190_checked.dxf` | **obrysy użytkownika (obowiązujące)** | – | patrz README tego folderu |

## Usunięte przez użytkownika – decyzja i uwagi z weryfikacji
| Usunięte | Czy potrzebne? | Gdzie jest informacja |
|---|---|---|
| `PW_1A…PW_8B-K-01 Rzut fundamentów` (8 plików, po 0,8 MB, wektorowe) | **TAK – dane nie są w DXF** (poziomy spodu płyty, elementy głębsze, uwagi o wykopie) | skrót w `prace/FAKTY_Z_USUNIETYCH_DOKUMENTOW.md`; tekst w `ekstrakty_tekstu`; uwagi ogólne są rysowane obrysami liter, więc tylko na obrazie – odzyskaj z gita i obejrzyj wycinek (`renderuj_pdf.py`) |
| `F Zestawienie wyników badań lab gruntów.pdf` | **TAK (wartości)** – wilgotność, granice plastyczności, IL, gęstość | pełna tabela w `ekstrakty_tekstu/F …txt`, skrót w pliku faktów |
| `7. PZT GARAŻE.pdf` | nie | poziomy posadzek (122,57 przy wszystkich halach) są w pliku faktów; obrysy hal w DXF |
| `1. MDCP.pdf` (skan) | częściowo | granica działki jest w DXF; **rzędne terenu z MDCP nie zostały przeniesione do DXF** (rzędne w węzłach DXF to stare wstępne z 17 otworów) – teren liczyć z tekstu PZT i otworów |
| mapy 1, 2, 3, 4.2–4.8 | nie | treść w kartach otworów, przekrojach 6.x i tekście; mapa 4.3 (nasyp) mogłaby rozstrzygnąć sprzeczność 20/23 – rozstrzyga karta otworu |
| `7 CPTU`, `C`, `D`, `E` (analizy) | nie (opcjonalnie) | tekst w ekstraktach |
| `A decyzja PRG`, `B licencje`, `G chemia wody` | nie (poza zakresem) | – |
| poprzednia wersja PZT (17,5 MB, **wektorowa**) | **TAK** – sesja 7.10 (wieczór): na niej sprawdzono obrysy hal i granicę (pliki `*_checked` są pomniejszone o 0,37%), posłuży do stref | odzysk: `git show 851b25a:"dokumentacja/04_projekt_zagospodarowania_i_architektura/6. PZT.pdf" > prace/_odzyskane/PZT_wektorowy.pdf` (robi to sam `prace/weryfikacja/pzt_wektor_hale.py`) |
| mapa 4.3 (nasypy) | sprawdzona tekstowo – etykiety nasypu przy otworach 5, 17, 20 | `git show 851b25a:"…/4.3 Mapa gruntów antropogenicznych.pdf"` |

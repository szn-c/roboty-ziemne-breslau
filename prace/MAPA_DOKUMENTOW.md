# Mapa dokumentów w repo (stan po optymalizacji użytkownika)

Zasada: **nie trzymamy w sesji niepotrzebnych dużych plików**. Teksty wszystkich dokumentów (także usuniętych) są w `prace/ekstrakty_tekstu/` – czytaj najpierw je.
Usunięte pliki **nie zniknęły**: leżą w historii gita. Odzyskasz je tylko gdy naprawdę potrzebne:
`git show 851b25a:"dokumentacja/04_projekt_zagospodarowania_i_architektura/PW_4B-K-01_Rzut fundamentów.pdf" > /tmp_nie_uzywac/plik.pdf` (zapisz w katalogu roboczym, nie w `/tmp`; plik wektorowy, nie renderuj go dużym zoomem).

## Dokumenty w repo (do czytania)
| Dokument | Rola | Tekst | Uwagi |
|---|---|---|---|
| `01.../DGI Wrocław Wojszyce.doc` | **dokumentacja geologiczno-inżynierska (priorytet 1)** | tak | DOC, tekst przez `wyciagnij_tekst_dokumentow.py` |
| `01.../4.1 Mapa sytuacyjno-wysokościowa.pdf` | lokalizacja otworów, raster 1:1000 | prawie brak | 3070 px osadzonego obrazu – tylko wycinki |
| `01.../5.1 - 5.28 Karty otworów geol-inż.pdf` | **profile 28 otworów (dane pierwotne)** | tak | |
| `01.../8 Tabela parametrów geologiczno-inżynierskich.pdf` | parametry warstw (ρ, φ, c, M…) | tak | |
| `01.../zał. 6 przekroje.../6.1…6.12` | przekroje geologiczno-inżynierskie | tak | wektorowe |
| `02.../3. PROJEKT GEOTECHNICZNY…pdf` | projekt geotechniczny (pomocniczo) | tak | |
| `03.../2. OPINIA GEOTECHNICZA…pdf` | opinia geotechniczna (pomocniczo) | tak | 206 obrazów osadzonych (do 4605 px) – nie renderować wprost |
| `04.../6. PZT.pdf` | PZT „wyniesienie" 1:250: rzędne, Bilans terenu | tak (39 637 zn.) | **spłaszczony do rastra** (jeden obraz 8503×5181 px, zero wektorów) |
| `04.../8. Przekroje terenowe z naniesionym średnim poziomem wody gruntowej.pdf` | rzędne i poziom wody | tak | wektorowy, strona 4252×1684 pt |
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
| poprzednia wersja PZT (17,5 MB, **wektorowa**) | tylko jeśli strefy z rastra okażą się niewystarczające | w historii gita; wektory pozwalają wyciągnąć strefy po kolorach wypełnień |

# GstarCAD – sprawdzenie obrysów i siatki (bez Civil 3D)

Bilans jest już policzony dla wykopu w ściance szczelnej (plik `../00_WYNIKI/BILANS_ROBOT_ZIEMNYCH_dz190.xlsx`). Ten folder służy do **sprawdzenia geometrii** w GstarCAD i do ewentualnego przeliczenia własnych obrysów.
Układ: PL-2000 strefa 6. **X w CAD = Easting (E, 6 433 xxx), Y w CAD = Northing (N, 5 658 xxx).**

## Pliki
| Plik | Co to jest |
|---|---|
| `obrysy_projektanta_i_siatka_dz190.dxf` | ścianka, hale 1–8, granica działki, siatka 10 m z rzędnymi terenu i głębokościami, otwory, krzyże 50 m |
| `rysuj_obrysy_projektanta.scr` | to samo, tylko ścianka + hale + granica, jako skrypt (gdyby DXF się nie otworzył) |
| `wierzcholki_scianka_wg_projektanta.txt` | 11 wierzchołków ścianki (E, N) |
| `wierzcholki_hala_1-8_wg_projektanta.txt` | 8 hal po 4 wierzchołki, oddzielone pustą linią |
| `wierzcholki_granica_dzialki_z_rysunku.txt` | granica działki z rysunku (pole 25 611 m², oficjalnie 25 290 m²) |
| `lisp/PLXY.lsp`, `lisp/TXTXY.lsp` | eksport wierzchołków polilinii / tekstów do pliku (jak wcześniej) |

## Krok 1 – otwórz DXF
1. `OTWÓRZ` (OPEN) → wybierz `obrysy_projektanta_i_siatka_dz190.dxf`.
2. Jeśli nic nie widać: wpisz `ZOOM`, Enter, `E`, Enter (zoom do zasięgu).
3. Warstwy (`LAYER`): włącz / wyłącz według potrzeby.
   - `01_SCIANKA_wg_projektanta` – linia przerywana (pole 20 662 m², obwód 563,5 m)
   - `02_HALE_1-8_wg_projektanta` – hale z numerami i polami
   - `03_GRANICA_DZIALKI_z_rysunku`
   - `06_WEZLY_10m`, `07_RZEDNE_TERENU` (górna liczba), `08_GLEBOKOSC_WYKOPU` (czerwona, głębokość do dna 121,97)
   - `09_OTWORY_DGI`, `10_KRZYZE_50m_do_ALIGN`
   - `11_STARE_OBRYSY_UZYTKOWNIKA_3.7pct_za_male` – Twój wcześniejszy szkic (szary)

## Krok 2 – sprawdź, czy Twój PDF ma dobrą skalę
1. Wstaw PDF rzutu zabezpieczenia: `PDFATTACH`.
2. Dopasuj go do krzyży 50 m z warstwy `10_KRZYZE_50m_do_ALIGN` poleceniem `ALIGN` (dwie pary punktów, przy pytaniu o skalowanie wybierz **Tak**).
   Krzyże na rysunku PDF to małe plusy co 50 m. Jeden z nich (przy napisach 5659050 i 6433700, u góry rysunku) ma podpisane współrzędne: E = 6433700, N = 5659050. Pozostałe leżą co 50 m od niego, a w DXF mają opisy np. „E6433700 N5659050".
3. Sprawdź: ścianka z PDF ma leżeć na polilinii `01_SCIANKA...`, a hale na `02_HALE...`. Odchyłka powinna być rzędu 0,2–0,5 m.
4. Kontrola szybka bez ALIGN: `DIST` między dwoma sąsiednimi krzyżami PDF ma dać **50,00 m**.

## Krok 3 – jeśli chcesz policzyć własny obrys (inny zakres wykopu)
1. Narysuj polilinię (`PLINE`, `C` na końcu) wzdłuż granicy wykopu.
2. Załaduj `lisp/PLXY.lsp` (`APPLOAD`), wpisz `PLXY`, wskaż polilinię. Powstanie plik `wierzcholki_polilinii.txt` obok rysunku.
3. Pole policzysz poleceniem `AREA` → `O` (obiekt). Dla porównania: ścianka 20 662 m², hale razem 11 927 m².
4. Objętość ≈ pole × średnia głębokość. Średnia głębokość od terenu do dna 121,97 to ok. **2,69 m** (teren istniejący średnio 124,66 m npm). Od tej liczby odejmij humus (średnio 0,61 m) i nasyp.
   Dokładniejsza wersja: arkusz `WEZLY_10m` w pliku `../00_WYNIKI/BILANS_dz190_dane_dodatkowe.xlsx` – zmień rzędne terenu w kolumnie D albo flagę „W ściance" i objętość przeliczy się sama.

## Uwaga o rzędnych terenu na siatce
Rzędne terenu w węzłach 10 m pochodzą z modelu: pomiar geodezyjny z PZT + 17 otworów + siatka z rzutu (po korekcie −0,1 m). Dokładność ok. ±0,05–0,10 m w pojedynczym węźle, a w średniej z całego obszaru ok. ±0,02 m.

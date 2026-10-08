# Model 3D robót ziemnych – instrukcja (dz. 1/90 Wojszyce)

Model jest zrobiony z tych samych danych co bilans (arkusz `BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx`), w obu wariantach: **A** (wykop pod garażami + rozkop) i **B** (cały obszar w ściance). Układ PL-2000/6, wysokości PL-KRON86-NH, jednostki: metry. Pliki leżą w tym samym układzie co `PODKLAD_dz190_v3.dxf`, więc można je wstawić jeden na drugi.

## Pliki
| Plik | Do czego |
|---|---|
| `MODEL3D_dz190.dxf` | model 3D do AutoCAD-a i GstarCAD-a (siatki trójkątów 3DFACE, linie 3D, opisy). Około 19 MB. |
| `MODEL3D_dz190_LandXML.xml` | te same 5 powierzchni jako TIN do **Civil 3D** (import LandXML). |
| `PRZEKROJE_dz190.dxf` | przekroje T1–T4 (2D) z warstwami gruntu z DGI. Podgląd: `PRZEKROJE_dz190_podglad.png`. |
| `MAPA_GLEBOKOSCI_dz190.dxf` | mapy 2D: głębokość wykopu i grubość wypełnienia (A i B). Podgląd: `MAPA_GLEBOKOSCI_dz190.png`. |

## Etapy (powierzchnie)
Każdy etap to osobna powierzchnia i osobna warstwa w DXF. Włączasz i wyłączasz je poleceniem `LAYER`.

| Etap | Warstwa DXF | Powierzchnia w Civil 3D |
|---|---|---|
| 1. Teren istniejący | `3D_1_TEREN_ISTNIEJACY` | `1_TEREN_ISTNIEJACY` |
| 2. Po zdjęciu humusu i nasypu | `3D_2_PO_ZDJECIU_HUMUSU` | `2_PO_ZDJECIU_HUMUSU_I_NASYPU` |
| 3A. Po wykopie – wariant A | `3D_3A_WYKOP_A` | `3A_WYKOP_A` |
| 3B. Po wykopie – wariant B | `3D_3B_WYKOP_B` | `3B_WYKOP_B` |
| 4. Stan końcowy (rzędne projektowe z PZT) | `3D_4_STAN_KONCOWY` | `4_STAN_KONCOWY` |

Powierzchnie 3A i 3B pokazują całą działkę: dno 121,86, skarpy, ściankę i teren, który zostaje poza wykopem.

Zaznaczone linie 3D:
- obrysy hal na dnie (121,86) i na rzędnej projektowej oraz ich krawędzie pionowe (`3D_LINIA_HALE_*`),
- zadaszone dojazdy do garaży (`3D_LINIA_ZADASZONE_*`),
- rampy: powierzchnia i spód wykopu (`3D_LINIA_RAMPY_*`),
- ścianka: góra i dół (`3D_LINIA_SCIANKA_*`); przerywana linia to odcinek, w którym ścianki nie ma (od południa jest skarpa 1:1,5),
- górna krawędź i dno wykopu A i B (`3D_LINIA_A_*`, `3D_LINIA_B_*`),
- granica działki (`3D_LINIA_GRANICA`),
- pionowe płaszczyzny ścianki (`3D_SCIANKA_A`, `3D_SCIANKA_B`).

## AutoCAD / GstarCAD
1. Otwórz `MODEL3D_dz190.dxf`, wpisz `ZOOM` → `E`.
2. Widok 3D: `3DORBIT` albo widok SW Isometric. Styl wizualny: `VSCURRENT` → `C` (Conceptual) lub `S` (Shaded).
3. Pokaż etapy po kolei: zostaw włączoną tylko jedną z warstw `3D_1…` do `3D_4…`. Żeby porównać dwa etapy, włącz dwie naraz (np. `3D_2…` i `3D_3B…`).
4. Pomiary: `DIST` w widoku 3D, rzędne dna – punkty linii `3D_LINIA_*_DNO`.

## Civil 3D (LandXML)
1. Nowy rysunek (metryczny). Najlepiej ustaw układ współrzędnych **ETRF2000-PL / CS2000/18** (EPSG 2177). W pliku nie ma układu, więc możesz też zostawić rysunek bez układu.
2. Karta *Insert* → *Import* → *LandXML* (nazwy w menu mogą się różnić zależnie od wersji). Wybierz plik i zaznacz wszystkie 5 powierzchni.
3. Powierzchnie pojawią się w *Prospector → Surfaces*. Zmień styl na taki, który pokazuje trójkąty lub warstwice co 0,5 m.
4. Objętości: *Analyze → Volumes Dashboard* → *Create new volume surface*. Baza i porównanie jak w tabeli:

| Baza | Porównanie | Wykop (cut) w modelu | Bilans (arkusz) |
|---|---|---:|---:|
| `2_PO_ZDJECIU_HUMUSU_I_NASYPU` | `3A_WYKOP_A` | około **34 269 m³** | 34 264,887 m³ |
| `2_PO_ZDJECIU_HUMUSU_I_NASYPU` | `3B_WYKOP_B` | około **45 209 m³** | 45 202,425 m³ |
| `1_TEREN_ISTNIEJACY` | `2_PO_ZDJECIU_HUMUSU_I_NASYPU` | około **15 536 m³** | 15 533,494 m³ (humus 15 274,147 + nasyp 259,347) |

Różnica do bilansu to około 0,01% (4–6 m³) i wynika z tego, że powierzchnie są siatką trójkątów, a bilans liczył raster 0,25 m. Jeśli w Civil 3D wyjdzie różnica większa niż kilkadziesiąt m³, napisz – sprawdzimy.

W kolumnie *Fill* wyjdzie kilka m³ (A: ok. 5, B: ok. 2). To drobny błąd siatki na stromych skarpach, nie zasyp.

## Przekroje T1–T4
- Linie przekrojów wzięte z rysunku projektanta (Z-04 „Przekroje terenowe", plan lokalizacji przekrojów) i dopasowane do układu PL-2000 po niebieskich obrysach garaży (błąd dopasowania ok. 0,2 m). Współrzędne: `prace/dane/linie_przekrojow.json`.
- Kolejność jak na rysunku projektanta: T1 i T2 od ul. Drabika (zachód) do ul. Buforowej (wschód), T3 i T4 od ul. Asfaltowej (południe) do ul. Lutosławskiego (północ).
- **T1 ma przesunięcie linii przekroju** (ok. 17 m na północ–południe, na wschodniej krawędzi hali 6, między halami 6 i 7). Tak jak na rysunku projektanta, odcinek przesunięcia nie wlicza się do odległości.
- Na przekroju: teren istniejący, po zdjęciu humusu i nasypu, po wykopie A i B, stan końcowy (PZT), humus i nasyp, warstwy gruntu z DGI (klasy Ia…IVd), hale, zadaszone dojazdy, rampy, ścianka, granica działki, otwory w odległości do 25 m i średni poziom wody wg DGI (123,39 m npm).
- Warstwy gruntu to interpolacja profili 17 otworów i 5 CPTU (tak jak w bilansie). Między otworami to model, nie pomiar.
- DXF jest w skali 1:1 (odległość w metrach w poziomie, rzędne w metrach w pionie), przekroje ułożone jeden pod drugim. W podglądzie PNG pion jest przewyższony ok. 4 razy.

**Zgodność terenu z rysunkiem projektanta.** Porównałem rzędne terenu opisane na przekrojach projektanta z modelem (tylko w obrębie działki, bez 1,5 m przy granicy):

| Przekrój | Teren istniejący (etykiety / RMS / największa różnica) | Teren projektowany (etykiety / RMS / największa różnica) |
|---|---|---|
| T1 | 16 / 0,38 m / 1,34 m | 17 / 0,36 m / 1,08 m |
| T2 | 17 / 0,10 m / 0,33 m | 13 / 0,11 m / 0,21 m |
| T3 | 18 / 0,14 m / 0,36 m | 8 / 0,11 m / 0,18 m |
| T4 | 15 / 0,36 m / 0,97 m | 9 / 0,13 m / 0,20 m |

Na T2 i T3 zgodność jest dobra (etykiety projektanta mają dokładność 0,1 m). Na T1 i T4 jest kilka punktów z różnicą ok. 1 m: T1 przy odległości 122,4 m (rysunek 126,20, model 124,86) oraz 168–171 m (stan projektowany, rysunek 125,98, model 124,9–125,1), T4 przy 129 i 139 m (rysunek 125,3, model 124,3–124,4). To miejsca do wyjaśnienia – możliwe lokalne nasypy lub skarpy na rysunku projektanta, których nie ma w punktach rzędnych PZT.

## Mapy 2D
- **Głębokość wykopu** (klasy co 0,5 m): teren po zdjęciu humusu i nasypu minus powierzchnia po wykopie. Maksimum ok. 3,1 m. Razem: A 34 264 m³ (17 799 m²), B 45 202 m³ (21 457 m²).
- **Grubość wypełnienia**: rzędna projektowa z PZT minus powierzchnia po wykopie, bez hal i zadaszonych dojazdów. To wypełnienie razem z warstwami konstrukcyjnymi (humus, konstrukcja nawierzchni, substrat, płyta rampy), a nie sam grunt rodzimy. Razem: A 27 674 m³, B 38 611 m³.
- Czarne kontury na mapie pokazują miejsca wymiany gruntu w strefie przemarzania poza wykopem.
- W DXF każda klasa ma osobną warstwę (`MAPA_A_WYKOP_01…`), a w rogu jest legenda z polami i objętościami.

## Czego w modelu nie ma
- **Fundamentów głębszych** (pogrubienia płyt, rdzenie, szyby wind, studzienki). W bilansie są osobną pozycją, liczoną z liczby sztuk i wymiarów, bez położeń, więc nie da się ich umieścić w modelu.
- **Pionowej ścianki w LandXML.** Siatka TIN nie ma ścian pionowych, więc ścianka jest bardzo stromym pasem (szerokości jednej komórki, 0,25 m). W DXF ścianka jest dodatkowo narysowana jako pionowe płaszczyzny.
- Budynków nad garażami (tylko obrysy hal).

## Co sprawdziłem, a czego nie
- Pliki odczytane od nowa niezależnym skryptem (`prace/obliczenia_v2/kontrola_modelu3d.py`): struktura LandXML (kolejność północ–wschód–rzędna, numeracja, trójkąty przeciwnie do ruchu wskazówek zegara, brak powtórzonych punktów), zgodność DXF z LandXML, brak dziur (suma pól trójkątów = pole działki 25 289,68 m², krawędzie brzegowe = obwód działki), objętości wyliczone z plików, audyt DXF (0 błędów).
- Błąd siatki względem rastra bilansu: średnio ≤ 0,002 m, w 99% punktów ≤ 0,024 m, największy ok. 0,11 m (przy stromych skarpach).
- **Nie otwierałem** plików w AutoCAD-zie, GstarCAD-zie ani Civil 3D (nie mam tych programów). Format LandXML jest zgodny ze specyfikacją 1.2, ale nie przeszedł walidacji schematem ani importu w Civil 3D. Jeśli import się nie uda, napisz, co wyświetla program.

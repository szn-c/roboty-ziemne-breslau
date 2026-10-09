# Model 3D robót ziemnych – instrukcja (dz. 1/90 Wojszyce)

Model jest zrobiony z tych samych danych co bilans (arkusz `BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx`), w obu wariantach: **A** (wykop pod garażami + rozkop) i **B** (cały obszar w ściance). Układ PL-2000/6, wysokości PL-KRON86-NH, jednostki: metry. Pliki leżą w tym samym układzie co `PODKLAD_dz190_v3.dxf`, więc można je wstawić jeden na drugi.

## Pliki
| Plik | Do czego |
|---|---|
| `MODEL3D_dz190.dxf` | model 3D do AutoCAD-a i GstarCAD-a (siatki trójkątów 3DFACE, linie 3D, opisy). Około 19 MB. |
| `MODEL3D_dz190_LandXML.xml` | te same 5 powierzchni jako TIN do **Civil 3D** (import LandXML). |
| `MODEL3D_podglad.png` | podgląd wariantów A i B w widoku izometrycznym (kolor = głębokość wykopu). |
| `MODEL3D_dz190_podglad.html` | **podgląd 3D w przeglądarce** (jeden plik, bez instalacji i bez internetu) – opis niżej. |
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
- ścianka: góra i dół (`3D_LINIA_SCIANKA_*`); osobna szara linia (`3D_LINIA_SCIANKA_ZAMKNIECIE`) to odcinek między końcami ścianki, w którym ścianki nie ma (od południa jest skarpa 1:1,5),
- górna krawędź i dno wykopu A i B (`3D_LINIA_A_*`, `3D_LINIA_B_*`),
- granica działki (`3D_LINIA_GRANICA`),
- pionowe płaszczyzny ścianki (`3D_SCIANKA_A`, `3D_SCIANKA_B`).

## Podgląd w przeglądarce (`MODEL3D_dz190_podglad.html`)
1. Pobierz plik na dysk (GitHub: otwórz plik → przycisk *Download raw file*) i kliknij go dwa razy. Otworzy się w Chrome, Edge albo Firefox. Internet nie jest potrzebny – biblioteka Three.js jest w pliku.
2. Mysz: lewy przycisk – obrót, prawy – przesuw, kółko – zoom. Przyciski: izometria, z góry, od południa, od zachodu.
3. **Etapy:** zaznacz, które powierzchnie pokazać (można kilka), albo „Pokaż tylko: 1 / 2 / 3A / 3B / 4”. Kolor: wykop według głębokości (te same klasy co w DXF i na mapach), według rzędnej albo jednolity. Siatka trójkątów i przezroczystość – do włączenia.
4. **Garaże i zabezpieczenie:** bryły hal i zadaszonych dojazdów, rampy, ścianka szczelna z grodzic, odcinek bez ścianki (skarpa od południa), górne krawędzie wykopów A i B, granica działki.
5. **Woda i badania (DGI):** płaszczyzna wody (domyślnie średnie zwierciadło ustabilizowane 123,39 m npm, suwak w zakresie DGI 122,90–124,10), zwierciadło zmierzone w otworach (niebieskie krążki), profile 17 otworów i 5 sondowań CPTU w kolorach warstw. Profile są w gruncie – zwiększ przezroczystość albo zaznacz „otwory widoczne przez powierzchnie”.
6. **Przewyższenie pionowe** ×1–×6 (domyślnie ×2). Etykiety można wyłączyć.
7. **Kliknięcie w model** pokazuje w tym miejscu: współrzędne E, N, rzędne wszystkich etapów, grubość humusu i nasypu, głębokość wykopu A i B. Kliknięcie w otwór lub CPTU pokazuje jego profil (warstwy, rzędne, woda) z DGI.

Uproszczenia w podglądzie:
- Bryła garażu: od spodu płyty fundamentowej 121,96 do rzędnej terenu projektowanego nad garażem (strop razem z warstwą zieleni). Rzędnej stropu nie ma w danych bilansu.
- Ścianka szczelna: przebieg z obliczeń bilansu (430,9 m, bez strony południowej), od terenu istniejącego w dół na 8,0 m. Projekt geotechniczny (s. 10) podaje „do maksymalnej głębokości około 8,0 m ppt”; dokładna głębokość będzie ustalona później.
- Sondowania CPTU są narysowane 2,2 m na wschód od otworu, w którym je wykonano (w rzeczywistości są w tym samym miejscu).
- Fundamentów głębszych nie ma (brak położeń w danych).

Sprawdzenie: plik otworzyłem w przeglądarce Chromium bez okna (headless). Ładuje się bez błędów JavaScript, rysuje model, a przyciski i przełączniki działają. Rzędne po kliknięciu zgadzają się z obliczeniami bilansu (do 0,01 m). Nie sprawdzałem w Twojej przeglądarce ani na słabszym komputerze.

## AutoCAD / GstarCAD
1. Otwórz `MODEL3D_dz190.dxf`, wpisz `ZOOM` → `E`.
2. Widok 3D: `3DORBIT` albo widok SW Isometric. Styl wizualny: `VSCURRENT` → `C` (Conceptual) lub `S` (Shaded).
3. **Kolory.** Trójkąty na warstwach `3D_3A_WYKOP_A` i `3D_3B_WYKOP_B` są pokolorowane według głębokości wykopu (jasnoszary = poza wykopem). Legenda jest na prawo od działki, w warstwie `3D_OPISY`. Te same klasy i kolory są na mapach głębokości. W Civil 3D (LandXML) kolorów nie ma – tam użyj stylu typu *Elevation Banding (3D)* albo powierzchni objętościowej ze stylem *Cut and Fill Banding*.
4. Pokaż etapy po kolei: zostaw włączoną tylko jedną z warstw `3D_1…` do `3D_4…`. Żeby porównać dwa etapy, włącz dwie naraz (np. `3D_2…` i `3D_3B…`).
5. Pomiary: `DIST` w widoku 3D, rzędne dna – punkty linii `3D_LINIA_*_DNO`.

## Civil 3D (LandXML)
1. Nowy rysunek (metryczny). Najlepiej ustaw układ współrzędnych **ETRF2000-PL / CS2000/18** (EPSG 2177). W pliku nie ma układu, więc możesz też zostawić rysunek bez układu.
2. Karta *Insert* → *Import* → *LandXML* (nazwy w menu mogą się różnić zależnie od wersji). Wybierz plik i zaznacz wszystkie 5 powierzchni.
3. Powierzchnie pojawią się w *Prospector → Surfaces*. Domyślny styl (np. „Contours 2m and 10m") jest za rzadki dla wykopu głębokiego ok. 3 m, więc zrób własny styl:
   - *Prospector → Settings → Surface → Surface Styles* → prawy przycisk na stylu → *Copy*, nazwij np. „Warstwice 0,5 m i trójkąty".
   - W kopii (okno *Styl powierzchni*): karta **Warstwice** – ustaw odstęp warstwic (np. podstawowe 0,5 m, główne 2 m); karta **Wyświetl** – włącz widoczność *Trójkąty* w widoku *Model* (3D) i *Warstwice* w widoku *Plan* (2D); karta **Analiza** – opcjonalnie kolorowanie wg rzędnych.
   - Karta **Siatka** nie jest potrzebna (to siatka co 25 m).
   - Przypisanie stylu: prawy przycisk na powierzchni w *Prospector* → *Surface Properties* → karta *Information* → *Surface style*.
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

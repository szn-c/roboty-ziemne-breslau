# Fakty z usuniętych dokumentów (NIEZWERYFIKOWANE – sprawdź w pierwszej kolejności)

Wyciągnięte przy weryfikacji optymalizacji repo. Dotyczą wprost dna wykopu, ilości wykopu i oceny gruntu.

## 1. Rzuty fundamentów budynków 1A…8B (4IDEA, projekt wykonawczy konstrukcji, XI 2025)
Rzędne podane względem ±0,00 = 126,00 m npm; napisy „d.k." = dolna krawędź, „g.k." = górna krawędź elementu.

| Wielkość | Wartość [m od ±0,00] | m npm | Występuje |
|---|---|---|---|
| d.k. płyty (podstawowa) | −4,04 | **121,96** | wszystkie 8 |
| g.k. płyty | −3,54 („rzędne powyżej to nadbeton") | 122,46 | wszystkie 8 |
| posadzka garażu | −3,43 (też −3,41; −3,48; −3,51; −3,60 przy spadkach 3% i korytkach) | 122,57 (122,40–122,59) | wszystkie 8 |
| d.k. głębszych elementów | −4,34 | 121,66 | wszystkie 8 |
| | −4,54 | 121,46 | tylko 2C |
| | −4,93 | 121,07 | wszystkie 8 |
| | −5,40 | 120,60 | 1A, 4B, 6A, 8B |
| | −5,83 | 120,17 | wszystkie 8 |
| | −6,00 | **120,00** | wszystkie 8 |
| g.k. głębszych elementów | −4,53 / −5,00 / −5,43 / −5,60 | 121,47 / 121,00 / 120,57 / 120,40 | – |

**Wnioski robocze (do potwierdzenia na rysunkach):**
- Płyta ma 0,50 m (−3,54 → −4,04), a posadzka (−3,43) leży ok. 11 cm nad jej górą na nadbetonie. Wcześniejsze obliczenia (v1) przyjmowały dno wykopu **121,97 = 122,57 − 0,50 − 0,10** (płyta bezpośrednio pod posadzką). Wg rzutów dolna krawędź płyty to 121,96, a **pod fundamentami jest podbeton C8/10 min. 10 cm**, więc dno wykopu to ok. **121,86**, czyli o ok. 0,11 m niżej niż w v1 (około +1 800 m³ w wariancie A i +2 300 m³ w B).
- Elementy głębsze (do −6,00 = 120,00 m npm, ok. 2 m niżej) to lokalne pogłębienia (szyby, stopy, pogrubienia – przekroje A-A…I-I na arkuszu). Ich powierzchnie i położenie trzeba odczytać z rysunków; w DXF ich nie ma (obrysy hal mają elewację 0).

**Uwagi ogólne z arkusza (odczytane z obrazu; w warstwie tekstowej ich nie ma):**
- Bezpośrednio pod fundamentami warstwa betonu podkładowego **C8/10, grubość min. 10 cm**.
- Gleby i nasypy – grunty nienośne; grunty słabonośne: nasyp niekontrolowany i gleby.
- Płyty fundamentowe posadawiać na warstwach: **Ib** (piaski drobne, pylaste, Id = 0,5), **II** (piaski średnie, Id = 0,5), **IVd** (gliny piaszczyste i pyły piaszczyste, IL = 0,05).
- Odbiór gruntu w dnie wykopu, nadzór nad wymianą gruntu i kontrola zagęszczenia – uprawniony geolog, wpisy do dziennika budowy.
- Wysoki poziom wody: **szczelne zabezpieczenie wykopu po obwodzie inwestycji** (np. grodzice stalowe), **szczelny „korek" w technologii jet-grouting** (odcięcie dopływu od dołu), odwodnienie wykopu wg opracowania wykonawcy; pompowanie można przerwać dopiero po wykonaniu całego stanu surowego budynku.
- Głębokość przemarzania wg opinii geotechnicznej: 0,8 m.
- Beton wodoszczelny C30/37 W8, technologia „biała wanna".
- (Uwagi o numerach powyżej 14 nie zostały przeczytane.)

## 2. Badania laboratoryjne (zestawienie F, GEO-MI, 25.07.2025) – 10 próbek
| Grunt | wn [%] | Wp [%] | WL [%] | Ip | IL | ρ [g/cm³] |
|---|---|---|---|---|---|---|
| gliny piaszczyste (zwięzłe) z żwirem, 6 próbek (otwór 3 dwie próbki, 18, 21, 24, 25; głębokości 3,5–9,5 m) | 11,1–12,9 | 10–11 | 27–36 | 16–25 | 0,01–0,08 | **2,18–2,35** |
| piaski (Pd, Ps) z żwirem, 4 próbki, otwory 3, 18, 20, 27 | 14,6–21,0 | – | – | – | – | – |

- W tych 6 próbkach gliny są **twardoplastyczne (IL 0,01–0,08), o wilgotności tylko 0–2 punkty procentowe powyżej granicy plastyczności**. Założenie v1, że glina pod zwierciadłem wody jest „mokra" i nie do wbudowania, wymaga więc uzasadnienia w projekcie geotechnicznym lub opinii (dokumentacja: woda we wkładkach piasku, w gruntach spoistych tylko sączenia).
- Gęstość glin 2,18–2,35 g/cm³ (v1 przyjmowało 2,1 t/m³).
- Do oceny przydatności do nasypów potrzebna jest wilgotność optymalna (Proctor) z projektu geotechnicznego lub opinii – nie ma jej w zestawieniu F.

## 3. PZT garaże (usunięty)
Wszystkie 8 hal ma opis **122,57 (−3,43)**. Dodatkowo napisy 122,60 (4 razy) i 122,85 (4 razy) – prawdopodobnie poziomy dojść/ramp (do sprawdzenia).

## 4. DXF użytkownika (`siatka_10m_dz190_checked.dxf`)
- Zawiera: `HALE_GARAZOWE` (8 obrysów), `7_SCIANKA_ORIENTACYJNA` (dwie otwarte polilinie: 11-wierzchołkowy wykop = `wierzcholki_polilinii_wykop_checked.txt` oraz 3-wierzchołkowa pozostałość starego szkicu), `A-granica inwest.` (17 wierzchołków, domknięta, z opisami A–N).
- Warstwy `1_WEZLY`, `2_RZEDNE_TERENU`, `3_GLEBOKOSC_WYKOPU`, `4_HUMUS_m`, `0_SIATKA_10m`, `5_OTWORY`, `6_KRZYZE…`, `8_OZNACZENIA…` to **moja stara, wstępna siatka** (rzędne z interpolacji 17 otworów, różnica 0,001 ± 0,049 m) – **nie zawierają rzędnych z MDCP**. Nie używać.

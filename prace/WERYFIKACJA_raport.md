# Raport weryfikacji ustaleń (T2) – działka 1/90

Data: 7.10.2026. Sprawdzono wszystkie pozycje z `ZADANIA_I_WERYFIKACJA.md` (część 2) na dokumentach z repo.
Wynik: **ZGODNE** / **NIEZGODNE** / **BRAK DANYCH** (+ dowód). Parametry ze źródłami: `prace/ekstrakt_dokumentacji.md`.
Skrypty kontroli i wyniki: `prace/weryfikacja/` (karty otworów, geometria, PZT rastrowy i wektorowy). Obrazy w tej sesji: 1.

## Najważniejsze (do decyzji przed obliczeniami)
1. **Pliki `*_checked` są pomniejszone o 0,37%** (pola o 0,73%) i przesunięte o ok. 0,7 m względem PZT. Kształty hal są dokładne (34 narożniki hal po dopasowaniu podobieństwem: odchyłka ≤ 1 mm). Po tej samej korekcie 16 z 17 boków granicy działki leży na linii granicy z PZT (±0,01 m; przy boku 11, 15,9 m, linii brak), a pole wynosi **25 289,84 m²** (oficjalnie 25 290,00). Hale razem: **12 167,36 m²** (zamiast 12 078,68), ścianka domknięta: **20 414,86 m²**, obwód 564,96 m.
2. **Ścianka od południa:** odcinek zamykający przecina **dwie hale (7 i 8)**, nie jedną. Rzut zabezpieczenia projektanta (v1) miał tam ściankę (ok. 6,5 m dalej na południe). „Ok. 565 mb" z ustaleń pasuje do ścianki zamkniętej (sama linia otwarta ma 430,93 m). Od tego zależy ok. 440 m² wykopu w wariancie B.
3. **Dno wykopu 121,86 jest potwierdzone** (spód płyty −4,04 = 121,96 we wszystkich 8 rzutach + chudy beton 10 cm). Wartość z v1 (121,97) jest błędna. Do tego **lokalne pogłębienia**: 143 pogrubienia płyty 4,40 × 3,40 m o 0,30 m (ok. 640 m³) oraz doły do 120,00.
4. **Bilans terenu PZT ma literówkę:** zieleń na stropie garażu to **3 975,11 m²**, nie 3 575,11 (wynika z 50% = 1 987,56, sumy 10 408,05 i domknięcia powierzchni do 25 290,00).
5. **Brak w dokumentach:** przestrzeni roboczej, nachylenia skarp wykopu, współczynników spulchnienia, gęstości gleby i nasypu.
6. Woda: dokumentacja geologiczna – zwierciadło ustabilizowane 122,90–124,10 m npm (śr. 123,39), wahania ±0,5 m; architekt – „średni poziom" 124,30. Dno 121,86 jest 1,0–2,2 m pod wodą.

## 1. Układ odniesienia i mapa
| Nr | Wynik | Dowód |
|---|---|---|
| U1 | **ZGODNE** | DGI, karta informacyjna (s. 2): PL-2000 strefa 6, PL-KRON86-NH. Rzędne fundamentów liczone od ±0,00 = 126,00 (PZT – w każdym z 8 budynków; przekroje terenowe; przekrój B-B 2C). |
| U2 | **NIEZGODNE (skala)** | Linie „obrys kondygnacji garażu" z wektorowego PZT (odzyskany z gita, 851b25a) vs hale użytkownika: skala 1,003663, obrót −0,002°, przesunięcie (+0,40; −0,57) m, rms po dopasowaniu 0,001 m. Kontrolnie rzut zabezpieczenia (v1) vs PZT: 0,09%, rms 0,12 m – czyli zgodne. Skala PZT jest poprawna: obrys budynku na PZT ma dokładnie 16,90 × 49,42 m (jak opisy „1690", „4942"). Numeracja hal = numeracja budynków (etykiety „1."–„8." i „TYP A/A*/B/C" leżą w odpowiednich halach). Skrypty: `pzt_wektor_hale_dopasowanie.py`, `transformacja_uzytk_do_PZT.py`. |
| U3 | **ZGODNE** | PZT 1:250, obrót 7,366°: 17 krzyży siatki 50 m znalezionych w rastrze dokładnie w przewidzianych miejscach (±0,05 m), `pzt_raster_kontrola.py`. |
| U4 | **ZGODNE** (z dokładnością mapy ±5 m) | Mapa 4.1: etykiety 28 otworów vs współrzędne z tabeli – skala 0,355 m/pt (1:1000), rms 5,5 m (etykiety stoją obok symboli). Granica jest sprawdzona dokładniej na PZT (G3). |

## 2. Obrysy i granice
| Nr | Wynik | Dowód |
|---|---|---|
| G1 | **ZGODNE co do kształtu i położenia, NIEZGODNE co do skali** | Hala 2 (6 wierzchołków) potwierdzona na PZT; rozbieżność +11% z v1 to był błąd odczytu v1. Wymiary zewnętrznej linii garażu na PZT: typ A 31,28 × 49,22 m, typ B 31,28 × 51,92 m (u użytkownika 31,17 × 49,04 i 31,17 × 51,73). Pola po korekcie: 1 539,59 / 1 221,30 / 1 539,61 / 1 624,06 / 1 539,59 / 1 539,60 / 1 539,60 / 1 624,01 m²; razem **12 167,36 m²**. Uwaga: garaż na PZT ma dwie linie co 0,34 m (zewnętrzne i wewnętrzne lico ściany); obrysy użytkownika odpowiadają linii zewnętrznej. |
| G2 | **NIEZGODNE – do decyzji** | (1) Odcinek zamykający (134,03 m) przecina **halę 7 (13,02 m² poza) i halę 8 (10,40 m² poza)**. (2) Rzut projektanta (v1) miał od południa ściankę P0–P1–P2–P3 (84,0 + 43,5 + 36,8 m). (3) Długość: linia otwarta 430,93 m; domknięta prosto 564,96 m; projektant 563,49 m – „ok. 565 mb" oznacza ściankę zamkniętą. (4) Hala 1 jest tylko **0,42 m** od ścianki (przestrzeń robocza 1,0 m się nie zmieści – w wariancie A obcinamy do ścianki). Hale 6 i 7 są 30–38 m od linii otwartej. Warianty zamknięcia: patrz pytanie 2 (`scianka_warianty_zamkniecia.json`). |
| G3 | **NIEZGODNE (skala) → po korekcie ZGODNE** | Przed korektą boki odchodzą od linii granicy PZT o −0,33…+0,73 m; pole 25 105,56 m². Po korekcie (ta sama transformacja co hale): 16 z 17 boków na linii granicy PZT (szara linia 1,98 pt lub czarna 0,51 pt, ±0,01 m; przy boku 11 linii brak), pole **25 289,84 m²** (oficjalnie 25 290,00). Skrypt: `pzt_wektor_granica_scianka.py`. |
| G4 | informacja | Szkic nieużywany – nie sprawdzano. |
| G5 | **ZGODNE** | W granicy 1/90 leży 17 otworów: 2, 3, 5, 7, 9, 10, 11, 12, 14, 15, 16, 17, 18, 20, 21, 23, 24. Otwory 25–40 są poza działką. Otwór 7 jest w pasie poza ścianką, pozostałe 16 w ściance. |

## 3. Rzędne
| Nr | Wynik | Dowód |
|---|---|---|
| R1 | **ZGODNE** | „±0,00 = 126,00" na PZT (8×), przekrojach terenowych (9×) i przekroju B-B 2C. |
| R2 | **ZGODNE** | PZT garaże: 122,57 i −3,43 przy wszystkich 8 halach. PW: lokalnie −3,41, −3,48, −3,51, −3,60 (spadki 3%, korytka) – to warstwa nadbetonu nad płytą (g.k. płyty −3,54), więc nie zmienia dna wykopu. |
| R3 | **NIEZGODNE z v1 → dno 121,86** | PW (8 rysunków): g.k. płyty −3,54 „(rzędne powyżej to nadbeton)", d.k. płyty −4,04 = 121,96. Przekrój B-B 2C: „Warstwa wyrównująca – chudy beton gr. 10 cm" → **121,86**. v1 (121,97) zakładało płytę od razu pod posadzką. Elementy głębsze (wszystkie budynki, chyba że zaznaczono): pogrubienia 4,40 × 3,40 m d.k. −4,34 (121,66) – 143 szt. (1A 18, 2C 12, 3A 18, 4B 21, 5A 18, 6A 17, 7A 18, 8B 21), ok. 640 m³ bez podbetonu i skarp; doły g.k. −4,53 / d.k. −4,93 (121,07); −5,43 / −5,83 (120,17); −5,60 / −6,00 (120,00); −5,00 / −5,40 (120,60) tylko 1A, 4B, 6A, 8B; −4,54 (121,46) tylko 2C. Położenie elementów da się odczytać z wektorowych PW (bez obrazów). Uwag ogólnych PW (obraz) w tej sesji nie oglądałem – chudy beton potwierdza przekrój B-B. |
| R4 | **ZGODNE** | Otwory vs pomiar na PZT: H − teren = +0,006 m, odchylenie 0,069 m (n = 17). 239 punktów pomiaru: 93 w działce, 61 w ściance (średnia punktów w ściance 124,62). Średnią modelu policzę od nowa w T4. |
| R5 | **ZGODNE (potwierdzone)** | Siatka 10 m z rzutu zabezpieczenia vs PZT: średnio +0,11 m, odchylenie 0,28 m, literówki do +1,53 m (np. 126,1 przy terenie 124,57). Nie używać. |
| R6 | **ZGODNE (zakres)** | 90 rzędnych projektowych: w ściance poza halami 125,40–125,98 (śr. 125,90, n = 51); przy halach 125,85–125,98 (n = 19); pas poza ścianką 124,40–125,98 (śr. 125,66, n = 15). Średnie różnią się od v1, bo zależą od podziału na strefy (policzę w T5). W pasie poza ścianką 14 z 15 punktów leży 0,23–1,01 m nad terenem; **jeden punkt (E 6 433 623,4; N 5 659 053,8): projekt 124,40 = teren 124,41** – tam po zdjęciu humusu rzędna podbudowy wypadnie poniżej terenu (zgłoszenie wg pkt 4.2 ustaleń). |
| R7 | **ZGODNE** | Rzędne na 28 kartach = tabela DGI (zaokrąglenie 0,1 m). |
| R8 | **ZGODNE** | PG s. 10: ścianka szczelna z grodzic stalowych po obwodzie, wyjmowana, do ok. 8,0 m ppt; studnie odwadniające wewnątrz; korek jet-grouting możliwy lokalnie. DGI rozdz. 11, 20: odwodnienie konieczne. |

## 4. Dane geologiczne
| Nr | Wynik | Dowód |
|---|---|---|
| D1 | **ZGODNE** | Słownik `W` z v1 = karty 5.1–5.17 (odczyt wg położenia słów: `odczyt_kart_otworow.py` → `karty_otworow_odczyt.json`). Jedna drobna różnica: otwór 15 – granica IVc/IVd na 2,5 m (v1: 2,1 m); obie warstwy to gliny, wpływ pomijalny. |
| D2 | **ZGODNE z kartami** | Nasyp: otwór 5 (0,20 m), 17 (0,30 m), 20 (0,20 m) – karty i mapa 4.3 (etykiety przy otworach 5, 17, 20; z gita). Tekst DGI (rozdz. 10, 13, 19) podaje „5, 17 i 23" – to omyłka (karta 23 nie ma nasypu). Maks. 0,30 m. |
| D3 | **częściowo NIEZGODNE** | **Otwór 12:** Y w tabeli uszkodzone („643368,27"). Przekroje IV-IV' (24→12: 85,8 m) i XI-XI' (11→12: 31,1 m) dają E ≈ 6 433 687–688, mapa 4.1 ≈ 6 433 688,6 → przyjmuję **6 433 688,2** (jak v1); odczyt „przesunięty przecinek" 6 433 682,7 odrzucam (5–6 m różnicy). **Otwór 17:** przekroje (do 20, 18, 16) i mapa 4.1 stawiają go ok. 5,5 m na południe od współrzędnych z tabeli; proponuję zostawić tabelę (pomiar), wpływ znikomy. **Otwór 11:** przy warstwie 1,5–2,5 m symbol ISO „saclSi" (glina), ale opis, symbol PN (Pr+Ż), warstwa IIb, stan (szg) i wilgotność (nw) wskazują piasek gruby → literówka, liczę jako piasek IIb. |
| D4 | **do ustalenia (propozycja)** | DGI tab. 1: woda ustabilizowana 0,9–1,7 m ppt w 12 otworach = 122,90–124,10 m npm (śr. 123,39); otw. 24: 3,7 m; otw. 18: 5,8 m; otw. 17, 20, 21 – brak (tylko sączenia lub nawiercona). Wahania ±0,5 m. Architekt: 124,30. PG (wg OG): 1,5–2,0 m ppt. **v1 w otworach 18, 20, 21 wzięło głębokość sączeń jako zwierciadło** (3,3 / 2,7 / 3,0 m) – do poprawy. |
| D5 | **ZGODNE** | Gleba w 17 otworach 0,40–0,80 m (średnio 0,63 m); 0,90 m to otwór 36 (poza działką). W otworach 5, 17, 20 gleba leży pod nasypem. |
| D6 | **częściowo (kryteria są, decyzja użytkownika)** | PG s. 12: grunt z wykopu można użyć do makroniwelacji działki i zasypów niebudowlanych (warstwy ≤ 0,30 m, Is > 0,95); nasyp nośny w wykopie: grunt niespoisty, zagęszczalny, E2 > 40 MPa, Is > 0,97. DGI: IIa i IVa słabonośne, IVb obniżona nośność, gliny wysadzinowe, chronić przed zawilgoceniem, roboty w porze suchej; przemarzanie 0,80 m. DGI rozdz. 16: „nie przewiduje się poboru gruntów z działek… materiały dostarczy wykonawca" (rozdział o kopalinach). Brak wilgotności optymalnej (Proctor). |
| D7 | **częściowo / BRAK DANYCH** | Gęstości są dla warstw Ia–V (DGI rozdz. 10, zał. 8; F: gliny 2,18–2,35 g/cm³). **Brak** gęstości gleby i nasypu oraz **brak spulchnienia** w dokumentach. |
| D8 | **częściowo** | F: **7 próbek glin** (nie 6 – plik faktów pominął otw. 39 z 1/97): IL 0,01–0,08, wn 11,1–12,9% przy Wp 10–11%, opis „mało wilgotne". Woda jest we wkładkach piasków, w glinach tylko sączenia. Założenie v1 „glina pod wodą = mokra, nieprzydatna" nie ma podstawy w dokumentach; ryzyko dotyczy zawilgocenia w trakcie robót (DGI). |

## 5. Powierzchnie (PZT, „Bilans terenu")
| Nr | Wynik | Dowód |
|---|---|---|
| Z1 | **NIEZGODNE (literówka w PZT)** | Zabudowa 6 680,59 ✓; utwardzone 6 899,75 ✓ (6 771,72 liczone 100% + geokrata 12% i 6%); razem biologicznie czynna 10 408,05 ✓. **Zieleń na stropie: w tabeli 3 575,11, ale 50% = 1 987,56** (a nie 1 787,56). Suma powierzchni rzeczywistych daje 25 290,00 **tylko przy 3 975,11** (przy 3 575,11 brakuje dokładnie 400,00 m²). Drobna literówka: „utwardzenia pod infrastrukturę 44,99 m² – 1,78%" (powinno 0,18%). Zieleń na gruncie 6 443,06 obejmuje części miejsc rekreacji i placu zabaw na gruncie (tekst PZT + domknięcie sumy). Strefy (hale / zieleń / nawierzchnie) wezmę z wektorowego PZT w T5. |

## 6. Metoda
| Nr | Wynik | Dowód |
|---|---|---|
| M1 | **ZGODNE** | `wyciagnij_dane_z_pdf.py`: 239 rzędnych terenu i 90 projektowych identycznych z v1 (`prace/weryfikacja/dane_odtworzone/`). |
| M2 | do wykonania w T7 | Dotyczy obliczeń. |

## 7. Inne uwagi
- Opinia geotechniczna (IV 2025) ma 7 otworów (1, 4, 6, 8, 13, 19, 22), bez współrzędnych; z mapy opinii położenie wychodzi niepewnie (±15–40 m). Gleba 0,3–0,8 m, nasyp 0,2 m (otw. 8) i 0,3 m (otw. 19). Propozycja: tylko pomocniczo.
- Wariant A, ustalenia pkt 4.1: wartości przestrzeni roboczej (1,0 m) i skarpy (1:1,5) **nie występują** w DGI, PG ani OG (PG: „bezpieczne nachylenie", zabezpieczenie wykopu w osobnym opracowaniu). „Skarpa 1:1 do 155 cm" na PZT dotyczy terenu docelowego, nie wykopu.
- Pliki pomocnicze (w `.gitignore`): `prace/_odzyskane/PZT_wektorowy.pdf`, `PW_1A.pdf`, `4.3.pdf`; cache w `prace/weryfikacja/_cache/`. Skrypty same je odtworzą.

## 8. Pytania do użytkownika (T3) – czekam na odpowiedzi przed obliczeniami
1. **Korekta geometrii:** przyjąć dla hal, ścianki i granicy korektę do PZT (skala 1,003663, przesunięcie +0,40 / −0,57 m)? *Propozycja: tak* (zgodność z PZT i z polem 25 290,00). Mogę przygotować poprawiony DXF do GstarCAD.
2. **Ścianka od południa (wariant B):** (a) prosto między końcami linii – 20 414,86 m², hale 7 i 8 wystają o 23,42 m²; (b) cały obrys projektanta z v1 – 20 661,71 m²; (c) linia użytkownika + południe wg projektanta – 20 855,22 m², obwód 565,16 m. *Propozycja: (c)* (nie przecina hal, długość zgadza się z „ok. 565 mb").
3. **Dno wykopu:** 121,86 pod płytą + lokalne pogłębienia z rzutów PW (pogrubienia −4,34, doły do −6,00) jako osobna pozycja? *Propozycja: tak, oba.*
4. **Wariant A:** dokumenty nie podają przestrzeni roboczej ani skarpy. Zostawić 1,0 m i 1:1,5 (z obcięciem do ścianki)? *Propozycja: tak.*
5. **Grunty przydatne:** pod zieleń – wszystkie grunty rodzime z wykopu poza glebą i nasypem (PG s. 12: zasypy niebudowlane z gruntu rodzimego); pod nawierzchnie (poniżej 0,50 m konstrukcji) – tylko piaski i pospółki (Ia, IIb, IIc, IIIa, IIIb), bo gliny są wysadzinowe, a przemarzanie 0,80 m sięga poniżej konstrukcji. *Propozycja: tak.*
6. **Gęstości i spulchnienie:** w dokumentach brak gęstości gleby i nasypu oraz brak spulchnienia. *Propozycja:* objętości w stanie rodzimym; tony z gęstości DGI dla warstw, dla gleby 1,60 i nasypu 1,80 t/m³ (założenie); spulchnienie jako żółte pola informacyjne (1,25 / 1,25 / 1,30 / 1,15 jak w v1).
7. **Drobne (wystarczy „tak"):** (a) zieleń na stropie = 3 975,11 m²; (b) woda do oceny gruntu wg dokumentacji geologicznej (otwory), nie 124,30 architekta; (c) otwór 12: E = 6 433 688,2, otwór 17 wg tabeli; (d) otwory z opinii tylko pomocniczo.

## Aneks 8.10.2026 – kontrola DXF v2 i stref (po odpowiedziach użytkownika)
| Nr | Wynik | Dowód |
|---|---|---|
| V1 | **NIEZGODNE** | `siatka_10m_dz190_checked_v2.dxf`: hale, granica i ścianka mają wierzchołki identyczne z v1 (maks. 0,7 mm) – korekta skali 0,37% nie została naniesiona. Usunięto tylko 3-wierzchołkową pozostałość ścianki. Do obliczeń użyto geometrii przeliczonej do PZT (`prace/dane/geometria.json`). Skrypt: `prace/weryfikacja/kontrola_dxf_v2.py`. |
| V2 | **NIEZGODNE** | `ZIELEN-NA-GRUNCIE` (23 polilinie, z łukami): 6 264,04 m²; jedna polilinia (5,89 m²) leży w drugiej, 9,3 m² w hali 6. Wobec wypełnienia PZT (6 417,55 m²; Bilans 6 443,06): brakuje ok. 358 m² (głównie przy halach 1, 2, 5 i w pasie SE), dodane są ogrody deszczowe (ok. 229 m²). |
| V3 | **NIEZGODNE** | `ZIELEN-NA-STROPIE` (38 polilinii): 3 572,61 m², jedna polilinia samoprzecinająca się. PZT: **3 979,48 m²** (potwierdza 3 975,11 z domknięcia Bilansu; 3 575,11 w tabeli to literówka). Brakuje ok. 369 m² (pasy przy halach 1, 2, 5, 6, 7, 8 i zadaszony dojazd przy hali 1). `prace/weryfikacja/pzt_strefy_widoczne.py`. |
| V4 | informacja | Zieleń na stropie poza obrysami hal (396 m²) = zadaszone dojazdy do 4 pochylni (5,0 × 25,0 m) między halami 1/5, 3/4, 5/6 i 7/8 – obiekty podziemne. |
| V5 | informacja | Wypełnienie (152,152,152) to wiaty (144,00 m² ≈ 143,15 z Bilansu), nie mury pochylni. |
| V6 | **ZGODNE** (korekta R3) | Fundamenty głębsze z rzutów PW (`fundamenty_glebsze.py`): 143 etykiety d.k. −4,34 to 135 pogrubień + 8 rdzeni (nie 143 pogrubienia 4,40 × 3,40 jak w R3). Razem 137 pogrubień (w tym 6 szt. 4,40 × 6,54 w 2C, 4 szt. 4,40 × 6,59 w 4B i 8B oraz 2 szt. d.k. −4,54 w 2C), 8 rdzeni z szybami wind, 20 studzienek; objętość wszystkich obniżeń 1 294,323 m³ (bryły ze skosem 0,50 m – w R3 szacowano tylko pogrubienia, ok. 640 m³). |
| V7 | **ZGODNE** | Nasyp z mapy 4.3 (georeferencja na 27 symbolach otworów, rms 0,76 m): strefy przy otworach 17+20 i 5 – zgodnie z kartami. |
| V8 | informacja | Obrysy dróg, chodników, placu i parkingów do wymiany w strefie przemarzania (ustalenie 21) wzięto z wypełnień wektorowego PZT (`ciagi_pieszo_jezdne`, `ciagi_piesze`, `plac_uslugowy`, `geokrata_na_gruncie` w `prace/dane/strefy.json`). Wymiana: 471,81 m², 77,070 m³ (A). |
| V9 | **ZGODNE** | Wariant A liczony zasadą z v1 („A (skarpy 1:1,5)”, `prace/obliczenia_v1/_skrypt/wyniki_bilans.json`: 29 234,555 m³). Przy zasadach v1 i nowych danych wynik to 30 733,696 m³. Różnica +1 499 m³ wynika z danych: obrysy w PZT, model terenu, humus z otworów. Rozkład krok po kroku: arkusz WARIANT_A. |

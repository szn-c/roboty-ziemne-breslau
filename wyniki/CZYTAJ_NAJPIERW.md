# Bilans robót ziemnych – działka 1/90 (stan po ustaleniach 18–23)

## Pliki
- `AUDYT_BILANSU_I_OPTYMALIZACJI.md` – niezależne sprawdzenie obliczeń i założeń, lista ryzyk oraz możliwości ograniczenia kosztów.
- `MODEL_ROBOT_ZIEMNYCH_AUDYT.html` – nowy, samodzielny model 3D z przełączaniem A/B, pulpitem bilansu, ryzykami, kalkulatorem kosztowym i kontrolami. Działa bez internetu; pobierz plik i otwórz go dwuklikiem w przeglądarce.
- `BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx` – arkusz z wynikiem. Zacznij od zakładki **WYNIK** (warianty A i B obok siebie). Żółte pola to Twoje decyzje – możesz je zmieniać, arkusz przeliczy się sam. Zakładka **WARIANT_A** pokazuje krok po kroku, jak powstaje wykop A.
- `PODKLAD_dz190_v3.dxf` – podkład do GstarCAD (opis warstw niżej).
- `OPIS_WYLICZEN.md` – opis wyliczeń w punktach: dane, metoda, zasady, wyniki, kontrola, niepewność, założenia.
- `MODEL3D_dz190.dxf` i `MODEL3D_dz190_LandXML.xml` – model 3D wykopu w etapach (teren istniejący → po zdjęciu humusu → po wykopie A i B → stan końcowy), do AutoCAD-a, GstarCAD-a i Civil 3D. Instrukcja i kontrola: `MODEL3D_INSTRUKCJA.md`.
- `MODEL3D_dz190_podglad.html` – model 3D do oglądania w przeglądarce (etapy do wyboru, garaże, ścianka szczelna, woda, otwory i CPTU z DGI). Pobierz i kliknij dwa razy.
- `PRZEKROJE_dz190.dxf` (podgląd: `PRZEKROJE_dz190_podglad.png`) – przekroje T1–T4 z warstwami gruntu z DGI.
- `MAPA_GLEBOKOSCI_dz190.dxf` (podgląd: `MAPA_GLEBOKOSCI_dz190.png`) – mapy głębokości wykopu i grubości wypełnienia.

## Wynik w skrócie (m³ w stanie rodzimym)
| | Wariant A – wykop pod garażami + rozkop | Wariant B – cały obszar w ściance |
|---|---:|---:|
| Humus zdjęty / na odkład / do wywozu | 15 274,147 / 1 771,842 / 13 502,305 | jak w A |
| Nasyp niekontrolowany – wywóz | 259,347 | 259,347 |
| Wykop gruntu rodzimego razem (cały na odkład) | 34 264,887 | 45 202,425 |
| – w tym spod hal i zadaszonych dojazdów | 27 062,629 | 27 062,629 |
| – w tym wymiana w strefie przemarzania pod drogami, chodnikami, parkingami | 77,070 | 77,055 |
| Grunt z odkładu wbudowany ponownie | 19 260,539 | 30 198,076 |
| Grunt rodzimy – nadwyżka do wywozu | 15 004,348 | 15 004,349 |
| Fundamenty głębsze (osobno, wywóz) | 1 294,323 | 1 294,323 |
| **RAZEM DO WYWOZU** | **30 060,323** (55 926,115 t) | **30 060,324** (55 974,728 t) |
| Dowóz: grunt do zasypu | 0,000 | 0,000 |
| Dowóz: grunt niewysadzinowy (strefa przemarzania 0,50–1,00 m) | 2 735,129 | 2 735,130 |
| **RAZEM DO DOWIEZIENIA** | **2 735,129** | **2 735,130** |

W skrócie:
- Wywóz jest w obu wariantach taki sam. Cały grunt rodzimy nadaje się do zasypu, więc wywozimy tylko to, co zajmą garaże.
- W wariancie B kopiemy o 10 937,538 m³ więcej, ale ten grunt wraca do zasypu. Trzeba go więc odłożyć na odkład i potem wbudować z powrotem.
- Wobec poprzedniej wersji wywóz spadł z 42 133 do 30 060 m³, a dowóz z 14 395 do 2 735 m³. Powód: grunt spod hal idzie do zasypu (ustalenie 18).

## Jak liczony jest wariant A
Tak jak wcześniej: **wykop tylko pod garażami, dalej rozkop**:
- obrys garażu do dna 121,86;
- przestrzeń robocza 1,0 m;
- skarpa 1:1,5 aż do terenu po zdjęciu humusu;
- przy ściance rozkop jest obcięty (za ścianką nie kopiemy), od południa skarpa jest swobodna;
- między halami, gdzie skarpy się nie spotykają, teren zostaje (zdejmujemy tylko humus).

To ta sama zasada co w poprzednim arkuszu, w wariancie „A (skarpy 1:1,5)” (`prace/obliczenia_v1`). Do garażu doszły jeszcze rampy i zadaszone dojazdy. Skąd różnica (arkusz WARIANT_A):

| Krok | Co się zmienia | Wykop gruntu rodzimego [m³] | Różnica [m³] |
|---|---|---:|---:|
| poprzedni arkusz | hale + 1,0 m + skarpa 1:1,5, dno 121,97 | 29 234,555 | |
| 1d | te same zasady, nowe dane: obrysy w PZT, nowy model terenu, humus z 17 otworów i 5 CPTU | 30 733,696 | +1 499,141 |
| 1c | dno 121,86 zamiast 121,97 | 32 549,392 | +1 815,696 |
| 1b | wymiana w strefie przemarzania pod drogami, chodnikami i parkingami | 32 626,461 | +77,069 |
| 1 | od południa skarpa zamiast prostego obcięcia | 32 970,669 | +344,208 |
| 2 | zadaszone dojazdy (zieleń na stropie poza obrysem hal) | 34 071,578 | +1 100,909 |
| 3 | rampy = **obecny wariant A** | **34 264,887** | +193,309 |

Twój załącznik „BILANS_ROBOT_ZIEMNYCH_wczesniej” dotarł do mnie jako nieczytelne dane. Nie ma go też w repo. Porównałem więc z wynikiem poprzedniego arkusza zapisanym w repo (`prace/obliczenia_v1/_skrypt/wyniki_bilans.json`). Tam wariant A ze skarpami ma 29 234,555 m³, a A0 ze ścianami pionowymi 26 248,528 m³. Jeśli w Twoim pliku są inne liczby, wgraj go do `prace/dane_wejsciowe_uzytkownika/`, to porównam.

## Co przyjąłem (zgodnie z Twoimi odpowiedziami)
- Geometria przeliczona do PZT (granica 25 289,68 m², hale 12 167,36 m²). Strefy wziąłem z wektorowego PZT. Zieleń na stropie ma 3 975,11 m².
- Dno 121,86. Fundamenty głębsze liczę osobno (wywóz): 137 pogrubień płyty, 8 rdzeni z szybami wind i 20 studzienek.
- W wariancie A przestrzeń robocza 1,0 m i skarpa 1:1,5. Od południa nie ma ścianki, jest skarpa 1:1,5. W wariancie B podnóże skarpy od południa leży na prostym odcinku między końcami ścianki, poszerzonym o hale 7 i 8.
- Rampy i zadaszone dojazdy liczę jak część garażu. Pod rampą kopiemy co najmniej do powierzchni rampy minus 0,71 m. Tam, gdzie wykop jest głębszy (przy hali), zasypujemy do tego poziomu gruntem z odkładu.
- Zieleń: 0,25 m humusu, niżej grunt rodzimy z odkładu.
- Ogrody deszczowe: 0,30 m substratu (poza bilansem), niżej grunt rodzimy z odkładu.
- Nawierzchnie:
  - 0,50 m konstrukcji (poza bilansem);
  - do 1,00 m dowożony grunt niewysadzinowy;
  - niżej grunt rodzimy z odkładu.
- Pod drogami, chodnikami, placem i parkingami wymieniamy grunt w strefie przemarzania także tam, gdzie wykop nie sięga tak głęboko: kopiemy do 1,00 m pod nawierzchnią. W wariancie A to 471,81 m² i 77,070 m³.
- Grunt rodzimy z całego wykopu, także spod hal, idzie na odkład i do zasypu.

## Warunki użycia gruntu spod hal do zasypu
Dokumentacja geologiczna, projekt geotechniczny i opinia nie zawierają przeciwwskazań. Projekt geotechniczny (s. 12) pozwala użyć gruntu z wykopu do makroniwelacji i zasypów niebudowlanych.

Warunki z dokumentacji:
- grunt zagęszczać warstwami do 0,30 m, do Is > 0,95;
- gliny (ok. 80% urobku) wbudowywać w porze suchej i chronić przed wodą na odkładzie, bo po zawilgoceniu pęcznieją i uplastyczniają się;
- piaski spod zwierciadła wody (122,90–124,10) odsączyć na odkładzie przed wbudowaniem;
- glinę plastyczną IVa oddzielić, jeśli się trafi (w badaniach są tylko cienkie wkładki w CPTU-18 i CPTU-24).

Szczegóły i źródła są w zakładce GRUNTY.

## Drobne miejsca – tylko do wiadomości (nie kopiemy, nie liczę)
Wszystkie są poza ścianką, w pasie podnoszonym do rzędnej projektowej:
- zieleń: na 131,38 m² warstwa humusu 0,25 m wchodzi w grunt rodzimy (24,015 m³);
- inne nawierzchnie niż drogi, chodniki, plac i parkingi: na 48,69 m² w strefie przemarzania zostaje grunt rodzimy (14,964 m³);
- konstrukcja nawierzchni wchodzi w grunt rodzimy na 2,44 m² (0,079 m³).

Jeśli chcesz, mogę te miejsca też wymienić. Zmiana to mniej niż 40 m³.

## Założenia, które zostały bez Twojej uwagi (nie blokują)
- Spód wykopu pod rampą = powierzchnia rampy − 0,71 m. Zmiana o ±0,2 m daje ok. ±70 m³ wykopu i ok. ±110 m³ wywozu.
- Nasyp niekontrolowany wg stref z mapy 4.3 DGI, grubość 0,20–0,25 m.
- Wymiary studzienek odczytałem z rzutu 1A i przyjąłem dla wszystkich budynków.

## Podkład DXF v3
- Twoje warstwy `HALE_GARAZOWE`, `A-granica inwest.`, `7_SCIANKA_ORIENTACYJNA` i `ZIELEN-*` są przeliczone do PZT (te same obiekty, poprawione położenie).
- Stare warstwy wstępnej siatki (0_…8_) są wyłączone, nie usunięte.
- Nowe warstwy `BILANS_*`:
  - strefy z PZT, rampy z kierunkiem spadku, zadaszone dojazdy;
  - nasyp z mapy 4.3, otwory i CPTU;
  - dolna i górna krawędź wykopu dla A i B;
  - `BILANS_WYMIANA_PRZEMARZANIE_A` i `_B`: miejsca wymiany gruntu pod drogami, chodnikami i parkingami poza wykopem.

## Gdzie co jest
- Szczegóły weryfikacji: `prace/WERYFIKACJA_raport.md`.
- Dane wejściowe ze źródłami: `prace/dane/`.
- Obliczenia: `prace/obliczenia_v2/` (silnik, arkusz, wrażliwość, rozkład wariantu A).
- Zakładka NIEPEWNOSC pokazuje, o ile zmienia się wynik, gdy zmienia się jedno założenie. Największy wpływ mają:
  - grubość humusu: ±0,10 m daje ok. ±2 500 m³ humusu i ok. ±2 500 m³ wywozu gruntu rodzimego (w przeciwną stronę);
  - rzędne terenu: ±0,05 m daje ok. ±900 m³ wykopu A i ok. ±1 250 m³ wywozu.

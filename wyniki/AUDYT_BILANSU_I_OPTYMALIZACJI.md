# Audyt bilansu robót ziemnych i możliwości optymalizacji

**Obiekt:** działka 1/90, Wojszyce, Wrocław  
**Data audytu:** 28.10.2026  
**Zakres:** sprawdzenie obliczeń, założeń, kontroli oraz możliwości ograniczenia kosztów.

## 1. Wniosek końcowy

**Obliczenia są spójne arytmetycznie i odtwarzalne, ale bilansu nie należy jeszcze uznawać za bezwarunkowo zatwierdzony do rozliczenia kontraktowego.**

Silnik obliczeniowy został ponownie uruchomiony podczas audytu. Odtworzył zapisany wynik identycznie. Kontrola arkusza oraz przeniesienia ilości do zeszytu scenariusza B również nie wykazała różnic liczbowych.

Największym ryzykiem nie jest błąd dodawania, lecz założenie, że **cały grunt rodzimy z wykopu nadaje się do ponownego wbudowania**. Dokumentacja dopuszcza wykorzystanie gruntu do makroniwelacji i zasypów niebudowlanych pod określonymi warunkami, ale nie ma badań Proctora ani potwierdzenia przydatności całej przewidzianej objętości w konkretnych strefach. Bez tego wynik „0 m³ zwykłego gruntu z dowozu” pozostaje założeniem organizacyjno-geotechnicznym.

Najkorzystniejszy ilościowo jest **wariant A**. Wariant B nie zmniejsza wywozu ani dowozu, a wymaga dodatkowo wykopać i ponownie wbudować około **10 937,538 m³** gruntu.

## 2. Wyniki poddane kontroli

| Pozycja | Wariant A | Wariant B |
|---|---:|---:|
| Humus zdjęty | 15 274,147 m³ | 15 274,147 m³ |
| Humus do wywozu | 13 502,305 m³ | 13 502,305 m³ |
| Nasyp niekontrolowany do wywozu | 259,347 m³ | 259,347 m³ |
| Wykop gruntu rodzimego | 34 264,887 m³ | 45 202,425 m³ |
| Ponowne wbudowanie gruntu | 19 260,539 m³ | 30 198,076 m³ |
| Grunt rodzimy do wywozu | 15 004,348 m³ | 15 004,349 m³ |
| Fundamenty głębsze do wywozu | 1 294,323 m³ | 1 294,323 m³ |
| Razem do wywozu | 30 060,323 m³ | 30 060,324 m³ |
| Grunt niewysadzinowy z dowozu | 2 735,129 m³ | 2 735,130 m³ |
| Zwykły grunt z dowozu | 0,000 m³ | 0,000 m³ |

## 3. Kontrole wykonane podczas audytu

1. **Ponowne obliczenie silnika:** wynik w pamięci był identyczny z `prace/obliczenia_v2/wyniki.json`, w tym humus 15 274,147 m³, nasyp 259,347 m³ i fundamenty 1 294,365 m³ według niezaokrąglonego sposobu sumowania silnika.
2. **Kontrola arkusza:** skrypt `kontrola_arkusza.py` zakończył się bez błędu. Arkusz zawiera żywe formuły i zapisane wyniki.
3. **Kontrola zeszytu scenariusza B:** 17 formuł przeliczono niezależnie; różnica względem zapisanych wartości wyniosła 0. Wszystkie kontrolowane pozycje AD4–AD11 były zgodne z bilansem.
4. **Kontrola numeryczna rastra:** zmiana oczka z 0,25 na 0,50 m zmieniła wykop A o +38,155 m³, czyli około 0,11%, a wykop B o +9,582 m³, czyli około 0,02%. Dokładność rastra jest wystarczająca w stosunku do jakości danych wejściowych.
5. **Kontrola modelu 3D:** różnica TIN względem bilansu wynosi około 4,4 m³ dla A i 6,2 m³ dla B, czyli około 0,013%. Jest pomijalna.

## 4. Usterki i niespójności do poprawienia

### 4.1. Różnica objętości fundamentów — mała, ale wymaga ujednolicenia

`prace/obliczenia_v2/wyniki.json` podaje **1 294,365 m³**, a końcowy arkusz i raporty **1 294,323 m³**. Różnica 0,042 m³ wynika z kolejności zaokrąglania: arkusz najpierw zaokrągla objętość jednej sztuki, a następnie mnoży przez liczbę sztuk. To nie wpływa praktycznie na koszt, ale jedno oficjalne źródło wyniku powinno stosować tę samą regułę.

### 4.2. Opis nasypu zawiera niezgodną arytmetykę

W opisie podano:

`759,28 m² × 0,25 m + 350,30 m² × 0,20 m = 259,347 m³`.

Prosty iloczyn daje **259,880 m³**, nie 259,347 m³. Wynik 259,347 m³ pochodzi z maski rastra 0,25 m. Obliczenie przestrzenne może być poprawne, ale opis powinien wskazywać, że pola po rasteryzacji są nieco inne. Różnica wynosi 0,533 m³.

### 4.3. Kontrola modelu 3D zbyt łatwo zwraca „OK”

Dla humusu i nasypu model 3D podaje 15 536,149 m³, a bilans 15 533,494 m³, czyli różnicę **2,655 m³**. Mimo tego pole `objetosci_ok` ma wartość `true`, ponieważ kontrola ocenia przede wszystkim wykopy A i B. Należy rozszerzyć warunek kontroli także na humus i nasyp.

### 4.4. Plik wejściowy DXF nie zawiera faktycznie użytej korekty

Plik `siatka_10m_dz190_checked_v2.dxf` nadal ma geometrię pomniejszoną o około 0,37% i przesuniętą o około 0,7 m. Obliczenia korzystają z poprawionego `prace/dane/geometria.json`, a wynikowy `PODKLAD_dz190_v3.dxf` zawiera geometrię po korekcie. Do dalszej pracy CAD należy używać wyłącznie poprawionego podkładu, aby nie mieszać dwóch geometrii.

### 4.5. Kontrole potwierdzają spójność modelu, nie pełną prawdziwość danych

Porównanie arkusza z `wyniki.json` nie jest niezależnym pomiarem geodezyjnym. Potwierdza prawidłowe przeniesienie tych samych danych. Nadal niewyjaśnione są lokalne różnice rzędnych na przekrojach T1 i T4, dochodzące do około 1,0–1,34 m.

## 5. Ocena najważniejszych założeń

| Założenie | Ocena | Zalecenie |
|---|---|---|
| Dno wykopu 121,86 m npm | dobrze udokumentowane | pozostawić |
| Raster 0,25 m | wystarczający | pozostawić |
| Przestrzeń robocza 1,0 m | decyzja użytkownika, brak w dokumentacji | potwierdzić z technologią wykonawcy |
| Skarpa 1:1,5 | decyzja użytkownika, brak w dokumentacji | potwierdzić z projektantem zabezpieczenia i BHP robót |
| Strefa przemarzania 1,00 m | konserwatywna; DGI wskazuje 0,80 m | sprawdzić wymagania branży drogowej i konstrukcję nawierzchni |
| Cały grunt rodzimy przydatny | założenie wysokiego ryzyka | wykonać program badań i podział urobku na strefy |
| Humus średnio 0,604 m | duża wartość, wyznaczona interpolacją | potwierdzić odkrywkami przed rozpoczęciem robót |
| Fundamenty głębsze | ilości bez lokalizacji i z częścią wymiarów uogólnioną | potwierdzić wszystkie rzuty i kolizje; przyjęta niepewność około ±400 m³ |
| CPTU i otwór po 50% | arbitralne uśrednienie | wykonać kontrolny wariant wag lub przyjąć zasady geotechnika |
| Brak wody ustabilizowanej = 3,0 m ppt | ukryte założenie modelu | potwierdzić lub usunąć wartość zastępczą |

## 6. Najważniejsze ryzyko ilościowe — przydatność gruntu

Planowane ponowne wbudowanie wynosi 19 260,539 m³ w A i 30 198,076 m³ w B. Jeżeli część tej masy nie przejdzie wymagań wilgotności, zagęszczalności lub nośności, trzeba będzie zwiększyć jednocześnie wywóz i dowóz materiału zastępczego.

| Odrzucona część planowanego ponownego użycia | A: dodatkowy wywóz i dowóz | B: dodatkowy wywóz i dowóz |
|---:|---:|---:|
| 10% | po 1 926,054 m³ | po 3 019,808 m³ |
| 20% | po 3 852,108 m³ | po 6 039,615 m³ |
| 30% | po 5 778,162 m³ | po 9 059,423 m³ |

Dlatego przed zawarciem stawek ryczałtowych zalecane są: badania Proctora, wilgotności naturalnej, kontrola możliwości doprowadzenia do wilgotności optymalnej oraz uzgodnienie wymaganych parametrów dla każdej strefy zasypu. Warstwę IVa należy wydzielać, a gliny zabezpieczać przed opadami.

## 7. Możliwości optymalizacji kosztowej

### 7.1. Wybrać wariant A, jeśli technologia i harmonogram na to pozwalają

Wariant B wymaga dodatkowo wykopać **10 937,538 m³**, odłożyć ten grunt, a następnie wbudować go z powrotem. Wywóz i dowóz pozostają praktycznie takie same jak w A.

Oszczędność wariantu A można policzyć wzorem:

`10 937,538 × (stawka wykopu + transport wewnętrzny/odkład + ponowny załadunek + rozłożenie i zagęszczenie + badania)`.

Wariant B może być uzasadniony prostszą organizacją frontu, dostępem sprzętu albo wymaganiami zabezpieczenia wykopu, lecz ilościowo jest droższy i nie daje oszczędności transportu zewnętrznego.

### 7.2. Sprawdzić możliwość przyjęcia przemarzania 0,80 m zamiast 1,00 m

DGI wskazuje 0,80 m, natomiast bilans przyjmuje 1,00 m. Kontrolne przeliczenie audytowe dla 0,80 m dało:

- grunt niewysadzinowy z dowozu: **1 644,476 m³**, czyli mniej o **1 090,653–1 090,654 m³**;
- grunt rodzimy do wywozu: mniej o około **1 090,653–1 090,654 m³**, ponieważ większa ilość gruntu rodzimego może pozostać pod nawierzchniami;
- wykop: mniej o około 59,7 m³.

Jest to potencjalnie bardzo korzystna optymalizacja, ale można ją zastosować wyłącznie po potwierdzeniu przez projektanta branży drogowej/geotechnika, że 0,80 m spełnia wymagania konstrukcji nawierzchni i warunków lokalnych.

### 7.3. Ująć pełny koszt odkładu i ponownego wbudowania

W zeszycie scenariusza B brakuje osobnej pozycji dla **30 198,076 m³** gruntu odkładanego i ponownie wbudowywanego. Należy wycenić:

- transport wewnętrzny i urządzenie odkładu;
- zabezpieczenie glin przed wodą oraz odwodnienie/odsączenie;
- ponowny załadunek;
- rozłożenie warstwami do 0,30 m;
- zagęszczenie do wymaganego `Is`;
- badania kontrolne;
- ewentualne suszenie, mieszanie lub stabilizację.

Bez tych pozycji koszt scenariusza B będzie istotnie zaniżony.

### 7.4. Prowadzić selektywne wydobycie i bezpośrednie wbudowanie

Najtańszy grunt to materiał, którego nie trzeba dwa razy ładować i długo magazynować. Harmonogram powinien łączyć wykop w jednej strefie z zasypem w innej. Materiał należy dzielić co najmniej na: piaski, gliny przydatne, warstwę IVa/urobek wątpliwy oraz humus. Pozwoli to ograniczyć degradację gruntu i liczbę przeładunków.

### 7.5. Zweryfikować grubość humusu w terenie

Zmiana modelowej grubości humusu o 0,10 m przesuwa około **2 529 m³** między kategorią humusu i gruntu rodzimego. Łączny wolumen robót nie zmienia się w tej samej skali, ale stawki za zagospodarowanie humusu i gruntu mogą być różne. Siatka odkrywek przed robotami ograniczy ryzyko błędnej wyceny.

### 7.6. Zweryfikować pogłębienia przed zamówieniem transportu

Niepewność fundamentów głębszych oceniono na około ±400 m³. Potwierdzenie liczby, wymiarów i lokalizacji wszystkich studzienek oraz pogrubień pozwoli uniknąć rezerwy transportowej i podwójnego liczenia nakładających się brył.

## 8. Proponowany model porównania ofert

Do porównania A i B oraz ofert podwykonawców należy żądać osobnych stawek netto za 1 m³ dla:

1. wykopu i załadunku;
2. transportu wewnętrznego na odkład;
3. utrzymania i zabezpieczenia odkładu;
4. ponownego załadunku;
5. rozłożenia i zagęszczenia;
6. badań zagęszczenia;
7. wywozu z transportem na wskazaną odległość;
8. opłaty za przyjęcie materiału;
9. zakupu i dowozu gruntu niewysadzinowego;
10. ewentualnego ulepszenia/stabilizacji gruntu rodzimego;
11. odwodnienia wykopu i odkładu.

Bez tych stawek nie da się wiarygodnie podać oszczędności w PLN. Samo porównanie objętości pokazuje jednak, że wariant A powinien być bazą kosztową, a wariant B wariantem technologicznym wymagającym dodatkowego uzasadnienia.

## 9. Warunki zatwierdzenia bilansu

Przed użyciem bilansu jako podstawy rozliczenia zaleca się:

1. potwierdzić rzędne w rejonach rozbieżności T1 i T4;
2. zatwierdzić nachylenie skarp, przestrzeń roboczą i rozwiązanie południowej krawędzi wykopu;
3. uzgodnić wymaganą głębokość wymiany pod nawierzchniami: 0,80 czy 1,00 m;
4. przeprowadzić badania przydatności i zagęszczalności gruntu oraz ustalić kryteria odbioru;
5. potwierdzić komplet pogłębień fundamentowych;
6. uzupełnić kosztorys o cały cykl odkładu i ponownego wbudowania;
7. ujednolicić regułę zaokrąglania fundamentów oraz poprawić opis nasypu;
8. używać w CAD wyłącznie geometrii po korekcie do PZT.

Po spełnieniu tych warunków model stanowi dobrą bazę ilościową do planowania i porównania wariantów.
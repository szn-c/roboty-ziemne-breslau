# Opis wyliczeń – bilans robót ziemnych, działka 1/90, Wojszyce (Wrocław)

Stan: po ustaleniach 1–30 (`USTALENIA.md`). Liczby pochodzą z arkusza `BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx` (zakładka WYNIK). Szczegóły postępowania i weryfikacji dokumentów: `prace/POSTEP.md`, `prace/WERYFIKACJA_raport.md`.

## 1. Cel i zakres
- Obliczono bilans mas ziemnych dla ośmiu podziemnych hal garażowych: humusu, nasypu niekontrolowanego i gruntu rodzimego.
- Dla każdego składnika określono ilości do zdjęcia, na odkład, do ponownego wbudowania, do wywozu i do dowozu.
- Bilans wykonano w dwóch wariantach:
  - **A:** wykop pod garażami wraz z rozkopem.
  - **B:** wykop w obrębie całych ścian, czyli cały obszar w ściance do dna.
- Objętości podano w stanie rodzimym. Tony i objętości luzem podano informacyjnie.
- Wynik: arkusz Excel z formułami i zapisanymi wartościami, podkład DXF, model 3D, przekroje i mapy.

## 2. Dane wejściowe i ich hierarchia
- Przyjęto następującą kolejność źródeł przy sprzeczności:
  - dokumentacja geologiczno-inżynierska (DGI),
  - projekt geotechniczny,
  - opinia geotechniczna,
  - rysunki projektu (PZT, przekroje, rzuty fundamentów),
  - obrysy użytkownika,
  - wcześniejsze obliczenia.
- **Układ:** PL-2000 strefa 6, wysokości PL-KRON86-NH.
- **Geometria hal, granicy i ścianki:** obrysy użytkownika okazały się o 0,37% mniejsze niż w PZT. Przeliczono je do PZT (skala 1,003663, przesunięcie ok. 0,7 m, błąd dopasowania 1 mm).
  - Powierzchnia działki: 25 289,68 m².
  - Powierzchnia hal: 12 167,36 m².
  - Od południa nie ma ścianki, jest skarpa swobodna.
- **Teren:** rzędne istniejące i projektowane z PZT, interpolowane siecią trójkątów (TIN).
- **Grunt:** 17 otworów (nr 2–24) i 5 sondowań CPTU (10, 12, 18, 21, 24).
  - Profil otworu i CPTU w tym samym miejscu uśredniono po 0,5.
  - Warstwy sklasyfikowano jako Ia…IVd.
  - Między otworami profile interpolowano TIN-em.
- **Nasyp niekontrolowany** (grunty antropogeniczne): strefy z mapy 4.3 DGI.
  - 759,28 m² × 0,25 m oraz 350,30 m² × 0,20 m, razem 259,347 m³.
- **Strefy zagospodarowania** wzięto z wektorowego PZT, w kolejności pierwszeństwa: hale i zadaszone dojazdy, rampy, ogrody deszczowe, zieleń na gruncie, nawierzchnie.
  - Zieleń na stropie: 3 975,11 m² (w tabeli PZT jest literówka 3 575,11).
  - Cztery pochylnie 5 × 25 m (ok. 554 m²).
  - Zadaszone dojazdy poza halami: ok. 396 m².

## 3. Parametry wykopu
- **Dno wykopu:** 121,86 m npm (dolna krawędź płyty 121,96 minus 0,10 m podbetonu).
- **Przestrzeń robocza:** 1,0 m. **Skarpy:** 1:1,5.
- **Rampy:** powierzchnia rampy zmienia się liniowo od 122,85 do 125,80. Spód wykopu pod rampą to powierzchnia rampy minus 0,71 m.
- **Fundamenty głębsze** (137 pogrubień płyty, 8 rdzeni z szybami wind, 20 studzienek) policzono osobno.
  - Zastosowano bryły ścięte z poszerzeniem 0,50 m.
  - Razem 1 294,323 m³, w całości do wywozu.
- Za ścianką (zachód, północ, wschód) wykopu nie prowadzi się. Teren tam podnosi się do rzędnej projektowej.

## 4. Metoda obliczeń
- Obliczenia wykonano na rastrze 0,25 m. Kontrolnie przeliczono też raster 0,5 m. Różnice wyniosły poniżej 40 m³.
- Najpierw obliczono powierzchnię po zdjęciu humusu i nasypu. Wykop liczono od niej do powierzchni dna lub skarpy.
- **Wariant A:** powierzchnia wykopu to najniższa z powierzchni dołów. Pod halami i zadaszonymi dojazdami jest to dno 121,86, a pod rampami ich własny spód. Do każdego dołu doliczono 1,0 m przestrzeni roboczej, a dalej skarpę 1:1,5 do terenu. Rozkop obcięto do ścianki.
- **Wariant B:** w obrębie ścianki wykop sięga do dna ze ścianami pionowymi. Dochodzą hale 7 i 8 z przestrzenią roboczą 1,0 m. Od południa przyjęto skarpę 1:1,5, której podnóże leży na prostym odcinku między końcami ścianki.
- Skład gruntu w wykopie (klasy Ia…IVd) wyznaczono z krzywych skumulowanych profili. Na ich podstawie obliczono masy gruntu.

## 5. Zasady zagospodarowania gruntu
- **Humus** zdjęto z całej działki (średnio 0,604 m, razem 15 274,147 m³).
  - Na odkład trafia 0,25 m × 6 443,06 m² (zieleń na gruncie) × 1,10 (zapas 10%), czyli 1 771,842 m³.
  - Reszta, 13 502,305 m³, idzie do wywozu.
- **Nasyp niekontrolowany:** w całości do wywozu.
- **Grunt rodzimy** z całego wykopu, także spod hal, jest przydatny do zasypu i trafia na odkład.
  - Warunki wbudowania: pora sucha, ochrona glin przed wodą, warstwy do 0,30 m, Is > 0,95, odsączenie piasków nawodnionych, oddzielenie gliny plastycznej IVa.
- **Zapotrzebowanie według stref:**
  - zieleń na gruncie: 0,25 m humusu i niżej grunt rodzimy do dna wykopu,
  - ogrody deszczowe: 0,30 m substratu (poza bilansem) i niżej grunt rodzimy,
  - nawierzchnie: 0,50 m konstrukcji (poza bilansem), 0,50 m dowożonego gruntu niewysadzinowego (do głębokości przemarzania 1,00 m), niżej grunt rodzimy,
  - rampy: grunt do spodu płyty rampy,
  - hale: substrat na stropie jest dowożony i leży poza bilansem gruntu rodzimego.
- **Wymiana gruntu w strefie przemarzania** pod drogami, chodnikami, placem i parkingami obejmuje także miejsca poza wykopem. Wykop prowadzi się tam do 1,00 m pod nawierzchnią (A: 471,81 m², 77,070 m³; B: 471,44 m², 77,055 m³).
- **Ponowne wbudowanie** gruntu z odkładu przyjęto domyślnie jako mniejszą z wartości: grunt dostępny albo zapotrzebowanie. W arkuszu jest to żółte pole do ręcznej zmiany.
- **Gęstości:** z tabeli 8 DGI. Dla gleby przyjęto 1,60, dla nasypu 1,80 t/m³ (brak w tabeli). Spulchnienie podano tylko informacyjnie.

## 6. Wyniki (wariant A / B, m³ w stanie rodzimym)
- **Wykop gruntu rodzimego:** 34 264,887 / 45 202,425, w tym spod hal 27 062,629.
- **Zapotrzebowanie na grunt rodzimy:** 19 260,539 / 30 198,076. Ten sam grunt wraca z odkładu.
- **Do wywozu:** humus 13 502,305, nasyp 259,347, grunt rodzimy 15 004,348 / 15 004,349, fundamenty głębsze 1 294,323.
  - **Razem 30 060,323 / 30 060,324** (55 926,115 / 55 974,728 t).
- **Do dowozu:** grunt do zasypu 0, grunt niewysadzinowy **2 735,129 / 2 735,130**.
- Wywóz i dowóz są w obu wariantach praktycznie takie same. Dodatkowy wykop B (ok. 10 940 m³) wraca do zasypu.
- Przeniesienie do kosztorysu (scenariusz B): `Zeszyt2 - scenariusz B wg bilansu.xlsx`.

## 7. Kontrola i weryfikacja
- Bilans urobku i bilans zapotrzebowania są równe 0,000.
- Wszystkie pozycje zaokrąglono funkcją ROUND (m³ i t do 0,000, m² do 0,00), a sumy są sumami zaokrąglonych pozycji.
- Formuły arkusza przeliczono niezależną biblioteką dla 36 pozycji. Różnica wyniosła 0,000 m³.
- Wariant A porównano z poprzednim arkuszem (29 234,555 m³) krok po kroku w zakładce WARIANT_A.
- Model 3D i przekroje odczytano z plików od nowa. Objętości wykopu różnią się od bilansu o 0,013%.
- Rzędne terenu porównano z etykietami przekrojów T1–T4:
  - na T2 i T3 RMS wynosi 0,10–0,14 m,
  - na T1 i T4 są pojedyncze punkty z różnicą ok. 1 m, do wyjaśnienia.

## 8. Niepewność wyników (zmiana jednego założenia)
- Grubość humusu ±0,10 m: ok. ±2 500 m³ humusu, a wykop A zmienia się odwrotnie o ok. 1 800 m³.
- Rzędne terenu ±0,05 m: ok. ±900 m³ wykopu A.
- Przestrzeń robocza 0,5 / 1,5 m: −1 073 / +982 m³ wykopu A.
- Skarpa 1:1 / 1:2: −1 060 / +981 m³ wykopu A.
- Spód wykopu pod rampą ±0,2 m: ok. ±70 m³ wykopu.
- Zasięg nasypu: ok. ±100 m³. Fundamenty głębsze: ok. ±400 m³ (wymiary studzienek odczytano z jednego rzutu).
- Podział na piaski i gliny między otworami: ok. ±20%.
- Pełne zestawienie: zakładka NIEPEWNOSC arkusza bilansu.

## 9. Założenia i ograniczenia
- Przestrzeń robocza (1,0 m), skarpy (1:1,5), strefa przemarzania (1,00 m wobec 0,80 m w DGI) oraz spód wykopu pod rampą (−0,71 m) nie wynikają z dokumentacji. To decyzje i założenia użytkownika.
- Pominięto drobne miejsca poza ścianką, gdzie projekt wchodzi w grunt rodzimy (ok. 39 m³).
- Warstwy gruntu między otworami są interpolacją, nie pomiarem. Brak badań Proctora.
- Fundamenty głębsze liczono z liczby sztuk, bez położeń. Dlatego nie ma ich w modelu 3D.
- Głębokość grodzic (ok. 8,0 m wg projektu geotechnicznego, s. 10) nie wpływa na bilans, a w podglądzie 3D jest tylko pokazowa.

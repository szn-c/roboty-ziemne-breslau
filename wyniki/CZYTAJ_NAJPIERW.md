# Bilans robót ziemnych – działka 1/90 (stan 8.10.2026)

## Pliki
- `BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx` – arkusz z wynikiem. Zacznij od zakładki **WYNIK** (warianty A i B obok siebie). Żółte pola to Twoje decyzje – możesz je zmieniać, arkusz przeliczy się sam.
- `PODKLAD_dz190_v3.dxf` – nowy podkład do GstarCAD (opis warstw niżej).

## Wynik w skrócie (m³ w stanie rodzimym)
| | Wariant A – wykop pod halami | Wariant B – cały obszar w ściance |
|---|---:|---:|
| Humus zdjęty / na odkład / do wywozu | 15 274,147 / 1 771,842 / 13 502,305 | jak w A |
| Nasyp niekontrolowany – wywóz | 259,347 | 259,347 |
| Wykop gruntu rodzimego razem | 33 899,193 | 45 125,370 |
| – w tym spod hal (wywóz, zasada strefy hal) | 27 062,629 | 27 062,629 |
| Fundamenty głębsze (osobno, wywóz) | 1 294,323 | 1 294,323 |
| Grunt z odkładu wbudowany ponownie (propozycja) | 6 821,819 | 17 501,861 |
| **RAZEM DO WYWOZU** | **42 133,349** (80 922,128 t) | **42 679,484** (82 057,025 t) |
| Dowóz: grunt do zasypu | 11 734,690 | 11 734,677 |
| Dowóz: grunt niewysadzinowy (strefa przemarzania) | 2 660,253 | 2 660,267 |
| **RAZEM DO DOWIEZIENIA** | **14 394,943** | **14 394,944** |

Prosto: wywóz i dowóz są w obu wariantach prawie takie same. Wariant B ma o 11 226 m³ większy wykop, ale prawie cały ten grunt wraca do zasypu.

## Co przyjąłem (zgodnie z Twoimi odpowiedziami)
- Geometria: w DXF v2 hale, granica i ścianka były **takie same jak w v1** (różnica < 1 mm), czyli dalej o 0,37% za małe. Przeliczyłem je do PZT: granica 25 289,68 m², hale 12 167,36 m².
- Strefy (zieleń na gruncie, ogrody deszczowe, zieleń na stropie, rampy) wziąłem z wektorowego PZT. Twoje obrysy zieleni z v2 różnią się od PZT:
  - na gruncie brakuje ok. 360 m² zieleni, a są wliczone ogrody deszczowe;
  - na stropie brakuje ok. 370 m².
- Zieleń na stropie na PZT ma 3 979,48 m², czyli w tabeli PZT powinno być 3 975,11 m², a nie 3 575,11.
- Dno 121,86. Fundamenty głębsze liczę osobno: 137 pogrubień płyty, 8 rdzeni z szybami wind i 20 studzienek – razem 1 294,323 m³.
- Od południa nie ma ścianki, jest skarpa 1:1,5. W A przestrzeń robocza 1,0 m i skarpa 1:1,5, obcięte do ścianki.
- Zieleń: 0,25 m humusu, a niżej grunt rodzimy z odkładu.
- Nawierzchnie: 0,50 m konstrukcji (poza bilansem), potem 0,50 m dowożonego gruntu niewysadzinowego (do 1,00 m), a niżej grunt rodzimy.
- Gęstości z tabeli 8 DGI. Gleba 1,60, nasyp 1,80 t/m³. Nasyp liczony ze stref na mapie 4.3.

## Do decyzji (pytania z propozycją)
1. **Grunt spod hal.** Według zasady idzie w całości na wywóz (27 062,629 m³), a jednocześnie trzeba dowieźć 11 734,7 m³ gruntu do zasypu. To ten sam grunt rodzimy. Czy wolno go użyć do zasypu? *Propozycja: tak.* Wtedy dowóz gruntu do zasypu spada do 0 (zostaje tylko 2 660 m³ gruntu niewysadzinowego), a wywóz zmniejsza się o ok. 11 735 m³.
2. **Rampy i zadaszone dojazdy poza obrysami hal** (4 pochylnie ok. 554 m² i ok. 396 m² zadaszonych części) – liczę je jak część garażu:
   - w A wykop z przestrzenią roboczą i skarpą;
   - pod rampą wykop do powierzchni rampy minus 0,71 m.
   *Proponuję tak zostawić.*
3. **Ogrody deszczowe w wariancie B.** Leżą w wykopie i według zasady „bez gruntu z odkładu" zostaje pod nimi 1 037,6 m³ pustki. Zasypać ją gruntem z odkładu do spodu substratu? Jeśli tak, podaj grubość substratu. *Propozycja: tak.*
4. **Grunt rodzimy w strefie przemarzania poza wykopem.** Na 512 m² (głównie pas poza ścianką) pod nawierzchnią zostaje 89,8 m³ gruntu rodzimego w strefie 0,50–1,00 m. Nie kopałem tam. *Propozycja: wymienić* – wtedy wywóz i dowóz rosną o ok. 90 m³.
5. **Wariant B od południa.** Podnóże skarpy przyjąłem na prostym odcinku między końcami ścianki, poszerzonym o hale 7 i 8. *Proponuję tak zostawić.*

## Podkład DXF v3
- Twoje warstwy `HALE_GARAZOWE`, `A-granica inwest.`, `7_SCIANKA_ORIENTACYJNA` i `ZIELEN-*` są przeliczone do PZT (te same obiekty, poprawione położenie).
- Stare warstwy wstępnej siatki (0_…8_) są wyłączone, nie usunięte.
- Nowe warstwy `BILANS_*`:
  - strefy z PZT, rampy z kierunkiem spadku, zadaszone dojazdy;
  - nasyp z mapy 4.3, otwory i CPTU;
  - dolna i górna krawędź wykopu dla A i B.

## Gdzie co jest
- Szczegóły weryfikacji: `prace/WERYFIKACJA_raport.md` (aneks z 8.10).
- Dane wejściowe ze źródłami: `prace/dane/`.
- Obliczenia: `prace/obliczenia_v2/` (silnik, arkusz, wrażliwość).
- Zakładka NIEPEWNOSC: o ile zmienia się wynik, gdy zmienia się jedno założenie. Największy wpływ ma grubość humusu (±0,10 m daje ok. ±2 500 m³ humusu) i rzędne terenu (±0,05 m daje ok. ±900 m³ wykopu).

---
inclusion: always
---

# USTALENIA – bilans robót ziemnych, działka 1/90, Wojszyce (Wrocław)

Ten plik jest wiążący. Czytaj go na początku każdej sesji. Jest identyczny z `USTALENIA.md` w katalogu głównym repo (kopia na wypadek, gdyby folder `.kiro` nie wgrał się na GitHub).
Szczegółowy plan prac i lista weryfikacji: `ZADANIA_I_WERYFIKACJA.md`.

## 1. Użytkownik i sposób pracy
- Inżynier robót ziemnych, początkujący w CAD, ma tylko **GstarCAD** (bez Civil 3D, bez DWG od projektanta – tylko PDF-y i pliki z repo).
- **Pisz po polsku, bardzo prostym językiem.** Nie zalewaj szczegółami technicznymi.
- **Nie analizuj aspektów prawnych** (odpady, rolnictwo, pozwolenia). Wszystko jest ustalone.
- Nie zgaduj. Jeśli brakuje danych albo dokumenty są sprzeczne, **zapytaj użytkownika** i podaj, czego dokładnie brakuje.
- Pytania zadawaj krótko, najlepiej z propozycją odpowiedzi.

## 2. Zadanie
Policzyć **bilans mas ziemnych** dla działki 1/90 (osiem podziemnych hal garażowych, wykop w ściance szczelnej/berlińskiej, ok. 565 mb):
humus, nasyp niekontrolowany i grunt rodzimy: ile zebrać, ile na odkład (ponowne wbudowanie), ile do wywozu, ile do dowiezienia.
Wynik w **arkuszu Excel**, w **dwóch wariantach** (A i B), po polsku.

## 3. OBOWIĄZKOWA KOLEJNOŚĆ PRACY
1. Przeczytaj ten plik i `ZADANIA_I_WERYFIKACJA.md`.
2. **Zapoznaj się z dokumentacją** przed jakimikolwiek obliczeniami. Pliki PDF wgrał użytkownik bezpośrednio do repo. Zwykle leżą w `dokumentacja/`, ale mogą być gdzie indziej:
   znajdź je po nazwie i treści, a ścieżki zapisz w `prace/MAPA_DOKUMENTOW.md`. Kolejność czytania:
   1. **dokumentacja geologiczno-inżynierska** (`01_geologiczno_inzynierska/`) – **największy priorytet**;
   2. projekt geotechniczny (`02_projekt_geotechniczny/`) – pomocniczo;
   3. opinia geotechniczna (`03_opinia_geotechniczna/`) – pomocniczo;
   4. dokumentacja z rzędnymi i obrysami fundamentów (`05_rzedne_i_obrysy_fundamentow/`);
   5. **mapa do celów projektowych** (w repo) – źródło geodezyjne dla **granicy działki** i rzędnych terenu istniejącego;
   6. PZT, PZT garaże, przekroje terenowe z poziomem wody gruntowej i **rzuty fundamentów `PW_*-K-01`** (folder `04_...`, w nich obrysy fundamentów). Rzutu zabezpieczenia wykopu (PDF) i przekroju B-B **nie ma już w repo** (decyzja użytkownika: zbędne).
3. **Zweryfikuj wszystkie dotychczasowe ustalenia** w oparciu o dokumentację z repo (lista w `ZADANIA_I_WERYFIKACJA.md`, w tym: **rzędne, mapa, lokalizacja obrysów hal garażowych i ścianek wykopu**).
   Wynik zapisz w `prace/WERYFIKACJA_raport.md`. Niezgodności zgłoś użytkownikowi **przed** obliczeniami.
4. Dopiero potem obliczenia i arkusz.

Hierarchia źródeł przy sprzeczności: dokumentacja geologiczno-inżynierska > projekt geotechniczny > opinia geotechniczna > rysunki projektu (PZT, rzuty) > dotychczasowe obliczenia (`prace/obliczenia_v1`). Granicę działki i rzędne terenu istniejącego porównuj z mapą do celów projektowych.
Dane z poprzednich sesji (również te z plików `prace/obliczenia_v1`) traktuj jako **niezweryfikowane**, dopóki nie sprawdzisz ich w dokumentacji.

## 4. Założenia bilansu
### 4.1 Warianty wykopu (oba liczyć obok siebie)
- **Wariant A** – wykop pod halami: obrys hali + przestrzeń robocza (dotąd 1,0 m), dalej skarpa (dotąd 1:1,5), wszystko w obrębie ścianki. Wartości przestrzeni roboczej i skarp sprawdź w dokumentacji/projekcie geotechnicznym.
- **Wariant B** – cały obszar w ściance wykopany do dna, ściany pionowe.
- Dno wykopu dotąd: **121,97 m npm** = posadzka 122,57 (±0,00 = 126,00; −3,43) − płyta 0,50 − chudy beton 0,10. **Do weryfikacji** z dokumentacją konstrukcji i rzędnymi.

### 4.2 Pas poza ścianką
Pas działki poza ścianką jest **odhumusowany, bez wykopów** (nie obniżamy gruntu rodzimego) i **podnoszony do rzędnej projektowej** (wbudowanie wg stref, pkt 4.4).
Jeśli rzędna podbudowy wychodzi poniżej powierzchni po zdjęciu humusu, nie kopiemy – zgłoś takie miejsca użytkownikowi.

### 4.3 Humus i nasyp
- Humus zdejmowany z całej działki 1/90 (obrys ścianki + pas poza ścianką).
- **Humus na odkład** = 0,25 m × powierzchnia zieleni na gruncie rodzimym × **1,10** (zapas 10% – decyzja użytkownika); nie więcej niż zebrano. Przy 6 443,06 m² to 1 771,842 m³. Nadwyżkę humusu liczymy do wywozu.
- **Nasyp niekontrolowany: 100% na wywóz.**

### 4.4 Zasady wbudowania wg stref (rzędna docelowa z dokumentacji)
| Strefa | Co wbudowujemy | Co w bilansie |
|---|---|---|
| **Hale garażowe** (pod obrysem hal) wraz z **zielenią na stropie garażu, geokratą na stropie i dachami** | nic z wykopu; na stropie **dowożony dedykowany substrat** (poza bilansem gruntu rodzimego) | **cały wykop z tego obszaru do wywiezienia** |
| **Tereny zielone na gruncie** | **0,25 m humusu** (z odkładu) + poniżej, **do poziomu dna wykopu, ziemia z odkładu** | humus 0,25 m × powierzchnia; reszta to grunt z odkładu |
| **Nawierzchnie utwardzone** (w tym **geokrata na parkingach**) | **0,50 m konstrukcji drogowej** (kruszywo – **poza bilansem**) + poniżej, **do dna wykopu, grunt z odkładu** | tylko grunt poniżej konstrukcji |
| **Ogrody deszczowe** (253,00 m²) | **poza opracowaniem**, dedykowany substrat jak na halach | nie wbudowujemy tam humusu ani gruntu z odkładu; traktować jak hale |
| **Nasyp niekontrolowany** | nigdy | 100% na wywóz |

**Definicje stref (rozstrzygnięte przez użytkownika):**
- **Tereny zielone na gruncie** = wyłącznie pozycja „zieleń na gruncie rodzimym" z tabeli Bilans terenu na PZT (6 443,06 m²; wg tekstu PZT zawiera już części miejsc rekreacji i placu zabaw na gruncie rodzimym – do sprawdzenia). Nic więcej nie liczymy jako zieleń.
- **Geokrata na parkingach (na gruncie, 980,05 m²)** = **nawierzchnia utwardzona**: 0,50 m konstrukcji (poza bilansem) + poniżej grunt z odkładu do dna wykopu. Humusu 0,25 m tam nie wbudowujemy.
- **Zieleń na stropie garażu (3 575,11 m²), geokrata na stropie (173,70 m²), zieleń na dachu (1 824,12 m²)** = strefa „hale" (wywóz, dedykowany substrat dowożony).

**Pas poza ścianką:** po zdjęciu humusu teren podnosimy do rzędnej projektowej według tych samych stref (zieleń: 0,25 m humusu + grunt poniżej; nawierzchnie: 0,50 m konstrukcji + grunt poniżej). Grunt do podniesienia pochodzi z odkładu albo z dowozu – zob. pkt 4.5.

### 4.5 Grunty przydatne i nieprzydatne
- Podziel grunty z wykopu na **przydatne** i **nieprzydatne** do ponownego wbudowania. Kryteria wyciągnij **z dokumentacji** (warstwy geologiczno-inżynierskie Ia…V, stan, wilgotność, woda) i pomocniczo z projektu/opinii geotechnicznej. Przy każdym kryterium podaj źródło (dokument, strona).
- **Decyzję, ile gruntu rodzimego wbudować ponownie, a ile dowieźć, podejmuje użytkownik.** W arkuszu zrób **żółte pole** z ilością do ponownego wbudowania; pokaż limity (przydatny grunt dostępny, zapotrzebowanie) i wylicz dowóz = zapotrzebowanie − ponowne wbudowanie. Nie narzucaj decyzji; możesz dać oznaczoną „propozycję".

## 5. Format wyników (Excel)
- **m² – dokładność 0,00. m³ – dokładność 0,000.** (Tony i inne jednostki: 0,000 (decyzja użytkownika). Rzędne: 0,00 m, chyba że źródło podaje więcej.)
- Zaokrąglaj **w każdej pozycji** (`ROUND(x;2)` dla m², `ROUND(x;3)` dla m³); sumy = sumy zaokrąglonych pozycji, żeby tabela się dodawała.
- Dokładność zapisu to nie dokładność danych. Niepewność podawaj **osobno** (blok „niepewność"), nie w liczbach głównych.
- Oba warianty obok siebie. Żywe formuły + wartości zapisane w komórkach (podgląd w przeglądarce nie liczy formuł). Kontrola bilansu = 0. Arkusz zweryfikuj niezależnym przeliczeniem formuł.
- Komentarze w komórkach **nie mogą zaczynać się od znaku „="** (zapisze się jako błędna formuła).

## 6. Środowisko techniczne
- Powłoka nie pamięta ustawień: każde polecenie zaczynaj od `export PYENV_VERSION=3.12.13`.
- Biblioteki znikają między sesjami: `python -m pip install -q numpy scipy shapely ezdxf openpyxl formulas pymupdf pillow olefile`.
- **Katalog `/tmp` jest czyszczony między wywołaniami** – pracuj w katalogu repo.
- Brak LibreOffice i narzędzi DWG. Użytkownik widzi tylko pliki w przeglądarce (bez terminala) – pokazuj wyniki w odpowiedzi.
- Dane geometrii odtworzysz z PDF jednym poleceniem: `prace/obliczenia_v1/_skrypt/wyciagnij_dane_z_pdf.py`.
  Teksty dokumentów: `prace/obliczenia_v1/_skrypt/wyciagnij_tekst_dokumentow.py`.
- Silnik obliczeń rastra 0,5 m (teren, humus, skład gruntu): `prace/obliczenia_v1/_skrypt/oblicz_bilans.py` (do przeróbki pod nowe założenia).

### 6a. Obrazy – twardy limit 2000 px (wcześniej zablokował sesję)
Gdy w rozmowie jest **ponad 20 obrazów**, każdy obraz (także stary) musi mieć **≤ 2000 px** na każdym boku, inaczej sesja blokuje się na stałe (błąd „image dimensions exceed max allowed size for many-image requests"). Szczegóły i tabela dokumentów: `prace/OBRAZY_LIMIT_2000PX.md`.
- **Najpierw tekst** (`prace/ekstrakty_tekstu/`, dane wektorowe PDF). Obraz tylko gdy nie ma innej drogi.
- **Obrazy renderuj tylko** `prace/obliczenia_v1/_skrypt/renderuj_pdf.py` (max 1500 px, wycinki/kafelki). Nigdy `Matrix(2,2)` na dużych stronach (PZT ma 4252 pt szerokości).
- Przed wczytaniem obrazu: `python renderuj_pdf.py --sprawdz plik.png`. Nie wczytuj obrazów > 1500 px; nie więcej niż ok. 15 obrazów na sesję.
- **Zapisuj postęp do repo** po każdym etapie w `prace/POSTEP.md`. Gdy sesja się zablokuje: nowa sesja, kontynuacja od tego pliku.

## 7. Co już wiadomo (NIEZWERYFIKOWANE – sprawdź w pkt 3)
- Układ: PL-2000 strefa 6 (EPSG 2177), wysokości PL-KRON86-NH (dokumentacja geol.-inż. to podaje). W CAD X = E (6 433 xxx), Y = N (5 658 xxx).
- Geometria ścianki, hal i granicy została odczytana w poprzednich sesjach z rzutu zabezpieczenia wykopu (PDF wektorowy z siatką krzyży co 50 m; **tego PDF nie ma już w repo**) i zapisana w `prace/obliczenia_v1/_skrypt/dane/geometria_G.json` (ścianka: pole 20 661,7 m², obwód 563,5 m; 8 obrysów hal razem 11 927,1 m²; granica z rysunku 25 611 m² wobec oficjalnych 25 290,00 m²). Poprawny DXF z tymi obrysami: `prace/obliczenia_v1/04_gstarcad_siatka/obrysy_projektanta_i_siatka_dz190.dxf`.
- **Podkład użytkownika** `prace/dane_wejsciowe_uzytkownika/podklad_uzytkownika_SZKIC_v0.dwg` to **DWG** (mimo wcześniejszego rozszerzenia .dxf; ezdxf go nie czyta – użyj `prace/obliczenia_v1/_skrypt/odczyt_dwg/`, odczyt gotowy w `..._odczyt.json`). Jego warstwy `OBRYS_HAL` i `7_SCIANKA_ORIENTACYJNA` zawierają **pierwszy szkic użytkownika, o 3,7% za mały** (hale 1 429,13 / 1 024,67 / 1 507,53 m²; ścianka 19 244,63 m²) – **NIE używać**. Warstwa `A-granica inwest.` (17 wierzchołków, otwarta polilinia, 25 105,44 m² wobec 25 290,00 m²) to granica działki narysowana przez użytkownika – **kandydat** do granicy (do porównania z MDCP).
- Teren istniejący: średnio 124,66 m npm w obrysie ścianki (pomiar z PZT + otwory). Siatka 10 m z rzutu zabezpieczenia jest zawyżona o ok. 0,1 m i ma literówki – nie używać wprost.
- Poprzednie wyniki (inne założenia, nieaktualne): humus ok. 15,4 tys. m³, grunt z wykopu 29,3 tys. m³ (A) i 42,0 tys. m³ (B).

## 8. Decyzje użytkownika (wszystkie dotychczasowe pytania rozstrzygnięte)
1. Zieleń na gruncie = tylko „zieleń na gruncie rodzimym" (6 443,06 m²). Geokrata na parkingach = zasady jak dla nawierzchni utwardzonych.
2. Zieleń na stropie garażu (oraz geokrata na stropie i dachy) = jak hale: cały wykop z tego obszaru na wywóz, dowożony dedykowany substrat.
3. Poza ścianką teren jest podnoszony do rzędnej projektowej (bez wykopów).
4. Granicę działki odczytaj z **mapy do celów projektowych** (jest w repo). Jeśli się nie da, użytkownik doda wierzchołki ręcznie z Geoportalu do `prace/dane_wejsciowe_uzytkownika/wierzcholki_granica_dzialki.txt` (E i N, tabulator).
5. Tony z dokładnością 0,000.
6. Zapas humusu 10% zostaje.
7. Ogrody deszczowe (253,00 m²): poza opracowaniem, dedykowany substrat jak na halach (w bilansie jak hale, bez gruntu z odkładu).
8. Rzut zabezpieczenia wykopu (PDF) i przekrój B-B budynku 2C są zbędne i usunięte z repo. Zastępują je: podkład użytkownika (DWG, ale uwaga na stary szkic – pkt 7) oraz rysunek „Przekroje terenowe z naniesionym średnim poziomem wody gruntowej". Grubość chudego betonu (10 cm) pochodziła z przekroju B-B – potwierdź w dokumentacji (projekt geotechniczny wspomina o chudym betonie).

**Otwarte:** brak. Jeśli dokumentacja wykaże niejasność, zapytaj użytkownika.

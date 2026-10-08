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
1. Przeczytaj ten plik, `prace/MAPA_DOKUMENTOW.md`, `prace/FAKTY_Z_USUNIETYCH_DOKUMENTOW.md`, `prace/OBRAZY_LIMIT_2000PX.md` i `ZADANIA_I_WERYFIKACJA.md`.
2. **Zapoznaj się z dokumentacją** przed jakimikolwiek obliczeniami (czytaj najpierw teksty z `prace/ekstrakty_tekstu/`). Kolejność:
   1. **dokumentacja geologiczno-inżynierska** (`dokumentacja/01_geologiczno_inzynierska/`) – **największy priorytet**;
   2. projekt geotechniczny (`02_...`) – pomocniczo;
   3. opinia geotechniczna (`03_...`) – pomocniczo;
   4. PZT i przekroje terenowe z poziomem wody gruntowej (`04_...`);
   5. obrysy użytkownika `*_checked` (`prace/dane_wejsciowe_uzytkownika/`) – obowiązująca geometria hal, ścianki i granicy.
   Użytkownik **świadomie usunął z repo duże pliki** (MDCP, PZT garaże, rzuty fundamentów, mapy 4.2–4.8, analizy laboratoryjne, CPTU): wszystko naniósł na DXF i woli **uzupełniać brakujące dane w obliczeniach**, niż zapychać sesję plikami. Gdy czegoś brakuje: (a) sprawdź ekstrakty i `prace/FAKTY_Z_USUNIETYCH_DOKUMENTOW.md`, (b) odzyskaj plik z historii gita (komenda w `prace/MAPA_DOKUMENTOW.md`; nie renderuj go dużym zoomem), (c) dopiero potem zapytaj użytkownika.
3. **Zweryfikuj wszystkie dotychczasowe ustalenia** w oparciu o dokumentację z repo (lista w `ZADANIA_I_WERYFIKACJA.md`, w tym: **rzędne, mapa, lokalizacja obrysów hal garażowych i ścianek wykopu**).
   Wynik zapisz w `prace/WERYFIKACJA_raport.md`. Niezgodności zgłoś użytkownikowi **przed** obliczeniami.
4. Dopiero potem obliczenia i arkusz.

Hierarchia źródeł przy sprzeczności: dokumentacja geologiczno-inżynierska > projekt geotechniczny > opinia geotechniczna > rysunki projektu (PZT, przekroje terenowe, fundamenty) > obrysy użytkownika (geometria) > dotychczasowe obliczenia (`prace/obliczenia_v1`).
Dane z poprzednich sesji (również z `prace/obliczenia_v1`) traktuj jako **niezweryfikowane**, dopóki nie sprawdzisz ich w dokumentacji.

## 4. Założenia bilansu
### 4.1 Warianty wykopu (oba liczyć obok siebie)
- **Wariant A** – wykop tylko pod garażami + rozkop: obrys garażu (hale, zadaszone dojazdy i rampy – pkt 19) + przestrzeń robocza **1,0 m**, dalej skarpa **1:1,5** do terenu po zdjęciu humusu; przy ściance obcięte, od południa skarpa swobodna (pkt 12, 14). Ta sama zasada co wariant „A (skarpy 1:1,5)” w `prace/obliczenia_v1`; rozkład krok po kroku – arkusz WARIANT_A.
- **Wariant B** – cały obszar w ściance wykopany do dna, ściany pionowe; od południa skarpa 1:1,5 (pkt 12, 22).
- Dno wykopu: **121,86 m npm** (pkt 13; v1 przyjmowało 121,97). Elementy głębsze (do 120,00) – osobna pozycja. Szczegóły: `prace/FAKTY_Z_USUNIETYCH_DOKUMENTOW.md`.

### 4.2 Pas poza ścianką
Pas działki poza ścianką jest **odhumusowany, bez wykopów** (nie obniżamy gruntu rodzimego) i **podnoszony do rzędnej projektowej** (wbudowanie wg stref, pkt 4.4).
Jeśli rzędna podbudowy wychodzi poniżej powierzchni po zdjęciu humusu, nie kopiemy – zgłoś takie miejsca użytkownikowi.
**Wyjątek (pkt 21):** pod projektowaną drogą, chodnikiem, placem i parkingiem wymieniamy grunt rodzimy w strefie przemarzania – wykop do 1,00 m pod nawierzchnią (także poza ścianką).

### 4.3 Humus i nasyp
- Humus zdejmowany z całej działki 1/90 (obrys ścianki + pas poza ścianką).
- **Humus na odkład** = 0,25 m × powierzchnia zieleni na gruncie rodzimym × **1,10** (zapas 10% – decyzja użytkownika); nie więcej niż zebrano. Przy 6 443,06 m² to 1 771,842 m³. Nadwyżkę humusu liczymy do wywozu.
- **Nasyp niekontrolowany: 100% na wywóz.**

### 4.4 Zasady wbudowania wg stref (rzędna docelowa z dokumentacji)
| Strefa | Co wbudowujemy | Co w bilansie |
|---|---|---|
| **Hale garażowe** (pod obrysem hal) wraz z **zielenią na stropie garażu, geokratą na stropie i dachami** | nic z wykopu; na stropie **dowożony dedykowany substrat** (poza bilansem gruntu rodzimego) | **cały wykop z tego obszaru na odkład i do zasypu** (pkt 18; wcześniej: wywóz) |
| **Tereny zielone na gruncie** | **0,25 m humusu** (z odkładu) + poniżej, **do poziomu dna wykopu, ziemia z odkładu** | humus 0,25 m × powierzchnia; reszta to grunt z odkładu |
| **Nawierzchnie utwardzone** (w tym **geokrata na parkingach**) | **0,50 m konstrukcji drogowej** (kruszywo – **poza bilansem**) + 0,50 m **dowożonego gruntu niewysadzinowego** (do 1,00 m – pkt 15) + poniżej, **do dna wykopu, grunt z odkładu** | grunt niewysadzinowy (dowóz) i grunt poniżej 1,00 m |
| **Ogrody deszczowe** (253,00 m²) | **0,30 m dedykowanego substratu** (poza bilansem) + poniżej **grunt rodzimy z odkładu** (pkt 20) | tylko grunt pod substratem |
| **Nasyp niekontrolowany** | nigdy | 100% na wywóz |

**Definicje stref (rozstrzygnięte przez użytkownika):**
- **Tereny zielone na gruncie** = wyłącznie pozycja „zieleń na gruncie rodzimym" z tabeli Bilans terenu na PZT (6 443,06 m²; wg tekstu PZT zawiera już części miejsc rekreacji i placu zabaw na gruncie rodzimym – do sprawdzenia). Nic więcej nie liczymy jako zieleń.
- **Geokrata na parkingach (na gruncie, 980,05 m²)** = **nawierzchnia utwardzona**: 0,50 m konstrukcji (poza bilansem) + poniżej grunt z odkładu do dna wykopu. Humusu 0,25 m tam nie wbudowujemy.
- **Zieleń na stropie garażu (3 975,11 m² – w tabeli PZT literówka 3 575,11, pkt 17), geokrata na stropie (173,70 m²), zieleń na dachu (1 824,12 m²)** = strefa „hale" (wykop na odkład – pkt 18, dedykowany substrat dowożony).

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
- Rzędne z tekstu PZT odtworzysz jednym poleceniem: `prace/obliczenia_v1/_skrypt/wyciagnij_dane_z_pdf.py`. Geometrii z PDF już nie odtwarzamy (rzutu zabezpieczenia nie ma w repo) – obowiązują pliki `*_checked`.
  Teksty dokumentów: `prace/obliczenia_v1/_skrypt/wyciagnij_tekst_dokumentow.py`.
- Silnik obliczeń rastra 0,5 m (teren, humus, skład gruntu): `prace/obliczenia_v1/_skrypt/oblicz_bilans.py` (do przeróbki pod nowe założenia).

### 6a. Obrazy – twardy limit 2000 px (wcześniej zablokował sesję)
Użytkownik **nie dołącza PDF-ów ani zrzutów ekranu do rozmowy** (repo jest dołączone do sesji); ty też nie ładuj całych PDF-ów jako obrazów.
Gdy w rozmowie jest **ponad 20 obrazów**, każdy obraz (także stary) musi mieć **≤ 2000 px** na każdym boku, inaczej sesja blokuje się na stałe (błąd „image dimensions exceed max allowed size for many-image requests"). Szczegóły i tabela dokumentów: `prace/OBRAZY_LIMIT_2000PX.md`.
- **Najpierw tekst** (`prace/ekstrakty_tekstu/`, dane wektorowe PDF). Obraz tylko gdy nie ma innej drogi.
- **Obrazy renderuj tylko** `prace/obliczenia_v1/_skrypt/renderuj_pdf.py` (max 1500 px, wycinki/kafelki). Nigdy `Matrix(2,2)` na dużych stronach (PZT ma 4252 pt szerokości).
- Przed wczytaniem obrazu: `python renderuj_pdf.py --sprawdz plik.png`. Nie wczytuj obrazów > 1500 px; nie więcej niż ok. 15 obrazów na sesję.
- **Zapisuj postęp do repo** po każdym etapie w `prace/POSTEP.md`. Gdy sesja się zablokuje: nowa sesja, kontynuacja od tego pliku.

## 7. Co już wiadomo (stan sprzed weryfikacji)
> Zweryfikowane – wynik w `prace/WERYFIKACJA_raport.md`. Przy sprzeczności obowiązuje pkt 8 (np. geometria przeliczona do PZT, `prace/dane/geometria.json`). Aktualny wynik bilansu: `wyniki/CZYTAJ_NAJPIERW.md`.

- Układ: PL-2000 strefa 6 (EPSG 2177), wysokości PL-KRON86-NH (dokumentacja geol.-inż. to podaje). W CAD X = E (6 433 xxx), Y = N (5 658 xxx).
- **Obrysy obowiązujące (od użytkownika, poprawione):** w `prace/dane_wejsciowe_uzytkownika/`: `wierzcholki_polilinii_hala1-8_checked.txt` (8 hal; hala 2 ma 6 wierzchołków i jest poprawna), `wierzcholki_polilinii_wykop_checked.txt` (ścianka wykopu, 11 wierzchołków, polilinia **otwarta**: odcinek zamykający nie istnieje w rzeczywistości i przecina jedną halę – wystawanie hali poza tak zamkniętą linię jest OK), `wierzcholki_polilinii_granica_działki_checked.txt` (17 wierzchołków, 25 105,56 m² wobec oficjalnych 25 290,00 m²) i `siatka_10m_dz190_checked.dxf` (ważne warstwy: `HALE_GARAZOWE`, `A-granica inwest.`, `7_SCIANKA_ORIENTACYJNA` – w niej 11-wierzchołkowy wykop i 3-wierzchołkowa pozostałość starego szkicu; pozostałe warstwy to stara siatka wstępna – nie używać).
- Pola z tych plików: ścianka 20 266,12 m², obwód 562,89 m; hale razem 12 078,68 m². Dla porównania odczyt z rysunku projektanta (v1, PDF usunięty): `prace/obliczenia_v1/_skrypt/dane/geometria_G.json` – hale 1, 3–8 zgodne z obrysami użytkownika w granicach +0,2–0,4% pola, ścianka 20 661,7 m².
- Pierwszy szkic użytkownika (hale i ścianka o 3,7% za małe) jest nieaktualny.
- Teren istniejący: średnio 124,66 m npm w obrysie ścianki (v1: czarne rzędne pomiarowe z PZT + otwory). Nowy `6. PZT.pdf` jest **spłaszczony do rastra** (jeden obraz 8503×5181 px, zero wektorów), ale **warstwa tekstowa jest nienaruszona**: 239 rzędnych terenu i 90 projektowych wychodzi identycznie jak z wersji wektorowej (`wyciagnij_dane_z_pdf.py`). Strefy (zieleń, nawierzchnie) trzeba wziąć z rastra (ok. 4,4 cm na piksel) albo odzyskać wektorowy PZT z historii gita (wypełnienia kolorami).
- Wnioski z usuniętych rzutów fundamentów i badań laboratoryjnych: `prace/FAKTY_Z_USUNIETYCH_DOKUMENTOW.md` (dno wykopu ok. 121,86, elementy do 120,00, szczelna ścianka z korkiem jet-grouting, gliny twardoplastyczne o IL 0,01–0,08, ρ 2,18–2,35).
- Poprzednie wyniki (inne założenia, nieaktualne): humus ok. 15,4 tys. m³, grunt z wykopu 29,3 tys. m³ (A) i 42,0 tys. m³ (B).

## 8. Decyzje użytkownika (wszystkie dotychczasowe pytania rozstrzygnięte)
1. Zieleń na gruncie = tylko „zieleń na gruncie rodzimym" (6 443,06 m²). Geokrata na parkingach = zasady jak dla nawierzchni utwardzonych.
2. Zieleń na stropie garażu (oraz geokrata na stropie i dachy) = jak hale, dowożony dedykowany substrat. *(Wywóz całego wykopu z tego obszaru – zmienione w pkt 18: grunt idzie do zasypu.)*
3. Poza ścianką teren jest podnoszony do rzędnej projektowej (bez wykopów; wyjątek – wymiana w strefie przemarzania pod drogami, chodnikami i parkingami, pkt 21).
4. Granica działki: 17 wierzchołków z `wierzcholki_polilinii_granica_działki_checked.txt` (użytkownik naniósł ją z mapy do celów projektowych na DXF).
5. Tony z dokładnością 0,000.
6. Zapas humusu 10% zostaje.
7. Ogrody deszczowe (253,00 m²): dedykowany substrat (poza bilansem). *(Bez gruntu z odkładu – zmienione w pkt 20: substrat 0,30 m, niżej grunt z odkładu.)*
8. Rzut zabezpieczenia wykopu (PDF) i przekrój B-B budynku 2C są zbędne i usunięte z repo. Zastępują je pliki `*_checked` oraz rysunek „Przekroje terenowe z naniesionym średnim poziomem wody gruntowej" (wrócił do repo). Podbeton C8/10 min. 10 cm potwierdzają rzuty fundamentów (zob. pkt 7).

**Decyzje z 8.10.2026 (odpowiedzi na pytania z `prace/WERYFIKACJA_raport.md`):**
11. Geometria: DXF `siatka_10m_dz190_checked_v2.dxf` – hale, granica i ścianka okazały się **takie same jak w v1** (pomniejszone o 0,37%). Obowiązuje geometria **przeliczona do PZT** (skala 1,003663; `prace/dane/geometria.json`, nowy podkład `wyniki/PODKLAD_dz190_v3.dxf`): granica 25 289,68 m², hale 12 167,36 m².
12. Od południa **nie ma ścianki** – wykop ze skarpą 1:1,5 (w A i w B). W wariancie B podnóże skarpy = prosty odcinek między końcami ścianki, poszerzony o hale 7 i 8 z przestrzenią roboczą 1,0 m. Za ścianką (W, N, E) nie kopiemy.
13. Dno wykopu **121,86**; fundamenty głębsze (pogrubienia, rdzenie, szyby wind, studzienki) liczone **osobno** (wywóz).
14. Wariant A: przestrzeń robocza 1,0 m i skarpa 1:1,5 (obcięte do ścianki).
15. Zieleń: wszystkie grunty rodzime z wykopu poza glebą i nasypem nadają się do zasypu. Nawierzchnie: **strefa przemarzania 1,00 m** – od 0,50 do 1,00 m pod nawierzchnią **dowożony grunt niewysadzinowy**, poniżej 1,00 m grunt rodzimy z odkładu.
16. Gęstości z tabeli 8 DGI (piaski wg wilgotności z kart, gliny – średnia z zakresu); gleba 1,60 i nasyp 1,80 t/m³ (brak w tabeli 8); spulchnienie (humus 1,25, nasyp 1,25, gliny 1,30, piaski 1,15) tylko informacyjnie.
17. Zieleń na stropie = **3 975,11 m²** (PZT wektorowy: 3 979,48 m²; DXF v2 użytkownika ma 3 572,61 m² – brakuje ok. 370 m²). Strefy brane z wypełnień wektorowego PZT. Woda wg otworów DGI (nie 124,30). Otwór 12: E = 6 433 688,2. Analiza tylko otworów 2–24 z działki 1/90 + CPTU 10, 12, 18, 21, 24 (CPTU uśrednione z otworem w tym samym miejscu).

**Decyzje – trzecia runda (odpowiedzi na pytania z `wyniki/CZYTAJ_NAJPIERW.md`):**
18. **Grunt spod hal i zadaszonych dojazdów** jest przydatny i idzie **na odkład i do zasypu** (DGI, projekt i opinia geotechniczna nie zawierają przeciwwskazań; PG s. 12 dopuszcza grunt z wykopu do zasypów). Cały grunt rodzimy z wykopu (poza glebą, nasypem i fundamentami głębszymi) jest dostępny do ponownego wbudowania. Warunki (pora sucha, ochrona glin przed wodą, warstwy ≤ 0,30 m, Is > 0,95, odsączenie piasków nawodnionych, oddzielenie IVa) – arkusz GRUNTY.
19. **Rampy** (4 pochylnie z murami, ok. 554 m²) i **zadaszone dojazdy** poza obrysami hal (ok. 396 m²) = część garażu (w A wykop z przestrzenią roboczą i skarpą).
20. **Ogrody deszczowe:** 0,30 m substratu (poza bilansem), poniżej grunt rodzimy z odkładu (w A i w B).
21. **Wymiana gruntu w strefie przemarzania** tam, gdzie jest projektowana droga, chodnik, plac lub parking: wykop do 1,00 m pod nawierzchnią (urobek na odkład), w to miejsce grunt niewysadzinowy z dowozu. W innych miejscach poza wykopem nie kopiemy – tylko informacja (sekcja 10 arkusza WYNIK).
22. **Wariant B od południa:** podnóże skarpy na prostym odcinku między końcami ścianki, poszerzone o hale 7 i 8 z przestrzenią roboczą 1,0 m – zostaje.
23. Rozbieżność geometrii DXF v2 (0,37%) zaakceptowana – zostaje geometria przeliczona do PZT (pkt 11). Zieleń na stropie z PZT (pkt 17) – zaakceptowana.

24. Drobne miejsca poza ścianką, gdzie projekt wchodzi w grunt rodzimy (ok. 39 m³): wartość znikoma – **pomijamy** (nie kopiemy, nie liczymy).
25. Spód wykopu pod rampą = powierzchnia rampy − 0,71 m – **zostaje**.
26. Wymiary studzienek z rzutu 1A przyjęte dla wszystkich budynków – **zostaje**, chyba że analiza pozostałych rzutów pokaże błąd.
Nasyp niekontrolowany wg stref z mapy 4.3 DGI (otwory 5, 17, 20) – bez uwag.

**Pozostałe ustalenia:**
9. Użytkownik usunął z repo MDCP, PZT garaże, rzuty fundamentów PW_*, mapy 1–4.8 (poza 4.1), CPTU i analizy laboratoryjne, bo wszystko naniósł na DXF. **Weryfikacja (sesja z 7.10) wykazała wyjątki:** rzuty fundamentów (poziomy płyty i głębsze elementy) i zestawienie F (wilgotność, IL, gęstość) niosą dane, których nie ma w DXF – ich wyciąg jest w `prace/FAKTY_Z_USUNIETYCH_DOKUMENTOW.md`. Rzędne terenu z MDCP nie trafiły do DXF (rzędne w DXF to stare wstępne).
10. Hala 2 (6 wierzchołków) jest poprawna. Ścianka jest obrysem otwartym; hala przecięta linią zamykającą nie jest błędem.

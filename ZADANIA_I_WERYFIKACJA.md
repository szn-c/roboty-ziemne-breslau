# Plan prac i lista weryfikacji (dla nowej sesji)

Zasady: `USTALENIA.md` (to samo co `.kiro/steering/ustalenia.md`).
**Najpierw dokumentacja i weryfikacja, dopiero potem obliczenia.** Weryfikację robi się po uruchomieniu nowej sesji, na podstawie dokumentacji z repo.

## Część 1. Kolejność prac

| Krok | Co zrobić | Wynik (plik) | Gotowe, gdy |
|---|---|---|---|
| T0 | Przeczytaj `USTALENIA.md`, obejrzyj strukturę repo, zainstaluj biblioteki. **Znajdź wszystkie dokumenty w repo** (mogą leżeć poza `dokumentacja/`) i zapisz ścieżki. Uruchom `wyciagnij_tekst_dokumentow.py` dla nowych dokumentów. **Przeczytaj `prace/OBRAZY_LIMIT_2000PX.md`** (limit obrazów!). Zakładaj `prace/POSTEP.md`. | `prace/MAPA_DOKUMENTOW.md` | wiesz, gdzie jest każdy dokument (w tym mapa do celów projektowych) |
| T1 | Przeczytaj dokumentację **w kolejności priorytetu** (geologiczno-inżynierska, projekt geotechniczny, opinia). Wypisz: warstwy i ich opis, zalecenia robót ziemnych, zwierciadło wody i wahania, odwodnienie, skarpy, przydatność gruntów do nasypów, gęstości, ewentualne spulchnienie. | `prace/ekstrakt_dokumentacji.md` (z numerami stron) | każdy parametr ma źródło |
| T2 | **Weryfikacja ustaleń** (Część 2). | `prace/WERYFIKACJA_raport.md` | każda pozycja: ZGODNE / NIEZGODNE / BRAK DANYCH + dowód |
| T3 | Zgłoś użytkownikowi niezgodności i pytania otwarte (`USTALENIA.md` pkt 8). Poczekaj na odpowiedzi. | – | decyzje zapisane w `USTALENIA.md` |
| T4 | Zaktualizuj dane wejściowe: tabela 17 otworów (ze źródłem: karta/strona), geometria hal/ścianki/granicy, rzędne terenu, rzędne projektowe. | `prace/dane/*.csv, *.json` | dane mają źródła |
| T5 | **Strefy:** hale, zieleń na gruncie, nawierzchnie utwardzone, inne (z PZT i dokumentacji z rzędnymi). Pola w m² z dokładnością 0,01; kontrola z tabelą „Bilans terenu" na PZT. | `prace/strefy.*` | sumy pól zgadzają się z PZT |
| T6 | **Klasyfikacja gruntów** przydatne / nieprzydatne wg dokumentacji. | arkusz GRUNTY | każde kryterium ma źródło |
| T7 | **Obliczenia** obu wariantów (A, B) wg zasad stref z `USTALENIA.md` pkt 4.4. | – | kontrola bilansu = 0 |
| T8 | **Arkusz Excel** (format 0,00 m², 0,000 m³, żywe formuły + wartości zapisane, żółte pola decyzji użytkownika), niezależna weryfikacja formuł. Raport po polsku, prostym językiem. | `wyniki/BILANS_...xlsx`, `wyniki/CZYTAJ_NAJPIERW.md` | użytkownik ma tabelę i krótki opis |

Proponowany układ arkusza: WYNIK (A i B obok siebie), ZALOZENIA (żółte pola), GRUNTY (klasyfikacja), STREFY (pola i miąższości), OBLICZENIA, NIEPEWNOSC, KONTROLE.

## Część 2. Lista weryfikacji (wykonać w T2, nie wcześniej)

Kolumna „Dotychczas" to **tylko wiedza z poprzednich sesji, niezweryfikowana**. Nie zakładaj, że jest prawdziwa.

### Układ odniesienia i mapa
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| U1 | PL-2000 strefa 6 (EPSG 2177), wysokości PL-KRON86-NH | dokumentacja geol.-inż. tak podaje | przeczytać w dokumentacji i w rzędnych fundamentów |
| U2 | Układ współrzędnych i położenie obrysów jest zgodne (PL-2000/6, wysokości PL-KRON86-NH) | dokumentacja geol.-inż. podaje układ; obrysy `*_checked` użytkownika zgadzają się z odczytem z rysunku projektanta (hale 1, 3–8: pola +0,2–0,4%, środki do ok. 1 m) | sprawdzić zgodność obrysów z siatką/współrzędnymi na PZT i na przekrojach terenowych oraz z otworami (4.1) |
| U3 | PZT w skali 1:250, obrót ok. 7,37° względem układu | zgodność z rzutem zabezpieczenia na 649 wspólnych rzędnych (śr. różnica 0,05/0,14 m) | porównać z dokumentacją z rzędnymi |
| U4 | Mapa 4.1 (raster 1:1000) jest zgodna z PZT co do położenia otworów i granicy | nie sprawdzano | nałożyć otwory z tabeli współrzędnych na mapę i granicę |

### Obrysy i granice
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| G1 | **Obrysy 8 hal** (`wierzcholki_polilinii_hala1-8_checked.txt`): pola 1528,37 / 1212,39 / 1528,36 / 1612,25 / 1528,38 / 1528,38 / 1528,38 / 1612,17 m²; razem 12 078,68 m² | hala 2 (6 wierzchołków) potwierdzona przez użytkownika jako poprawna; rzuty fundamentów usunięte (obrysy naniesione na DXF) | porównać z PZT; rozbieżność z odczytem z rysunku projektanta tylko przy hali 2 (+11%), reszta +0,2–0,4% |
| G2 | **Ścianka wykopu** (`..._wykop_checked.txt`): 11 wierzchołków, polilinia **otwarta**; pole po sztucznym domknięciu 20 266,12 m², obwód 562,89 m | użytkownik: odcinek zamykający nie istnieje i przecina jedną halę (to nie błąd); rysunek projektanta dawał 20 661,7 m² | ustalić, jak definiujemy granicę wykopu w miejscu otwarcia ścianki (zamknięcie przez obrys hali?) i sprawdzić odległości hala–ścianka (hala 1 blisko ścianki) |
| G3 | **Granica działki** (`..._granica_działki_checked.txt`): 17 wierzchołków, 25 105,56 m² (oficjalnie 25 290,00 m², −0,73%) | użytkownik naniósł ją z MDCP na DXF; wcześniejszy odczyt z rysunku projektanta: 25 611 m² | zaakceptować plik użytkownika; różnica 184 m² do pola oficjalnego wynika z dokładności odczytu |
| G4 | Dotychczasowy szkic użytkownika jest o 3,7% za mały | skala 1,0371, odchyłka 0,13 m | tylko informacja; nie używać szkicu |
| G5 | 17 otworów leży w obrębie działki 1/90 (2, 3, 5, 7, 9–12, 14–18, 20, 21, 23, 24) | wybór z mapy 4.1; dokumentacja ma otwory 2–40 | sprawdzić każdy otwór względem granicy 1/90; otwory 25–40 prawdopodobnie na 1/97 |

### Rzędne
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| R1 | ±0,00 = 126,00 m npm | z PZT i przekroju | potwierdzić w dokumentacji z rzędnymi |
| R2 | Posadzka garażu 122,57 (−3,43); korytka −3,51 | z przekroju B-B i opisów na rzucie | potwierdzić; sprawdzić, czy wszystkie hale mają ten sam poziom i czy są miejsca głębsze (−3,60?) |
| R3 | **Dno wykopu** | v1: 121,97 (= 122,57 − 0,50 − 0,10). Rzuty fundamentów: d.k. płyty −4,04 (**121,96**), podbeton C8/10 ≥ 10 cm pod fundamentami → ok. **121,86**; posadzka −3,43 leży na nadbetonie ok. 11 cm nad płytą; elementy głębsze do −6,00 (120,00) | uzgodnić z użytkownikiem dno wykopu (121,86 czy 121,97); zmapować elementy głębsze (powierzchnie i głębokości) z przekrojów A-A…I-I na rzutach (odzyskać PW_* z gita, patrz `prace/MAPA_DOKUMENTOW.md`) |
| R4 | **Teren istniejący** (model): średnio 124,66 m npm w obrysie ścianki | czarne rzędne pomiarowe z tekstu PZT (239) + otwory; zgodność rzędnych otworów z PZT: śr. +0,017 m, odch. std. 0,062 m (n = 16); rzędne w warstwach DXF użytkownika to stare wstępne (z 17 otworów) – nie MDCP | porównać z przekrojami terenowymi (8.) i otworami; MDCP usunięty – nie ma niezależnego źródła poza PZT |
| R5 | Teren istniejący – **siatka 10 m z rzutu zabezpieczenia** jest zawyżona o 0,08–0,11 m i ma literówki (np. 126,2) | tak wynikało z porównania | potwierdzić albo odrzucić; nie używać wprost |
| R6 | **Teren projektowany**: ok. 125,98 przy narożnikach budynków; 125,40–125,98 (śr. 125,77) między halami; 124,40–125,96 (śr. 125,52) poza ścianką; przekrój: 125,89 | z napisów na PZT, 90 punktów | wziąć pełne rzędne projektowe z nowej dokumentacji (podział na strefy) |
| R7 | Rzędne otworów H (zaokrąglone do 0,1 m) | z tabeli DGI | porównać z mapą 4.1, PZT i rzędnymi |

### Dane geologiczne (największy priorytet)
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| D1 | Profile 17 otworów (grubości humusu, nasypu, warstw) wpisane ręcznie z kart 5.x | w `prace/obliczenia_v1/_skrypt/generuj_pliki.py` (słownik `W`) | **sprawdzić każdą kartę** przeciw tabeli; zapisać źródło (karta/strona) |
| D2 | Nasyp niekontrolowany | karty: otwory 5, 17, 20; tekst dokumentacji: 5, 17, 23 (sprzeczność) | rozstrzygnąć na podstawie pełnej dokumentacji (karty, mapa 4.3) |
| D3 | Otwór 12: współrzędna Y uszkodzona w źródle; otwór 17: symbol na mapie przesunięty; otwór 11: symbol `saclSi` to prawdopodobnie literówka (piasek, warstwa IIb) | zgłoszone wcześniej | sprawdzić w pełnej tabeli współrzędnych |
| D4 | Zwierciadło wody: użyto „ustabilizowanego" (0,9–3,7 m p.p.t.) | badania 15–31.07.2025 (okres suchy); dokumentacja: wahania co najmniej ±0,5 m, woda w wkładkach piasku, swobodna i naporowa, „nie zawsze możliwy pomiar" | ustalić poziom miarodajny do odwodnienia i do oceny wilgotności gruntu |
| D5 | Grubość gleby: 0,40–0,80 m w 17 otworach | dokumentacja podaje maksimum 0,90 m (prawdopodobnie inny otwór) | sprawdzić wszystkie otwory |
| D6 | Przydatność gruntów do nasypów | nie ustalono | wyciągnąć kryteria z dokumentacji i projektu/opinii geotechnicznej |
| D7 | Współczynniki spulchnienia (humus 1,25; nasyp 1,25; glina 1,30; piasek 1,15) i gęstości | v1: typowe wartości (glina 2,1 t/m³); badania lab. (F): ρ glin 2,18–2,35 g/cm³, piaski wn 14,6–21,0% | zastąpić wartościami z tabeli parametrów (zał. 8), badań F i projektu geotechnicznego; spulchnienie z projektu/opinii lub zapytać użytkownika |

| R8 | Szczelne zabezpieczenie wykopu po obwodzie z korkiem jet-grouting (uwagi na rzutach fundamentów) | w uwagach ogólnych rzutów PW_*, nie w tekście PDF | uwzględnić przy założeniach o odwodnieniu i wykopie; potwierdzić w projekcie geotechnicznym i opinii |
| D8 | Przydatność glin do wbudowania | badania F: 6 próbek glin twardoplastycznych (IL 0,01–0,08), wn tylko 0–2 pp powyżej Wp; założenie v1 „gliny pod wodą = mokre, nieprzydatne" nieudowodnione | oprzeć klasyfikację na dokumentacji (Wopt/Proctor, kryteria dla nasypów w projekcie geotechnicznym) |

### Powierzchnie zagospodarowania (PZT, „Bilans terenu")
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| Z1 | Działka 25 290,00; zabudowa 6 680,59; utwardzone 6 899,75 (w tym rampy 553,77); zieleń na gruncie rodzimym 6 443,06; ogrody deszczowe 253,00; geokrata na gruncie 980,05; zieleń na stropie garażu 3 575,11; geokrata na stropie 173,70; zieleń na dachu 1 824,12 | odczytane z tekstu PZT | sprawdzić arytmetykę; zmapować te powierzchnie do stref w T5 (zieleń = tylko „zieleń na gruncie rodzimym"; geokrata na gruncie = nawierzchnia; zieleń na stropie, geokrata na stropie, dachy i ogrody deszczowe = jak hale; patrz USTALENIA.md pkt 4.4) |

### Metoda
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| M1 | Rzędne z PZT można odtworzyć skryptem | `wyciagnij_dane_z_pdf.py`: 239 rzędnych terenu i 90 projektowych identyczne jak wcześniej (nowy PZT ma nienaruszoną warstwę tekstową); geometrii z PDF już nie odtwarza (rzutu zabezpieczenia nie ma) | uruchomić skrypt |
| M2 | Kontrola metodą siatki 10 m zgadza się z rastrem 0,5 m | różnica −0,12% | powtórzyć dla nowych założeń |

## Część 3. Czego nie liczyć ponownie
Nie trzeba powtarzać analizy skali (3,7%), modelu terenu ani odtwarzania geometrii z PDF, jeśli weryfikacja (T2) wyjdzie zgodnie. Silnik rastra (`oblicz_bilans.py`, `eg_model.py`) można wykorzystać po dostosowaniu do nowych założeń stref.

# Plan prac i lista weryfikacji (dla nowej sesji)

Zasady: `USTALENIA.md` (to samo co `.kiro/steering/ustalenia.md`).
**Najpierw dokumentacja i weryfikacja, dopiero potem obliczenia.** Weryfikację robi się po uruchomieniu nowej sesji, na podstawie dokumentacji z repo.

## Część 1. Kolejność prac

| Krok | Co zrobić | Wynik (plik) | Gotowe, gdy |
|---|---|---|---|
| T0 | Przeczytaj `USTALENIA.md`, obejrzyj strukturę repo, zainstaluj biblioteki. **Znajdź wszystkie dokumenty w repo** (mogą leżeć poza `dokumentacja/`) i zapisz ścieżki. Uruchom `wyciagnij_tekst_dokumentow.py` dla nowych dokumentów. | `prace/MAPA_DOKUMENTOW.md` | wiesz, gdzie jest każdy dokument (w tym mapa do celów projektowych) |
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
| U2 | Siatka krzyży co 50 m na rzucie zabezpieczenia; napisy 6433700 (E) i 5659050 (N) przy jednym krzyżu | 20 krzyży, skala 1:1270,5, odchyłka 1,4 cm | porównać z siatką/współrzędnymi w nowej dokumentacji z rzędnymi i obrysami |
| U3 | PZT w skali 1:250, obrót ok. 7,37° względem układu | zgodność z rzutem zabezpieczenia na 649 wspólnych rzędnych (śr. różnica 0,05/0,14 m) | porównać z dokumentacją z rzędnymi |
| U4 | Mapa 4.1 (raster 1:1000) jest zgodna z PZT co do położenia otworów i granicy | nie sprawdzano | nałożyć otwory z tabeli współrzędnych na mapę i granicę |

### Obrysy i granice
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| G1 | **Obrysy 8 hal** (zewnętrzne, z rzutu zabezpieczenia): pola 1524,4 / 1092,2 / 1523,4 / 1605,8 / 1524,5 / 1523,3 / 1525,0 / 1608,6 m² | odtwarzalne z PDF (`wyciagnij_dane_z_pdf.py`) | **porównać z obrysami fundamentów** z nowej dokumentacji: położenie, wymiary, czy to zewnętrzna krawędź ściany/płyty |
| G2 | **Ścianka wykopu**: wielokąt 11 wierzchołków, pole 20 661,7 m², obwód 563,5 m (na rysunku ok. 565 mb) | łańcuch kresek niebieskiej linii; luka zamknięcia łańcucha 8,6 m (wierzchołki uzupełniono przecięciem prostych) | porównać z projektem zabezpieczenia; sprawdzić odległości hala–ścianka (0,78–8,9 m; hala 1 ma 0,78 m, czyli mniej niż 1,0 m przestrzeni roboczej) |
| G3 | **Granica działki** 1/90: oficjalnie 25 290,00 m² | z rysunku 25 611 m² (+1,27%); wierzchołki do odczytu z mapy do celów projektowych | odczytać wierzchołki z **mapy do celów projektowych** (jest w repo); jeśli się nie da, użytkownik doda je ręcznie z Geoportalu; porównać z 25 290,00 m² |
| G4 | Dotychczasowy szkic użytkownika jest o 3,7% za mały | skala 1,0371, odchyłka 0,13 m | tylko informacja; nie używać szkicu |
| G5 | 17 otworów leży w obrębie działki 1/90 (2, 3, 5, 7, 9–12, 14–18, 20, 21, 23, 24) | wybór z mapy 4.1; dokumentacja ma otwory 2–40 | sprawdzić każdy otwór względem granicy 1/90; otwory 25–40 prawdopodobnie na 1/97 |

### Rzędne
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| R1 | ±0,00 = 126,00 m npm | z PZT i przekroju | potwierdzić w dokumentacji z rzędnymi |
| R2 | Posadzka garażu 122,57 (−3,43); korytka −3,51 | z przekroju B-B i opisów na rzucie | potwierdzić; sprawdzić, czy wszystkie hale mają ten sam poziom i czy są miejsca głębsze (−3,60?) |
| R3 | **Dno wykopu 121,97** = 122,57 − płyta 0,50 (użytkownik) − chudy beton 0,10 (przekrój) | płyta 0,50 m podana przez użytkownika, nie z dokumentu | sprawdzić grubość płyty i warstw w dokumentacji konstrukcji; czy jest podsypka |
| R4 | **Teren istniejący** (model): średnio 124,66 m npm w obrysie ścianki | czarne rzędne pomiarowe z PZT + otwory; zgodność rzędnych otworów z PZT: śr. różnica +0,017 m, odch. std. 0,062 m (n = 16) | porównać z **mapą do celów projektowych**, mapą 4.1 i nową dokumentacją z rzędnymi; sprawdzić datę pomiaru |
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
| D7 | Współczynniki spulchnienia (humus 1,25; nasyp 1,25; glina 1,30; piasek 1,15) i gęstości (1,5 / 1,8 / 2,1 / 1,9 t/m³) | typowe wartości, nie z dokumentu | zastąpić wartościami z dokumentacji (tabela parametrów, załącznik 8) |

### Powierzchnie zagospodarowania (PZT, „Bilans terenu")
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| Z1 | Działka 25 290,00; zabudowa 6 680,59; utwardzone 6 899,75 (w tym rampy 553,77); zieleń na gruncie rodzimym 6 443,06; ogrody deszczowe 253,00; geokrata na gruncie 980,05; zieleń na stropie garażu 3 575,11; geokrata na stropie 173,70; zieleń na dachu 1 824,12 | odczytane z tekstu PZT | sprawdzić arytmetykę; zmapować te powierzchnie do stref w T5 (zieleń = tylko „zieleń na gruncie rodzimym"; geokrata na gruncie = nawierzchnia; zieleń na stropie, geokrata na stropie, dachy i ogrody deszczowe = jak hale; patrz USTALENIA.md pkt 4.4) |

### Metoda
| Nr | Ustalenie | Dotychczas | Jak sprawdzić |
|---|---|---|---|
| M1 | Geometria i rzędne odtwarzają się z PDF jednym skryptem | wszystkie pola i środki hal identyczne z danymi wersji 1 | uruchomić `wyciagnij_dane_z_pdf.py` i porównać |
| M2 | Kontrola metodą siatki 10 m zgadza się z rastrem 0,5 m | różnica −0,12% | powtórzyć dla nowych założeń |

## Część 3. Czego nie liczyć ponownie
Nie trzeba powtarzać analizy skali (3,7%), modelu terenu ani odtwarzania geometrii z PDF, jeśli weryfikacja (T2) wyjdzie zgodnie. Silnik rastra (`oblicz_bilans.py`, `eg_model.py`) można wykorzystać po dostosowaniu do nowych założeń stref.

# Dane od użytkownika

| Plik | Co to jest | Użycie |
|---|---|---|
| `podklad_uzytkownika_SZKIC_v0.dwg` | podkład z GstarCAD. To **DWG** (AutoCAD 2018), wcześniej błędnie nazwany `.dxf`. Zawiera moją starą siatkę 10 m oraz rysunki użytkownika. | czytaj narzędziem `prace/obliczenia_v1/_skrypt/odczyt_dwg/` (ezdxf DWG nie czyta) |
| `podklad_uzytkownika_SZKIC_v0_odczyt.json` | odczyt warstw: `A-granica inwest.`, `OBRYS_HAL`, `7_SCIANKA_ORIENTACYJNA`, `5_OTWORY` | do szybkiego wglądu bez narzędzi |
| `wierzcholki_granica_inwest_z_DWG_uzytkownika.txt` | 17 wierzchołków z warstwy `A-granica inwest.` (E, N w PL-2000). Polilinia była otwarta; pole po domknięciu 25 105,44 m² (oficjalnie 25 290,00 m²) | **kandydat** do granicy działki |
| `wierzcholki_zabezpieczenie_wykopu_SZKIC_...` i `wierzcholki_hala_1-8_SZKIC_...` | pierwszy szkic ścianki i hal | **o 3,7% za mały – nie używać**; to samo jest w warstwach `OBRYS_HAL` i `7_SCIANKA_ORIENTACYJNA` DWG |

**Uwaga:** w DWG tylko warstwa `A-granica inwest.` nadaje się do dalszej pracy. Poprawne obrysy ścianki i hal są w `prace/obliczenia_v1/04_gstarcad_siatka/obrysy_projektanta_i_siatka_dz190.dxf` (prawdziwy DXF) i w `prace/obliczenia_v1/_skrypt/dane/geometria_G.json`.
Jeśli użytkownik ma nowszy, poprawiony podkład (np. z właściwą ścianką), wgrywa go tutaj jako **prawdziwy DXF** (GstarCAD: ZAPISZ JAKO → DXF, wersja 2018 ASCII).

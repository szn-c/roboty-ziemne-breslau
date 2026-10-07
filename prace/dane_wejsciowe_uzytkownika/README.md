# Dane od użytkownika

## Obowiązujące (poprawione przez użytkownika)
| Plik | Zawartość |
|---|---|
| `wierzcholki_polilinii_hala1-8_checked.txt` | 8 obrysów hal garażowych (E, N w PL-2000); bloki podpisane `hala1`…`hala8`; hala 2 ma 6 wierzchołków (poprawna) |
| `wierzcholki_polilinii_wykop_checked.txt` | ścianka wykopu: 11 wierzchołków, polilinia **otwarta** (odcinek zamykający nie istnieje i przecina jedną halę) |
| `wierzcholki_polilinii_granica_działki_checked.txt` | granica działki 1/90: 17 wierzchołków; 25 105,56 m² (oficjalnie 25 290,00 m²) |
| `siatka_10m_dz190_checked.dxf` | DXF AutoCAD 2018 (tekstowy). **Ważne warstwy:** `HALE_GARAZOWE` (8 obrysów), `A-granica inwest.` (granica z opisami punktów A–N), `7_SCIANKA_ORIENTACYJNA` (11-wierzchołkowy wykop oraz 3-wierzchołkowa pozostałość starego szkicu). **Nieaktualne:** `0_SIATKA_10m`, `1_WEZLY`, `2_RZEDNE_TERENU` (stare wstępne rzędne z 17 otworów, nie z MDCP), `3_GLEBOKOSC_WYKOPU`, `4_HUMUS_m`, `5_OTWORY`, `6_KRZYZE…`, `8_OZNACZENIA…` |

## Historyczne (nie używać do obliczeń)
`podklad_uzytkownika_SZKIC_v0.dwg` (DWG, usunięty z repo przez użytkownika) – pierwszy szkic hal i ścianki, o 3,7% za mały. Pliki `*_odczyt.json` i `wierzcholki_granica_inwest_z_DWG_uzytkownika.txt`, jeśli są, pochodzą z niego (granica jest taka sama jak w `*_checked.txt`).
Narzędzie do odczytu DWG (gdyby się pojawił): `prace/obliczenia_v1/_skrypt/odczyt_dwg/`.

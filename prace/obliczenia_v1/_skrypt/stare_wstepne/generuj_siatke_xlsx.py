"""Dodaje do bilans_robot_ziemnych.xlsx arkusze: Dane_siatki, Obrys, Siatka, Pikiety (metoda siatki 10 x 10 m, bez Civil 3D)."""
import os
import sys

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generuj_siatke_gstarcad import DNO, KROK, SCIANKA, wezly  # noqa: E402
from generuj_pliki import OUT  # noqa: E402

SCIEZKA = os.path.join(OUT, "02_zestawienia_excel", "bilans_robot_ziemnych.xlsx")
ZOLTY = PatternFill("solid", fgColor="FFF2CC")
SZARY = PatternFill("solid", fgColor="D9D9D9")
ZIELONY = PatternFill("solid", fgColor="E2EFDA")
B = Font(bold=True)
cienka = Side(style="thin", color="999999")
RAMKA = Border(left=cienka, right=cienka, top=cienka, bottom=cienka)

wb = load_workbook(SCIEZKA)
for nazwa in ("Dane_siatki", "Obrys", "Siatka", "Pikiety"):
    if nazwa in wb.sheetnames:
        del wb[nazwa]

nodes, es, ns = wezly()
N_W = len(nodes)
R0 = 6                      # pierwszy wiersz danych w arkuszu Siatka
R1 = R0 + N_W - 1           # ostatni wiersz danych
NP = 600                    # pojemnosc arkusza Pikiety

# ---------------------------------------------------------------- Obrys
wo = wb.create_sheet("Obrys")
wo["A1"], wo["B1"], wo["C1"], wo["D1"], wo["E1"] = "Nr", "E (X) - wklej", "N (Y) - wklej", "E (liczba)", "N (liczba)"
for c in ("A1", "B1", "C1", "D1", "E1"):
    wo[c].font = B
    wo[c].fill = SZARY
wo["G1"] = "OBRYS SCIANKI (lub inny obszar liczenia). Wyczysc zolte B2:C41, potem wklej w komorke B2 dwie kolumny z pliku PLXY (E i N, bez naglowka). Do 40 wierzcholkow."
wo["G2"] = "Tekst z kropka dziesietna jest zamieniany na liczby automatycznie. Puste wiersze sa ignorowane."
wo["G3"] = "Domyslnie: obrys orientacyjny (+-3 m) odczytany z rysunku. Zastap go obrysem narysowanym w GstarCAD po dopasowaniu rzutu."
for k in range(2, 42):
    wo.cell(k, 1, k - 1)
    for col in (2, 3):
        wo.cell(k, col).fill = ZOLTY
    if k - 2 < len(SCIANKA):
        wo.cell(k, 2, SCIANKA[k - 2][0])
        wo.cell(k, 3, SCIANKA[k - 2][1])
    for col, src in ((4, "B"), (5, "C")):
        L = "D" if col == 4 else "E"
        if k == 2:
            f = f'=IF({src}2="","",VALUE(SUBSTITUTE({src}2&"",".",MID(1/2,2,1)))+0)'
        else:
            f = f'=IF({src}{k}="",${L}$2,VALUE(SUBSTITUTE({src}{k}&"",".",MID(1/2,2,1)))+0)'
        wo.cell(k, col, f).number_format = "0.000"
wo.cell(42, 1, "zamkn.")
wo.cell(42, 4, "=D2").number_format = "0.000"
wo.cell(42, 5, "=E2").number_format = "0.000"
for col, w in zip("ABCDE", (8, 20, 20, 16, 16)):
    wo.column_dimensions[col].width = w
wo.column_dimensions["G"].width = 110
wo.freeze_panes = "A2"

# ---------------------------------------------------------------- Pikiety
wp = wb.create_sheet("Pikiety")
for c, t in zip("ABCDEFG", ("E (X) - wklej", "N (Y) - wklej", "Z / tekst - wklej", "E", "N", "Z", "OK (1/0)")):
    wp[f"{c}1"] = t
    wp[f"{c}1"].font = B
    wp[f"{c}1"].fill = SZARY
wp["I1"] = "OPCJA: pikiety wysokosciowe terenu z mapy. Po PDFIMPORT i ALIGN w GstarCAD uzyj TXTXY i wklej trzy kolumny (E, N, tekst) w komorke A2 (do 600 wierszy)."
wp["I2"] = "Brane sa tylko wartosci w przedziale z arkusza Dane_siatki (B7:B8), np. 123,5-126,6. Inne (rzedne kanalow, numery) sa odrzucane."
wp["I3"] = "Gdy wklejisz >= 3 pikiet, rzedne terenu w wezlach siatki beda liczone z nich (srednia wazona odwrotnoscia kwadratu odleglosci, promien z Dane_siatki B9)."
for k in range(2, NP + 2):
    for col in (1, 2, 3):
        wp.cell(k, col).fill = ZOLTY
    wp.cell(k, 4, f'=IF(A{k}="",0,IFERROR(VALUE(SUBSTITUTE(A{k}&"",".",MID(1/2,2,1)))+0,0))')
    wp.cell(k, 5, f'=IF(B{k}="",0,IFERROR(VALUE(SUBSTITUTE(B{k}&"",".",MID(1/2,2,1)))+0,0))')
    wp.cell(k, 6, f'=IF(C{k}="",0,IFERROR(VALUE(SUBSTITUTE(C{k}&"",".",MID(1/2,2,1)))+0,0))')
    wp.cell(k, 7, f"=IF(AND(D{k}>0,E{k}>0,F{k}>=Dane_siatki!$B$7,F{k}<=Dane_siatki!$B$8),1,0)")
for col, w in zip("ABCDEFG", (18, 18, 18, 16, 16, 10, 10)):
    wp.column_dimensions[col].width = w
wp.column_dimensions["I"].width = 120
wp.freeze_panes = "A2"

# ---------------------------------------------------------------- Dane_siatki
wd = wb.create_sheet("Dane_siatki", index=wb.sheetnames.index("Bilans wstępny") + 1)
wd.column_dimensions["A"].width = 64
wd.column_dimensions["B"].width = 18
wd.column_dimensions["C"].width = 10
wd.column_dimensions["D"].width = 90
wd["A1"] = "SIATKA 10 x 10 m - parametry i wyniki (metoda węzłów, bez Civil 3D)"
wd["A1"].font = Font(bold=True, size=14)


def dr(r, opis, val, jedn="", uw="", wej=False, fmt="#,##0"):
    wd.cell(r, 1, opis)
    c = wd.cell(r, 2, val)
    c.number_format = fmt
    c.border = RAMKA
    c.fill = ZOLTY if wej else ZIELONY
    wd.cell(r, 3, jedn)
    wd.cell(r, 4, uw).alignment = Alignment(wrap_text=True)


wd["A2"] = "Żółte = dane, które możesz zmienić. Zielone = wyniki."
wd["A2"].font = Font(italic=True)
dr(3, "Rzędna dna wykopu", DNO, "m npm", "122,57 - płyta 0,50 - chudy beton 0,10. Kolumna piasków w arkuszu Siatka jest policzona TYLKO dla 121,97.", True, "0.00")
dr(4, "Odstęp siatki", KROK, "m", "stały (siatka w DXF ma 10 m)", False, "0")
dr(5, "Pole przypadające na węzeł", "=B4^2", "m²", "", False, "0")
dr(6, "Korekta rzędnych NMT (dodawana do kolumny NMT w arkuszu Siatka)", 0.16, "m", "ustalona z porównania z otworami", True, "0.00")
dr(7, "Rzędna terenu - minimum akceptowane dla pikiet", 123.5, "m npm", "odrzuca rzędne kanałów i studni", True, "0.0")
dr(8, "Rzędna terenu - maksimum akceptowane dla pikiet", 126.6, "m npm", "", True, "0.0")
dr(9, "Promień uwzględniania pikiet wokół węzła", 25, "m", "pikiety dalsze niż tyle są pomijane", True, "0")

wd["A11"] = "WYNIKI (korygowane o efekt brzegu obrysu)"
wd["A11"].font = B
rng = f"$K${R0}:$K${R1}"
dr(12, "Pole obrysu (wzór Gaussa)", "=ABS(SUMPRODUCT((Obrys!$D$2:$D$41-Obrys!$D$2)*(Obrys!$E$3:$E$42-Obrys!$E$2)-(Obrys!$D$3:$D$42-Obrys!$D$2)*(Obrys!$E$2:$E$41-Obrys!$E$2)))/2", "m²", "KONTROLA: ścianka z rzutu ma ok. 19 600 m²")
dr(13, "Obwód obrysu", "=SUMPRODUCT(SQRT((Obrys!$D$3:$D$42-Obrys!$D$2:$D$41)^2+(Obrys!$E$3:$E$42-Obrys!$E$2:$E$41)^2))", "m", "KONTROLA: rzut podaje ok. 565 m ścianki", False, "0.0")
dr(14, "Pole z liczby węzłów w obrysie", f"=SUM(Siatka!{rng})*B5", "m²", "")
dr(15, "Współczynnik korekty brzegu (pole obrysu / pole z węzłów)", "=B12/B14", "", "przelicza sumy z węzłów na dokładne pole obrysu", False, "0.000")
dr(16, "Liczba węzłów w obrysie", f"=SUM(Siatka!{rng})", "szt.", "")
dr(17, "Średnia rzędna terenu w obrysie", f"=SUMPRODUCT(Siatka!{rng},Siatka!$G${R0}:$G${R1})/B16", "m npm", "", False, "0.00")
dr(18, "Wykop brutto (teren → dno), ściany pionowe", f"=SUM(Siatka!$N${R0}:$N${R1})*B15", "m³", "cały obrys, razem z humusem i nasypem")
dr(19, "Humus w obrysie", f"=SUM(Siatka!$O${R0}:$O${R1})*B15", "m³", "")
dr(20, "Nasyp niekontrolowany w obrysie", f"=SUM(Siatka!$P${R0}:$P${R1})*B15", "m³", "")
dr(21, "Grunt pod humusem i nasypem, do dna", f"=SUM(Siatka!$Q${R0}:$Q${R1})*B15", "m³", "")
dr(22, "   w tym piaski/pospółki", f"=SUM(Siatka!$R${R0}:$R${R1})*B15", "m³", "dla dna 121,97")
dr(23, "Średnia grubość humusu", "=B19/B12", "m", "", False, "0.00")
dr(24, "Średnia grubość nasypu", "=B20/B12", "m", "", False, "0.000")
dr(25, "Udział piasków w gruncie pod humusem", "=B22/B21", "", "", False, "0%")
wd["A27"] = "ŹRÓDŁO RZĘDNYCH TERENU W WĘZŁACH"
wd["A27"].font = B
dr(28, "Węzły z pikiet (arkusz Pikiety)", f"=COUNT(Siatka!$F${R0}:$F${R1})", "szt.", "najwyższy priorytet")
dr(29, "Węzły z NMT (kolumna E w arkuszu Siatka)", f"=SUMPRODUCT(ISNUMBER(Siatka!$E${R0}:$E${R1})*(1-ISNUMBER(Siatka!$F${R0}:$F${R1})))", "szt.", "wartość + korekta z B6")
dr(30, "Węzły tylko z 17 otworów (wstępne)", f"=ROWS(Siatka!$G${R0}:$G${R1})-B28-B29", "szt.", "to jest wartość WSTĘPNA (±0,15 m); zastąp pikietami lub NMT")

# ---------------------------------------------------------------- Siatka
ws = wb.create_sheet("Siatka")
ws["A1"] = "WĘZŁY SIATKI 10 x 10 m (PL-2000 strefa 6). ID zgodne z opisami kolumn (litery) i wierszy (numery) w rysunku DXF."
ws["A1"].font = Font(bold=True, size=12)
ws["A2"] = "Kolumna E (NMT) i arkusz Pikiety: wklej własne rzędne terenu. Kolumny D, H, I, J są wstępne (z 17 otworów)."
ws["A2"].font = Font(italic=True)
ws["A3"] = "SUMY:"
ws["A3"].font = B
ws["K3"] = f"=SUM(K{R0}:K{R1})"
for col in "NOPQR":
    ws[f"{col}3"] = f"=SUM({col}{R0}:{col}{R1})"
    ws[f"{col}3"].number_format = "#,##0"
    ws[f"{col}3"].font = B
naglowki = ["ID", "E (X) [m]", "N (Y) [m]", "Teren z 17 otworów [m npm] (wstępne)", "Teren z NMT [m npm] - WKLEJ", "Teren z pikiet [m npm] (auto)",
            "Teren użyty [m npm]", "Humus [m]", "Nasyp [m]", "Piasek nad dnem 121,97 [m]", "W obrysie (1/0)", "Głębokość do dna [m]",
            "Grunt pod humusem [m]", "V wykop brutto [m³]", "V humus [m³]", "V nasyp [m³]", "V grunt pod humusem [m³]", "V piasek [m³]"]
for k, t in enumerate(naglowki, start=1):
    c = ws.cell(5, k, t)
    c.font = B
    c.fill = SZARY
    c.alignment = Alignment(wrap_text=True, vertical="top")
ws.row_dimensions[5].height = 62
pod = "$G"  # tylko czytelnosc
for idx, w in enumerate(nodes):
    r = R0 + idx
    ws.cell(r, 1, w["id"])
    ws.cell(r, 2, w["E"]).number_format = "0.0"
    ws.cell(r, 3, w["N"]).number_format = "0.0"
    ws.cell(r, 4, round(w["eg"], 3)).number_format = "0.000"
    ws.cell(r, 5).fill = ZOLTY
    d2 = f"((Pikiety!$D$2:$D${NP + 1}-$B{r})^2+(Pikiety!$E$2:$E${NP + 1}-$C{r})^2)"
    mask = f"(Pikiety!$G$2:$G${NP + 1}*({d2}<=Dane_siatki!$B$9^2))"
    ws.cell(r, 6, f'=IFERROR(SUMPRODUCT({mask}*Pikiety!$F$2:$F${NP + 1}/({d2}+1))/SUMPRODUCT({mask}/({d2}+1)),"")').number_format = "0.000"
    ws.cell(r, 7, f"=IF(ISNUMBER(F{r}),F{r},IF(ISNUMBER(E{r}),E{r}+Dane_siatki!$B$6,D{r}))").number_format = "0.000"
    ws.cell(r, 8, round(w["hum"], 3)).number_format = "0.000"
    ws.cell(r, 9, round(w["nas"], 3)).number_format = "0.000"
    ws.cell(r, 10, round(w["pia"], 3)).number_format = "0.000"
    ws.cell(r, 11, (
        f"=MOD(SUMPRODUCT(((Obrys!$E$2:$E$41>$C{r})-(Obrys!$E$3:$E$42>$C{r}))^2*"
        f"($B{r}<(Obrys!$D$3:$D$42-Obrys!$D$2:$D$41)*($C{r}-Obrys!$E$2:$E$41)"
        f"/(Obrys!$E$3:$E$42-Obrys!$E$2:$E$41+(Obrys!$E$3:$E$42=Obrys!$E$2:$E$41))+Obrys!$D$2:$D$41)),2)"))
    ws.cell(r, 12, f"=MAX(0,G{r}-Dane_siatki!$B$3)").number_format = "0.000"
    ws.cell(r, 13, f"=MAX(0,L{r}-H{r}-I{r})").number_format = "0.000"
    ws.cell(r, 14, f"=K{r}*L{r}*Dane_siatki!$B$5").number_format = "#,##0.0"
    ws.cell(r, 15, f"=K{r}*H{r}*Dane_siatki!$B$5").number_format = "#,##0.0"
    ws.cell(r, 16, f"=K{r}*I{r}*Dane_siatki!$B$5").number_format = "#,##0.0"
    ws.cell(r, 17, f"=K{r}*M{r}*Dane_siatki!$B$5").number_format = "#,##0.0"
    ws.cell(r, 18, f"=K{r}*MIN(J{r},M{r})*Dane_siatki!$B$5").number_format = "#,##0.0"
for col, wdt in zip("ABCDEFGHIJKLMNOPQR", (8, 13, 13, 16, 16, 16, 14, 10, 10, 14, 10, 12, 12, 13, 12, 12, 14, 12)):
    ws.column_dimensions[col].width = wdt
ws.freeze_panes = f"B{R0}"

# ---------------------------------------------------------------- powiazanie z 'Bilans wstępny'
bw = wb["Bilans wstępny"]
powiazania = {
    5: ("=Dane_siatki!B12", "z arkusza Dane_siatki (pole obrysu ścianki); możesz nadpisać"),
    10: ("=Dane_siatki!B17", "z siatki 10 m (arkusz Dane_siatki); wstępnie z 17 otworów, zastąp pikietami/NMT"),
    14: ("=Dane_siatki!B23", "z siatki 10 m (arkusz Dane_siatki)"),
    15: ("=Dane_siatki!B24", "z siatki 10 m (arkusz Dane_siatki)"),
    16: ("=Dane_siatki!B25", "z siatki 10 m (arkusz Dane_siatki), dla dna 121,97"),
}
for r, (f, uw) in powiazania.items():
    bw.cell(r, 2).value = f
    bw.cell(r, 4).value = uw

wb.save(SCIEZKA)
print("zapisano", SCIEZKA, "| arkusze:", wb.sheetnames, "| wiersze Siatka:", R0, R1)

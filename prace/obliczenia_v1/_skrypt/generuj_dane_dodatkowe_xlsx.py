"""Drugi, pomocniczy plik: 00_WYNIKI/BILANS_dz190_dane_dodatkowe.xlsx
Arkusze: WEZLY_10m (kontrola klasyczna metoda siatki kwadratow dla wykopu w scianie szczelnej), GEOMETRIA (wierzcholki), OTWORY (17 otworow).
Plik jest samodzielny (nie laczy sie z glownym arkuszem)."""
import json
import os
import sys

import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from shapely import contains_xy, points as spoints
from shapely.geometry import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bilans_formuly import wczytaj  # noqa: E402
from eg_model import geometria, zbuduj  # noqa: E402
from generuj_pliki import OTWORY, OUT  # noqa: E402
from generuj_wynik_prosty_xlsx import policz_formuly, wpisz_wartosci  # noqa: E402
from oblicz_bilans import Pola, profil_otworu  # noqa: E402

R = wczytaj()
SB = R["scenariusze"]["B"]
SCIEZKA = os.path.join(OUT, "00_WYNIKI", "BILANS_dz190_dane_dodatkowe.xlsx")

ZOLTY = PatternFill("solid", fgColor="FFF2CC")
SZARY = PatternFill("solid", fgColor="D9D9D9")
ZIELONY = PatternFill("solid", fgColor="E2EFDA")
B = Font(bold=True)
cienka = Side(style="thin", color="999999")
RAMKA = Border(left=cienka, right=cienka, top=cienka, bottom=cienka)
WRAP = Alignment(wrap_text=True, vertical="top")
rd = lambda v, k: int(round(v / k)) * k

wb = Workbook()
# ======================================================================= WEZLY_10m
wn = wb.active
wn.title = "WEZLY_10m"
Wp, HALE, PAR = geometria()
eg, _, _ = zbuduj(uzyj_trend=False)
es = np.arange(6433570.0, 6433731.0, 10.0)
ns = np.arange(5658890.0, 5659061.0, 10.0)
EE, NN = np.meshgrid(es, ns)
e_, n_ = EE.ravel(), NN.ravel()
eg_ = eg(e_, n_)
inW_ = contains_xy(Wp, e_, n_)
prof = [profil_otworu(nr) for nr in OTWORY]
pola = Pola(prof, "tin")
hum_ = pola([p["h"] for p in prof], e_, n_)
nas_ = pola([p["n"] for p in prof], e_, n_)
letter = lambda i: chr(ord("A") + i) if i < 26 else "A" + chr(ord("A") + i - 26)
wn["A1"] = "KONTROLA KLASYCZNĄ METODĄ SIATKI KWADRATÓW 10 × 10 m (węzły co 10 m w ściance, układ PL-2000; ID jak w DXF). Wynik ma zgadzać się z modelem."
wn["A1"].font = B
wn["A2"] = "Rzędna dna [m npm]"
wn["B2"] = R["DNO"]
wn["A3"] = "Zmiana dna [m] (ujemna = głębiej)"
wn["B3"] = 0.0
for c in ("B2", "B3"):
    wn[c].fill = ZOLTY
    wn[c].border = RAMKA
hdrs = ["ID", "E (X) [m]", "N (Y) [m]", "Teren istn. [m npm]", "Humus [m]", "Nasyp [m]", "W ściance (1/0)", "Głębokość wykopu [m]", "V brutto [m³]", "V humus+nasyp [m³]"]
for k, t in enumerate(hdrs):
    c = wn.cell(5, 1 + k, t)
    c.font = B
    c.fill = SZARY
    c.alignment = Alignment(wrap_text=True, vertical="top")
wn.row_dimensions[5].height = 48
r0 = 6
r = r0
for j, nv in enumerate(ns):
    for i, ev in enumerate(es):
        k = j * len(es) + i
        if not inW_[k]:
            continue
        wn.cell(r, 1, f"{letter(i)}{j + 1:02d}")
        wn.cell(r, 2, float(e_[k])).number_format = "0.0"
        wn.cell(r, 3, float(n_[k])).number_format = "0.0"
        wn.cell(r, 4, round(float(eg_[k]), 2)).number_format = "0.00"
        wn.cell(r, 5, round(float(hum_[k]), 2)).number_format = "0.00"
        wn.cell(r, 6, round(float(nas_[k]), 2)).number_format = "0.00"
        wn.cell(r, 7, 1)
        wn.cell(r, 8, f"=MAX(0,D{r}-($B$2+$B$3))").number_format = "0.00"
        wn.cell(r, 9, f"=H{r}*100").number_format = "#,##0"
        wn.cell(r, 10, f"=MIN(H{r},E{r}+F{r})*100").number_format = "#,##0"
        r += 1
rl = r - 1
pole_W = round(Wp.area, 1)
Vb = rd(SB["V_brutto"], 100)
Vhn = rd(SB["V_humus_nasyp_w_wykopie"], 100)
wn["L5"] = "WYNIK KONTROLI"
wn["L5"].font = B
tab = [
    (6, "Pole ścianki [m²] (z modelu)", pole_W, "#,##0"),
    (7, "Liczba węzłów w ściance", f"=SUM(G{r0}:G{rl})", "#,##0"),
    (8, "Współczynnik brzegu = pole / (węzły × 100)", "=M6/(M7*100)", "0.000"),
    (9, "Wykop brutto z węzłów (po korekcie brzegu) [m³]", f"=SUM(I{r0}:I{rl})*M8", "#,##0"),
    (10, "Wykop brutto z modelu 0,5 m [m³]", Vb, "#,##0"),
    (11, "Różnica", "=M9/M10-1", "0.0%"),
    (13, "Humus+nasyp z węzłów (po korekcie brzegu) [m³]", f"=SUM(J{r0}:J{rl})*M8", "#,##0"),
    (14, "Humus+nasyp z modelu 0,5 m [m³]", Vhn, "#,##0"),
    (15, "Różnica", "=M13/M14-1", "0.0%"),
]
for rr, opis, val, fmt in tab:
    wn.cell(rr, 12, opis)
    c = wn.cell(rr, 13, val)
    c.number_format = fmt
    c.border = RAMKA
    c.fill = ZIELONY if isinstance(val, str) else SZARY
wn.column_dimensions["A"].width = 32
for c in "BCDEFGHIJ":
    wn.column_dimensions[c].width = 13
wn.column_dimensions["L"].width = 52
wn.column_dimensions["M"].width = 14
wn.freeze_panes = "B6"

# ======================================================================= GEOMETRIA
wg = wb.create_sheet("GEOMETRIA")
geo = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dane", "geometria_G.json")))
wg["A1"] = "GEOMETRIA Z RYSUNKU PROJEKTANTA (PL-2000 strefa 6, metry; E = X w CAD, N = Y w CAD)"
wg["A1"].font = Font(bold=True, size=13)
wg["A2"] = ("Źródło: wektorowy rzut zabezpieczenia wykopu zgrany z siatką współrzędnych projektanta (krzyże co 50 m, odchyłka 1,4 cm). "
            "Twój wcześniejszy szkic jest wszędzie o 3,7% mniejszy.")
wg["A2"].alignment = WRAP
wg.merge_cells("A2:H3")
bloki = [("ŚCIANKA", geo["scianka"])] + [(f"HALA {k}", geo["hale"][str(k)]) for k in range(1, 9)] + [("GRANICA DZIAŁKI (rysunek)", geo["dzialka"][:-1] if geo["dzialka"][0] == geo["dzialka"][-1] else geo["dzialka"])]
rowp = 5
for nazwa, pts in bloki:
    wg.cell(rowp, 1, nazwa).font = B
    wg.cell(rowp, 2, "E [m]").font = B
    wg.cell(rowp, 3, "N [m]").font = B
    for k, (ev, nv) in enumerate(pts):
        wg.cell(rowp + 1 + k, 1, k + 1)
        wg.cell(rowp + 1 + k, 2, round(float(ev), 3)).number_format = "0.000"
        wg.cell(rowp + 1 + k, 3, round(float(nv), 3)).number_format = "0.000"
    wg.cell(rowp, 5, "pole [m²]").font = B
    wg.cell(rowp, 6, round(Polygon(pts).area, 0)).number_format = "#,##0"
    rowp += len(pts) + 3
wg.column_dimensions["A"].width = 30
for c in "BCDEF":
    wg.column_dimensions[c].width = 16

# ======================================================================= OTWORY
wo = wb.create_sheet("OTWORY")
hd = ["Otwór", "N [m]", "E [m]", "H terenu [m npm]", "Humus [m]", "Nasyp [m]", "Zwierciadło wody ustabilizowane [m npm]", "Uwagi"]
for k, t in enumerate(hd):
    c = wo.cell(2, 1 + k, t)
    c.font = B
    c.fill = SZARY
    c.alignment = Alignment(wrap_text=True, vertical="top")
wo.row_dimensions[2].height = 48
wo["A1"] = "17 OTWORÓW DGI – dane użyte do grubości humusu i nasypu"
wo["A1"].font = B
for k, p in enumerate(R["otwory"]):
    rr = 3 + k
    vals = [p["nr"], p["N"], p["E"], p["H"], p["h"], p["n"], p["zw"], OTWORY[p["nr"]][4]]
    for c, v in enumerate(vals):
        cell = wo.cell(rr, 1 + c, round(v, 2) if isinstance(v, float) else v)
        if isinstance(v, float):
            cell.number_format = "0.00"
for c, w in zip("ABCDEFGH", (8, 13, 13, 12, 10, 10, 18, 70)):
    wo.column_dimensions[c].width = w
wo.freeze_panes = "B3"

wb.calculation.fullCalcOnLoad = True
wb.save(SCIEZKA)
print("zapisano", SCIEZKA, "| wezlow:", rl - r0 + 1)
print("wpisano wartosci:", wpisz_wartosci(SCIEZKA))
w = policz_formuly(SCIEZKA)
for a in ("M7", "M8", "M9", "M10", "M11", "M13", "M14", "M15"):
    print(a, round(w[("WEZLY_10M", a)], 4))

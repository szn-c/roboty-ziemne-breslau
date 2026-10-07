"""DXF + pliki tekstowe z poprawna geometria (rysunek projektanta) dla GstarCAD. Uklad PL-2000 strefa 6: X = E, Y = N."""
import json
import math
import os
import sys

import ezdxf
import numpy as np
from ezdxf import bbox as _bbox
from shapely import contains_xy
from shapely.geometry import Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bilans_formuly import wczytaj  # noqa: E402
from dane_uzytkownika import HALE_UZ, SCIANKA_UZ  # noqa: E402
from eg_model import geometria, zbuduj  # noqa: E402
from generuj_pliki import OTWORY, OUT  # noqa: E402
from oblicz_bilans import DNO, PRZESTRZEN_ROBOCZA, Pola, profil_otworu  # noqa: E402

FOLDER = os.path.join(OUT, "04_gstarcad_siatka")
os.makedirs(FOLDER, exist_ok=True)
R = wczytaj()
W, HALE, PAR = geometria()
eg, _, _ = zbuduj(uzyj_trend=False)
prof = [profil_otworu(nr) for nr in OTWORY]
pola = Pola(prof, "tin")

# ------------------------------------------------------------------ pliki tekstowe (ten sam format co Twoje: E <tab> N)
def zapisz_txt(nazwa, bloki):
    with open(os.path.join(FOLDER, nazwa), "w", encoding="ascii", newline="\r\n") as f:
        for i, b in enumerate(bloki):
            if i:
                f.write("\n")
            for e, n in b:
                f.write(f"{e:.3f}\t{n:.3f}\n")

zapisz_txt("wierzcholki_scianka_wg_projektanta.txt", [list(W.exterior.coords)[:-1]])
zapisz_txt("wierzcholki_hala_1-8_wg_projektanta.txt", [list(HALE[k].exterior.coords)[:-1] for k in range(1, 9)])
zapisz_txt("wierzcholki_granica_dzialki_z_rysunku.txt", [list(PAR.exterior.coords)[:-1]])

# ------------------------------------------------------------------ DXF
doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.M
doc.header["$PDMODE"] = 3
doc.header["$PDSIZE"] = 1.0
msp = doc.modelspace()
warstwy = [("01_SCIANKA_wg_projektanta", 5), ("02_HALE_1-8_wg_projektanta", 6), ("03_GRANICA_DZIALKI_z_rysunku", 30),
           ("05_SIATKA_10m", 8), ("06_WEZLY_10m", 7), ("07_RZEDNE_TERENU", 7),
           ("08_GLEBOKOSC_WYKOPU", 1), ("09_OTWORY_DGI", 2), ("10_KRZYZE_50m_do_ALIGN", 4),
           ("11_STARE_OBRYSY_UZYTKOWNIKA_3.7pct_za_male", 9), ("12_LEGENDA", 7)]
for n, c in warstwy:
    doc.layers.add(n, color=c)
doc.layers.get("05_SIATKA_10m").off()
doc.layers.get("06_WEZLY_10m").off()


def pline(pts, warstwa, lt=None):
    a = {"layer": warstwa}
    if lt:
        a["linetype"] = lt
    msp.add_lwpolyline([(float(e), float(n)) for e, n in pts], close=True, dxfattribs=a)


pline(list(W.exterior.coords)[:-1], "01_SCIANKA_wg_projektanta", "DASHED")
for k, p in HALE.items():
    pline(list(p.exterior.coords)[:-1], "02_HALE_1-8_wg_projektanta")
    c = p.centroid
    msp.add_text(f"HALA {k}  {p.area:.0f} m2", height=2.2, dxfattribs={"layer": "02_HALE_1-8_wg_projektanta"}).set_placement((c.x - 9, c.y))
pline(list(PAR.exterior.coords)[:-1], "03_GRANICA_DZIALKI_z_rysunku", "DASHED")
# siatka 10 m i wezly
es = np.arange(6433570.0, 6433731.0, 10.0)
ns = np.arange(5658890.0, 5659061.0, 10.0)
for e in es:
    msp.add_line((e, ns[0], 0), (e, ns[-1], 0), dxfattribs={"layer": "05_SIATKA_10m"})
for n in ns:
    msp.add_line((es[0], n, 0), (es[-1], n, 0), dxfattribs={"layer": "05_SIATKA_10m"})
letter = lambda i: chr(ord("A") + i) if i < 26 else "A" + chr(ord("A") + i - 26)
for j, n in enumerate(ns):
    for i, e in enumerate(es):
        if not W.buffer(10).contains(Polygon([(e - 1, n - 1), (e + 1, n - 1), (e + 1, n + 1), (e - 1, n + 1)]).centroid):
            continue
        z_eg = float(eg(np.array([e]), np.array([n]))[0])
        msp.add_point((e, n, round(z_eg, 3)), dxfattribs={"layer": "06_WEZLY_10m"})
        msp.add_text(f"{z_eg:.2f}", height=1.0, dxfattribs={"layer": "07_RZEDNE_TERENU"}).set_placement((e + 0.4, n + 0.4))
        if contains_xy(W, e, n):
            msp.add_text(f"{max(0.0, z_eg - DNO):.2f}", height=1.0, dxfattribs={"layer": "08_GLEBOKOSC_WYKOPU"}).set_placement((e + 0.4, n - 1.5))
            msp.add_text(f"{letter(i)}{j + 1:02d}", height=0.7, dxfattribs={"layer": "06_WEZLY_10m"}).set_placement((e + 0.4, n - 2.5))
# otwory
for p in prof:
    msp.add_circle((p["E"], p["N"]), 1.0, dxfattribs={"layer": "09_OTWORY_DGI"})
    msp.add_text(f"OTW {p['nr']}  H={p['H']:.2f}  humus {p['h']:.2f}", height=1.3, dxfattribs={"layer": "09_OTWORY_DGI"}).set_placement((p["E"] + 1.5, p["N"] + 1.5))
# krzyze 50 m (uklad wspolrzednych projektanta) - do ALIGN przy dopasowaniu PDF
for e in np.arange(6433550.0, 6433801.0, 50.0):
    for n in np.arange(5658850.0, 5659101.0, 50.0):
        a = {"layer": "10_KRZYZE_50m_do_ALIGN"}
        msp.add_line((e - 4, n, 0), (e + 4, n, 0), dxfattribs=a)
        msp.add_line((e, n - 4, 0), (e, n + 4, 0), dxfattribs=a)
        msp.add_text(f"E{e:.0f} N{n:.0f}", height=1.4, dxfattribs=a).set_placement((e + 1.5, n + 1.2))
# stare obrysy uzytkownika
pline(SCIANKA_UZ, "11_STARE_OBRYSY_UZYTKOWNIKA_3.7pct_za_male", "DASHED")
for k, pts in HALE_UZ.items():
    pline(pts, "11_STARE_OBRYSY_UZYTKOWNIKA_3.7pct_za_male")
# legenda
x0, y0 = 6433570.0, 5658860.0
linie = [
    "GEOMETRIA WG RYSUNKU PROJEKTANTA (rzut zabezpieczenia wykopu, siatka wspolrzednych 50 m). Uklad PL-2000 strefa 6, X = wschod, Y = polnoc.",
    "01 scianka (pole %.0f m2, obwod %.1f m)   02 hale 1-8 (obrys zewnetrzny, razem %.0f m2)   03 granica dzialki z rysunku (%.0f m2; oficjalnie 25 290 m2)" % (W.area, W.length, sum(p.area for p in HALE.values()), PAR.area),
    "06-08 wezly 10 m: gorna liczba = rzedna terenu istniejacego, dolna (czerwona) = glebokosc wykopu do dna 121,97 m npm (wykop w scianie szczelnej)",
    "11 szary: Twoj wczesniejszy szkic - wszedzie o 3,7% mniejszy niz rysunek projektanta (patrz CZYTAJ_NAJPIERW.md)",
]
for k, s in enumerate(linie):
    msp.add_text(s, height=1.5, dxfattribs={"layer": "12_LEGENDA"}).set_placement((x0, y0 - 2.6 * k))

ext = _bbox.extents(msp, fast=True)
doc.header["$EXTMIN"] = (ext.extmin.x, ext.extmin.y, 0)
doc.header["$EXTMAX"] = (ext.extmax.x, ext.extmax.y, 0)
doc.set_modelspace_vport(height=(ext.extmax.y - ext.extmin.y) * 1.1, center=((ext.extmin.x + ext.extmax.x) / 2, (ext.extmin.y + ext.extmax.y) / 2))
sciezka = os.path.join(FOLDER, "obrysy_projektanta_i_siatka_dz190.dxf")
doc.saveas(sciezka)


def napraw_zasieg(sciezka, ext):
    """ezdxf 1.4 zapisuje $EXTMIN/$EXTMAX jako 1e+20 - wpisujemy prawdziwy zasieg, zeby ZOOM EXTENTS dzialal od razu."""
    import re
    t = open(sciezka, encoding="utf-8", errors="surrogateescape").read()
    for nazwa, v in (("$EXTMIN", ext.extmin), ("$EXTMAX", ext.extmax)):
        t = re.sub(r"(\n\s*9\n" + re.escape(nazwa) + r"\n\s*10\n)[^\n]+(\n\s*20\n)[^\n]+(\n\s*30\n)[^\n]+",
                   lambda m: m.group(1) + f"{v.x:.3f}" + m.group(2) + f"{v.y:.3f}" + m.group(3) + "0.0", t, count=1)
    open(sciezka, "w", encoding="utf-8", errors="surrogateescape", newline="").write(t)


napraw_zasieg(sciezka, ext)

# skrypt .scr (alternatywa dla DXF) - rysuje tylko scianke, hale i granice
with open(os.path.join(FOLDER, "rysuj_obrysy_projektanta.scr"), "w", encoding="ascii", newline="\r\n") as s:
    s.write("_OSMODE\n0\n")
    for nazwa, kolor in (("01_SCIANKA", 5), ("02_HALE", 6), ("03_GRANICA_DZIALKI", 30)):
        s.write(f"_-LAYER\n_M\n{nazwa}\n_C\n{kolor}\n\n\n")
    def plinia(pts, warstwa):
        s.write(f"_-LAYER\n_S\n{warstwa}\n\n")
        s.write("_PLINE\n" + "".join(f"{e:.3f},{n:.3f}\n" for e, n in pts) + "_C\n")
    plinia(list(W.exterior.coords)[:-1], "01_SCIANKA")
    for k in range(1, 9):
        plinia(list(HALE[k].exterior.coords)[:-1], "02_HALE")
    plinia(list(PAR.exterior.coords)[:-1], "03_GRANICA_DZIALKI")
    s.write("_ZOOM\n_E\n")

print("DXF:", sciezka)
print("pliki:", sorted(os.listdir(FOLDER)))

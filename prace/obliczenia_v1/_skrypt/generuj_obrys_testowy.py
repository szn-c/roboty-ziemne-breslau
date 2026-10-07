"""
Obrys testowy = otoczka wypukła 17 otworów (warstwa ZAKRES_TEST).
1) zapisuje skrypt AutoCAD 03_dxf_kontrolny/rysuj_obrys_testowy.scr
2) liczy, jaki wynik powinien dać Civil 3D (interpolacja liniowa TIN) dla humusu i nasypu w tym obrysie.
"""
import csv
import os
import sys

import numpy as np
from scipy.interpolate import LinearNDInterpolator
from shapely import contains_xy
from shapely.geometry import MultiPoint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generuj_pliki import OTWORY, OUT  # noqa: E402

hull = MultiPoint([(v[1], v[0]) for v in OTWORY.values()]).convex_hull  # (E, N)

# --- skrypt AutoCAD ---
sciezka = os.path.join(OUT, "03_dxf_kontrolny", "rysuj_obrys_testowy.scr")
with open(sciezka, "w", encoding="ascii", newline="\r\n") as s:
    s.write("_OSMODE\n0\n")
    s.write("_-LAYER\n_M\nZAKRES_TEST\n_C\n6\n\n\n")
    s.write("_PLINE\n")
    for x, y in list(hull.exterior.coords)[:-1]:
        s.write(f"{x:.2f},{y:.2f}\n")
    s.write("_C\n")
    s.write("_OSMODE\n4141\n")  # przywrócenie przyciągania: End, Center, Node, Intersection, Extension
print("Zapisano:", sciezka)


# --- oczekiwany wynik ---
def wczytaj(plik):
    a = np.loadtxt(os.path.join(OUT, "01_pliki_punktow_PNEZD", plik), delimiter=",", usecols=(1, 2, 3))
    return a[:, 1], a[:, 0], a[:, 2]  # E, N, Z


minx, miny, maxx, maxy = hull.bounds
krok = 0.5
gx, gy = np.meshgrid(np.arange(minx + krok / 2, maxx, krok), np.arange(miny + krok / 2, maxy, krok))
maska = contains_xy(hull, gx, gy)
print(f"Pole obrysu testowego: {hull.area:.0f} m2  (obwod {hull.length:.0f} m)")
for nazwa, plik in [("humus", "02_miazszosc_humus.csv"), ("nasyp", "03_miazszosc_nasyp.csv")]:
    e, n, z = wczytaj(plik)
    f = LinearNDInterpolator(np.column_stack([e, n]), z)
    v = f(gx[maska], gy[maska])
    v = np.nan_to_num(v)
    print(f"{nazwa}: {v.sum() * krok * krok:.0f} m3   (srednia grubosc {v.mean():.3f} m)")

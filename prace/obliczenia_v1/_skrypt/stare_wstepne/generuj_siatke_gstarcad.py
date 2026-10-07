"""
Siatka 10 x 10 m do bilansu mas ziemnych w GstarCAD + Excel (bez Civil 3D).
Wejscie: otwory z generuj_pliki.py, pliki miazszosci (01_pliki_punktow_PNEZD).
Wyjscie: 04_gstarcad_siatka/siatka_10m_dz190.dxf, lisp/*.lsp, oraz nowe arkusze w bilans_robot_ziemnych.xlsx
Uklad: PL-2000 strefa 6 (EPSG:2177); X w CAD = Easting (E), Y w CAD = Northing (N).
"""
import math
import os
import sys

import ezdxf
import numpy as np
from ezdxf import bbox as _bbox
from scipy.interpolate import LinearNDInterpolator
from shapely import contains_xy
from shapely.geometry import Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generuj_pliki import OTWORY, OUT, miazszosc, najblizszy, ramka  # noqa: E402

FOLDER = os.path.join(OUT, "04_gstarcad_siatka")
DNO = 121.97
KROK = 10.0
E_MIN, E_MAX = 6433560.0, 6433740.0
N_MIN, N_MAX = 5658880.0, 5659070.0

# Orientacyjny obrys scianki (z odczytu rysunku i siatki 50 m, +-3 m) - do zamiany na wlasny
SCIANKA = [
    (6433582.9, 5659056.3),
    (6433724.3, 5659031.1),
    (6433723.4, 5658892.9),
    (6433687.1, 5658892.9),
    (6433571.4, 5658942.0),
]


def litera(i):
    return chr(ord("A") + i)


def interpolator_z_plikow(plik):
    a = np.loadtxt(os.path.join(OUT, "01_pliki_punktow_PNEZD", plik), delimiter=",", usecols=(1, 2, 3))
    return LinearNDInterpolator(np.column_stack([a[:, 1], a[:, 0]]), a[:, 2])


def interpolator_eg():
    e = [v[1] for v in OTWORY.values()]
    n = [v[0] for v in OTWORY.values()]
    z = [v[2] for v in OTWORY.values()]
    _, rpts = ramka()
    for pt in rpts:
        nr = najblizszy(pt.x, pt.y)
        e.append(pt.x)
        n.append(pt.y)
        z.append(OTWORY[nr][2])
    return LinearNDInterpolator(np.column_stack([e, n]), z)


def wezly():
    f_eg = interpolator_eg()
    f_h = interpolator_z_plikow("02_miazszosc_humus.csv")
    f_n = interpolator_z_plikow("03_miazszosc_nasyp.csv")
    f_p = interpolator_z_plikow("05_piaski_nad_dnem_wykopu/05_piasek_nad_dnem_121_97.csv")
    es = np.arange(E_MIN, E_MAX + 0.1, KROK)
    ns = np.arange(N_MIN, N_MAX + 0.1, KROK)
    poly = Polygon(SCIANKA)
    out = []
    for j, n in enumerate(ns):
        for i, e in enumerate(es):
            eg = float(f_eg(e, n))
            out.append(dict(
                id=f"{litera(i)}{j + 1:02d}", i=i, j=j, E=float(e), N=float(n), eg=eg,
                hum=float(f_h(e, n)), nas=float(f_n(e, n)), pia=float(f_p(e, n)),
                w=bool(contains_xy(poly, e, n)),
            ))
    return out, es, ns


def dxf(nodes, es, ns):
    os.makedirs(FOLDER, exist_ok=True)
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.M
    doc.header["$PDMODE"] = 3
    doc.header["$PDSIZE"] = 1.0
    msp = doc.modelspace()
    warstwy = [
        ("0_SIATKA_10m", 8), ("1_WEZLY", 7), ("2_RZEDNE_TERENU", 7), ("3_GLEBOKOSC_WYKOPU", 1),
        ("4_HUMUS_m", 3), ("5_OTWORY", 2), ("6_KRZYZE_50m_DO_DOPASOWANIA", 6),
        ("7_SCIANKA_ORIENTACYJNA", 5), ("8_OZNACZENIA_SIATKI", 4), ("9_LEGENDA", 7),
    ]
    for nazwa, kolor in warstwy:
        doc.layers.add(nazwa, color=kolor)
    doc.layers.get("4_HUMUS_m").off()

    # siatka
    for e in es:
        msp.add_line((e, ns[0], 0), (e, ns[-1], 0), dxfattribs={"layer": "0_SIATKA_10m"})
    for n in ns:
        msp.add_line((es[0], n, 0), (es[-1], n, 0), dxfattribs={"layer": "0_SIATKA_10m"})
    # oznaczenia kolumn/wierszy
    for i, e in enumerate(es):
        for n in (ns[0] - 4, ns[-1] + 2):
            msp.add_text(litera(i), height=2.0, dxfattribs={"layer": "8_OZNACZENIA_SIATKI"}).set_placement((e - 0.7, n))
    for j, n in enumerate(ns):
        for e in (es[0] - 6, es[-1] + 2):
            msp.add_text(f"{j + 1}", height=2.0, dxfattribs={"layer": "8_OZNACZENIA_SIATKI"}).set_placement((e, n - 0.7))
    # wezly i opisy
    for w in nodes:
        msp.add_point((w["E"], w["N"], round(w["eg"], 3)), dxfattribs={"layer": "1_WEZLY"})
        msp.add_text(f"{w['eg']:.2f}", height=1.0, dxfattribs={"layer": "2_RZEDNE_TERENU"}).set_placement((w["E"] + 0.5, w["N"] + 0.5))
        if w["w"]:
            msp.add_text(f"{max(0.0, w['eg'] - DNO):.2f}", height=1.0, dxfattribs={"layer": "3_GLEBOKOSC_WYKOPU"}).set_placement((w["E"] + 0.5, w["N"] - 1.5))
        msp.add_text(f"{w['hum']:.2f}", height=0.8, dxfattribs={"layer": "4_HUMUS_m"}).set_placement((w["E"] + 0.5, w["N"] - 2.6))
    # otwory
    for nr, (N, E, H, zw, uw) in OTWORY.items():
        msp.add_circle((E, N), 1.0, dxfattribs={"layer": "5_OTWORY"})
        msp.add_point((E, N, H), dxfattribs={"layer": "5_OTWORY"})
        msp.add_text(f"OTW {nr}  H={H:.2f}  hum={miazszosc(nr, 'H'):.2f}", height=1.3,
                     dxfattribs={"layer": "5_OTWORY"}).set_placement((E + 1.5, N + 1.5))
    # krzyze siatki 50 m (do dopasowania rzutu/mapy poleceniem ALIGN)
    for e in np.arange(6433500.0, 6433801.0, 50.0):
        for n in np.arange(5658850.0, 5659151.0, 50.0):
            a = {"layer": "6_KRZYZE_50m_DO_DOPASOWANIA"}
            msp.add_line((e - 3, n, 0), (e + 3, n, 0), dxfattribs=a)
            msp.add_line((e, n - 3, 0), (e, n + 3, 0), dxfattribs=a)
            msp.add_point((e, n, 0), dxfattribs=a)
            msp.add_text(f"E {e:.0f}", height=1.4, dxfattribs=a).set_placement((e + 1.5, n + 1.0))
            msp.add_text(f"N {n:.0f}", height=1.4, dxfattribs=a).set_placement((e + 1.5, n - 1.1))
    # scianka orientacyjna
    msp.add_lwpolyline(SCIANKA, close=True, dxfattribs={"layer": "7_SCIANKA_ORIENTACYJNA", "linetype": "DASHED"})
    msp.add_text("SCIANKA - OBRYS ORIENTACYJNY (+-3 m). ZASTAP WLASNYM OBRYSEM Z RZUTU", height=1.6,
                 dxfattribs={"layer": "7_SCIANKA_ORIENTACYJNA"}).set_placement((SCIANKA[4][0] + 2, SCIANKA[4][1] - 6))
    # legenda
    x0, y0 = E_MIN, N_MIN - 22
    linie = [
        "LEGENDA  (uklad PL-2000 strefa 6, metry; X = wschod, Y = polnoc)",
        f"Siatka {KROK:.0f} x {KROK:.0f} m. Przy wezle: gorna liczba = rzedna terenu [m npm] (WSTEPNA - z 17 otworow),",
        f"dolna czerwona liczba = glebokosc wykopu do dna {DNO:.2f} m npm (tylko wezly w obrysie scianki).",
        "Warstwa 4_HUMUS_m (wylaczona) = grubosc humusu z otworow.",
        "Krzyze 50 m (warstwa 6): cel dla ALIGN przy dopasowaniu rzutu/mapy. Punkty 1_WEZLY maja Z = rzedna terenu.",
    ]
    for k, s in enumerate(linie):
        msp.add_text(s, height=1.6 if k else 2.2, dxfattribs={"layer": "9_LEGENDA"}).set_placement((x0, y0 - 2.6 * k))

    ext = _bbox.extents(msp, fast=True)
    doc.header["$EXTMIN"] = (ext.extmin.x, ext.extmin.y, 0)
    doc.header["$EXTMAX"] = (ext.extmax.x, ext.extmax.y, 0)
    doc.set_modelspace_vport(height=(ext.extmax.y - ext.extmin.y) * 1.1,
                             center=((ext.extmin.x + ext.extmax.x) / 2, (ext.extmin.y + ext.extmax.y) / 2))
    sciezka = os.path.join(FOLDER, "siatka_10m_dz190.dxf")
    doc.saveas(sciezka)
    return sciezka


LISP_PLXY = r''';;; PLXY.lsp - eksport wierzcholkow JEDNEJ polilinii (LWPOLYLINE) do pliku tekstowego
;;; Uzycie: APPLOAD -> PLXY.lsp -> Zaladuj. Wpisz PLXY i wskaz polilinie.
;;; Plik "wierzcholki_polilinii.txt" powstaje w folderze rysunku (zapisz rysunek wczesniej!).
;;; Dwie kolumny rozdzielone tabulatorem: E (X) i N (Y). Bez naglowka. Wklej do Excela w komorke B2 arkusza Obrys.
(defun c:PLXY ( / e ed f fn k)
  (setq e (car (entsel "\nWskaz polilinie (LWPOLYLINE): ")))
  (if (and e (= (cdr (assoc 0 (entget e))) "LWPOLYLINE"))
    (progn
      (setq ed (entget e))
      (setq fn (strcat (getvar "DWGPREFIX") "wierzcholki_polilinii.txt"))
      (setq f (open fn "w") k 0)
      (foreach p ed
        (if (= (car p) 10)
          (progn
            (setq k (1+ k))
            (write-line (strcat (rtos (cadr p) 2 3) "\t" (rtos (caddr p) 2 3)) f))))
      (close f)
      (princ (strcat "\nZapisano " (itoa k) " wierzcholkow: " fn)))
    (princ "\nNie wskazano polilinii typu LWPOLYLINE."))
  (princ))
(princ "\nPLXY zaladowane. Wpisz PLXY.")
(princ)
'''

LISP_TXTXY = r''';;; TXTXY.lsp - eksport zaznaczonych napisow (TEXT, MTEXT) z polozeniem do pliku tekstowego
;;; Uzycie: APPLOAD -> TXTXY.lsp -> Zaladuj. Wpisz TXTXY, zaznacz napisy (np. pikiety wysokosciowe z mapy), Enter.
;;; Plik "teksty_xy.txt" powstaje w folderze rysunku. Trzy kolumny (tabulator): E (X), N (Y), tekst. Bez naglowka.
;;; Wklej do Excela w komorke A2 arkusza Pikiety.
(defun c:TXTXY ( / ss i ed f fn p s)
  (setq ss (ssget '((0 . "TEXT,MTEXT"))))
  (if ss
    (progn
      (setq fn (strcat (getvar "DWGPREFIX") "teksty_xy.txt"))
      (setq f (open fn "w"))
      (setq i 0)
      (repeat (sslength ss)
        (setq ed (entget (ssname ss i)))
        (setq p (cdr (assoc 10 ed)))
        (setq s (cdr (assoc 1 ed)))
        (if (and p s)
          (write-line (strcat (rtos (car p) 2 3) "\t" (rtos (cadr p) 2 3) "\t" s) f))
        (setq i (1+ i)))
      (close f)
      (princ (strcat "\nZapisano: " fn))))
  (princ))
(princ "\nTXTXY zaladowane. Wpisz TXTXY.")
(princ)
'''


def lisp():
    d = os.path.join(FOLDER, "lisp")
    os.makedirs(d, exist_ok=True)
    for nazwa, tresc in (("PLXY.lsp", LISP_PLXY), ("TXTXY.lsp", LISP_TXTXY)):
        with open(os.path.join(d, nazwa), "w", encoding="ascii", newline="\r\n") as f:
            f.write(tresc)


if __name__ == "__main__":
    nodes, es, ns = wezly()
    p = dxf(nodes, es, ns)
    lisp()
    print("DXF:", p)
    print("wezly:", len(nodes), "w obrysie:", sum(w["w"] for w in nodes))
    poly = Polygon(SCIANKA)
    print("pole obrysu %.0f m2, obwod %.1f m" % (poly.area, poly.length))

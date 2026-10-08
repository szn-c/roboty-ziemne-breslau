"""
Widoczny podział PZT na strefy (wypełnienia w kolejności rysowania: późniejsze przykrywają wcześniejsze)
+ pochylnie (kreskowanie (0,45; 0,45; 0,45) 0,71 pt i ściany pochylni – wypełnienie (152,152,152))
+ porównanie z obrysami zieleni użytkownika (DXF v2) po korekcie skali do PZT.
Wynik: _cache/pzt_strefy_widoczne.pkl, pzt_strefy_widoczne.json; ekran.
"""
import json
import math
import os
import pickle
from collections import defaultdict

import ezdxf
import numpy as np
import pymupdf
from ezdxf import path as ezpath
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

import pzt_wektor_hale as W
from pzt_strefy_wektor import pierscienie, wielokat

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache", "pzt_strefy_widoczne.pkl")
V2 = os.path.join(W.DU, "siatka_10m_dz190_checked_v2.dxf")

RGB = {  # kolor wypełnienia -> strefa; zieleń (13,206,96) rozróżniona kryciem: 0,298 = na gruncie, 0,498 = ogrody deszczowe
    (219, 219, 219): "ciagi_pieszo_jezdne", (219, 219, 20): "ciagi_piesze", (125, 180, 163): "plac_uslugowy",
    (120, 246, 173): "zielen_strop", (136, 179, 137): "geokrata", (99, 100, 102): "opaski", (207, 182, 113): "plac_zabaw",
    (155, 117, 198): "miejsca_rekreacji", (152, 152, 152): "sciany_pochylni",
}


def transformacja():
    T = json.load(open(os.path.join(HERE, "transformacja_uzytk_do_PZT.json")))
    s, a = T["skala"], math.radians(T["obrot_deg"])
    cs, cd = np.array(T["srodek_uzytk"]), np.array(T["srodek_PZT"])
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return T, (lambda pts: [tuple(p) for p in (s * ((np.array(pts) - cs) @ R.T) + cd)])


def polilinie_v2(warstwa, f=None):
    msp = ezdxf.readfile(V2).modelspace()
    out = []
    for e in msp:
        if e.dxf.layer != warstwa or e.dxftype() != "LWPOLYLINE":
            continue
        pts = [(v.x, v.y) for v in ezpath.make_path(e).flattening(distance=0.005)]
        if math.dist(pts[0], pts[-1]) < 1e-6:
            pts = pts[:-1]
        if f:
            pts = f(pts)
        P = Polygon(pts)
        out.append((e.dxf.handle, P if P.is_valid else P.buffer(0)))
    return out


def strefy_pzt():
    if os.path.exists(CACHE):
        return pickle.load(open(CACHE, "rb"))
    pg = pymupdf.open(W.PDF_WEKT)[0]
    dr = pg.get_drawings()
    warstwy = []  # (indeks rysowania, strefa, wielokąt)
    kresk = []
    for i, d in enumerate(dr):
        if d["rect"][0] < 600:
            continue
        if d["type"] in ("f", "fs") and d.get("fill"):
            rgb = tuple(round(v * 255) for v in d["fill"])
            op = round((d.get("fill_opacity") or 1) * 1000)
            if rgb == (13, 206, 96):
                nazwa = "zielen_grunt" if op < 400 else "ogrody_deszczowe"
            else:
                nazwa = RGB.get(rgb)
            if nazwa:
                P = wielokat(pierscienie(d["items"]), d.get("even_odd", False))
                if P is not None:
                    warstwy.append((i, nazwa, P))
        if d["type"] == "s" and d.get("color") and all(abs(c - 0.45) < 0.02 for c in d["color"]) and abs((d.get("width") or 0) - 0.71) < 0.03:
            for it in d["items"]:
                if it[0] == "l":
                    kresk.append(LineString([W.pt_do_pl(it[1].x, it[1].y), W.pt_do_pl(it[2].x, it[2].y)]))
    # widoczne części: od góry (ostatnio rysowane) w dół
    widoczne = defaultdict(list)
    przykryte = None
    for i, nazwa, P in sorted(warstwy, key=lambda t: -t[0]):
        V = P if przykryte is None else P.difference(przykryte)
        if V.area > 0.01:
            widoczne[nazwa].append(V)
        przykryte = P if przykryte is None else unary_union([przykryte, P])
    widoczne = {k: unary_union(v) for k, v in widoczne.items()}
    pelne = defaultdict(list)
    for i, nazwa, P in warstwy:
        pelne[nazwa].append(P)
    pelne = {k: unary_union(v) for k, v in pelne.items()}
    # pochylnie: kreskowanie -> grupy -> obwiednia
    pochylnie = unary_union([l.buffer(0.35, cap_style=2) for l in kresk]) if kresk else None
    wyn = {"widoczne": widoczne, "pelne": pelne, "pochylnie_kresk": pochylnie}
    pickle.dump(wyn, open(CACHE, "wb"))
    return wyn


def main():
    T, f = transformacja()
    G = Polygon(T["granica_po"])
    H = unary_union([Polygon(v) for v in T["hale_po"].values()])
    S = strefy_pzt()
    print("PZT – pola widoczne / pełne (w granicy działki) [m2]; w obrysach hal / poza:")
    out = {}
    for k in sorted(set(S["widoczne"]) | set(S["pelne"])):
        V = S["widoczne"].get(k, Polygon()).intersection(G)
        Pp = S["pelne"].get(k, Polygon()).intersection(G)
        out[k] = {"widoczne": round(V.area, 2), "pelne": round(Pp.area, 2), "widoczne_w_halach": round(V.intersection(H).area, 2),
                  "widoczne_poza_halami": round(V.difference(H).area, 2)}
        print("  %-22s widoczne %9.2f | pełne %9.2f | w halach %8.2f | poza halami %8.2f" % (k, V.area, Pp.area, V.intersection(H).area, V.difference(H).area))
    pk = S["pochylnie_kresk"]
    if pk is not None:
        czesci = sorted(list(pk.geoms) if hasattr(pk, "geoms") else [pk], key=lambda g: -g.area)
        print("Pochylnie (kreskowanie, bufor 0,35 m): %d skupisk > 20 m2:" % sum(1 for g in czesci if g.area > 20))
        for g in czesci:
            if g.area > 20:
                hull = g.convex_hull
                mr = hull.minimum_rotated_rectangle
                xy = list(mr.exterior.coords)
                b = sorted([math.dist(xy[i], xy[i + 1]) for i in range(2)])
                print("   pole kreskowania %.1f, obwiednia wypukła %.1f m2, prostokąt %.1f x %.1f m, środek (%.1f, %.1f), odl. do hal %.2f m, w halach %.1f m2" % (
                    g.area, hull.area, b[0], b[1], hull.centroid.x, hull.centroid.y, hull.distance(H), hull.intersection(H).area))
    # porównanie z użytkownikiem
    for warstwa, klucz in (("ZIELEN-NA-GRUNCIE", "zielen_grunt"), ("ZIELEN-NA-STROPIE", "zielen_strop")):
        U_raw = unary_union([P for _, P in polilinie_v2(warstwa)])
        U = unary_union([P for _, P in polilinie_v2(warstwa, f)])
        for nazwa, Z in (("widoczne", S["widoczne"].get(klucz)), ("pełne", S["pelne"].get(klucz))):
            Z = Z.intersection(G)
            print("%s vs PZT %s: użytk. po korekcie %.2f m2, PZT %.2f m2; wspólne %.2f; tylko użytk. %.2f; tylko PZT %.2f; IoU %.3f (bez korekty skali IoU %.3f)" % (
                warstwa, nazwa, U.area, Z.area, U.intersection(Z).area, U.difference(Z).area, Z.difference(U).area,
                U.intersection(Z).area / U.union(Z).area, U_raw.intersection(Z).area / U_raw.union(Z).area))
        out[warstwa] = {"uzytk_po_korekcie": round(U.area, 2), "uzytk_bez_korekty": round(U_raw.area, 2)}
    json.dump(out, open(os.path.join(HERE, "pzt_strefy_widoczne.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

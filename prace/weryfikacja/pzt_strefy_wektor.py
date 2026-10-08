"""
Strefy zagospodarowania z WEKTOROWEGO PZT (odzyskany z gita): wypełnienia w kolorach legendy -> wielokąty PL-2000.
Klucz strefy = (kolor wypełnienia RGB 0-255, krycie). Legenda PZT (x < 290 pt) – patrz LEGENDA niżej.
Wynik: _cache/pzt_strefy.pkl (wielokąty shapely) + pzt_strefy_pola.json (pola w granicy działki).
Uruchom: python prace/weryfikacja/pzt_strefy_wektor.py
"""
import json
import math
import os
import pickle
from collections import defaultdict

import pymupdf
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

import pzt_wektor_hale as W

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache", "pzt_strefy.pkl")

# (R, G, B, krycie*1000 zaokrąglone) -> nazwa (z legendy PZT, wypełnienia przy x 200-288 pt)
LEGENDA = {
    (219, 219, 219, 698): "ciągi pieszo-jezdne (kostka 8 cm)",
    (219, 219, 20, 498): "ciągi piesze (kostka 6 cm)",
    (125, 180, 163, 298): "plac przy lokalach usługowych",
    (13, 206, 96, 298): "zieleń na gruncie rodzimym",
    (120, 246, 173, 298): "zieleń na stropie garażu",
    (136, 179, 137, 600): "geokrata (miejsca postojowe, rowery)",
    (13, 206, 96, 498): "ogrody deszczowe",
    (99, 100, 102, 498): "opaski z kostki",
    (207, 182, 113, 498): "plac zabaw",
    (155, 117, 198, 498): "miejsca rekreacji",
    (152, 152, 152, 298): "ściany zabezpieczające pochylnie",
}


def bez(p0, p1, p2, p3, n=8):
    out = []
    for i in range(1, n + 1):
        t = i / n
        a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t ** 2; d = t ** 3
        out.append((a * p0.x + b * p1.x + c * p2.x + d * p3.x, a * p0.y + b * p1.y + c * p2.y + d * p3.y))
    return out


def pierscienie(items, tol=0.05):
    rings, cur, last = [], [], None
    for it in items:
        if it[0] == "re":
            r = it[1]
            rings.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)])
            last = None
            continue
        if it[0] == "qu":
            q = it[1]
            rings.append([(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)])
            last = None
            continue
        p0 = it[1]
        if last is None or math.dist((p0.x, p0.y), last) > tol:
            if len(cur) >= 3:
                rings.append(cur)
            cur = [(p0.x, p0.y)]
        if it[0] == "l":
            cur.append((it[2].x, it[2].y))
            last = (it[2].x, it[2].y)
        elif it[0] == "c":
            cur += bez(it[1], it[2], it[3], it[4])
            last = (it[4].x, it[4].y)
    if len(cur) >= 3:
        rings.append(cur)
    return rings


def wielokat(rings, even_odd):
    polys = []
    for r in rings:
        pl = [W.pt_do_pl(x, y) for x, y in r]
        P = make_valid(Polygon(pl)).buffer(0)
        if P.area > 0.01:
            polys.append(P)
    if not polys:
        return None
    if even_odd:
        acc = polys[0]
        for P in polys[1:]:
            acc = acc.symmetric_difference(P)
        return acc.buffer(0)
    return unary_union(polys)


def main():
    if os.path.exists(CACHE):
        strefy = pickle.load(open(CACHE, "rb"))
    else:
        pg = pymupdf.open(W.PDF_WEKT)[0]
        dr = pg.get_drawings()
        strefy = defaultdict(list)
        for d in dr:
            if d["type"] not in ("f", "fs") or not d.get("fill") or d["rect"][0] < 600:
                continue
            k = tuple(round(v * 255) for v in d["fill"]) + (round((d.get("fill_opacity") or 1) * 1000),)
            if k not in LEGENDA:
                continue
            P = wielokat(pierscienie(d["items"]), d.get("even_odd", False))
            if P is not None:
                strefy[k].append(P)
        strefy = {k: unary_union(v) for k, v in strefy.items()}
        pickle.dump(strefy, open(CACHE, "wb"))
    T = json.load(open(os.path.join(HERE, "transformacja_uzytk_do_PZT.json")))
    G = Polygon(T["granica_po"])
    H = unary_union([Polygon(v) for v in T["hale_po"].values()])
    wyn = {}
    print("%-40s %10s %10s %10s %10s" % ("strefa (wypełnienie PZT)", "pole", "w działce", "w halach", "poza hal."))
    for k, nazwa in LEGENDA.items():
        P = strefy.get(k)
        if P is None:
            print("%-40s  brak" % nazwa); continue
        Pd = P.intersection(G)
        wyn[nazwa] = {"pole": round(P.area, 2), "w_dzialce": round(Pd.area, 2), "w_halach": round(Pd.intersection(H).area, 2),
                      "poza_halami": round(Pd.difference(H).area, 2)}
        print("%-40s %10.2f %10.2f %10.2f %10.2f" % (nazwa, P.area, Pd.area, Pd.intersection(H).area, Pd.difference(H).area))
    json.dump(wyn, open(os.path.join(HERE, "pzt_strefy_pola.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

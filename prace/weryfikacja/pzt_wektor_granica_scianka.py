"""
Jakie linie wektorowego PZT biegną wzdłuż granicy działki i ścianki użytkownika?
Dla każdego stylu (kolor, grubość, typ) liczona jest długość odcinków równoległych (do 3°) i leżących w pasie +-2 m
od boku użytkownika. Dla stylu dominującego: odsunięcie linii PZT od każdego boku (mediana, + = na zewnątrz),
a potem pole wielokąta z bokami przesuniętymi do linii PZT.
"""
import json
import math
import os
import pickle
from collections import defaultdict

import numpy as np
from shapely.geometry import LineString, Polygon

import pzt_wektor_hale as W
from pzt_wektor_hale_dopasowanie import przeciecie

HERE = os.path.dirname(os.path.abspath(__file__))


def wszystkie_odcinki(dr, xmin=1000):
    """(styl, a, b) dla wszystkich linii prostych na mapie (bez legendy)."""
    out = []
    for d in dr:
        if d["rect"][0] < xmin:
            continue
        col = d.get("color") if d["type"] in ("s", "fs") else d.get("fill")
        if not col:
            continue
        styl = (d["type"], tuple(round(v, 2) for v in col), round(d.get("width") or 0, 2))
        for it in d["items"]:
            if it[0] == "l":
                out.append((styl, W.pt_do_pl(it[1].x, it[1].y), W.pt_do_pl(it[2].x, it[2].y)))
    return out


def analiza(odc, pts, zamkniety, nazwa, pas=2.0):
    P = Polygon(pts)
    if zamkniety and not P.exterior.is_ccw:
        pts = pts[::-1]
    n = len(pts)
    boki = [(pts[i], pts[(i + 1) % n]) for i in range(n if zamkniety else n - 1)]
    styl_dl = defaultdict(float)
    per_bok = defaultdict(lambda: defaultdict(list))
    for bi, (p, q) in enumerate(boki):
        L = math.dist(p, q)
        ue, un = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        ne, nn = un, -ue
        for styl, a, b in odc:
            la = math.dist(a, b)
            if la < 0.05:
                continue
            if abs(((b[0] - a[0]) * ue + (b[1] - a[1]) * un) / la) < math.cos(math.radians(3)):
                continue
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            t = (m[0] - p[0]) * ue + (m[1] - p[1]) * un
            d = (m[0] - p[0]) * ne + (m[1] - p[1]) * nn
            if 0 <= t <= L and abs(d) <= pas:
                styl_dl[styl] += la
                per_bok[styl][bi].append((d, la))
    calk = sum(math.dist(p, q) for p, q in boki)
    print("\n=== %s: długość %.1f m; style PZT biegnące wzdłuż (łączna długość w pasie +-%.0f m):" % (nazwa, calk, pas))
    ranking = sorted(styl_dl.items(), key=lambda kv: -kv[1])[:8]
    for styl, dl in ranking:
        nb = sum(1 for bi in per_bok[styl] if sum(l for _, l in per_bok[styl][bi]) > 0.3 * math.dist(*boki[bi]))
        print("   %-45s %8.1f m  (boków pokrytych >30%%: %d z %d)" % (styl, dl, nb, len(boki)))
    return boki, per_bok, ranking


def odsuniecia(boki, per_bok, styl):
    wyn = []
    for bi, (p, q) in enumerate(boki):
        L = math.dist(p, q)
        dd = per_bok[styl].get(bi, [])
        if not dd or sum(l for _, l in dd) < 0.3 * L:
            wyn.append(None)
            continue
        d = np.array([x for x, _ in dd]); w = np.array([l for _, l in dd])
        # dominująca linia: najcięższy koszyk 0,1 m
        h, kr = np.histogram(d, bins=40, range=(-2, 2), weights=w)
        k = int(np.argmax(h))
        sel = (d >= kr[k] - 0.1) & (d <= kr[k + 1] + 0.1)
        wyn.append(float(np.average(d[sel], weights=w[sel])))
    return wyn


def main():
    dr = W.wczytaj_sciezki()
    odc = wszystkie_odcinki(dr)
    print("odcinków prostych na mapie:", len(odc))
    gr = [tuple(map(float, l.split())) for l in open(os.path.join(W.DU, "wierzcholki_polilinii_granica_działki_checked.txt"), encoding="utf-8") if l.strip()]
    sc = [tuple(map(float, l.split())) for l in open(os.path.join(W.DU, "wierzcholki_polilinii_wykop_checked.txt"), encoding="utf-8") if l.strip()]
    wynik = {}
    boki, per_bok, ranking = analiza(odc, gr, True, "GRANICA DZIAŁKI (użytkownik)")
    for styl, _ in ranking[:3]:
        od = odsuniecia(boki, per_bok, styl)
        print("   styl %s – odsunięcie linii PZT od boków użytk. [m, + na zewnątrz]: %s" % (styl, ", ".join("%d:%s" % (i + 1, "%+.2f" % o if o is not None else "–") for i, o in enumerate(od))))
        if None not in od:
            linie = []
            for (p, q), o in zip(boki, od):
                L = math.dist(p, q); ue, un = (q[0] - p[0]) / L, (q[1] - p[1]) / L
                linie.append(((p[0] + un * o, p[1] - ue * o), (ue, un)))
            rog = [przeciecie(linie[i - 1][0], linie[i - 1][1], linie[i][0], linie[i][1]) for i in range(len(linie))]
            Pp = Polygon(rog)
            print("   -> wielokąt z bokami na linii PZT: pole %.2f m2 (użytk. %.2f; oficjalnie 25 290,00)" % (Pp.area, Polygon(gr).area))
            wynik.setdefault("granica", {})[str(styl)] = {"odsuniecia": od, "pole": round(Pp.area, 2), "wierzcholki": [(round(x, 3), round(y, 3)) for x, y in rog]}
    boki, per_bok, ranking = analiza(odc, sc, False, "ŚCIANKA (użytkownik, linia otwarta)", pas=2.0)
    for styl, _ in ranking[:4]:
        od = odsuniecia(boki, per_bok, styl)
        print("   styl %s – odsunięcie od boków ścianki: %s" % (styl, ", ".join("%d:%s" % (i + 1, "%+.2f" % o if o is not None else "–") for i, o in enumerate(od))))
    json.dump(wynik, open(os.path.join(HERE, "pzt_wektor_granica.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

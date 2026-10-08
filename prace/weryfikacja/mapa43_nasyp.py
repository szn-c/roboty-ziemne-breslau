"""
Zasięg nasypu niekontrolowanego z mapy 4.3 DGI (odzyskana z gita: prace/_odzyskane/4.3.pdf).
Georeferencja: środki 28 wektorowych symboli otworów (zielone kółka 11×11 pt) -> współrzędne z tabeli DGI
(otwór 12: E = 6 433 688,2; dopasowanie afiniczne, numery wg najbliższej etykiety).
Strefy nasypu: wypełnienia szare (0,43; 0,43; 0,43).
Wynik: mapa43_nasyp.json (wielokąty PL-2000, pola, otwory w strefach).
"""
import json
import math
import os
import re

import numpy as np
import pymupdf
from shapely.geometry import Point, Polygon

from geometria_kontrola import OTWORY
from pzt_strefy_wektor import pierscienie

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PDF = os.path.join(REPO, "prace", "_odzyskane", "4.3.pdf")


def main():
    O = dict(OTWORY)
    O[12] = (5659037.4, 6433688.2, 124.50)
    pg = pymupdf.open(PDF)[0]
    dr = pg.get_drawings()
    sym = [((d["rect"].x0 + d["rect"].x1) / 2, (d["rect"].y0 + d["rect"].y1) / 2) for d in dr
           if d["type"] == "fs" and d.get("fill") and all(abs(a - b) < 0.02 for a, b in zip(d["fill"], (0.2, 0.63, 0.17)))]
    lab = [(int(w[4]), ((w[0] + w[2]) / 2, (w[1] + w[3]) / 2)) for w in pg.get_text("words") if re.fullmatch(r"\d{1,2}", w[4]) and int(w[4]) in O]
    # para: numer -> najbliższy symbol (każdy numer raz, pierwsze wystąpienie etykiety)
    pary = {}
    for nr, (lx, ly) in lab:
        if nr in pary:
            continue
        s = min(sym, key=lambda q: math.dist(q, (lx, ly)))
        if math.dist(s, (lx, ly)) < 25:
            pary[nr] = s

    def dopasuj(pp):
        A, b = [], []
        for nr, (x, y) in pp.items():
            N, E, H = O[nr]
            A += [[x, y, 1, 0, 0, 0], [0, 0, 0, x, y, 1]]
            b += [E, N]
        p, *_ = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)
        f = lambda x, y: (p[0] * x + p[1] * y + p[2], p[3] * x + p[4] * y + p[5])
        res = {nr: math.dist(f(x, y), (O[nr][1], O[nr][0])) for nr, (x, y) in pp.items()}
        return p, f, res

    p, f, res = dopasuj(pary)
    for _ in range(5):  # odrzucanie błędnych par (np. etykieta CPTU obok symbolu innego otworu)
        med = float(np.median(list(res.values())))
        zle = [nr for nr, r in res.items() if r > max(3 * med, 3.0)]
        if not zle:
            break
        print("  odrzucam pary (reszta > 3×mediana):", {nr: round(res[nr], 1) for nr in zle})
        pary = {nr: s for nr, s in pary.items() if nr not in zle}
        p, f, res = dopasuj(pary)
    res = list(res.values())
    print("georeferencja: %d otworów, rms %.2f m, maks. %.2f m (skala %.4f m/pt)" % (len(pary), float(np.sqrt(np.mean(np.square(res)))), max(res), math.hypot(p[0], p[3])))
    strefy = []
    for d in dr:
        if d["type"] in ("f", "fs") and d.get("fill") and all(abs(a - 0.43) < 0.02 for a in d["fill"]):
            for r in pierscienie(d["items"]):
                P = Polygon([f(x, y) for x, y in r]).buffer(0)
                if P.area > 1:
                    strefy.append(P)
    out = []
    for P in strefy:
        w = [nr for nr, (N, E, H) in O.items() if P.contains(Point(E, N))]
        print("  strefa nasypu: pole %.1f m2, otwory w strefie: %s" % (P.area, w))
        out.append({"wierzcholki": [(round(x, 3), round(y, 3)) for x, y in P.exterior.coords], "pole": round(P.area, 2), "otwory": w})
    json.dump({"rms_georef_m": float(np.sqrt(np.mean(np.square(res)))), "strefy": out}, open(os.path.join(HERE, "mapa43_nasyp.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

"""
Elementy fundamentów głębsze niż spód płyty (rzuty PW_1A…PW_8B, odzyskane z gita do prace/_odzyskane/).
Dla każdej etykiety "d.k. −x,xx" (−4,34 / −4,54 / −4,93 / −5,40 / −5,83 / −6,00) szukam najmniejszej ścieżki
w stylu obrysu obniżenia (linia 0,85 pt), której obwiednia zawiera etykietę (pogrubienia, rdzenie).
Doły (PF): obrys brany z wymiarów na rysunku (tabela DOLY niżej – odczyt z wycinków PW_1A, sesja 8.10).
Wynik: fundamenty_glebsze.json + ekran.
"""
import json
import math
import os
import re
from collections import Counter, defaultdict

import pymupdf
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ODZ = os.path.join(REPO, "prace", "_odzyskane")
M = 0.0352778  # m na pt przy skali 1:100
BUD = ("1A", "2C", "3A", "4B", "5A", "6A", "7A", "8B")
ETYK = ("4,34", "4,54", "4,93", "5,40", "5,83", "6,00")


def etykiety(pg):
    out = []
    for b in pg.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            t = " ".join(s["text"] for s in l["spans"]).strip()
            for m in re.finditer(r"d\.k\.\s*-\s*(\d,\d\d)", t):
                if m.group(1) in ETYK and l["bbox"][0] < 2050:
                    out.append((m.group(1), ((l["bbox"][0] + l["bbox"][2]) / 2, (l["bbox"][1] + l["bbox"][3]) / 2)))
    return out


def main():
    wynik = {}
    for b in BUD:
        pg = pymupdf.open(os.path.join(ODZ, f"PW_{b}.pdf"))[0]
        dr = pg.get_drawings()
        # obrysy obniżeń: (a) pojedyncze ścieżki 0,85 pt (rdzenie), (b) obszary zamknięte z odcinków 0,85 pt (pogrubienia)
        obr = [Polygon([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]) for r in
               (d["rect"] for d in dr if d["type"] == "s" and abs((d.get("width") or 0) - 0.85) < 0.02 and d["rect"].x0 < 2050)
               if 2.0 < r.width * M < 12 and 2.0 < r.height * M < 12]
        seg = [LineString([(it[1].x, it[1].y), (it[2].x, it[2].y)]) for d in dr if d["type"] == "s" and abs((d.get("width") or 0) - 0.85) < 0.02
               and d["rect"].x0 < 2050 for it in d["items"] if it[0] == "l"]
        obr += [p for p in polygonize(unary_union(seg)) if 4.0 < p.area * M * M < 150]
        el = []
        for poz, (x, y) in etykiety(pg):
            P = Point(x, y)
            kand = [g for g in obr if g.buffer(3).contains(P)]
            if kand:
                g = min(kand, key=lambda g: g.area)
                minx, miny, maxx, maxy = g.bounds
                w, h = sorted((round((maxx - minx) * M, 2), round((maxy - miny) * M, 2)))
                el.append((poz, w, h))
            else:
                el.append((poz, None, None))
        wynik[b] = el
        c = Counter((p, w, h) for p, w, h in el)
        print("%s: %s" % (b, "; ".join("d.k. −%s %s ×%d" % (p, ("%.2f×%.2f m" % (w, h)) if w else "bez obrysu 0,85", n) for (p, w, h), n in sorted(c.items(), key=lambda kv: (kv[0][0], -kv[1])))))
    json.dump(wynik, open(os.path.join(HERE, "fundamenty_glebsze.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

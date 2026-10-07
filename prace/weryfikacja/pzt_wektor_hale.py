"""
Porównanie obrysów hal użytkownika (*_checked) z obrysem garażu z WEKTOROWEGO PZT (odzyskany z gita, commit 851b25a).
Styl z legendy PZT: "obrys projektowanej kondygnacji garażu podziemnego" = linia (0.42, 0.04, 0.30), grubość 0.85 pt, przerywana.
Transformacja strona PZT -> PL-2000: jak w wyciagnij_dane_z_pdf.py (sprawdzona na krzyżach siatki 50 m, błąd ok. 0,05 m).

Wymaga: prace/weryfikacja/_cache/pzt_wekt_drawings.pkl (ścieżki z prace/_odzyskane/PZT_wektorowy.pdf).
Wynik: ekran + prace/weryfikacja/pzt_wektor_hale.json
"""
import json
import math
import os
import pickle

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import linemerge, polygonize, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DU = os.path.join(REPO, "prace", "dane_wejsciowe_uzytkownika")
E0, N0 = 6433700.0, 5659050.0
X0, Y0, KAT, K = 2879.2, 309.7, 7.365944612743048, 72 / 0.0254 / 250
c, s = math.cos(math.radians(KAT)), math.sin(math.radians(KAT))


def pt_do_pl(x, y):
    dx, dy = (x - X0) / K, (y - Y0) / K
    return E0 + dx * c + dy * (-s), N0 + dx * (-s) + dy * (-c)


PDF_WEKT = os.path.join(REPO, "prace", "_odzyskane", "PZT_wektorowy.pdf")
CACHE_PKL = os.path.join(HERE, "_cache", "pzt_wekt_drawings.pkl")


def wczytaj_sciezki():
    """Ścieżki wektorowego PZT. Gdy brak: odzysk PDF z gita (commit 851b25a) i zapis do _cache (ok. 1 min)."""
    if not os.path.exists(CACHE_PKL):
        import subprocess
        import pymupdf
        if not os.path.exists(PDF_WEKT):
            os.makedirs(os.path.dirname(PDF_WEKT), exist_ok=True)
            with open(PDF_WEKT, "wb") as f:
                f.write(subprocess.run(["git", "show", "851b25a:dokumentacja/04_projekt_zagospodarowania_i_architektura/6. PZT.pdf"],
                                       cwd=REPO, check=True, capture_output=True).stdout)
        dr = pymupdf.open(PDF_WEKT)[0].get_drawings()
        os.makedirs(os.path.dirname(CACHE_PKL), exist_ok=True)
        pickle.dump([{k: v for k, v in x.items() if k in ("items", "color", "fill", "width", "rect", "type", "dashes")} for x in dr],
                    open(CACHE_PKL, "wb"))
    return pickle.load(open(CACHE_PKL, "rb"))


def segmenty_stylu(dr, kolor, szer, tol_k=0.02, tol_w=0.03, xmin=1000):
    out = []
    for d in dr:
        col = d.get("color")
        if not col or d["type"] not in ("s", "fs"):
            continue
        if max(abs(col[i] - kolor[i]) for i in range(3)) > tol_k or abs((d.get("width") or 0) - szer) > tol_w:
            continue
        if d["rect"][0] < xmin:
            continue
        for it in d["items"]:
            if it[0] == "l":
                a, b = it[1], it[2]
                out.append((pt_do_pl(a.x, a.y), pt_do_pl(b.x, b.y)))
            elif it[0] == "re":
                r = it[1]
                pts = [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1), (r.x0, r.y0)]
                for i in range(4):
                    out.append((pt_do_pl(*pts[i]), pt_do_pl(*pts[i + 1])))
            elif it[0] == "c":
                a, b = it[1], it[4]
                out.append((pt_do_pl(a.x, a.y), pt_do_pl(b.x, b.y)))
    return out


def wczytaj_hale():
    hale, cur = {}, None
    for l in open(os.path.join(DU, "wierzcholki_polilinii_hala1-8_checked.txt"), encoding="utf-8"):
        t = l.strip()
        if not t:
            continue
        if t.startswith("hala"):
            cur = int(t[4:]); hale[cur] = []
        else:
            hale[cur].append(tuple(map(float, t.split())))
    return hale


def main():
    dr = wczytaj_sciezki()
    seg = segmenty_stylu(dr, (0.42, 0.04, 0.30), 0.85)
    print("odcinków w stylu 'obrys garażu':", len(seg), " łączna długość %.1f m" % sum(math.dist(a, b) for a, b in seg))
    hale = wczytaj_hale()
    wynik = {}
    for nr, pts in hale.items():
        P = Polygon(pts)
        if not P.exterior.is_ccw:
            pts = pts[::-1]
        n = len(pts)
        boki = []
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            L = math.dist(p, q)
            ue, un = (q[0] - p[0]) / L, (q[1] - p[1]) / L
            ne, nn = un, -ue  # normalna na zewnątrz (CCW)
            # odcinki stylu leżące wzdłuż boku: równoległe (kąt < 3°), w pasie +-3 m, rzut w obrębie boku
            odl, dl = [], 0.0
            for a, b in seg:
                la = math.dist(a, b)
                if la < 0.05:
                    continue
                va = ((b[0] - a[0]) / la, (b[1] - a[1]) / la)
                if abs(va[0] * ue + va[1] * un) < math.cos(math.radians(3)):
                    continue
                for m in (a, b, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)):
                    t = (m[0] - p[0]) * ue + (m[1] - p[1]) * un
                    d = (m[0] - p[0]) * ne + (m[1] - p[1]) * nn
                    if -1 <= t <= L + 1 and abs(d) <= 3.0:
                        odl.append(d)
                        dl += la / 3
            if odl:
                h, kr = np.histogram(odl, bins=120, range=(-3, 3))
                k = int(np.argmax(h))
                sel = [d for d in odl if kr[k] - 0.1 <= d <= kr[k + 1] + 0.1]
                boki.append({"bok": i + 1, "dl": round(L, 2), "odsuniecie_PZT_na_zewnatrz_m": round(float(np.median(sel)), 3),
                             "pokrycie_dl_m": round(dl, 1), "inne_linie": sorted({round(float((kr[j] + kr[j + 1]) / 2), 2) for j in range(len(h)) if h[j] >= max(3, h[k] / 3) and abs((kr[j] + kr[j + 1]) / 2 - kr[k]) > 0.3})})
            else:
                boki.append({"bok": i + 1, "dl": round(L, 2), "odsuniecie_PZT_na_zewnatrz_m": None, "pokrycie_dl_m": 0})
        wynik[nr] = boki
        print("hala %d (pole użytk. %.2f):" % (nr, P.area))
        for b in boki:
            print("   bok %d (%.2f m): PZT %s m na zewnątrz, linia PZT wzdłuż boku na dł. %.1f m %s" %
                  (b["bok"], b["dl"], "%+.3f" % b["odsuniecie_PZT_na_zewnatrz_m"] if b["odsuniecie_PZT_na_zewnatrz_m"] is not None else "brak",
                   b["pokrycie_dl_m"], ("inne równoległe: %s" % b["inne_linie"]) if b.get("inne_linie") else ""))
    # obrysy z PZT: domknięcie przerywanej linii przez bufor i poligonizację
    lin = unary_union([LineString([a, b]) for a, b in seg]).buffer(0.6)
    otwory = [Polygon(r) for r in lin.interiors] if lin.geom_type == "Polygon" else [Polygon(r) for g in lin.geoms for r in g.interiors]
    print("\nZamknięte obrysy z PZT (wnętrza buforu 0,6 m linii garażu, pole > 500 m2) – pole powiększone o bufor:")
    for o in sorted(otwory, key=lambda g: -g.area):
        if o.area < 500:
            continue
        ob = o.buffer(0.6, join_style=2)
        traf = [nr for nr, pts in hale.items() if Polygon(pts).intersection(ob).area > 0.5 * Polygon(pts).area]
        hal = traf[0] if traf else None
        Pu = Polygon(hale[hal]) if hal else None
        print("  obrys PZT %.2f m2, środek E=%.2f N=%.2f; hala użytk. %s: pole %.2f, przesunięcie środków %.2f m, wspólne/suma %.1f%%" %
              (ob.area, ob.centroid.x, ob.centroid.y, hal, Pu.area if Pu else 0, Pu.centroid.distance(ob.centroid) if Pu else 0,
               Pu.intersection(ob).area / Pu.union(ob).area * 100 if Pu else 0))
        if hal:
            wynik.setdefault("obrysy_pzt", {})[hal] = {"pole": round(ob.area, 2), "przes_srodka": round(Pu.centroid.distance(ob.centroid), 2)}
    json.dump(wynik, open(os.path.join(HERE, "pzt_wektor_hale.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

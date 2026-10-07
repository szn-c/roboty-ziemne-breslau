"""
Dokładne porównanie hal: użytkownik (*_checked) vs PZT wektorowy (obrys garażu) vs rzut zabezpieczenia (v1, geometria_G.json).
Dla każdego boku hali użytkownika: linie PZT w stylu "obrys garażu" równoległe do boku, w pasie +-3 m;
grupowanie po odsunięciu (co 0,05 m), z długością pokrycia. Linia zewnętrzna = najdalej na zewnątrz z pokryciem >= 40% boku.
Narożniki PZT = przecięcia linii zewnętrznych sąsiednich boków. Potem transformacja przez podobieństwo (Helmert 4p)
użytkownik -> PZT na wszystkich narożnikach.
"""
import json
import math
import os
import pickle

import numpy as np
from shapely.geometry import Polygon

import pzt_wektor_hale as W

HERE = os.path.dirname(os.path.abspath(__file__))


def linie_boku(seg, p, q, zakres=3.0):
    L = math.dist(p, q)
    ue, un = (q[0] - p[0]) / L, (q[1] - p[1]) / L
    ne, nn = un, -ue
    grupy = {}
    for a, b in seg:
        la = math.dist(a, b)
        if la < 0.05:
            continue
        if abs(((b[0] - a[0]) * ue + (b[1] - a[1]) * un) / la) < math.cos(math.radians(2)):
            continue
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        t = (m[0] - p[0]) * ue + (m[1] - p[1]) * un
        d = (m[0] - p[0]) * ne + (m[1] - p[1]) * nn
        if -1 <= t <= L + 1 and abs(d) <= zakres:
            k = round(d / 0.05) * 0.05
            g = grupy.setdefault(round(k, 2), [0.0, []])
            g[0] += la
            g[1].append(d)
    # scal sąsiednie koszyki
    klucze = sorted(grupy)
    scalone = []
    for k in klucze:
        if scalone and k - scalone[-1]["k_max"] <= 0.051:
            s = scalone[-1]
            s["dl"] += grupy[k][0]; s["d"] += grupy[k][1]; s["k_max"] = k
        else:
            scalone.append({"k_max": k, "dl": grupy[k][0], "d": list(grupy[k][1])})
    out = [{"odsuniecie": float(np.median(s["d"])), "pokrycie": s["dl"] / L} for s in scalone]
    return out, (ue, un, ne, nn), L


def przeciecie(p1, d1, p2, d2):
    A = np.array([[d1[0], -d2[0]], [d1[1], -d2[1]]])
    t = np.linalg.solve(A, np.array([p2[0] - p1[0], p2[1] - p1[1]]))
    return (p1[0] + d1[0] * t[0], p1[1] + d1[1] * t[0])


def helmert(src, dst):
    """dst = s*R*src + t ; zwraca (s, kąt_deg, tE, tN, rms) oraz funkcję."""
    S = np.array(src); D = np.array(dst)
    cs, cd = S.mean(0), D.mean(0)
    s0, d0 = S - cs, D - cd
    a = (s0[:, 0] * d0[:, 0] + s0[:, 1] * d0[:, 1]).sum() / (s0 ** 2).sum()
    b = (s0[:, 0] * d0[:, 1] - s0[:, 1] * d0[:, 0]).sum() / (s0 ** 2).sum()
    f = lambda P: np.column_stack([a * (P[:, 0] - cs[0]) - b * (P[:, 1] - cs[1]) + cd[0], b * (P[:, 0] - cs[0]) + a * (P[:, 1] - cs[1]) + cd[1]])
    res = f(S) - D
    return math.hypot(a, b), math.degrees(math.atan2(b, a)), cs, cd, float(np.sqrt((res ** 2).sum(1).mean())), f


def main():
    dr = W.wczytaj_sciezki()
    seg = W.segmenty_stylu(dr, (0.42, 0.04, 0.30), 0.85)
    hale = W.wczytaj_hale()
    G = json.load(open(os.path.join(W.REPO, "prace/obliczenia_v1/_skrypt/dane/geometria_G.json")))
    wynik, src_all, dst_all = {}, [], []
    for nr, pts in hale.items():
        if not Polygon(pts).exterior.is_ccw:
            pts = pts[::-1]
        n = len(pts)
        zew, wew, opis = [], [], []
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            lin, (ue, un, ne, nn), L = linie_boku(seg, p, q)
            mocne = [l for l in lin if l["pokrycie"] >= 0.4]
            if not mocne:
                zew.append(None); wew.append(None)
                opis.append("bok %d: brak linii" % (i + 1))
                continue
            lz = max(mocne, key=lambda l: l["odsuniecie"])
            lw = min(mocne, key=lambda l: l["odsuniecie"])
            zew.append(((p[0] + ne * lz["odsuniecie"], p[1] + nn * lz["odsuniecie"]), (ue, un)))
            wew.append(((p[0] + ne * lw["odsuniecie"], p[1] + nn * lw["odsuniecie"]), (ue, un)))
            opis.append("bok %d (%.2f m): linie PZT [m na zewnątrz / pokrycie]: %s" % (
                i + 1, L, ", ".join("%+.2f/%.0f%%" % (l["odsuniecie"], l["pokrycie"] * 100) for l in lin if l["pokrycie"] >= 0.15)))
        rog_z = []
        for i in range(n):
            a, b = zew[i - 1], zew[i]
            rog_z.append(przeciecie(a[0], a[1], b[0], b[1]) if a and b else None)
        rog_w = []
        for i in range(n):
            a, b = wew[i - 1], wew[i]
            rog_w.append(przeciecie(a[0], a[1], b[0], b[1]) if a and b else None)
        Pz = Polygon(rog_z) if None not in rog_z else None
        Pw = Polygon(rog_w) if None not in rog_w else None
        Pu = Polygon(pts)
        Pg = Polygon(G["hale"][str(nr)])
        przes = [(rog_z[i][0] - pts[i][0], rog_z[i][1] - pts[i][1]) for i in range(n)] if Pz else []
        for i in range(n):
            if rog_z[i]:
                src_all.append(pts[i]); dst_all.append(rog_z[i])
        wynik[nr] = {"pole_uzytk": round(Pu.area, 2), "pole_PZT_zewn": round(Pz.area, 2) if Pz else None,
                     "pole_PZT_wewn": round(Pw.area, 2) if Pw else None, "pole_rzut_zabezp_v1": round(Pg.area, 2),
                     "narozniki_PZT_zewn": [(round(x, 3), round(y, 3)) for x, y in rog_z] if Pz else None,
                     "przesuniecia_naroznikow_uzytk_do_PZT": [(round(a, 2), round(b, 2)) for a, b in przes]}
        print("hala %d: pole użytk. %.2f | PZT zewn. %s | PZT wewn. %s | rzut zabezp. (v1) %.2f" % (
            nr, Pu.area, "%.2f" % Pz.area if Pz else "-", "%.2f" % Pw.area if Pw else "-", Pg.area))
        for o in opis:
            print("    " + o)
        if Pz:
            print("    narożniki: przesunięcie użytk. -> PZT zewn. [m]: " + "; ".join("(%+.2f, %+.2f)" % d for d in przes))
            print("    PZT zewn. vs rzut zabezp.: przesunięcie środków %.2f m, wspólne/suma %.1f%%" % (
                Pz.centroid.distance(Pg.centroid), Pz.intersection(Pg).area / Pz.union(Pg).area * 100))
    s, kat, cs, cd, rms, f = helmert(src_all, dst_all)
    print("\nPodobieństwo użytkownik -> PZT (wszystkie narożniki, n=%d): skala %.5f (%.2f%%), obrót %+.4f°, przesunięcie środka (%+.2f, %+.2f) m, "
          "błąd rms po dopasowaniu %.2f m" % (len(src_all), s, (s - 1) * 100, kat, cd[0] - cs[0], cd[1] - cs[1], rms))
    wynik["helmert_uzytk_do_PZT"] = {"skala": s, "obrot_deg": kat, "srodek_uzytk": list(cs), "srodek_PZT": list(cd), "rms": rms}
    # to samo dla rzutu zabezpieczenia (v1) -> PZT: narożniki v1 przypisane do najbliższych narożników PZT
    src2, dst2 = [], []
    for nr in hale:
        rz = wynik[nr]["narozniki_PZT_zewn"]
        if not rz:
            continue
        for p in G["hale"][str(nr)]:
            q = min(rz, key=lambda r: math.dist(r, p))
            if math.dist(q, p) < 3:
                src2.append(tuple(p)); dst2.append(q)
    s2, kat2, cs2, cd2, rms2, _ = helmert(src2, dst2)
    print("Podobieństwo rzut zabezpieczenia (v1) -> PZT (n=%d): skala %.5f (%.2f%%), obrót %+.4f°, przesunięcie (%+.2f, %+.2f) m, rms %.2f m" % (
        len(src2), s2, (s2 - 1) * 100, kat2, cd2[0] - cs2[0], cd2[1] - cs2[1], rms2))
    wynik["helmert_v1_do_PZT"] = {"skala": s2, "obrot_deg": kat2, "rms": rms2}
    json.dump(wynik, open(os.path.join(HERE, "pzt_wektor_hale_dopasowanie.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

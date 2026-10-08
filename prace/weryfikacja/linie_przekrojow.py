"""
Linie przekrojów terenowych T1–T4 (rysunek Z-04 „Przekroje terenowe", 4IDEA, XI 2025) w układzie PL-2000/6.

Co robi:
1. Z wektorów rysunku (plan lokalizacji przekrojów) bierze 4 kropkowane linie przekrojów (kolejność rysowania = kolejność kropek).
2. Dopasowuje plan do PL-2000: niebieskie obrysy garaży na planie ↔ hale z prace/dane/geometria.json
   (podobieństwo: skala, obrót ok. −7,4°, przesunięcie; błąd ok. 0,2 m).
3. Zapisuje wierzchołki linii (PL-2000) do prace/dane/linie_przekrojow.json, w kolejności od LEWEJ do PRAWEJ strony rysunku przekroju.
Uruchomienie: python prace/weryfikacja/linie_przekrojow.py
"""
import json
import math
import os

import numpy as np
import pymupdf as fitz
from scipy.optimize import linear_sum_assignment
from shapely.geometry import LineString, MultiPoint, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PDF = os.path.join(REPO, "dokumentacja", "04_projekt_zagospodarowania_i_architektura",
                   "8. Przekroje terenowe z naniesionym średnim poziomem wody gruntowej.pdf")
DANE = os.path.join(REPO, "prace", "dane")
# etykiety T1..T4 w planie (pt strony): para (koniec lewy w przekroju, koniec prawy w przekroju) – wg opisów miejsc na rysunku
# T1, T2: ul. Drabika (zachód) -> ul. Buforowa (wschód); T3, T4: ul. Asfaltowa (południe) -> ul. Lutosławskiego (północ)
ETYKIETY = {"T1": [(116, 901), (1184, 861)], "T2": [(103, 556), (1093, 428)], "T3": [(1049, 1389), (905, 277)], "T4": [(276, 1134), (235, 215)]}


def transformacja_planu(pg):
    """plan (pt strony, y w dół) -> PL-2000: E = a·x − b·(−y) + tx ; N = b·x + a·(−y) + ty"""
    segs = []
    for x in pg.get_drawings():
        if x["rect"].x0 > 1300:
            continue
        col = tuple(round(v, 2) for v in (x.get("color") or ()))
        if col == (0.0, 0.0, 1.0) and round(x.get("width") or 0, 2) == 2.0:
            it = x["items"][0]
            segs.append(((it[1].x, it[1].y), (it[2].x, it[2].y)))
    n = len(segs)
    par = list(range(n))

    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if any(math.dist(a, b) < 4 for a in segs[i] for b in segs[j]):
                par[f(i)] = f(j)
    grp = {}
    for i in range(n):
        grp.setdefault(f(i), []).append(i)
    quads = [MultiPoint([pt for i in g for pt in segs[i]]).convex_hull for g in grp.values()]
    geo = json.load(open(os.path.join(DANE, "geometria.json"), encoding="utf-8"))
    H = {int(k): Polygon(v) for k, v in geo["hale"].items()}
    s0 = 0.0254 / 72 * 500
    Xf = np.array([(q.centroid.x, -q.centroid.y) for q in quads])
    ch = np.array([(H[k].centroid.x, H[k].centroid.y) for k in sorted(H)])
    cp = Xf * s0
    off = ch.mean(0) - cp.mean(0)
    pred = cp + off
    r, c = linear_sum_assignment(np.linalg.norm(pred[:, None, :] - ch[None, :, :], axis=2))
    M, v = [], []
    for (x, y), (E, N) in zip(Xf[r], ch[c]):
        M.append([x, -y, 1, 0]); v.append(E)
        M.append([y, x, 0, 1]); v.append(N)
    a, b, tx, ty = np.linalg.lstsq(np.array(M), np.array(v), rcond=None)[0]

    def tr(x, y):
        X, Y = x, -y
        return a * X - b * Y + tx, b * X + a * Y + ty
    # dopasowanie na wierzchołkach czworokątów (bez hali 2 – sześciokąt)
    pary = []
    for qi, q in enumerate(quads):
        hall = H[sorted(H)[c[list(r).index(qi)]]]
        if len(hall.exterior.coords) - 1 != 4:
            continue
        for pt in list(q.exterior.coords)[:-1]:
            E, N = tr(*pt)
            hp = min(hall.exterior.coords[:-1], key=lambda h: math.dist(h, (E, N)))
            pary.append((pt, hp))
    M, v = [], []
    for (x0, y0), (E, N) in pary:
        x, y = x0, -y0
        M.append([x, -y, 1, 0]); v.append(E)
        M.append([y, x, 0, 1]); v.append(N)
    a, b, tx, ty = np.linalg.lstsq(np.array(M), np.array(v), rcond=None)[0]
    res = [math.dist(tr(*pt), hp) for pt, hp in pary]
    info = {"a": a, "b": b, "tx": tx, "ty": ty, "skala_wzgledem_1_500": math.hypot(a, b) / s0, "obrot_stopnie": math.degrees(math.atan2(b, a)),
            "rms_m": float(np.sqrt(np.mean(np.square(res)))), "max_m": float(max(res)), "liczba_punktow": len(res)}
    return tr, info


def linie_kropkowane(pg):
    """Kolejność rysowania kropek = kolejność wzdłuż linii (kropkowane linie przekrojów mają grubość 1,13)."""
    rows = []
    for x in pg.get_drawings():
        if x["rect"].x0 > 1300:
            continue
        w = round(x.get("width") or 0, 2)
        for it in x["items"]:
            if it[0] == "l":
                a, b = it[1], it[2]
                rows.append((a.x, a.y, b.x, b.y, w))
    R = np.array(rows)
    L = np.hypot(R[:, 2] - R[:, 0], R[:, 3] - R[:, 1])
    mid = (R[:, :2] + R[:, 2:4]) / 2
    d = np.hypot(*(mid[1:] - mid[:-1]).T)
    ok = (d < 6) & (L[:-1] < 3) & (L[1:] < 3) & (R[:-1, 4] == 1.13) & (R[1:, 4] == 1.13)
    runs, i = [], 0
    while i < len(ok):
        if ok[i]:
            j = i
            while j < len(ok) and ok[j]:
                j += 1
            if j - i >= 300:
                runs.append(mid[i:j + 1])
            i = j
        else:
            i += 1
    return runs


def main():
    pg = fitz.open(PDF)[0]
    tr, info = transformacja_planu(pg)
    runs = linie_kropkowane(pg)
    wynik = {"zrodlo": "rysunek Z-04 Przekroje terenowe (4IDEA, XI 2025), plan lokalizacji przekrojów; kropkowane linie przekrojów",
             "transformacja_planu": info, "przekroje": {}}
    for nm, (pl, pr) in ETYKIETY.items():
        # linia, której któryś koniec jest najbliżej etykiet
        best = None
        for q in runs:
            for rev in (False, True):
                qq = q[::-1] if rev else q
                dist = math.dist(qq[0], pl) + math.dist(qq[-1], pr)
                if best is None or dist < best[0]:
                    best = (dist, qq)
        qq = best[1]
        pl_simpl = LineString(qq).simplify(0.35)
        pts_pdf = list(pl_simpl.coords)
        pts = [tr(x, y) for x, y in pts_pdf]
        dl = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        wynik["przekroje"][nm] = {"wierzcholki_PL2000": [[round(e, 3), round(n, 3)] for e, n in pts], "dlugosc_m": round(dl, 2),
                                  "liczba_kropek": len(qq), "odleglosc_etykiet_pt": round(best[0], 1)}
        print(nm, "wierzchołków", len(pts), "długość %.1f m" % dl, "start", [round(v, 1) for v in pts[0]], "koniec", [round(v, 1) for v in pts[-1]])
    json.dump(wynik, open(os.path.join(DANE, "linie_przekrojow.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("dopasowanie planu: skala %.5f (1:500=1), obrót %.3f°, rms %.2f m, max %.2f m (%d punktów)" % (
        info["skala_wzgledem_1_500"], info["obrot_stopnie"], info["rms_m"], info["max_m"], info["liczba_punktow"]))


if __name__ == "__main__":
    main()

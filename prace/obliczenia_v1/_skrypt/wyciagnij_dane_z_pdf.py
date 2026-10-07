"""ODTWARZALNE WYCIAGANIE DANYCH Z PDF (bez recznego klikania).

Z wektorowego rzutu zabezpieczenia wykopu (PDF projektanta z siatka wspolrzednych PL-2000) wyciaga:
  - sciane szczelna (niebieskie kreski) -> wielokat
  - obrysy 8 hal garazowych (purpurowe podwojne obrysy, bierze zewnetrzny)
  - granice dzialki (gruba szara polilinia zamknieta)
  - rzedne terenu istniejacego z siatki 10 m (szare liczby)
Z PZT (PDF, skala 1:250) wyciaga:
  - czarne rzedne pomiarowe terenu istniejacego (kropka, 1 miejsce)
  - czarne rzedne projektowe (przecinek, 2 miejsca)
Uklad: PL-2000 strefa 6 (EPSG 2177): E = X w CAD, N = Y w CAD. Wysokosci: PL-KRON86-NH.

Uzycie:  python wyciagnij_dane_z_pdf.py [--wyjscie KATALOG]
Domyslnie zapisuje do _skrypt/dane_odtworzone/ i porownuje z _skrypt/dane/ (to sa dane uzyte w wersji 1).
Zaleznosci: pymupdf, numpy, shapely."""
import argparse
import csv
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np
import pymupdf
from shapely.geometry import Polygon, Point

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
from lancuch import chain_polygon  # noqa: E402



def _norm(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)


def znajdz_pdf(znacznik):
    """Szuka w calym repo jednostronicowego PDF, ktorego tekst zawiera znacznik (niezaleznie od nazwy pliku i folderu)."""
    for f in sorted(REPO.rglob("*.pdf")):
        try:
            d = pymupdf.open(str(f))
            if d.page_count > 3:
                continue
            if znacznik in _norm(d[0].get_text("text")):
                return f
        except Exception:
            continue
    return None


# rzut zabezpieczenia wykopu: w legendzie "Scianka szczelna lub berlinska wyciagana"; PZT: tabela "BILANS TERENU OPRACOWANIA"
PDF_ZABEZP = znajdz_pdf("scianka szczelna lub berlinska")
PDF_PZT = znajdz_pdf("bilans terenu opracowania")

E0, N0 = 6433700.0, 5659050.0       # wspolrzedne krzyza siatki opisanego na rysunku napisami 6433700 (E) i 5659050 (N)
# Rozmieszczenie hal na stronie rzutu zabezpieczenia [pt] - srodki, wg napisow 'BUDYNEK NR n'
SRODKI_HAL_PT = {1: (137, 243), 2: (211, 243), 3: (301, 281), 4: (389, 316), 5: (120, 386), 6: (217, 416), 7: (287, 465), 8: (378, 492)}
# PZT: transformacja strona (pt) -> PL-2000; dopasowana do krzyzy siatki i zweryfikowana na 649 wspolnych rzednych z rzutem zabezpieczenia
PZT_X0, PZT_Y0, PZT_KAT_DEG, PZT_K = 2879.2, 309.7, 7.365944612743048, 72 / 0.0254 / 250


def P(p):
    return (float(p[0]), float(p[1])) if not hasattr(p, "x") else (p.x, p.y)


# ------------------------------------------------------------------------------------------------ siatka 50 m
def znajdz_krzyze(dr):
    """Male czarne krzyze siatki: pozioma i pionowa kreska 8..40 pt o wspolnym srodku."""
    H, V = [], []
    for d in dr:
        c = d.get("color")
        if c is None or not (c[0] < 0.1 and c[1] < 0.1 and c[2] < 0.1):
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            a, b = P(it[1]), P(it[2])
            L = math.dist(a, b)
            if 8 <= L <= 40:
                if abs(a[1] - b[1]) < 0.05:
                    H.append((min(a[0], b[0]), max(a[0], b[0]), a[1]))
                elif abs(a[0] - b[0]) < 0.05:
                    V.append((min(a[1], b[1]), max(a[1], b[1]), a[0]))
    cr = set()
    for x0, x1, y in H:
        for y0, y1, x in V:
            if x0 < x < x1 and y0 < y < y1 and abs((x0 + x1) / 2 - x) < 0.5 and abs((y0 + y1) / 2 - y) < 0.5 and abs((x1 - x0) - (y1 - y0)) < 1.0:
                cr.add((round(x, 2), round(y, 2)))
    return sorted(cr)


class Rama:
    """Uklad G: PL-2000 z siatki wspolrzednych projektanta (krzyze co 50 m)."""
    def __init__(self, krzyze, etykieta_xy):
        xs = sorted({round(x, 1) for x, _ in krzyze})
        ys = sorted({round(y, 1) for _, y in krzyze})
        pitch = float(np.median(np.diff(xs)))
        xl, yl = min(krzyze, key=lambda c: math.dist(c, etykieta_xy))      # krzyz z napisami wspolrzednych
        A, Bv = [], []
        for x, y in krzyze:
            i = round((x - xl) / pitch)
            j = round((y - yl) / pitch)
            A.append([50.0 * i, 1, 0]); Bv.append(x)                     # x = x0 + s*(50 i)
            A.append([50.0 * j, 0, 1]); Bv.append(y)                     # y = y0 + s*(50 j)   (N maleje w dol strony)
        sol, *_ = np.linalg.lstsq(np.array(A), np.array(Bv), rcond=None)
        self.s, self.x0, self.y0 = [float(v) for v in sol]
        res = np.array(A) @ sol - np.array(Bv)
        self.rms_pt = float(np.sqrt((res ** 2).mean()))
        self.n_krzyzy = len(krzyze)

    def do_G(self, x, y):
        return (E0 + (x - self.x0) / self.s, N0 - (y - self.y0) / self.s)


class PztT:
    def __init__(self):
        a = math.radians(PZT_KAT_DEG)
        c, s = math.cos(a), math.sin(a)
        self.uE, self.uN = (c, -s), (-s, -c)

    def do_PL(self, x, y):
        dx, dy = (x - PZT_X0) / PZT_K, (y - PZT_Y0) / PZT_K
        return (E0 + dx * self.uE[0] + dy * self.uE[1], N0 + dx * self.uN[0] + dy * self.uN[1])


def segmenty(d):
    out = []
    for it in d["items"]:
        if it[0] == "l":
            out.append((P(it[1]), P(it[2])))
    return out


# ------------------------------------------------------------------------------------------------ geometria z rzutu zabezpieczenia
def geometria(pdf_path):
    pg = pymupdf.open(str(pdf_path))[0]
    dr = pg.get_cdrawings()
    spans = []
    for b in pg.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                if s["text"].strip():
                    spans.append(s)
    lab = [s for s in spans if s["text"].strip() in ("5659050", "6433700")]
    lab_xy = (np.mean([s["origin"][0] for s in lab]), np.mean([s["origin"][1] for s in lab]))
    rama = Rama(znajdz_krzyze(dr), lab_xy)
    # --- scianka: niebieskie (0,0,1) kreski o grubosci 2,04, bez legendy (y > 650 pt)
    seg = []
    for d in dr:
        c = d.get("color")
        if c and c[0] < 0.05 and c[1] < 0.05 and c[2] > 0.95 and abs((d.get("width") or 0) - 2.04) < 0.02:
            seg += segmenty(d)
    seg = [(a, b) for a, b in seg if a[1] < 650 and b[1] < 650]
    SG = [(rama.do_G(*a), rama.do_G(*b)) for a, b in seg]
    scianka = chain_polygon(SG, maxgap=10.0, corner_deg=2.0, simplify_tol=0.1, verbose=False)
    # --- hale: purpurowe (0.72, 0, 0.36), grubosc 0,96, obrysy >= 60 x 60 pt; zewnetrzny = najwiekszy z pary
    cand = []
    for d in dr:
        c = d.get("color")
        if c and abs(c[0] - 0.72) < 0.02 and abs(c[1]) < 0.02 and abs(c[2] - 0.36) < 0.02 and abs((d.get("width") or 0) - 0.96) < 0.02:
            r = d["rect"]
            if (r[2] - r[0]) >= 60 and (r[3] - r[1]) >= 60:
                pts = []
                for it in d["items"]:
                    if it[0] == "qu":
                        q = it[1]
                        pts += [P(q.ul), P(q.ur), P(q.lr), P(q.ll)] if hasattr(q, "ul") else [P(x) for x in q]
                    elif it[0] == "l":
                        pts += [P(it[1]), P(it[2])]
                    elif it[0] == "re":
                        rr = it[1]
                        pts += [(rr[0], rr[1]), (rr[2], rr[1]), (rr[2], rr[3]), (rr[0], rr[3])]
                cand.append((r, pts))
    hale = {}
    for nr, (cx, cy) in SRODKI_HAL_PT.items():
        w = [(r, p) for r, p in cand if r[0] - 2 <= cx <= r[2] + 2 and r[1] - 2 <= cy <= r[3] + 2]
        w.sort(key=lambda t: -((t[0][2] - t[0][0]) * (t[0][3] - t[0][1])))
        r, pts = w[0]
        hull = Polygon(pts).convex_hull
        c4 = [rama.do_G(x, y) for x, y in list(hull.exterior.coords)[:-1]]
        cxg = sum(p[0] for p in c4) / len(c4)
        cyg = sum(p[1] for p in c4) / len(c4)
        hale[nr] = sorted(c4, key=lambda p: math.atan2(p[1] - cyg, p[0] - cxg))
    # --- granica dzialki: gruba szara (0.73) polilinia 2,04, same odcinki, zamknieta; najdluzsza
    best = None
    for d in dr:
        c = d.get("color")
        if c and abs(c[0] - 0.729) < 0.01 and abs(c[1] - 0.729) < 0.01 and abs((d.get("width") or 0) - 2.04) < 0.02 and len(d["items"]) >= 10 \
                and all(it[0] == "l" for it in d["items"]):
            pts = [P(d["items"][0][1])] + [P(it[2]) for it in d["items"]]
            if math.dist(pts[0], pts[-1]) < 0.5 and (best is None or len(pts) > len(best)):
                best = pts
    dzialka = [rama.do_G(*p) for p in best]
    # --- siatka 10 m: szare liczby (0x767676) 1 miejsce po kropce
    siatka = []
    seen = set()
    for s in spans:
        t = s["text"].strip()
        if s["color"] == 0x767676 and re.fullmatch(r"1[12]\d\.\d", t):
            b = s["bbox"]
            k = (t, round(b[0]), round(b[1]))
            if k in seen:
                continue
            seen.add(k)
            E, N = rama.do_G((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
            siatka.append((E, N, float(t)))
    return dict(rama=rama, scianka=scianka, hale=hale, dzialka=dzialka, siatka=siatka)


# ------------------------------------------------------------------------------------------------ rzedne z PZT
def rzedne_pzt(pdf_path):
    pg = pymupdf.open(str(pdf_path))[0]
    T = PztT()
    seen = set()
    eg, fg = [], []
    for b in pg.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                t = s["text"].strip()
                if not re.fullmatch(r"1[12]\d[.,]\d{1,3}", t) or s["color"] != 0:
                    continue
                k = (t, round(s["origin"][0]), round(s["origin"][1]))
                if k in seen:
                    continue
                seen.add(k)
                bb = s["bbox"]
                E, N = T.do_PL((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)
                z = float(t.replace(",", "."))
                if "." in t and len(t.split(".")[-1]) == 1:
                    eg.append((E, N, z))
                elif "," in t and len(t.split(",")[-1]) == 2 and 123.5 < z < 127:
                    fg.append((E, N, z))
    return eg, fg


def zapisz(wyj, g, eg_pzt, fg_pzt):
    os.makedirs(wyj, exist_ok=True)
    PAR = Polygon(g["dzialka"])
    json.dump(dict(scianka=g["scianka"], hale={str(k): v for k, v in g["hale"].items()}, dzialka=g["dzialka"],
                   opis="Uklad PL-2000 strefa 6 (E,N). Zrodlo: wektorowy rzut zabezpieczenia wykopu (siatka wspolrzednych projektanta, krzyze co 50 m)."),
              open(os.path.join(wyj, "geometria_G.json"), "w"), indent=1)

    def csv_(nazwa, pts):
        with open(os.path.join(wyj, nazwa), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["E", "N", "z", "w_dzialce"])
            for E, N, z in pts:
                w.writerow([round(E, 2), round(N, 2), z, int(PAR.contains(Point(E, N)))])
    csv_("eg_siatka10m_z_rzutu_zabezpieczenia.csv", g["siatka"])
    csv_("eg_pomiar_PZT_czarne.csv", eg_pzt)
    csv_("fg_projekt_PZT.csv", fg_pzt)


def porownaj(wyj, ref):
    if not os.path.isdir(ref):
        print("brak katalogu referencyjnego", ref)
        return
    a = json.load(open(os.path.join(wyj, "geometria_G.json")))
    b = json.load(open(os.path.join(ref, "geometria_G.json")))
    print("\nPOROWNANIE Z DANYMI UZYTYMI W WERSJI 1 (dane/):")
    pa, pb = Polygon(a["scianka"]), Polygon(b["scianka"])
    print("  scianka: pole %.1f vs %.1f m2 ; obwod %.1f vs %.1f m" % (pa.area, pb.area, pa.length, pb.length))
    for k in map(str, range(1, 9)):
        ha, hb = Polygon(a["hale"][k]), Polygon(b["hale"][k])
        print("  hala %s: pole %.1f vs %.1f ; przesuniecie srodka %.3f m" % (k, ha.area, hb.area, ha.centroid.distance(hb.centroid)))
    da, db = Polygon(a["dzialka"][:-1] if a["dzialka"][0] == a["dzialka"][-1] else a["dzialka"]), Polygon(b["dzialka"])
    print("  granica dzialki: pole %.1f vs %.1f m2" % (da.area, db.area))
    for nazwa in ("eg_siatka10m_z_rzutu_zabezpieczenia.csv", "eg_pomiar_PZT_czarne.csv", "fg_projekt_PZT.csv"):
        ra = list(csv.DictReader(open(os.path.join(wyj, nazwa))))
        rb = list(csv.DictReader(open(os.path.join(ref, nazwa))))
        za = sorted((float(r["z"]), round(float(r["E"])), round(float(r["N"]))) for r in ra)
        zb = sorted((float(r["z"]), round(float(r["E"])), round(float(r["N"]))) for r in rb)
        print("  %-45s wierszy %d vs %d ; identycznych (z, E, N +-1 m): %d" % (nazwa, len(ra), len(rb), len(set(za) & set(zb))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wyjscie", default=str(HERE / "dane_odtworzone"))
    ap.add_argument("--zabezp", default=str(PDF_ZABEZP) if PDF_ZABEZP else None, help="PDF rzutu zabezpieczenia wykopu (domyslnie wyszukiwany po tresci)")
    ap.add_argument("--pzt", default=str(PDF_PZT) if PDF_PZT else None, help="PDF PZT (domyslnie wyszukiwany po tresci)")
    a = ap.parse_args()
    if not a.zabezp or not a.pzt:
        sys.exit("Nie znaleziono PDF rzutu zabezpieczenia wykopu i/lub PZT w repo. Podaj sciezki: --zabezp ... --pzt ...")
    print("Rzut zabezpieczenia:", a.zabezp)
    print("PZT:", a.pzt)
    g = geometria(a.zabezp)
    r = g["rama"]
    print("Siatka 50 m: krzyzy %d, skala %.5f pt/m (1:%.1f), rms %.3f pt = %.3f m" % (r.n_krzyzy, r.s, 72 / 0.0254 / r.s, r.rms_pt, r.rms_pt / r.s))
    eg, fg = rzedne_pzt(a.pzt)
    zapisz(a.wyjscie, g, eg, fg)
    print("zapisano w", a.wyjscie)
    porownaj(a.wyjscie, str(HERE / "dane"))

"""
PRZEKROJE T1–T4 (linie z rysunku Z-04 „Przekroje terenowe", prace/dane/linie_przekrojow.json) przez model bilansu.
Na każdym przekroju (kolejność od lewej do prawej jak na rysunku projektanta; w T1 przesunięcie linii przekroju nie wlicza się do odległości):
  teren istniejący, po zdjęciu humusu i nasypu, po wykopie A i B, stan końcowy (PZT), humus i nasyp, warstwy gruntu z DGI (klasy Ia…IVd),
  obrysy hal, zadaszone dojazdy, rampy, ścianka, granica działki, otwory DGI w pobliżu, średni poziom wody wg DGI.
Kontrola: rzędne terenu istniejącego i projektowanego opisane na rysunku projektanta (etykiety „… m n.p.m.") vs model.
Wyniki: wyniki/PRZEKROJE_dz190.dxf, wyniki/PRZEKROJE_dz190_podglad.png, prace/obliczenia_v2/przekroje_kontrola.json
Uruchomienie: python przekroje.py
"""
import json
import math
import os

import ezdxf
import matplotlib
import numpy as np
import pymupdf as fitz
from scipy.spatial import Delaunay
from shapely import wkt
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

import dane as D
import model3d as M
import silnik as S

matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WY_DXF = os.path.join(REPO, "wyniki", "PRZEKROJE_dz190.dxf")
WY_PNG = os.path.join(REPO, "wyniki", "PRZEKROJE_dz190_podglad.png")
WY_KONTROLA = os.path.join(HERE, "przekroje_kontrola.json")
PDF = os.path.join(REPO, "dokumentacja", "04_projekt_zagospodarowania_i_architektura",
                   "8. Przekroje terenowe z naniesionym średnim poziomem wody gruntowej.pdf")
PT_NA_M = 1.0 / (0.0254 / 72 * 200)           # skala 1:200 → punktów rysunku na metr
KROK = 0.5                                     # krok próbkowania przekroju [m]
KROK_GRUNT = 1.0                               # krok kolumn gruntu [m]
OPIS_PRZEKROJU = {"T1": "od ul. Drabika (zachód) do ul. Buforowej (wschód)", "T2": "od ul. Drabika (zachód) do ul. Buforowej (wschód)",
                  "T3": "od ul. Asfaltowej (południe) do ul. Lutosławskiego (północ)", "T4": "od ul. Asfaltowej (południe) do ul. Lutosławskiego (północ)"}
# znaczniki początku/końca przekroju w działce na rysunku projektanta (środki czerwonych słupków, pt strony) – kalibracja odległości
SLUPKI_X = {"T1": 1530.55, "T2": 1614.6, "T3": 1621.5, "T4": 1541.05}
PASMA_Y = {"T1": (40, 440), "T2": (445, 860), "T3": (865, 1240), "T4": (1245, 1680)}
KOLORY_KLAS = {"Ia": (250, 235, 150), "IIa": (245, 220, 110), "IIb": (235, 200, 70), "IIc": (220, 180, 40), "IIIa": (230, 150, 60), "IIIb": (205, 120, 40),
               "IVa": (150, 190, 140), "IVb": (120, 160, 120), "IVc": (170, 130, 100), "IVd": (130, 95, 70)}
OPIS_KLAS = {"Ia": "piaski drobne i pylaste", "IIa": "piaski średnie luźne", "IIb": "piaski średnie i grube", "IIc": "piaski średnie zagęszczone",
             "IIIa": "pospółki średniozagęszczone", "IIIb": "pospółki zagęszczone", "IVa": "gliny plastyczne", "IVb": "gliny tpl/pl",
             "IVc": "gliny, pyły tpl", "IVd": "gliny zwięzłe pzw/zw"}
KOLOR_HUMUS, KOLOR_NASYP = (80, 140, 70), (175, 175, 175)
WODA_SR = 123.39            # średnie zwierciadło ustabilizowane wg DGI (tab. 1: 122,90–124,10, wahania ±0,5 m)


# ------------------------------------------------------------------------------------------------ trasa przekroju
def nogi(wierzcholki):
    """Odcinki trasy: (p0, p1, s0, s1, przesuniecie). Przesunięcie linii przekroju (odcinek poprzeczny lub bardzo krótki) nie wlicza się do odległości s."""
    v = [np.array(p, float) for p in wierzcholki]
    glowny = v[-1] - v[0]
    glowny /= np.hypot(*glowny)
    out, s = [], 0.0
    for a, b in zip(v[:-1], v[1:]):
        d = b - a
        dl = float(np.hypot(*d))
        kat = abs(math.degrees(math.acos(max(-1, min(1, float(d @ glowny) / dl))))) if dl > 0 else 0
        jog = dl < 0.5 or kat > 45
        out.append((a, b, s, s + (0 if jog else dl), jog))
        if not jog:
            s += dl
    return out, s


def punkt_na_trasie(legs, s):
    for a, b, s0, s1, jog in legs:
        if jog:
            continue
        if s0 - 1e-9 <= s <= s1 + 1e-9:
            t = (s - s0) / (s1 - s0) if s1 > s0 else 0
            return a + (b - a) * t
    a, b, s0, s1, jog = [l for l in legs if not l[4]][-1]
    return b


def probki(legs, krok):
    """Lista (s, E, N). Przy przesunięciu linii dwa punkty o tym samym s (skok w profilu)."""
    out = []
    for a, b, s0, s1, jog in legs:
        if jog:
            continue
        n = max(int(round((s1 - s0) / krok)), 1)
        for i in range(n + 1):
            p = a + (b - a) * (i / n)
            out.append((s0 + (s1 - s0) * i / n, p[0], p[1]))
    return np.array(out)


def przeciecia(legs, geom):
    """Przedziały s, w których trasa leży wewnątrz wielokąta(ów) geom."""
    out = []
    for a, b, s0, s1, jog in legs:
        if jog:
            continue
        ln = LineString([a, b])
        it = ln.intersection(geom)
        segs = list(it.geoms) if hasattr(it, "geoms") else [it]
        for sg in segs:
            if sg.is_empty or sg.geom_type != "LineString":
                continue
            p0, p1 = Point(sg.coords[0]), Point(sg.coords[-1])
            u0, u1 = ln.project(p0), ln.project(p1)
            out.append((s0 + min(u0, u1), s0 + max(u0, u1)))
    return sorted(out)


def punkty_przeciecia(legs, geom_line):
    out = []
    for a, b, s0, s1, jog in legs:
        if jog:
            continue
        ln = LineString([a, b])
        it = ln.intersection(geom_line)
        pts = list(it.geoms) if hasattr(it, "geoms") else [it]
        for p in pts:
            if not p.is_empty and p.geom_type == "Point":
                out.append(s0 + ln.project(p))
    return sorted(out)


# ------------------------------------------------------------------------------------------------ grunt z DGI
def klasy_na_trasie(xy, zs_vals, L, CUM):
    """Dominująca klasa gruntu w przedziałach 0,1 m pod stropem gruntu mineralnego; interpolacja jak w bilansie (TIN otworów)."""
    LP = np.array([(l["E"], l["N"]) for l in L])
    tri = Delaunay(LP)
    s = tri.find_simplex(xy)
    W3 = np.zeros((len(xy), 3)); I3 = np.zeros((len(xy), 3), int)
    ok = s >= 0
    T = tri.transform[s[ok]]
    b2 = np.einsum("ijk,ik->ij", T[:, :2, :], xy[ok] - T[:, 2, :])
    W3[ok] = np.column_stack([b2, 1 - b2.sum(1)]); I3[ok] = tri.simplices[s[ok]]
    if (~ok).any():
        from scipy.interpolate import NearestNDInterpolator
        nn = NearestNDInterpolator(LP, np.arange(len(L)))(xy[~ok, 0], xy[~ok, 1]).astype(int)
        W3[~ok, 0] = 1.0; I3[~ok, 0] = nn
    nk = len(D.KLASY)
    bins = int(S.NK // 10) - 1                                   # przedziały 0,1 m do 8,0 m
    wynik = np.full((len(xy), bins), -1, int)
    for k in range(bins):
        a, b = k * 10, k * 10 + 10
        fr = np.zeros((len(xy), nk))
        for j in range(3):
            fr += W3[:, j][:, None] * (CUM[I3[:, j], :nk, b] - CUM[I3[:, j], :nk, a]) / (10 * S.DK)
        tot = fr.sum(1)
        wynik[:, k] = np.where(tot > 0.3, fr.argmax(1), -1)
    return wynik


def poligony_gruntu(s_kol, zs_kol, klasy):
    """Wielokąty klas (współrzędne: s, rzędna). Między sąsiednimi kolumnami lewa połowa ma klasę lewej kolumny, prawa – prawej (bez luk); łączone w obrębie klasy."""
    quads = {c: [] for c in range(len(D.KLASY))}
    bins = klasy.shape[1]
    for i in range(len(s_kol) - 1):
        ds = s_kol[i + 1] - s_kol[i]
        if ds < 1e-6:
            continue                                              # skok na przesunięciu linii
        for pol in (0, 1):
            sa, sb = s_kol[i] + pol * ds / 2, s_kol[i] + (pol + 1) * ds / 2
            za = zs_kol[i] + (zs_kol[i + 1] - zs_kol[i]) * (pol * 0.5)
            zb = zs_kol[i] + (zs_kol[i + 1] - zs_kol[i]) * ((pol + 1) * 0.5)
            kol = klasy[i + pol]
            for k in range(bins):
                c = kol[k]
                if c < 0:
                    continue
                d0, d1 = k * 0.1, (k + 1) * 0.1
                quads[c].append(Polygon([(sa, za - d0), (sb, zb - d0), (sb, zb - d1), (sa, za - d1)]))
    out = {}
    for c, q in quads.items():
        if q:
            out[D.KLASY[c]] = unary_union(q).simplify(0.02)
    return out


def scal(przedzialy, tol=0.6):
    out = []
    for a, b in sorted(przedzialy):
        if out and a - out[-1][1] <= tol:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def wielokaty(g):
    return [q for q in (list(g.geoms) if hasattr(g, "geoms") else [g]) if q.geom_type == "Polygon" and not q.is_empty and q.area > 1e-3]


# ------------------------------------------------------------------------------------------------ etykiety z rysunku projektanta
def etykiety_rysunku():
    pg = fitz.open(PDF)[0]
    out = {nm: {"ist": [], "proj": []} for nm in PASMA_Y}
    for b in pg.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for sp in l["spans"]:
                tx = sp["text"].strip()
                if "n.p.m" not in tx or sp["color"] not in (13311202, 4617942):
                    continue
                try:
                    val = float(tx.split("m")[0].replace(",", "."))
                except ValueError:
                    continue
                bb = sp["bbox"]
                xc, yc = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
                for nm, (y0, y1) in PASMA_Y.items():
                    if y0 <= yc <= y1:
                        out[nm]["ist" if sp["color"] == 13311202 else "proj"].append((xc, val))
    return out


# ------------------------------------------------------------------------------------------------ główne
def main():
    geo = json.load(open(os.path.join(D.DANE, "geometria.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(D.DANE, "strefy.json"), encoding="utf-8"))
    linie = json.load(open(os.path.join(D.DANE, "linie_przekrojow.json"), encoding="utf-8"))["przekroje"]
    oto = json.load(open(os.path.join(D.DANE, "otwory.json"), encoding="utf-8"))
    w, gm = S.licz(zapisz_geometrie=True)
    sg = gm["_siatka"]
    xs, ys, shape = sg["xs"], sg["ys"], sg["shape"]
    zs = sg["zs"]
    F = {"ist": sg["zt"], "hum": zs, "kon": sg["zp"], "hh": sg["hh"], "hn": sg["hn"]}
    for k in ("A", "B"):
        ze = sg[k]["ze"]
        F[k] = np.where(np.isfinite(ze), np.minimum(zs, ze), zs)
    FI = {k: M.interpolator(xs, ys, v.reshape(shape)) for k, v in F.items()}
    ev = lambda k, xy: FI[k](np.column_stack([xy[:, 1], xy[:, 0]]))
    G = Polygon(geo["granica"])
    HALE = unary_union([Polygon(v) for v in geo["hale"].values()])
    ZAD = wkt.loads(st["zadaszone_poza_halami"])
    RAMPY = unary_union([wkt.loads(r["obrys"]) for r in st["rampy"]])
    SCIANKA = LineString(geo["scianka_otwarta"])
    L = S.lokalizacje()
    CUM = np.stack([l["cum"] for l in L])
    dno = S.PARAMETRY["dno"]
    et = etykiety_rysunku()
    kontrola = {"przekroje": {}, "uwagi": ["odległość s liczona od lewego końca przekroju jak na rysunku projektanta; w T1 odcinek przesunięcia linii (ok. 17 m) nie wlicza się do s"]}
    dane_prz = {}
    for nm, d in linie.items():
        legs, total = nogi(d["wierzcholki_PL2000"])
        sm = probki(legs, KROK)
        xy = sm[:, 1:3]
        z = {k: ev(k, xy) for k in F}
        zex = {k: np.minimum(z["hum"], z[k]) for k in ("A", "B")}
        s_gr = punkty_przeciecia(legs, G.exterior)
        s_left = s_gr[0] if s_gr else 0.0
        # kolumny gruntu
        sk = probki(legs, KROK_GRUNT)
        zs_k = ev("hum", sk[:, 1:3])
        klasy = klasy_na_trasie(sk[:, 1:3], zs_k, L, CUM)
        pol = poligony_gruntu(sk[:, 0], zs_k, klasy)
        # obiekty
        hale_s = scal(przeciecia(legs, HALE))
        zad_s = [p for p in scal(przeciecia(legs, ZAD)) if p[1] - p[0] > 0.3]
        ramp_s = scal(przeciecia(legs, RAMPY))
        scianka_s = punkty_przeciecia(legs, SCIANKA)
        # otwory w pobliżu (<= 25 m od osi przekroju), rzut na oś
        otw = []
        osie = [LineString([a, b]) for a, b, s0, s1, jog in legs if not jog]
        for nr, o in oto.items():
            p = Point(o["E"], o["N"])
            best = min(((ln.distance(p), i) for i, ln in enumerate(osie)), key=lambda t: t[0])
            if best[0] <= 25.0:
                ln = osie[best[1]]
                s0 = [l for l in legs if not l[4]][best[1]][2]
                otw.append((nr, s0 + ln.project(p), best[0], o["H"], o["woda_ustab_m_ppt"]))
        # kontrola z rysunkiem projektanta: etykiety rzędnych terenu na przekrojach vs model (w działce, bez 1,5 m przy granicy – tam teren ma uskoki/ulice)
        xL = SLUPKI_X[nm]
        s_prawa = s_gr[-1] if s_gr else total
        por = {}
        for rodzaj, klucz in (("ist", "ist"), ("proj", "kon")):
            roz, poza = [], []
            for xlab, val in et[nm][rodzaj]:
                s = s_left + (xlab - xL) / PT_NA_M
                if s < 0 or s > total:
                    continue
                p = punkt_na_trasie(legs, s)
                zm = float(ev(klucz, np.array([p]))[0])
                (roz if s_left + 1.5 <= s <= s_prawa - 1.5 else poza).append((round(s, 2), val, round(zm, 2), round(zm - val, 2)))
            r = np.array([x[3] for x in roz]) if roz else np.array([0.0])
            por[rodzaj] = {"liczba_etykiet_w_dzialce": len(roz), "srednia_roznica_m": round(float(r.mean()), 3), "rms_m": round(float(np.sqrt((r ** 2).mean())), 3),
                           "max_abs_m": round(float(np.abs(r).max()), 3), "ponad_0_30_m": int((np.abs(r) > 0.30).sum()),
                           "najwieksze": sorted(roz, key=lambda x: -abs(x[3]))[:4], "etykiet_poza_dzialka_lub_przy_granicy": len(poza),
                           "poza_najwieksze": sorted(poza, key=lambda x: -abs(x[3]))[:3]}
        kontrola["przekroje"][nm] = {"dlugosc_m": round(total, 2), "s_wejscia_do_dzialki_m": round(s_left, 2), "zgodnosc_z_rysunkiem_projektanta": por,
                                     "hale_s": [(round(a, 1), round(b, 1)) for a, b in hale_s], "zadaszone_s": [(round(a, 1), round(b, 1)) for a, b in zad_s],
                                     "rampy_s": [(round(a, 1), round(b, 1)) for a, b in ramp_s], "scianka_s": [round(v, 1) for v in scianka_s],
                                     "otwory_do_25m": [(n_, round(s_, 1), round(o_, 1)) for n_, s_, o_, h_, w_ in otw]}
        print(nm, "dł. %.1f m | w działce: teren istniejący %d etykiet (śr. %+.3f, RMS %.3f, max %.3f m), projektowany %d (śr. %+.3f, RMS %.3f, max %.3f m)" % (
            total, por["ist"]["liczba_etykiet_w_dzialce"], por["ist"]["srednia_roznica_m"], por["ist"]["rms_m"], por["ist"]["max_abs_m"],
            por["proj"]["liczba_etykiet_w_dzialce"], por["proj"]["srednia_roznica_m"], por["proj"]["rms_m"], por["proj"]["max_abs_m"]))
        dane_prz[nm] = dict(sm=sm, z=z, zex=zex, pol=pol, hale=hale_s, zad=zad_s, ramp=ramp_s, scianka=scianka_s, otw=otw, s_gr=s_gr, total=total, legs=legs, sk=sk, zs_k=zs_k)
    json.dump(kontrola, open(WY_KONTROLA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    rysuj_dxf(dane_prz, dno)
    rysuj_png(dane_prz, dno)


# ------------------------------------------------------------------------------------------------ DXF
def rysuj_dxf(dane, dno):
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 6
    msp = doc.modelspace()
    warstwy = {"PRZ_TEREN_ISTNIEJACY": 8, "PRZ_PO_HUMUSIE": 40, "PRZ_WYKOP_A": 5, "PRZ_WYKOP_B": 4, "PRZ_STAN_KONCOWY": 3, "PRZ_HUMUS": 3, "PRZ_NASYP": 9, "PRZ_WODA": 5,
               "PRZ_HALE": 1, "PRZ_ZADASZONE": 30, "PRZ_RAMPY": 2, "PRZ_SCIANKA": 2, "PRZ_GRANICA": 6, "PRZ_OTWORY": 7, "PRZ_OPISY": 7, "PRZ_SIATKA": 8}
    for nm in D.KLASY:
        warstwy["PRZ_GRUNT_" + nm] = 7
    for nm, kol in warstwy.items():
        doc.layers.add(nm, color=kol)
    zmin, zmax = 115.5, 127.5
    odstep = zmax - zmin + 14
    for k, (nm, d) in enumerate(dane.items()):
        y0 = -k * odstep - zmin                                       # y_rysunku = z + y0

        def pl(s, z, warstwa, dash=False):
            pts = [(float(a), float(b) + y0) for a, b in zip(s, z)]
            e = msp.add_lwpolyline(pts, dxfattribs={"layer": warstwa})
            if dash:
                e.dxf.linetype = "DASHED"
            return e
        sm = d["sm"]
        s = sm[:, 0]
        # grunt
        for kl, geom in d["pol"].items():
            rgb = KOLORY_KLAS[kl]
            for q in wielokaty(geom):
                h = msp.add_hatch(dxfattribs={"layer": "PRZ_GRUNT_" + kl, "true_color": ezdxf.colors.rgb2int(rgb)})
                h.paths.add_polyline_path([(x, y + y0) for x, y in q.exterior.coords], is_closed=True)
                for ring in q.interiors:
                    h.paths.add_polyline_path([(x, y + y0) for x, y in ring.coords], is_closed=True)
        # humus i nasyp: pasy między terenem istniejącym a powierzchnią po zdjęciu
        zt, zh, hh, hn = d["z"]["ist"], d["z"]["hum"], d["z"]["hh"], d["z"]["hn"]
        for nazwa, gora, dol, rgb in (("PRZ_HUMUS", zt, zt - hh, KOLOR_HUMUS), ("PRZ_NASYP", zt - hh, zh, KOLOR_NASYP)):
            for i in range(len(s) - 1):
                if s[i + 1] - s[i] < 1e-6 or (gora[i] - dol[i] < 0.005 and gora[i + 1] - dol[i + 1] < 0.005):
                    continue
                h = msp.add_hatch(dxfattribs={"layer": nazwa, "true_color": ezdxf.colors.rgb2int(rgb)})
                h.paths.add_polyline_path([(s[i], gora[i] + y0), (s[i + 1], gora[i + 1] + y0), (s[i + 1], dol[i + 1] + y0), (s[i], dol[i] + y0)], is_closed=True)
        pl(s, d["z"]["ist"], "PRZ_TEREN_ISTNIEJACY")
        pl(s, d["z"]["hum"], "PRZ_PO_HUMUSIE")
        pl(s, d["zex"]["A"], "PRZ_WYKOP_A")
        pl(s, d["zex"]["B"], "PRZ_WYKOP_B")
        pl(s, d["z"]["kon"], "PRZ_STAN_KONCOWY")
        pl([0, d["total"]], [WODA_SR, WODA_SR], "PRZ_WODA", dash=True)
        for a, b in d["hale"]:
            msp.add_lwpolyline([(a, dno + y0), (b, dno + y0)], dxfattribs={"layer": "PRZ_HALE"})
            for x in (a, b):
                zk = float(np.interp(x, s, d["z"]["kon"]))
                msp.add_line((x, dno + y0), (x, zk + y0), dxfattribs={"layer": "PRZ_HALE"})
            msp.add_text("hala – dno %.2f" % dno, height=0.8, dxfattribs={"layer": "PRZ_OPISY", "insert": ((a + b) / 2 - 6, dno + 0.3 + y0)})
        for a, b in d["zad"]:
            msp.add_lwpolyline([(a, dno + y0), (b, dno + y0)], dxfattribs={"layer": "PRZ_ZADASZONE"})
            for x in (a, b):
                zk = float(np.interp(x, s, d["z"]["kon"]))
                msp.add_line((x, dno + y0), (x, zk + y0), dxfattribs={"layer": "PRZ_ZADASZONE"})
        for a, b in d["ramp"]:
            msp.add_text("rampa", height=0.8, dxfattribs={"layer": "PRZ_OPISY", "insert": ((a + b) / 2, float(np.interp((a + b) / 2, s, d["zex"]["B"])) - 1.0 + y0)})
        for x in d["scianka"]:
            msp.add_line((x, float(np.interp(x, s, d["z"]["hum"])) + y0), (x, dno + y0), dxfattribs={"layer": "PRZ_SCIANKA"})
            msp.add_text("ścianka", height=0.8, dxfattribs={"layer": "PRZ_OPISY", "insert": (x + 0.5, dno + 0.3 + y0)})
        for x in d["s_gr"]:
            zz = float(np.interp(x, s, d["z"]["ist"]))
            msp.add_line((x, zz - 0.5 + y0), (x, zz + 2.5 + y0), dxfattribs={"layer": "PRZ_GRANICA"})
            msp.add_text("granica działki", height=0.8, dxfattribs={"layer": "PRZ_OPISY", "insert": (x + 0.4, zz + 2.6 + y0), "rotation": 0})
        for nr, sx, odl, H, wod in d["otw"]:
            msp.add_line((sx, H + y0), (sx, H - 8.0 + y0), dxfattribs={"layer": "PRZ_OTWORY"})
            msp.add_text("otw. %s (%.0f m od osi)" % (nr, odl), height=0.7, dxfattribs={"layer": "PRZ_OPISY", "insert": (sx + 0.3, H + 0.2 + y0)})
            if wod is not None:
                msp.add_circle((sx, H - wod + y0), 0.25, dxfattribs={"layer": "PRZ_WODA"})
        # siatka rzędnych i oś odległości
        for zz in range(int(math.ceil(zmin)), int(zmax) + 1):
            msp.add_line((-2, zz + y0), (d["total"], zz + y0), dxfattribs={"layer": "PRZ_SIATKA", "linetype": "DASHED"})
            msp.add_text("%d,00" % zz, height=0.7, dxfattribs={"layer": "PRZ_SIATKA", "insert": (-9, zz - 0.3 + y0)})
        for sx in range(0, int(d["total"]) + 1, 10):
            msp.add_line((sx, zmin + y0), (sx, zmin - 0.6 + y0), dxfattribs={"layer": "PRZ_SIATKA"})
            msp.add_text("%d" % sx, height=0.7, dxfattribs={"layer": "PRZ_SIATKA", "insert": (sx - 1, zmin - 1.8 + y0)})
        msp.add_text("PRZEKRÓJ %s–%s  %s   (skala 1:1, odległość s [m], rzędne [m npm])" % (nm, nm, OPIS_PRZEKROJU[nm]), height=1.4,
                     dxfattribs={"layer": "PRZ_OPISY", "insert": (0, zmax + 1.5 + y0)})
    # legenda
    k = len(dane)
    y_leg = -k * odstep
    msp.add_text("LEGENDA: linie – teren istniejący (szary), po zdjęciu humusu i nasypu (brązowy), wykop A (niebieski), wykop B (turkusowy), stan końcowy PZT (zielony); "
                 "przerywana niebieska – średni poziom wody wg DGI (%.2f m npm)." % WODA_SR, height=0.9, dxfattribs={"layer": "PRZ_OPISY", "insert": (0, y_leg)})
    for i, (kl, rgb) in enumerate(KOLORY_KLAS.items()):
        x = i * 22
        h = msp.add_hatch(dxfattribs={"layer": "PRZ_GRUNT_" + kl, "true_color": ezdxf.colors.rgb2int(rgb)})
        h.paths.add_polyline_path([(x, y_leg - 3), (x + 3, y_leg - 3), (x + 3, y_leg - 5), (x, y_leg - 5)], is_closed=True)
        msp.add_text("%s – %s" % (kl, OPIS_KLAS[kl]), height=0.7, dxfattribs={"layer": "PRZ_OPISY", "insert": (x + 3.5, y_leg - 4.6)})
    msp.add_text("Grunt: interpolacja profili 17 otworów DGI i 5 CPTU (jak w bilansie); między otworami to model, nie pomiar. Fundamenty głębsze nie są pokazane.", height=0.9,
                 dxfattribs={"layer": "PRZ_OPISY", "insert": (0, y_leg - 7)})
    doc.saveas(WY_DXF)
    print("zapisano", WY_DXF, "%.1f MB" % (os.path.getsize(WY_DXF) / 1e6))


# ------------------------------------------------------------------------------------------------ PNG
def rysuj_png(dane, dno):
    fig, axs = plt.subplots(len(dane), 1, figsize=(14, 17.5))
    for ax, (nm, d) in zip(axs, dane.items()):
        s = d["sm"][:, 0]
        for kl, geom in d["pol"].items():
            c = tuple(v / 255 for v in KOLORY_KLAS[kl])
            for q in wielokaty(geom):
                ax.fill(*q.exterior.xy, color=c, lw=0)
        zt, zh, hh = d["z"]["ist"], d["z"]["hum"], d["z"]["hh"]
        ax.fill_between(s, zt, zt - hh, color=tuple(v / 255 for v in KOLOR_HUMUS), lw=0)
        ax.fill_between(s, zt - hh, zh, color=tuple(v / 255 for v in KOLOR_NASYP), lw=0)
        ax.plot(s, zt, color="0.35", lw=0.8, label="teren istniejący")
        ax.plot(s, zh, color="saddlebrown", lw=0.8, label="po zdjęciu humusu i nasypu")
        ax.plot(s, d["zex"]["A"], color="tab:blue", lw=1.3, label="po wykopie A")
        ax.plot(s, d["zex"]["B"], color="tab:cyan", lw=1.3, ls="--", label="po wykopie B")
        ax.plot(s, d["z"]["kon"], color="limegreen", lw=1.3, label="stan końcowy (PZT)")
        ax.axhline(WODA_SR, color="navy", lw=0.8, ls=":", label="średni poziom wody wg DGI %.2f" % WODA_SR)
        for a, b in d["hale"]:
            ax.plot([a, b], [dno, dno], color="red", lw=2)
            ax.text((a + b) / 2, dno + 0.15, "hala (dno %.2f)" % dno, ha="center", fontsize=7, color="red")
        for a, b in d["zad"]:
            ax.plot([a, b], [dno, dno], color="darkorange", lw=2)
        for a, b in d["ramp"]:
            ax.text((a + b) / 2, dno + 1.8, "rampa", ha="center", fontsize=7, color="goldenrod")
        for x in d["scianka"]:
            ax.plot([x, x], [dno, float(np.interp(x, s, zh))], color="gold", lw=2)
        for x in d["s_gr"]:
            ax.axvline(x, color="purple", lw=0.6, ls="-.")
        for nr, sx, odl, H, wod in d["otw"]:
            ax.plot([sx, sx], [H, H - 8], color="k", lw=0.5)
            ax.text(sx, H + 0.2, "otw. %s" % nr, fontsize=6, ha="center")
        ax.set_xlim(0, d["total"]); ax.set_ylim(116.0, 127.5)
        ax.set_title("PRZEKRÓJ %s–%s  %s" % (nm, nm, OPIS_PRZEKROJU[nm]), fontsize=9, loc="left")
        ax.set_aspect("auto")
        ax.grid(True, lw=0.2)
        ax.set_ylabel("m npm")
    axs[0].legend(loc="upper right", fontsize=6, ncol=3)
    hand = [plt.Rectangle((0, 0), 1, 1, color=tuple(v / 255 for v in c)) for c in KOLORY_KLAS.values()]
    fig.legend(hand + [plt.Rectangle((0, 0), 1, 1, color=tuple(v / 255 for v in KOLOR_HUMUS)), plt.Rectangle((0, 0), 1, 1, color=tuple(v / 255 for v in KOLOR_NASYP))],
               ["%s %s" % (k, OPIS_KLAS[k]) for k in KOLORY_KLAS] + ["humus", "nasyp niekontrolowany"], loc="lower center", ncol=6, fontsize=6.5)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    for ax, (nm, d) in zip(axs, dane.items()):
        bb = ax.get_position()
        ex = (bb.height * 17.5 / 11.5) / (bb.width * 14 / d["total"])
        ax.set_title("PRZEKRÓJ %s–%s  %s   (przewyższenie pionowe ok. ×%.1f)" % (nm, nm, OPIS_PRZEKROJU[nm], ex), fontsize=9, loc="left")
    fig.savefig(WY_PNG, dpi=85)
    print("zapisano", WY_PNG)


if __name__ == "__main__":
    main()

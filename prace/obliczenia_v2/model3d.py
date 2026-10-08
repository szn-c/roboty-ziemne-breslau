"""
MODEL 3D robót ziemnych – dz. 1/90 Wojszyce. Wariant A i B, etapy:
  1 teren istniejący  ->  2 po zdjęciu humusu i nasypu  ->  3A / 3B po wykopie  ->  4 stan końcowy (rzędne projektowe z PZT)
Dane: te same rastry co w bilansie (silnik.licz(zapisz_geometrie=True)); powierzchnie jako adaptacyjne TIN (błąd pionowy <= TOL).
Wyniki:
  wyniki/MODEL3D_dz190.dxf          – siatki 3DFACE na warstwach 3D_* + linie 3D (hale, ścianka, rampy, krawędzie wykopu) – AutoCAD / GstarCAD / Civil 3D
  wyniki/MODEL3D_dz190_LandXML.xml  – te same powierzchnie jako TIN do Civil 3D (Import LandXML)
  prace/obliczenia_v2/model3d_kontrola.json – liczby kontrolne (objętości z TIN vs bilans)
Uruchomienie: python model3d.py
"""
import json
import math
import os
import time

import ezdxf
import numpy as np
from matplotlib.tri import LinearTriInterpolator, Triangulation
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import Delaunay
from shapely import contains_xy, wkt
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

import dane as D
import silnik as S

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WY_DXF = os.path.join(REPO, "wyniki", "MODEL3D_dz190.dxf")
WY_XML = os.path.join(REPO, "wyniki", "MODEL3D_dz190_LandXML.xml")
WY_KONTROLA = os.path.join(HERE, "model3d_kontrola.json")
TOL = 0.01          # dopuszczalny błąd pionowy TIN względem rastra 0,25 m [m] (poza bezpośrednim sąsiedztwem uskoków)
FAKTOR_USKOKU = 0.25  # dodatkowa tolerancja = ułamek lokalnego przewyższenia rastra (komórka 0,25 m)

POWIERZCHNIE = [   # klucz, nazwa w Civil 3D, warstwa DXF, kolor ACI, opis
    ("ist", "1_TEREN_ISTNIEJACY", "3D_1_TEREN_ISTNIEJACY", 8, "teren istniejący (PZT + otwory)"),
    ("hum", "2_PO_ZDJECIU_HUMUSU_I_NASYPU", "3D_2_PO_ZDJECIU_HUMUSU", 40, "teren po zdjęciu humusu i nasypu niekontrolowanego"),
    ("A", "3A_WYKOP_A", "3D_3A_WYKOP_A", 5, "wariant A – powierzchnia po wykopie (dno, skarpy, teren poza wykopem)"),
    ("B", "3B_WYKOP_B", "3D_3B_WYKOP_B", 4, "wariant B – powierzchnia po wykopie (dno, skarpy, teren poza wykopem)"),
    ("kon", "4_STAN_KONCOWY", "3D_4_STAN_KONCOWY", 3, "stan końcowy – rzędne projektowe z PZT"),
]


# ------------------------------------------------------------------------------------------------ TIN
def interpolator(xs, ys, Z2d):
    return RegularGridInterpolator((ys, xs), Z2d, bounds_error=False, fill_value=None)


def tin_z_rastra(xs, ys, Z2d, G, tol=TOL, krok=1, ds_gr=2.0, maks=150000):
    """Adaptacyjne TIN: punkty dokładane tam, gdzie błąd pionowy względem rastra jest największy.
    Dopuszczalny błąd w próbce = tol + lokalne przewyższenie rastra (max różnica do sąsiada), czyli ok. jedna komórka rastra w poziomie
    (stromy uskok, np. ścianka, nie wymusza w nieskończoność zagęszczania).
    Zwraca (punkty Nx3, trójkąty Mx3 przeciwnie do ruchu wskazówek zegara, statystyki, funkcja z(x, y) → NaN poza TIN)."""
    f = interpolator(xs, ys, Z2d)
    Zs = Z2d[::krok, ::krok]
    pad = np.pad(Zs, 1, mode="edge")
    rel = np.maximum.reduce([np.abs(Zs - pad[1:-1, :-2]), np.abs(Zs - pad[1:-1, 2:]), np.abs(Zs - pad[:-2, 1:-1]), np.abs(Zs - pad[2:, 1:-1])])
    X, Y = np.meshgrid(xs[::krok], ys[::krok])
    qx, qy, qz, qr0 = X.ravel(), Y.ravel(), Zs.ravel(), rel.ravel()
    m = contains_xy(G, qx, qy)
    qx, qy, qz, qr0 = qx[m], qy[m], qz[m], qr0[m]
    qr = np.minimum(qr0, 0.6)                    # duże uskoki (ścianka) nie są „wybaczane”
    uskok = np.flatnonzero(qr0 > 0.5)             # próbki po obu stronach uskoku – od razu wierzchołki
    OFF = np.array([math.floor(xs[0]), math.floor(ys[0])], float)      # współrzędne lokalne – duże wartości PL-2000 psują precyzję Delaunaya
    Q = np.column_stack([qx, qy]) - OFF
    ring = G.exterior
    nb = int(ring.length // ds_gr) + 1
    bd = [ring.interpolate(i * ring.length / nb) for i in range(nb)]
    bx = np.array([p.x for p in bd] + [c[0] for c in list(ring.coords)[:-1]])
    by = np.array([p.y for p in bd] + [c[1] for c in list(ring.coords)[:-1]])
    P = np.column_stack([bx, by, f(np.column_stack([by, bx]))])
    gx, gy = np.meshgrid(np.arange(xs[0] + 10, xs[-1], 20.0), np.arange(ys[0] + 10, ys[-1], 20.0))
    gm = contains_xy(G.buffer(-3), gx.ravel(), gy.ravel())
    gx, gy = gx.ravel()[gm], gy.ravel()[gm]
    P = np.vstack([P, np.column_stack([gx, gy, f(np.column_stack([gy, gx]))]), np.column_stack([qx[uskok], qy[uskok], qz[uskok]])])

    def blad(tri):
        s = tri.find_simplex(Q)
        ok = s >= 0
        T = tri.transform[s[ok]]
        bc = np.einsum("ijk,ik->ij", T[:, :2, :], Q[ok] - T[:, 2, :])
        zi = (P[tri.simplices[s[ok]], 2] * np.column_stack([bc, 1 - bc.sum(1)])).sum(1)
        return s, ok, np.abs(qz[ok] - zi)
    for it in range(120):
        tri = Delaunay(P[:, :2] - OFF)
        s, ok, err = blad(tri)
        exc = err - FAKTOR_USKOKU * qr[ok]
        so = s[ok]
        order = np.lexsort((-exc, so))
        ss = so[order]
        cand = order[np.r_[True, ss[1:] != ss[:-1]]]
        cand = cand[exc[cand] > tol]
        if len(cand) == 0 or len(P) >= maks:
            break
        cand = cand[np.argsort(-exc[cand])][:max(2000, len(P) // 2)]
        qq = np.flatnonzero(ok)[cand]
        P = np.vstack([P, np.column_stack([qx[qq], qy[qq], qz[qq]])])
    tri = Delaunay(P[:, :2] - OFF)
    s, ok, err = blad(tri)
    exc = err - FAKTOR_USKOKU * qr[ok]
    F0 = tri.simplices
    cen = P[F0][:, :, :2].mean(1)
    a = P[F0[:, 0], :2]; b = P[F0[:, 1], :2]; c = P[F0[:, 2], :2]
    cr = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    keep = contains_xy(G, cen[:, 0], cen[:, 1]) & (np.abs(cr) > 1e-4)
    F0 = np.where((cr < 0)[:, None], F0[:, [0, 2, 1]], F0)
    F = F0[keep]
    st = {"punkty": int(len(P)), "trojkaty": int(len(F)), "iteracje": it + 1, "blad_sredni_m": round(float(err.mean()), 4),
          "blad_p99_m": round(float(np.quantile(err, 0.99)), 4), "blad_max_m": round(float(err.max()), 3), "blad_ponad_tol_poza_uskokami_max_m": round(float(max(exc.max(), 0)), 4),
          "probki_blad_ponad_5cm_proc": round(100 * float((err > 0.05).mean()), 3)}
    bary = tri.transform

    def ewaluuj(x, y):
        pts = np.column_stack([x, y]) - OFF
        sidx = tri.find_simplex(pts)
        z = np.full(len(pts), np.nan)
        good = (sidx >= 0)
        good[good] = keep[sidx[good]]
        T = bary[sidx[good]]
        bc = np.einsum("ijk,ik->ij", T[:, :2, :], pts[good] - T[:, 2, :])
        z[good] = (P[tri.simplices[sidx[good]], 2] * np.column_stack([bc, 1 - bc.sum(1)])).sum(1)
        return z
    return P, F, st, ewaluuj


def zbior_uzywanych(P, F):
    """Usuwa punkty nieużywane przez żaden trójkąt i przenumerowuje."""
    u = np.unique(F)
    mp = -np.ones(len(P), int)
    mp[u] = np.arange(len(u))
    return P[u], mp[F]


# ------------------------------------------------------------------------------------------------ zapisy
def zapisz_landxml(sciezka, powierzchnie, nazwa_projektu):
    zasieg = []
    with open(sciezka, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fh.write('<LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                 'xsi:schemaLocation="http://www.landxml.org/schema/LandXML-1.2 http://www.landxml.org/schema/LandXML-1.2/LandXML-1.2.xsd" '
                 'date="2026-10-08" time="12:00:00" version="1.2" language="English" readOnly="false">\n')
        fh.write('  <Units>\n    <Metric areaUnit="squareMeter" linearUnit="meter" volumeUnit="cubicMeter" temperatureUnit="celsius" '
                 'pressureUnit="HPA" diameterUnit="meter" angularUnit="decimal degrees" directionUnit="decimal degrees"/>\n  </Units>\n')
        fh.write('  <Project name="%s"/>\n' % nazwa_projektu)
        fh.write('  <Application name="bilans_robot_ziemnych" desc="generator Python (model3d.py)" manufacturer="" version="1.0"/>\n')
        fh.write("  <Surfaces>\n")
        for nazwa, opis, P, F in powierzchnie:
            fh.write('    <Surface name="%s" desc="%s">\n' % (nazwa, opis))
            fh.write('      <Definition surfType="TIN" elevMax="%.3f" elevMin="%.3f">\n' % (P[:, 2].max(), P[:, 2].min()))
            fh.write("        <Pnts>\n")
            for i, (x, y, z) in enumerate(P, start=1):
                fh.write('          <P id="%d">%.3f %.3f %.3f</P>\n' % (i, y, x, z))     # LandXML: północ wschód rzędna
            fh.write("        </Pnts>\n        <Faces>\n")
            for a, b, c in F:
                fh.write("          <F>%d %d %d</F>\n" % (a + 1, b + 1, c + 1))
            fh.write("        </Faces>\n      </Definition>\n    </Surface>\n")
        fh.write("  </Surfaces>\n</LandXML>\n")


def pierscien_3d(coords, zfun, ds=2.0, zamkniety=True):
    """Łamana z gęstszymi punktami co ds [m], rzędne z funkcji zfun(x, y)."""
    ln = LineString(list(coords) + ([coords[0]] if zamkniety and coords[0] != coords[-1] else []))
    n = max(int(ln.length // ds), 1)
    pts = [ln.interpolate(i * ln.length / n) for i in range(n + (0 if zamkniety else 1))]
    xy = np.array([(p.x, p.y) for p in pts])
    z = zfun(xy[:, 0], xy[:, 1])
    return [(float(x), float(y), float(zz)) for (x, y), zz in zip(xy, z)]


def wielokaty(g):
    return [q for q in (list(g.geoms) if hasattr(g, "geoms") else [g]) if q.geom_type == "Polygon" and not q.is_empty]


def main():
    t0 = time.time()
    geo = json.load(open(os.path.join(D.DANE, "geometria.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(D.DANE, "strefy.json"), encoding="utf-8"))
    w, gm = S.licz(zapisz_geometrie=True)
    sg = gm["_siatka"]
    xs, ys, shape, cell = sg["xs"], sg["ys"], sg["shape"], sg["cell"]
    A = cell * cell
    G = Polygon(geo["granica"])
    P_scianka = Polygon(geo["scianka_otwarta"])
    inG = sg["inG"]
    zs = sg["zs"]
    Z = {"ist": sg["zt"], "hum": zs, "kon": sg["zp"]}
    for k in ("A", "B"):
        ze = sg[k]["ze"]
        Z[k] = np.where(np.isfinite(ze), np.minimum(zs, ze), zs)
    Z2 = {k: v.reshape(shape) for k, v in Z.items()}
    kontrola = {"tolerancja_TIN_m": TOL, "powierzchnie": {}, "objetosci": {}}
    TIN = {}
    EV = {}
    for klucz, nazwa, warstwa, kol, opis in POWIERZCHNIE:
        P, F, stat, ev = tin_z_rastra(xs, ys, Z2[klucz], G)
        EV[klucz] = ev
        P, F = zbior_uzywanych(P, F)
        P = np.round(P, 3)                               # te same wartości w DXF i w LandXML
        stat["punkty"] = int(len(P))
        TIN[klucz] = (P, F)
        kontrola["powierzchnie"][nazwa] = stat
        print("TIN %-30s punktów %6d trójkątów %6d  błąd średni %.4f, p99 %.4f, max %.3f m; próbek >5 cm: %.3f%%  (%.0f s)" % (
            nazwa, stat["punkty"], stat["trojkaty"], stat["blad_sredni_m"], stat["blad_p99_m"], stat["blad_max_m"], stat["probki_blad_ponad_5cm_proc"], time.time() - t0))
    # --- kontrola objętości: TIN vs raster vs bilans
    XX, YY = np.meshgrid(xs, ys)
    zt_tin = {k: EV[k](XX.ravel(), YY.ravel()) for k in TIN}
    for k in ("A", "B"):
        raster = float(np.clip(zs - Z[k], 0, None)[inG].sum() * A)
        d = zt_tin["hum"] - zt_tin[k]
        mm = inG & np.isfinite(d)
        tin = float(np.clip(d[mm], 0, None).sum() * A)
        zasyp_r = float(np.clip(Z[k] - zs, 0, None)[inG].sum() * A)
        kontrola["objetosci"][k] = {"wykop_raster_m3": round(raster, 3), "wykop_TIN_m3": round(tin, 3), "roznica_m3": round(tin - raster, 3),
                                    "roznica_proc": round(100 * (tin - raster) / raster, 4), "bilans_wykop_rodzimy_m3": w["warianty"][k]["pole_wykopu_razem"] and sum(
                                        sum(v.values()) for v in w["warianty"][k]["wykop_m3"].values()), "zasyp_ponad_teren_m3": round(zasyp_r, 3)}
        print("objętość wykopu %s: raster %.3f, TIN %.3f (różnica %.3f m3 = %.4f%%), bilans %.3f" % (
            k, raster, tin, tin - raster, 100 * (tin - raster) / raster, kontrola["objetosci"][k]["bilans_wykop_rodzimy_m3"]))
    for nm, (a_, b_) in {"humus_i_nasyp_ist_hum": ("ist", "hum")}.items():
        d = zt_tin[a_] - zt_tin[b_]
        mm = inG & np.isfinite(d)
        kontrola["objetosci"][nm] = round(float(d[mm].sum() * A), 3)
        print("humus + nasyp (ist - hum) z TIN: %.3f m3 (bilans: %.3f + %.3f)" % (kontrola["objetosci"][nm], w["humus_m3"], w["nasyp_m3"]))
    # --- DXF
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6
    msp = doc.modelspace()
    for klucz, nazwa, warstwa, kol, opis in POWIERZCHNIE:
        doc.layers.add(warstwa, color=kol).description = opis
        P, F = TIN[klucz]
        for a, b, c in F:
            msp.add_3dface([tuple(P[a]), tuple(P[b]), tuple(P[c]), tuple(P[c])], dxfattribs={"layer": warstwa})
    LIN = {"3D_LINIA_GRANICA": (7, "granica działki na terenie istniejącym"),
           "3D_LINIA_HALE_DNO": (1, "obrysy hal (garaży) na dnie wykopu 121,86"),
           "3D_LINIA_HALE_GORA": (6, "obrysy hal na rzędnej projektowej"),
           "3D_LINIA_HALE_KRAWEDZIE": (6, "krawędzie pionowe hal (dno – rzędna projektowa)"),
           "3D_LINIA_ZADASZONE_DNO": (30, "zadaszone dojazdy do garaży (poza halami) – dno 121,86"),
           "3D_LINIA_ZADASZONE_GORA": (30, "zadaszone dojazdy do garaży – rzędna projektowa"),
           "3D_LINIA_RAMPY_POWIERZCHNIA": (2, "pochylnie – powierzchnia rampy (122,85 → 125,80)"),
           "3D_LINIA_RAMPY_SPOD_WYKOPU": (2, "pochylnie – spód wykopu (powierzchnia − 0,71 m)"),
           "3D_LINIA_SCIANKA_GORA": (2, "ścianka wykopu – górna krawędź (teren po zdjęciu humusu)"),
           "3D_LINIA_SCIANKA_DNO": (2, "ścianka wykopu – dolna krawędź (dno wykopu, wariant B)"),
           "3D_LINIA_SCIANKA_ZAMKNIECIE": (8, "odcinek między końcami ścianki (od południa nie ma ścianki – skarpa 1:1,5)"),
           "3D_LINIA_A_GORA": (150, "wariant A – górna krawędź wykopu"),
           "3D_LINIA_A_DNO": (150, "wariant A – krawędź płaskiego dna 121,86"),
           "3D_LINIA_B_GORA": (140, "wariant B – górna krawędź wykopu"),
           "3D_LINIA_B_DNO": (140, "wariant B – krawędź płaskiego dna 121,86"),
           "3D_SCIANKA_B": (2, "ścianka – pionowe płaszczyzny od terenu do dna (wariant B)"),
           "3D_SCIANKA_A": (2, "ścianka – pionowe płaszczyzny od terenu do dna wykopu (wariant A)"),
           "3D_OPISY": (7, "opisy")}
    for nm, (kol, op) in LIN.items():
        doc.layers.add(nm, color=kol).description = op
    fzt = interpolator(xs, ys, Z2["ist"]); fzs = interpolator(xs, ys, Z2["hum"]); fzp = interpolator(xs, ys, Z2["kon"])
    fA = interpolator(xs, ys, Z2["A"]); fB = interpolator(xs, ys, Z2["B"])
    zf = lambda f: (lambda x, y: f(np.column_stack([y, x])))
    z_ist, z_hum, z_kon, z_A, z_B = zf(fzt), zf(fzs), zf(fzp), zf(fA), zf(fB)
    dno = S.PARAMETRY["dno"]
    stały = lambda v: (lambda x, y: np.full(len(x), v))

    def linia(coords, zfun, warstwa, ds=2.0, zamkniety=True):
        pts = pierscien_3d(list(coords), zfun, ds, zamkniety)
        msp.add_polyline3d(pts, close=zamkniety, dxfattribs={"layer": warstwa})
        return pts

    def poly_rings(g, zfun, warstwa, ds=2.0, min_pole=1.0):
        n = 0
        for q in wielokaty(g):
            if q.area < min_pole:
                continue
            for ring in [q.exterior] + list(q.interiors):
                linia(list(ring.coords)[:-1], zfun, warstwa, ds)
                n += 1
        return n
    linia(list(G.exterior.coords)[:-1], z_ist, "3D_LINIA_GRANICA", 2.0)
    HALE = {int(k): Polygon(v) for k, v in geo["hale"].items()}
    for nr, h in HALE.items():
        c = list(h.exterior.coords)[:-1]
        linia(c, stały(dno), "3D_LINIA_HALE_DNO", 50.0)
        linia(c, z_kon, "3D_LINIA_HALE_GORA", 5.0)
        for (x, y) in c:
            zk = float(z_kon(np.array([x]), np.array([y]))[0])
            msp.add_line((x, y, dno), (x, y, zk), dxfattribs={"layer": "3D_LINIA_HALE_KRAWEDZIE"})
        cx, cy = h.centroid.x, h.centroid.y
        msp.add_text("HALA %d (dno %.2f)" % (nr, dno), height=1.8, dxfattribs={"layer": "3D_OPISY", "insert": (cx - 8, cy, dno + 0.3)})
    zad = wkt.loads(st["zadaszone_poza_halami"])
    poly_rings(zad, stały(dno), "3D_LINIA_ZADASZONE_DNO", 50.0)
    poly_rings(zad, z_kon, "3D_LINIA_ZADASZONE_GORA", 5.0)
    for r in st["rampy"]:
        (xd, yd), (xg, yg) = r["dol"], r["gora"]
        ux, uy = xg - xd, yg - yd
        L2 = ux * ux + uy * uy

        def zr(x, y, ux=ux, uy=uy, L2=L2, xd=xd, yd=yd):
            t = np.clip(((x - xd) * ux + (y - yd) * uy) / L2, 0, 1)
            return D.RAMPA_DOL + t * (D.RAMPA_GORA - D.RAMPA_DOL)
        for q in wielokaty(wkt.loads(r["obrys"])):
            c = list(q.exterior.coords)[:-1]
            linia(c, zr, "3D_LINIA_RAMPY_POWIERZCHNIA", 1.5)
            linia(c, lambda x, y, zr=zr: zr(x, y) - D.RAMPA_POD, "3D_LINIA_RAMPY_SPOD_WYKOPU", 1.5)
        msp.add_polyline3d([(xg, yg, D.RAMPA_GORA), (xd, yd, D.RAMPA_DOL)], dxfattribs={"layer": "3D_LINIA_RAMPY_POWIERZCHNIA"})
        msp.add_text("rampa %.2f → %.2f" % (D.RAMPA_GORA, D.RAMPA_DOL), height=1.0, dxfattribs={"layer": "3D_OPISY", "insert": ((xd + xg) / 2 + 3, (yd + yg) / 2, D.RAMPA_DOL + 1.0)})
    wall = geo["scianka_otwarta"]
    linia(wall, z_hum, "3D_LINIA_SCIANKA_GORA", 2.0, zamkniety=False)
    linia(wall, lambda x, y: np.minimum(z_hum(x, y), z_B(x, y)), "3D_LINIA_SCIANKA_DNO", 2.0, zamkniety=False)
    msp.add_polyline3d([(*geo["odcinek_zamykajacy"][0], float(z_hum(np.array([geo["odcinek_zamykajacy"][0][0]]), np.array([geo["odcinek_zamykajacy"][0][1]]))[0])),
                        (*geo["odcinek_zamykajacy"][1], float(z_hum(np.array([geo["odcinek_zamykajacy"][1][0]]), np.array([geo["odcinek_zamykajacy"][1][1]]))[0]))],
                       dxfattribs={"layer": "3D_LINIA_SCIANKA_ZAMKNIECIE"})
    # krawędzie wykopów: góra = obrys obszaru, gdzie teren po zdjęciu humusu jest wyższy od powierzchni po wykopie; dno = obszar płaskiego dna
    for k, zf_k in (("A", z_A), ("B", z_B)):
        gora = gm[k]
        poly_rings(gora.intersection(G), z_hum, "3D_LINIA_%s_GORA" % k, 2.0, 2.0)
        dno_m = (np.abs(Z[k] - dno) < 0.003) & inG
        dno_g = S.maska_na_wielokaty(dno_m.reshape(shape), xs, ys, cell, tol=0.1)
        poly_rings(dno_g, stały(dno), "3D_LINIA_%s_DNO" % k, 2.0, 2.0)
    # pionowe płaszczyzny ścianki: od terenu po zdjęciu humusu do powierzchni po wykopie tuż za ścianką (wewnątrz)
    wl = LineString(wall)
    ds = 1.5
    n = int(wl.length // ds)
    pts = []
    for i in range(n + 1):
        p = wl.interpolate(min(i * ds, wl.length))
        q = wl.interpolate(min(i * ds + 0.1, wl.length)) if i * ds + 0.1 <= wl.length else wl.interpolate(wl.length - 0.1)
        tx, ty = q.x - p.x, q.y - p.y
        nl = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / nl, tx / nl
        if not P_scianka.contains(__import__("shapely").geometry.Point(p.x + 0.3 * nx, p.y + 0.3 * ny)):
            nx, ny = -nx, -ny
        pts.append((p.x, p.y, p.x + 0.3 * nx, p.y + 0.3 * ny))
    pts = np.array(pts)
    zg = z_hum(pts[:, 0], pts[:, 1])
    nface = {"A": 0, "B": 0}
    for k, zf_k in (("A", z_A), ("B", z_B)):
        zd = np.minimum(zg, zf_k(pts[:, 2], pts[:, 3]))
        for i in range(len(pts) - 1):
            if (zg[i] - zd[i]) < 0.01 and (zg[i + 1] - zd[i + 1]) < 0.01:
                continue
            msp.add_3dface([(pts[i, 0], pts[i, 1], zg[i]), (pts[i + 1, 0], pts[i + 1, 1], zg[i + 1]),
                            (pts[i + 1, 0], pts[i + 1, 1], zd[i + 1]), (pts[i, 0], pts[i, 1], zd[i])], dxfattribs={"layer": "3D_SCIANKA_%s" % k})
            nface[k] += 1
    kontrola["plaszczyzny_scianki"] = nface
    # legenda
    x0, y0 = G.bounds[2] + 15, G.bounds[3]
    msp.add_text("MODEL 3D robót ziemnych – dz. 1/90 Wojszyce (PL-2000/6, wysokości PL-KRON86-NH)", height=1.6, dxfattribs={"layer": "3D_OPISY", "insert": (x0, y0, 0)})
    msp.add_text("Etapy: 1 teren istniejący → 2 po zdjęciu humusu i nasypu → 3A / 3B po wykopie → 4 stan końcowy. Włączaj i wyłączaj warstwy 3D_*.", height=1.0,
                 dxfattribs={"layer": "3D_OPISY", "insert": (x0, y0 - 3, 0)})
    msp.add_text("Fundamenty głębsze (pogrubienia, rdzenie, studzienki) nie są w modelu – w bilansie są osobną pozycją (liczba sztuk, bez położeń).", height=1.0,
                 dxfattribs={"layer": "3D_OPISY", "insert": (x0, y0 - 5, 0)})
    doc.header["$LASTSAVEDBY"] = "bilans_v2"
    doc.saveas(WY_DXF)
    print("zapisano", WY_DXF, "%.1f MB" % (os.path.getsize(WY_DXF) / 1e6), "(%.0f s)" % (time.time() - t0))
    # --- LandXML
    zapisz_landxml(WY_XML, [(nazwa, opis, *TIN[klucz]) for klucz, nazwa, warstwa, kol, opis in POWIERZCHNIE], "Bilans robot ziemnych dz. 1/90 Wojszyce")
    print("zapisano", WY_XML, "%.1f MB" % (os.path.getsize(WY_XML) / 1e6))
    json.dump(kontrola, open(WY_KONTROLA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # zwróć dane dla innych modułów
    return TIN, kontrola


if __name__ == "__main__":
    main()

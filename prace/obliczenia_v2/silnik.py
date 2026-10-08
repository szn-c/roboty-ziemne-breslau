"""
SILNIK BILANSU v2 – działka 1/90 (raster 0,25 m). Dane: prace/dane/ (dane.py). Wynik: prace/obliczenia_v2/wyniki.json

Zasady (USTALENIA.md, decyzje z 7–8.10.2026):
- humus i nasyp zdejmowane z całej działki; nasyp 100% wywóz; humus na odkład wg wzoru (arkusz);
- dno wykopu 121,86; fundamenty głębsze osobno (wywóz);
- wariant A: obiekty podziemne (hale, zadaszone dojazdy, rampy) + przestrzeń robocza 1,0 m + skarpa 1:1,5 do terenu po zdjęciu humusu;
  wariant B: cały obszar w ściance do dna 121,86, ściany pionowe; od południa brak ścianki – skarpa 1:1,5
  (podnóże skarpy = prosty odcinek między końcami ścianki, poszerzony o hale 7 i 8 z przestrzenią roboczą 1,0 m);
  za ścianką (W, N, E) nie kopiemy;
- strefy: H hale + zieleń na stropie poza halami (zadaszone dojazdy) – wykop na wywóz, bez zasypu;
  O ogrody deszczowe – jak hale; R rampy – wykop do spodu rampy (powierzchnia − 0,71 m), zasyp gruntem z odkładu do spodu rampy;
  Z zieleń na gruncie – 0,25 m humusu + grunt rodzimy z odkładu niżej;
  U nawierzchnie (w tym geokrata, wiaty) – 0,50 m konstrukcji (poza bilansem) + 0,50 m gruntu niewysadzinowego (strefa przemarzania 1,00 m – dowóz)
  + grunt rodzimy z odkładu poniżej 1,00 m;
- poza wykopem nie kopiemy: miejsca, gdzie konstrukcja / humus / strefa przemarzania wchodzą w grunt rodzimy, są raportowane.
"""
import json
import math
import os

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
from scipy.ndimage import distance_transform_edt
from scipy.spatial import Delaunay
from shapely import contains_xy, wkt
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

import dane as D

HERE = os.path.dirname(os.path.abspath(__file__))
WYN = os.path.join(HERE, "wyniki.json")
DK = 0.01          # krok krzywych skumulowanych [m]
NK = 801           # do 8,0 m pod stropem gruntu mineralnego

PARAMETRY = dict(cell=0.25, dno=D.DNO, przestrzen_robocza=1.0, skarpa=1.5, konstrukcja=0.50, przemarzanie=1.00, humus_ziel=0.25,
                 dz_teren=0.0, dz_humus=0.0, rampa_pod=D.RAMPA_POD)


# ------------------------------------------------------------------------------------------------ profile
def klucz_wilg(s):
    s = (s or "").strip()
    if s == "mw":
        return "mw"
    if "nw" in s or s == "m" or "m" in s.split("/"):
        return "nw"
    return "w"


def krzywe_profilu(warstwy, woda_m=None):
    """Krzywe skumulowane: objętość klas KLASY i masa [t] na 1 m² w funkcji głębokości pod stropem gruntu mineralnego."""
    h = sum(w["spag"] - w["strop"] for w in warstwy if w["kat"] == "H")
    n = sum(w["spag"] - w["strop"] for w in warstwy if w["kat"] == "N")
    top = h + n
    d = np.arange(NK) * DK
    cum = np.zeros((len(D.KLASY) + 2, NK))       # klasy + masa piasków + masa glin
    for w in warstwy:
        if w["kat"] not in ("P", "G"):
            continue
        a, b = w["strop"] - top, w["spag"] - top
        if b <= 0:
            continue
        lay = w["warstwa"]
        if w["kat"] == "P":
            k = klucz_wilg(w.get("wilgotnosc")) if w.get("wilgotnosc") else ("nw" if (woda_m is not None and (w["strop"] + w["spag"]) / 2 >= woda_m) else "w")
            rho = D.GESTOSC[lay][k]
        else:
            rho = D.GESTOSC[lay]
        frac = np.clip(np.minimum(d, b) - max(a, 0.0), 0, None)
        ci = D.KLASY.index(lay)
        cum[ci] += frac
        cum[len(D.KLASY) + (0 if lay in D.PIASKI else 1)] += frac * rho
    # poniżej 10 m (koniec otworu) – przedłużenie ostatnią warstwą
    return h, n, cum


def lokalizacje():
    oto = json.load(open(os.path.join(D.DANE, "otwory.json"), encoding="utf-8"))
    cp = json.load(open(os.path.join(D.DANE, "cptu.json"), encoding="utf-8"))
    L = []
    for nr, o in oto.items():
        h, n, cum = krzywe_profilu(o["warstwy"])
        rec = {"nr": int(nr), "E": o["E"], "N": o["N"], "humus": h, "nasyp": n, "cum": cum, "zrodla": ["otwór %s" % nr]}
        if nr in cp:
            woda = o["woda_ustab_m_ppt"] if o["woda_ustab_m_ppt"] is not None else 3.0
            h2, _, cum2 = krzywe_profilu(cp[nr]["warstwy"], woda_m=woda)
            rec["humus"] = 0.5 * (h + h2)
            rec["cum"] = 0.5 * (cum + cum2)
            rec["zrodla"].append("CPTU-%s" % nr)
            rec["humus_otwor"], rec["humus_cptu"] = h, h2
        L.append(rec)
    return L


# ------------------------------------------------------------------------------------------------ geometria pomocnicza
def odl_odcinki(x, y, pts):
    """Odległość punktów (x, y) od łamanej pts (numpy)."""
    best = np.full(x.shape, np.inf)
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = np.clip(((x - x1) * dx + (y - y1) * dy) / L2, 0, 1)
        best = np.minimum(best, np.hypot(x - (x1 + t * dx), y - (y1 + t * dy)))
    return best


def maska_na_wielokaty(mask, xs, ys, cell, tol=0.05):
    """Obrys maski rastra jako wielokąty (suma prostokątów z odcinków wierszy)."""
    boxes = []
    for j in range(mask.shape[0]):
        row = mask[j]
        if not row.any():
            continue
        idx = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(np.int8), [0]])))
        for a, b in zip(idx[::2], idx[1::2]):
            boxes.append(box(xs[a] - cell / 2, ys[j] - cell / 2, xs[b - 1] + cell / 2, ys[j] + cell / 2))
    return unary_union(boxes).simplify(tol) if boxes else Polygon()


# ------------------------------------------------------------------------------------------------ główne obliczenie
def licz(p=None, zapisz_geometrie=False):
    p = dict(PARAMETRY, **(p or {}))
    cell = p["cell"]
    A = cell * cell
    geo = json.load(open(os.path.join(D.DANE, "geometria.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(D.DANE, "strefy.json"), encoding="utf-8"))
    nas = json.load(open(os.path.join(D.DANE, "nasyp_strefy.json"), encoding="utf-8"))
    G = Polygon(geo["granica"])
    HALE = {int(k): Polygon(v) for k, v in geo["hale"].items()}
    WALL = geo["scianka_otwarta"]
    P = Polygon(WALL)
    minx, miny, maxx, maxy = G.buffer(3).bounds
    xs = np.arange(math.floor(minx) + cell / 2, maxx, cell)
    ys = np.arange(math.floor(miny) + cell / 2, maxy, cell)
    X, Y = np.meshgrid(xs, ys)
    x, y = X.ravel(), Y.ravel()
    shape = X.shape
    inG = contains_xy(G, x, y)
    # --- teren, projekt
    import csv
    T = np.array([(float(r["E"]), float(r["N"]), float(r["z"])) for r in csv.DictReader(open(os.path.join(D.DANE, "teren_istniejacy.csv"), encoding="utf-8"))])
    F = np.array([(float(r["E"]), float(r["N"]), float(r["z"])) for r in csv.DictReader(open(os.path.join(D.DANE, "teren_projektowany.csv"), encoding="utf-8"))])

    def tin(pts, xx, yy):
        z = LinearNDInterpolator(pts[:, :2], pts[:, 2])(xx, yy)
        bad = np.isnan(z)
        if bad.any():
            z[bad] = NearestNDInterpolator(pts[:, :2], pts[:, 2])(xx[bad], yy[bad])
        return z
    zt = tin(T, x, y) + p["dz_teren"]
    zp = tin(F, x, y)
    # --- profile i wagi TIN
    L = lokalizacje()
    LP = np.array([(l["E"], l["N"]) for l in L])
    tri = Delaunay(LP)
    s = tri.find_simplex(np.column_stack([x, y]))
    W3 = np.zeros((len(x), 3)); I3 = np.zeros((len(x), 3), int)
    ok = s >= 0
    Tm = tri.transform[s[ok]]
    b2 = np.einsum("ijk,ik->ij", Tm[:, :2, :], np.column_stack([x[ok], y[ok]]) - Tm[:, 2, :])
    W3[ok] = np.column_stack([b2, 1 - b2.sum(1)]); I3[ok] = tri.simplices[s[ok]]
    nn = NearestNDInterpolator(LP, np.arange(len(L)))(x[~ok], y[~ok]).astype(int)
    W3[~ok, 0] = 1.0; I3[~ok, 0] = nn
    hum_l = np.array([l["humus"] for l in L])
    hh = np.clip((W3 * hum_l[I3]).sum(1) + p["dz_humus"], 0, None)
    hn = np.zeros(len(x))
    for sfe in nas["strefy"]:
        hn[contains_xy(Polygon(sfe["wierzcholki"]), x, y)] = sfe["grubosc_m"]
    zs = zt - hh - hn
    CUM = np.stack([l["cum"] for l in L])          # (n_loc, n_ch, NK)

    def sklad(dz, idx=None):
        """Objętości klas i masa [na m²] dla wykopu dz [m] pod stropem gruntu mineralnego."""
        idx = np.arange(len(x)) if idx is None else idx
        k = np.clip(dz / DK, 0, NK - 1.0001)
        k0 = np.floor(k).astype(int); fr = k - k0
        out = np.zeros((len(idx), CUM.shape[1]))
        for j in range(3):
            l = I3[idx, j]
            v = CUM[l, :, k0] * (1 - fr)[:, None] + CUM[l, :, k0 + 1] * fr[:, None]
            out += W3[idx, j][:, None] * v
        return out
    # --- strefy
    Hst = unary_union(list(HALE.values()) + [wkt.loads(st["zielen_na_stropie"]), wkt.loads(st["zadaszone_poza_halami"])]).intersection(G)
    mH = contains_xy(Hst, x, y) & inG
    mR = np.zeros(len(x), bool); z_rampa = np.full(len(x), np.nan)
    for r in st["rampy"]:
        Pr = wkt.loads(r["obrys"])
        m = contains_xy(Pr, x, y) & inG & ~mH
        (xd, yd), (xg, yg) = r["dol"], r["gora"]
        ux, uy = xg - xd, yg - yd
        Lr = math.hypot(ux, uy)
        t = np.clip(((x[m] - xd) * ux + (y[m] - yd) * uy) / (Lr * Lr), 0, 1)
        z_rampa[m] = D.RAMPA_DOL + t * (D.RAMPA_GORA - D.RAMPA_DOL)
        mR |= m
    mO = contains_xy(wkt.loads(st["ogrody_deszczowe"]), x, y) & inG & ~mH & ~mR
    mZ = contains_xy(wkt.loads(st["zielen_na_gruncie"]), x, y) & inG & ~mH & ~mR & ~mO
    mU = inG & ~mH & ~mR & ~mO & ~mZ
    z_br = z_rampa - p["rampa_pod"]
    # --- obszar przed ścianką (D): wnętrze P + strona południowa otwarta
    inP = contains_xy(P, x, y)
    d_wall = odl_odcinki(x, y, WALL)
    d_clos = odl_odcinki(x, y, [WALL[-1], WALL[0]])
    Ddom = inP | (~inP & (d_clos < d_wall - 1e-6))
    # --- wariant A: obiekty podziemne S = H ∪ R
    S = (mH | mR)
    zbS = np.where(mR, z_br, p["dno"])
    dS, ind = distance_transform_edt(~S.reshape(shape), sampling=cell, return_indices=True)
    near = np.ravel_multi_index((ind[0].ravel(), ind[1].ravel()), shape)
    dS = np.maximum(dS.ravel() - cell / 2, 0) * (~S)
    zeA = zbS[near] + np.maximum(dS - p["przestrzen_robocza"], 0) / p["skarpa"]
    zeA = np.where(Ddom, zeA, np.inf)
    # --- wariant B
    dH = distance_transform_edt(~mH.reshape(shape), sampling=cell).ravel()
    Breg = (inP | ((dH <= p["przestrzen_robocza"] + cell / 2) & Ddom))
    dB = np.maximum(distance_transform_edt(~Breg.reshape(shape), sampling=cell).ravel() - cell / 2, 0)
    zeB = np.where(Breg, p["dno"], p["dno"] + dB / p["skarpa"])
    zeB = np.where(mR, np.minimum(zeB, z_br), zeB)
    zeB = np.where(Ddom, zeB, np.inf)
    # --- obiekty za ścianką wymagające wykopu (kontrola)
    za_scianka = {"H": int(((mH) & ~Ddom & (zs > p["dno"])).sum()), "R": int((mR & ~Ddom & (zs > z_br)).sum())}

    wynik = {"parametry": p, "pola": {}, "warianty": {}}
    wynik["pola"] = {k: round(float(m.sum() * A), 2) for k, m in (("dzialka_raster", inG), ("H_hale_i_zadaszone", mH), ("R_rampy", mR), ("O_ogrody", mO),
                                                                  ("Z_zielen", mZ), ("U_nawierzchnie", mU))}
    wynik["pola"]["hale_obrysy"] = round(sum(h.area for h in HALE.values()), 2)
    wynik["pola"]["zadaszone_poza_halami"] = round(Hst.area - unary_union(list(HALE.values())).area, 2)
    wynik["pola"]["dzialka"] = round(G.area, 2)
    wynik["pola"]["w_sciance_P"] = round(P.area, 2)
    wynik["humus_m3"] = round(float((hh * inG).sum() * A), 3)
    wynik["nasyp_m3"] = round(float((hn * inG).sum() * A), 3)
    wynik["humus_sr_grubosc"] = round(float(hh[inG].mean()), 3)
    wynik["teren_sr"] = {"dzialka": round(float(zt[inG].mean()), 3), "w_sciance": round(float(zt[inG & inP].mean()), 3)}
    wynik["za_scianka_komorek"] = za_scianka
    geom = {}
    for nazwa, ze in (("A", zeA), ("B", zeB)):
        dz = np.where(inG, np.clip(zs - ze, 0, None), 0.0)
        dz = np.nan_to_num(dz, posinf=0.0)
        exc = dz > 1e-9
        poza_dz = np.clip(zs - ze, 0, None); poza_dz = np.nan_to_num(poza_dz, posinf=0.0)
        poza = (~inG) & (poza_dz > 1e-9)
        idx = np.flatnonzero(exc)
        sk = sklad(dz[idx], idx) * A                  # (n, n_ch)
        zb = np.where(exc, ze, zs)                     # spód zasypu
        res = {"wykop_m3": {}, "masa_t": {}, "zapotrzebowanie": {}, "konflikty": {}, "pola_wykopu": {}}
        for zn, m in (("H", mH), ("O", mO), ("R", mR), ("Z", mZ), ("U", mU)):
            mm = m[idx]
            res["wykop_m3"][zn] = {k: round(float(sk[mm, i].sum()), 3) for i, k in enumerate(D.KLASY)}
            res["masa_t"][zn] = {"piaski": round(float(sk[mm, len(D.KLASY)].sum()), 3), "gliny": round(float(sk[mm, len(D.KLASY) + 1].sum()), 3)}
            res["pola_wykopu"][zn] = round(float(mm.sum() * A), 2)
        # zapotrzebowanie
        t_k, t_p, t_h = p["konstrukcja"], p["przemarzanie"], p["humus_ziel"]
        Zc = mZ
        humus_wb = np.where(Zc, np.clip(np.minimum(t_h, zp - zb), 0, None), 0)
        nat_Z = np.where(Zc, np.clip(zp - t_h - zb, 0, None), 0)
        konf_Z = np.where(Zc, np.clip(zb - (zp - t_h), 0, None), 0)
        Uc = mU
        mroz = np.where(Uc, np.clip((zp - t_k) - np.maximum(zb, zp - t_p), 0, None), 0)
        nat_U = np.where(Uc, np.clip(zp - t_p - zb, 0, None), 0)
        konf_U1 = np.where(Uc, np.clip(zb - (zp - t_k), 0, None), 0)                       # konstrukcja wchodzi w grunt
        konf_U2 = np.where(Uc, np.clip(np.minimum(zb, zp - t_k) - (zp - t_p), 0, None), 0)  # grunt rodzimy w strefie przemarzania
        nat_R = np.where(mR, np.clip(z_br - zb, 0, None), 0); nat_R = np.nan_to_num(nat_R)
        pustka_O = np.where(mO & exc, np.clip(zp - zb, 0, None), 0)
        obszar = {"wykop": exc, "poza_wykopem_w_sciance": (~exc) & inP, "poza_wykopem_poza_scianka": (~exc) & ~inP}
        for k, v in (("humus_warstwa_Z", humus_wb), ("rodzimy_Z", nat_Z), ("rodzimy_U", nat_U), ("rodzimy_R", nat_R), ("niewysadzinowy_U", mroz)):
            res["zapotrzebowanie"][k] = {o: round(float((v * mo * inG).sum() * A), 3) for o, mo in obszar.items()}
        for k, v in (("Z_humus_ponad_grunt", konf_Z), ("U_konstrukcja_w_gruncie", konf_U1), ("U_grunt_rodzimy_w_strefie_przemarzania", konf_U2), ("O_pustka_pod_ogrodem", pustka_O)):
            res["konflikty"][k] = {o: {"m3": round(float((v * mo * inG).sum() * A), 3), "m2": round(float(((v > 0.005) & mo & inG).sum() * A), 2)} for o, mo in obszar.items()}
        res["pole_wykopu_razem"] = round(float(exc.sum() * A), 2)
        res["wykop_poza_dzialka"] = {"m2": round(float(poza.sum() * A), 2), "m3": round(float((poza_dz * poza).sum() * A), 3)}
        res["glebokosc_sr"] = round(float(dz[exc].mean()), 3) if exc.any() else 0
        # skład do kontroli: piaski/gliny
        wynik["warianty"][nazwa] = res
        if zapisz_geometrie:
            geom[nazwa] = maska_na_wielokaty(exc.reshape(shape), xs, ys, cell)
    # --- fundamenty głębsze (osobno, pod halami)
    wynik["fundamenty"] = fundamenty(HALE, x, y, inG, zs, sklad, p)
    if zapisz_geometrie:
        return wynik, geom
    return wynik


ELEMENTY = {
    # nazwa: (krótszy bok, dłuższy bok, d.k. elementu, d.k. odniesienia (spód otoczenia))
    "pogrubienie 3,40×4,40 (d.k. −4,34)": (3.40, 4.40, -4.34, -4.04),
    "pogrubienie 3,40×4,40 (d.k. −4,54)": (3.40, 4.40, -4.54, -4.04),
    "pogrubienie 4,40×6,54 (d.k. −4,34)": (4.40, 6.54, -4.34, -4.04),
    "pogrubienie 4,40×6,59 (d.k. −4,34)": (4.40, 6.59, -4.34, -4.04),
    "rdzeń 7,48×8,57 (d.k. −4,34)": (7.48, 8.57, -4.34, -4.04),
    "rdzeń 8,57×9,48 (d.k. −4,34)": (8.57, 9.48, -4.34, -4.04),
    "szyb windy 2,09×2,96 (d.k. −4,93)": (2.09, 2.96, -4.93, -4.34),
    "studzienka 2,00×3,00 (d.k. −6,00)": (2.00, 3.00, -6.00, -4.04),
    "studzienka 1,455×1,80 (d.k. −5,83)": (1.455, 1.80, -5.83, -4.04),
    "studzienka 1,50×1,80 (d.k. −5,40)": (1.50, 1.80, -5.40, -4.04),
}
LICZBY = {  # sztuki w budynkach (rzuty PW_*, prace/weryfikacja/fundamenty_glebsze.py)
    "1A": {"pogrubienie 3,40×4,40 (d.k. −4,34)": 17, "rdzeń 7,48×8,57 (d.k. −4,34)": 1, "szyb windy 2,09×2,96 (d.k. −4,93)": 1,
           "studzienka 2,00×3,00 (d.k. −6,00)": 1, "studzienka 1,455×1,80 (d.k. −5,83)": 1, "studzienka 1,50×1,80 (d.k. −5,40)": 1},
    "2C": {"pogrubienie 3,40×4,40 (d.k. −4,34)": 5, "pogrubienie 4,40×6,54 (d.k. −4,34)": 6, "pogrubienie 3,40×4,40 (d.k. −4,54)": 2,
           "rdzeń 8,57×9,48 (d.k. −4,34)": 1, "szyb windy 2,09×2,96 (d.k. −4,93)": 1, "studzienka 2,00×3,00 (d.k. −6,00)": 1,
           "studzienka 1,455×1,80 (d.k. −5,83)": 1},
    "3A": {"pogrubienie 3,40×4,40 (d.k. −4,34)": 17, "rdzeń 7,48×8,57 (d.k. −4,34)": 1, "szyb windy 2,09×2,96 (d.k. −4,93)": 1,
           "studzienka 2,00×3,00 (d.k. −6,00)": 1, "studzienka 1,455×1,80 (d.k. −5,83)": 1},
    "4B": {"pogrubienie 3,40×4,40 (d.k. −4,34)": 18, "pogrubienie 4,40×6,59 (d.k. −4,34)": 2, "rdzeń 7,48×8,57 (d.k. −4,34)": 1,
           "szyb windy 2,09×2,96 (d.k. −4,93)": 1, "studzienka 2,00×3,00 (d.k. −6,00)": 1, "studzienka 1,455×1,80 (d.k. −5,83)": 1,
           "studzienka 1,50×1,80 (d.k. −5,40)": 1},
    "5A": {"pogrubienie 3,40×4,40 (d.k. −4,34)": 17, "rdzeń 7,48×8,57 (d.k. −4,34)": 1, "szyb windy 2,09×2,96 (d.k. −4,93)": 1,
           "studzienka 2,00×3,00 (d.k. −6,00)": 1, "studzienka 1,455×1,80 (d.k. −5,83)": 1},
    "6A": {"pogrubienie 3,40×4,40 (d.k. −4,34)": 16, "rdzeń 7,48×8,57 (d.k. −4,34)": 1, "szyb windy 2,09×2,96 (d.k. −4,93)": 1,
           "studzienka 2,00×3,00 (d.k. −6,00)": 1, "studzienka 1,455×1,80 (d.k. −5,83)": 1, "studzienka 1,50×1,80 (d.k. −5,40)": 1},
    "7A": {"pogrubienie 3,40×4,40 (d.k. −4,34)": 17, "rdzeń 7,48×8,57 (d.k. −4,34)": 1, "szyb windy 2,09×2,96 (d.k. −4,93)": 1,
           "studzienka 2,00×3,00 (d.k. −6,00)": 1, "studzienka 1,455×1,80 (d.k. −5,83)": 1},
    "8B": {"pogrubienie 3,40×4,40 (d.k. −4,34)": 18, "pogrubienie 4,40×6,59 (d.k. −4,34)": 2, "rdzeń 7,48×8,57 (d.k. −4,34)": 1,
           "szyb windy 2,09×2,96 (d.k. −4,93)": 1, "studzienka 2,00×3,00 (d.k. −6,00)": 1, "studzienka 1,455×1,80 (d.k. −5,83)": 1,
           "studzienka 1,50×1,80 (d.k. −5,40)": 1},
}
SKOS = 0.50   # obrys przerywany obniżenia = spód + 0,50 m z każdej strony (rzuty PW, pogrubienia)


def objetosc_elementu(a, b, dk, dk_ref):
    """Bryła ścięta: spód a×b, góra (a+2·SKOS)×(b+2·SKOS), wysokość = (d.k. elementu − chudy beton) − (d.k. otoczenia − chudy beton)."""
    h = (dk_ref - dk)
    A1, A2 = a * b, (a + 2 * SKOS) * (b + 2 * SKOS)
    return h, h / 3 * (A1 + A2 + math.sqrt(A1 * A2))


def fundamenty(HALE, x, y, inG, zs, sklad, p):
    bud = {"1A": 1, "2C": 2, "3A": 3, "4B": 4, "5A": 5, "6A": 6, "7A": 7, "8B": 8}
    out = {"elementy": {}, "budynki": {}, "razem_m3": 0.0, "klasy_m3": {k: 0.0 for k in D.KLASY}, "masa_t": {"piaski": 0.0, "gliny": 0.0}}
    for nazwa, (a, b, dk, ref) in ELEMENTY.items():
        h, v = objetosc_elementu(a, b, dk, ref)
        out["elementy"][nazwa] = {"wymiary": [a, b], "dk": dk, "glebokosc_ponizej_otoczenia": round(h, 3), "objetosc_szt": round(v, 3)}
    for bnaz, nr in bud.items():
        m = contains_xy(HALE[nr], x, y) & inG
        idx = np.flatnonzero(m)
        d0 = zs[idx] - p["dno"]
        V = 0.0; kl = np.zeros(len(D.KLASY) + 2)
        for nazwa, n in LICZBY[bnaz].items():
            a, b, dk, ref = ELEMENTY[nazwa]
            h, v = objetosc_elementu(a, b, dk, ref)
            top = d0 + (-4.04 - ref)            # strop elementu względem stropu gruntu mineralnego
            s1, s2 = sklad(top, idx), sklad(top + h, idx)
            fr = (s2 - s1).mean(0) / h           # udziały klas i gęstość na 1 m3
            V += n * v
            kl += n * v * fr
        out["budynki"][bnaz] = {"m3": round(V, 3), "klasy_m3": {k: round(float(kl[i]), 3) for i, k in enumerate(D.KLASY)},
                                "masa_t": {"piaski": round(float(kl[-2]), 3), "gliny": round(float(kl[-1]), 3)}}
        out["razem_m3"] += V
        for i, k in enumerate(D.KLASY):
            out["klasy_m3"][k] += float(kl[i])
        out["masa_t"]["piaski"] += float(kl[-2]); out["masa_t"]["gliny"] += float(kl[-1])
    out["razem_m3"] = round(out["razem_m3"], 3)
    out["klasy_m3"] = {k: round(v, 3) for k, v in out["klasy_m3"].items()}
    out["masa_t"] = {k: round(v, 3) for k, v in out["masa_t"].items()}
    return out


if __name__ == "__main__":
    import time
    t0 = time.time()
    w = licz()
    json.dump(w, open(WYN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("czas %.1f s" % (time.time() - t0))
    print("pola:", w["pola"])
    print("humus %.3f m3 (śr. %.3f m), nasyp %.3f m3, teren śr. %s, obiekty za ścianką: %s" % (w["humus_m3"], w["humus_sr_grubosc"], w["nasyp_m3"], w["teren_sr"], w["za_scianka_komorek"]))
    for k, r in w["warianty"].items():
        tot = {z: round(sum(v.values()), 1) for z, v in r["wykop_m3"].items()}
        print("== wariant %s: pole wykopu %.1f m2, śr. głęb. %.2f m; wykop rodzimy wg stref %s; razem %.1f m3; poza działką %s" % (
            k, r["pole_wykopu_razem"], r["glebokosc_sr"], tot, sum(tot.values()), r["wykop_poza_dzialka"]))
        print("   zapotrzebowanie:", {a: {o: round(v, 1) for o, v in b.items()} for a, b in r["zapotrzebowanie"].items()})
        print("   konflikty:", {a: {o: (round(v["m2"], 1), round(v["m3"], 1)) for o, v in b.items()} for a, b in r["konflikty"].items()})
    print("fundamenty głębsze: %.3f m3, klasy %s" % (w["fundamenty"]["razem_m3"], w["fundamenty"]["klasy_m3"]))

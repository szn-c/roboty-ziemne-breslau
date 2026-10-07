"""
GLOWNE OBLICZENIA MAS ZIEMNYCH - dz. 1/90 obr. Wojszyce (Wroclaw).

Wejscie (wszystko w folderze dane/ i w generuj_pliki.py):
  * obrys scianki, 8 hal, granica dzialki  - z WEKTOROWEGO rzutu zabezpieczenia (siatka wspolrzednych projektanta, uklad PL-2000 strefa 6)
  * teren istniejacy EG                    - model z eg_model.py (pomiar z PZT + otwory + siatka 10 m po korekcie)
  * grubosci humusu / nasypu, podzial piasek / glina, zwierciadlo wody - 17 otworow DGI (profile w generuj_pliki.py)
Metoda: raster 0,5 m, objetosc = suma (grubosc warstwy x pole komorki). Humus i nasyp licza sie jako GRUBOSC (nie jako roznica rzednych),
dzieki czemu zaokraglenie rzednych otworow do 0,1 m nie wchodzi do objetosci humusu.
Wyniki: wyniki_bilans.json (czyta je generuj_wynik_xlsx.py)
"""
import json
import math
import os
import sys

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
from scipy.ndimage import distance_transform_edt
from shapely import contains_xy
from shapely.geometry import Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eg_model import geometria, zbuduj  # noqa: E402
from generuj_pliki import OTWORY, W as WARSTWY  # noqa: E402

KAT = os.path.dirname(os.path.abspath(__file__))
DNO = 121.97            # rzedna dna wykopu (chudy beton) = 122,57 - 0,50 - 0,10
CELL = 0.5              # bok komorki rastra [m]
POLE_DZIALKI_OFICJALNE = 25290.00
PRZESTRZEN_ROBOCZA = 1.0  # m od obrysu hali (wariant A i C)
PROG_WARSTWY_SELEKTYWNEJ = 0.5  # m - warstwa piasku cienszza miesza sie z glina przy urabianiu


# ----------------------------------------------------------------------------------------------------------- otwory
def profil_otworu(nr, dno=DNO):
    N, E, H, zw_d, uw = OTWORY[nr]
    war = WARSTWY[nr]
    h = sum(b - t for t, b, k, *_ in war if k == "H")
    n = sum(b - t for t, b, k, *_ in war if k == "N")
    ztop = H - h - n                                   # wierzch gruntu mineralnego
    zw = H - zw_d if zw_d is not None else H - 1.9     # otwor 17: zwierciadlo nawiercone 1,9 m ppt
    col = max(0.0, ztop - dno)
    # odcinki mineralne (wysokosci bezwzgl.), scalamy sasiednie warstwy piaskowe
    odc = []
    for t, b, k, *_ in war:
        if k not in ("G", "P"):
            continue
        hi, lo = min(H - t, ztop), max(H - b, dno)
        if hi <= lo:
            continue
        if odc and odc[-1][2] == k and abs(odc[-1][1] - hi) < 1e-9:
            odc[-1] = (odc[-1][0], lo, k)
        else:
            odc.append((hi, lo, k))
    res = dict(piasek_sel_suchy=0.0, piasek_sel_mokry=0.0, piasek_cienki_suchy=0.0, piasek_cienki_mokry=0.0,
               glina_sucha=0.0, glina_mokra=0.0)

    def dodaj(nazwa, hi, lo):
        suchy = max(0.0, hi - max(lo, zw)) if hi > zw else 0.0      # czesc powyzej zwierciadla
        pelny = hi - lo
        res[nazwa + "_suchy"] += suchy
        res[nazwa + "_mokry"] += pelny - suchy
    for hi, lo, k in odc:
        if k == "G":
            # glina: suche / mokre
            suchy = max(0.0, hi - max(lo, zw)) if hi > zw else 0.0
            res["glina_sucha"] += suchy
            res["glina_mokra"] += (hi - lo) - suchy
        else:
            dodaj("piasek_sel" if (hi - lo) >= PROG_WARSTWY_SELEKTYWNEJ else "piasek_cienki", hi, lo)
    res.update(nr=nr, E=E, N=N, H=H, h=h, n=n, ztop=ztop, zw=zw, col=col)
    s = sum(res[x] for x in ("piasek_sel_suchy", "piasek_sel_mokry", "piasek_cienki_suchy", "piasek_cienki_mokry", "glina_sucha", "glina_mokra"))
    assert abs(s - col) < 1e-6, (nr, s, col)
    return res


# ----------------------------------------------------------------------------------------------------------- pola
class Pola:
    """Interpolacja z 17 otworow: TIN (liniowo) w obrysie otworow + najblizszy poza nim."""
    def __init__(self, prof, metoda="tin"):
        self.P = np.array([(p["E"], p["N"]) for p in prof])
        self.metoda = metoda

    def __call__(self, vals, x, y):
        vals = np.asarray(vals, float)
        if self.metoda == "tin":
            lin = LinearNDInterpolator(self.P, vals)
            z = lin(x, y)
            bad = np.isnan(z)
            if bad.any():
                z[bad] = NearestNDInterpolator(self.P, vals)(x[bad], y[bad])
            return z
        if self.metoda == "nn":
            return NearestNDInterpolator(self.P, vals)(x, y)
        if self.metoda == "idw":
            d2 = (x[:, None] - self.P[None, :, 0]) ** 2 + (y[:, None] - self.P[None, :, 1]) ** 2
            w = 1.0 / (d2 + 25.0)
            return (w * vals[None, :]).sum(1) / w.sum(1)
        raise ValueError(self.metoda)


def licz(metoda_pol="tin", eg_kw=None, dno=DNO, prz_rob=PRZESTRZEN_ROBOCZA, verbose=False):
    W, HALE, PAR = geometria()
    eg, eg_info, _ = zbuduj(**(eg_kw or dict(uzyj_trend=False)))
    prof = [profil_otworu(nr, dno) for nr in OTWORY]
    pola = Pola(prof, metoda_pol)
    # raster w obrysie dzialki + 5 m
    minx, miny, maxx, maxy = PAR.buffer(5).bounds
    xs = np.arange(math.floor(minx) + CELL / 2, maxx, CELL)
    ys = np.arange(math.floor(miny) + CELL / 2, maxy, CELL)
    X, Y = np.meshgrid(xs, ys)
    x, y = X.ravel(), Y.ravel()
    dA = CELL * CELL
    inW = contains_xy(W, x, y)
    inPAR = contains_xy(PAR, x, y)
    hall_union = unary_union(list(HALE.values()))
    inH = contains_xy(hall_union, x, y)
    hallmask = {nr: contains_xy(p, x, y) for nr, p in HALE.items()}
    # pola z otworow
    hum = pola([p["h"] for p in prof], x, y)
    nas = pola([p["n"] for p in prof], x, y)
    zw = pola([p["zw"] for p in prof], x, y)
    EG = eg(x, y)
    S0 = EG - hum - nas                              # wierzch gruntu mineralnego
    # ulamki skladu kolumny gruntu mineralnego (otwor: skladnik / col)
    skl = ("piasek_sel_suchy", "piasek_sel_mokry", "piasek_cienki_suchy", "piasek_cienki_mokry", "glina_sucha", "glina_mokra")
    frac = {}
    for k in skl:
        frac[k] = pola([(p[k] / p["col"]) if p["col"] > 1e-9 else 0.0 for p in prof], x, y)
    tot = sum(frac[k] for k in skl)
    for k in skl:
        frac[k] = frac[k] / tot                       # normalizacja (interpolacja ulamkow zachowuje sume=1, dla pewnosci)

    # odleglosc od hal (wykopy skarpowe C)
    nx, ny = len(xs), len(ys)
    maskH2 = inH.reshape(ny, nx)
    dist_h = distance_transform_edt(~maskH2) * CELL

    def scenariusz(nazwa, maska_wykopu, z_wyk):
        """maska_wykopu - komorki objete wykopem; z_wyk - rzedna powierzchni wykopu (dno lub skarpa)."""
        m = maska_wykopu
        gl = np.where(m, np.maximum(0.0, EG - z_wyk), 0.0)                 # glebokosc od terenu istniejacego
        kol = np.where(m, np.maximum(0.0, S0 - z_wyk), 0.0)                # grunt mineralny pod humusem
        hn = np.where(m, np.minimum(EG - z_wyk, hum + nas), 0.0)
        hn = np.maximum(hn, 0.0)
        out = dict(nazwa=nazwa, pole_wykopu=float(m.sum() * dA),
                   V_brutto=float(gl.sum() * dA), V_humus_nasyp_w_wykopie=float(hn.sum() * dA), V_mineralny=float(kol.sum() * dA),
                   srednia_glebokosc=float(gl[m].mean()) if m.any() else 0.0,
                   srednia_z_wykopu=float(z_wyk[m].mean()) if m.any() else dno,
                   pole_hal_w_wykopie=float(contains_xy(hall_union, x[m], y[m]).sum() * dA) if m.any() else 0.0)
        for k in skl:
            out["V_" + k] = float((kol * frac[k]).sum() * dA)
        # poza wykopem w obrysie scianki: teren podnoszony (nasyp) - potrzebne do zapotrzebowania
        poza = inW & ~m
        out["pole_w_scianie_poza_wykopem"] = float(poza.sum() * dA)
        out["srednia_S0_poza_wykopem"] = float(S0[poza].mean()) if poza.any() else 0.0
        out["srednia_EG_poza_wykopem"] = float(EG[poza].mean()) if poza.any() else 0.0
        return out

    sc = {}
    # B: caly obszar w scianke, do dna
    sc["B"] = scenariusz("B", inW, np.full(x.shape, dno))
    # A: tylko pod halami + przestrzen robocza, ściany pionowe
    kol_hali = unary_union([p.buffer(prz_rob) for p in HALE.values()]).intersection(W)
    inA = contains_xy(kol_hali, x, y)
    sc["A0"] = scenariusz("A0", inA, np.full(x.shape, dno))
    # C: hale + przestrzen robocza, dalej skarpa 1:m, wszystko w obrysie scianki
    for nazwa, m_skarpy in (("C10", 1.0), ("C15", 1.5)):
        d = dist_h.ravel()
        zc = dno + np.maximum(0.0, d - prz_rob) / m_skarpy
        mc = inW & (zc < EG - hum - nas - 1e-9)
        sc[nazwa] = scenariusz(nazwa, mc, zc)
        sc[nazwa]["uwaga"] = f"skarpa 1:{m_skarpy}, przestrzen robocza {prz_rob} m; skladniki gruntu z ulamkow dla pelnej glebokosci (przyblizenie)"

    # strefy humusu
    pole_W = float(inW.sum() * dA)
    poza = inPAR & ~inW
    hum_W = float((hum * inW).sum() * dA)
    nas_W = float((nas * inW).sum() * dA)
    zone = dict(
        pole_scianki_raster=pole_W, pole_scianki_wielokat=float(W.area), obwod_scianki=float(W.length),
        pole_dzialki_rysunek=float(PAR.area), pole_dzialki_oficjalne=POLE_DZIALKI_OFICJALNE,
        pole_poza_scianka_oficjalne=POLE_DZIALKI_OFICJALNE - float(W.area),
        pole_poza_scianka_rysunek=float(poza.sum() * dA),
        humus_w_scianie=hum_W, nasyp_w_scianie=nas_W,
        srednia_grub_humusu_w_scianie=hum_W / pole_W, srednia_grub_nasypu_w_scianie=nas_W / pole_W,
        srednia_grub_humusu_poza=float(hum[poza].mean()), srednia_grub_nasypu_poza=float(nas[poza].mean()),
        srednia_EG_w_scianie=float(EG[inW].mean()), srednia_EG_poza=float(EG[poza].mean()),
        srednia_S0_poza=float(S0[poza].mean()),
        pola_hal={int(nr): float(p.area) for nr, p in HALE.items()}, suma_hal=float(sum(p.area for p in HALE.values())),
    )
    zone["humus_poza_scianka"] = zone["srednia_grub_humusu_poza"] * zone["pole_poza_scianka_oficjalne"]
    zone["nasyp_poza_scianka"] = zone["srednia_grub_nasypu_poza"] * zone["pole_poza_scianka_oficjalne"]
    zone["humus_razem"] = zone["humus_w_scianie"] + zone["humus_poza_scianka"]
    zone["nasyp_razem"] = zone["nasyp_w_scianie"] + zone["nasyp_poza_scianka"]
    zone["pole_W_minus_hale"] = pole_W - float(inH[inW].sum() * dA)
    res = dict(DNO=dno, CELL=CELL, eg_info=eg_info, zone=zone, scenariusze=sc,
               otwory=[{k: (float(v) if not isinstance(v, (int, str)) else v) for k, v in p.items()} for p in prof])
    if verbose:
        print(json.dumps(res["zone"], indent=1, ensure_ascii=False))
    return res, dict(x=x, y=y, EG=EG, hum=hum, nas=nas, inW=inW, inH=inH, S0=S0, zw=zw, frac=frac)


if __name__ == "__main__":
    res, _ = licz(verbose=False)
    with open(os.path.join(KAT, "wyniki_bilans.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    z = res["zone"]
    print("Pole scianki: raster %.1f, wielokat %.1f, obwod %.1f" % (z["pole_scianki_raster"], z["pole_scianki_wielokat"], z["obwod_scianki"]))
    print("Hale razem %.1f m2 ; teren w scianie poza halami %.1f m2" % (z["suma_hal"], z["pole_W_minus_hale"]))
    print("Dzialka: rysunek %.0f, oficjalnie %.0f, poza scianka (oficj.) %.0f" % (z["pole_dzialki_rysunek"], z["pole_dzialki_oficjalne"], z["pole_poza_scianka_oficjalne"]))
    print("Humus: w scianie %.0f (sr. %.3f m), poza scianka %.0f (sr. %.3f m), RAZEM %.0f m3" % (z["humus_w_scianie"], z["srednia_grub_humusu_w_scianie"], z["humus_poza_scianka"], z["srednia_grub_humusu_poza"], z["humus_razem"]))
    print("Nasyp: w scianie %.0f, poza %.0f, RAZEM %.0f m3" % (z["nasyp_w_scianie"], z["nasyp_poza_scianka"], z["nasyp_razem"]))
    print("EG srednia: w scianie %.3f ; poza %.3f" % (z["srednia_EG_w_scianie"], z["srednia_EG_poza"]))
    for nazwa, s in res["scenariusze"].items():
        print("\n== %s: pole wykopu %.0f m2, sr. glebokosc %.2f m, V brutto %.0f, humus+nasyp w wykopie %.0f, grunt mineralny %.0f" % (nazwa, s["pole_wykopu"], s["srednia_glebokosc"], s["V_brutto"], s["V_humus_nasyp_w_wykopie"], s["V_mineralny"]))
        print("   piasek selekt. suchy %.0f, mokry %.0f ; piasek cienki %.0f ; glina sucha %.0f, mokra %.0f" % (s["V_piasek_sel_suchy"], s["V_piasek_sel_mokry"], s["V_piasek_cienki_suchy"] + s["V_piasek_cienki_mokry"], s["V_glina_sucha"], s["V_glina_mokra"]))

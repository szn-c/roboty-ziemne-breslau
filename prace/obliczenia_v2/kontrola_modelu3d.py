"""
NIEZALEŻNA KONTROLA MODELU 3D – czyta zapisane pliki (LandXML i DXF), nie dane z pamięci:
  - struktura LandXML (kolejność N E Z, numeracja, indeksy trójkątów, orientacja, brak powtórzonych punktów),
  - zgodność DXF z LandXML (liczba i położenie trójkątów na warstwach 3D_*),
  - spójność siatki (krawędzie brzegowe = obwód działki, suma pól trójkątów = pole działki),
  - objętości wykopu liczone z plików (rasteryzacja trójkątów) i porównanie z bilansem (wyniki.json).
Uruchomienie: python kontrola_modelu3d.py
"""
import json
import math
import os
import re
import time
import xml.etree.ElementTree as ET

import ezdxf
import numpy as np
from shapely.geometry import Polygon

import dane as D
import model3d as M
import silnik as S

HERE = os.path.dirname(os.path.abspath(__file__))


def czytaj_landxml(sciezka):
    ns = {"l": "http://www.landxml.org/schema/LandXML-1.2"}
    root = ET.parse(sciezka).getroot()
    out = {}
    for s in root.find("l:Surfaces", ns):
        d = s.find("l:Definition", ns)
        pts = []
        for p in d.find("l:Pnts", ns):
            pts.append((int(p.attrib["id"]), *map(float, p.text.split())))
        faces = [tuple(map(int, f.text.split())) for f in d.find("l:Faces", ns)]
        out[s.attrib["name"]] = (np.array(pts), np.array(faces))
    return out


def rasteryzuj(P, F, xs, ys, off):
    """Wartość Z trójkątów w środkach komórek rastra (NaN poza siatką) – bez bibliotek triangulacyjnych."""
    Z = np.full((len(ys), len(xs)), np.nan)
    cell = xs[1] - xs[0]
    x0, y0 = xs[0], ys[0]
    A = P[F]                                        # (n, 3, 3)
    for tri in A:
        (xa, ya, za), (xb, yb, zb), (xc, yc, zc) = tri
        i0 = int(math.floor((min(xa, xb, xc) - x0) / cell)); i1 = int(math.ceil((max(xa, xb, xc) - x0) / cell))
        j0 = int(math.floor((min(ya, yb, yc) - y0) / cell)); j1 = int(math.ceil((max(ya, yb, yc) - y0) / cell))
        i0, j0 = max(i0, 0), max(j0, 0)
        i1, j1 = min(i1, len(xs) - 1), min(j1, len(ys) - 1)
        if i1 < i0 or j1 < j0:
            continue
        gx, gy = np.meshgrid(xs[i0:i1 + 1], ys[j0:j1 + 1])
        det = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
        if abs(det) < 1e-12:
            continue
        l1 = ((yb - yc) * (gx - xc) + (xc - xb) * (gy - yc)) / det
        l2 = ((yc - ya) * (gx - xc) + (xa - xc) * (gy - yc)) / det
        l3 = 1 - l1 - l2
        inside = (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
        z = l1 * za + l2 * zb + l3 * zc
        sub = Z[j0:j1 + 1, i0:i1 + 1]
        sub[inside] = z[inside]
    return Z


def main():
    t0 = time.time()
    geo = json.load(open(os.path.join(D.DANE, "geometria.json"), encoding="utf-8"))
    G = Polygon(geo["granica"])
    surf = czytaj_landxml(M.WY_XML)
    wyn = {"plik_LandXML": os.path.basename(M.WY_XML), "plik_DXF": os.path.basename(M.WY_DXF), "powierzchnie": {}, "uwagi": []}
    ok_all = True
    for nazwa, (Pn, F) in surf.items():
        ids = Pn[:, 0].astype(int)
        N, E, Zv = Pn[:, 1], Pn[:, 2], Pn[:, 3]
        P = np.column_stack([E, N, Zv])               # LandXML: północ wschód rzędna -> x y z
        r = {}
        r["kolejnosc_N_E_Z_ok"] = bool(N.min() > 5.0e6 and E.min() > 6.0e6 and Zv.max() < 200)
        r["numeracja_ok"] = bool((ids == np.arange(1, len(ids) + 1)).all())
        Fi = F - 1
        r["indeksy_ok"] = bool(Fi.min() >= 0 and Fi.max() < len(P))
        a, b, c = P[Fi[:, 0], :2], P[Fi[:, 1], :2], P[Fi[:, 2], :2]
        cr = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
        r["trojkaty_ccw_ok"] = bool((cr > 0).all())
        r["najmniejsze_pole_trojkata_m2"] = round(float(cr.min() / 2), 6)
        r["punkty_unikalne_ok"] = bool(len(np.unique(np.round(P[:, :2], 3), axis=0)) == len(P))
        r["suma_pol_trojkatow_m2"] = round(float(cr.sum() / 2), 2)
        r["pole_dzialki_m2"] = round(G.area, 2)
        r["roznica_pola_m2"] = round(float(cr.sum() / 2 - G.area), 2)
        # krawędzie brzegowe
        kraw = {}
        for t in Fi:
            for u, v in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                k = (min(u, v), max(u, v))
                kraw[k] = kraw.get(k, 0) + 1
        r["krawedzie_ponad_2_trojkaty"] = int(sum(1 for v in kraw.values() if v > 2))
        brzeg = [k for k, v in kraw.items() if v == 1]
        r["dlugosc_krawedzi_brzegowych_m"] = round(float(sum(math.dist(P[u, :2], P[v, :2]) for u, v in brzeg)), 2)
        r["obwod_dzialki_m"] = round(G.length, 2)
        r["liczba_punktow"], r["liczba_trojkatow"] = int(len(P)), int(len(F))
        r["Z_min"], r["Z_max"] = round(float(Zv.min()), 3), round(float(Zv.max()), 3)
        ok = all([r["kolejnosc_N_E_Z_ok"], r["numeracja_ok"], r["indeksy_ok"], r["trojkaty_ccw_ok"], r["punkty_unikalne_ok"], r["krawedzie_ponad_2_trojkaty"] == 0,
                  abs(r["roznica_pola_m2"]) < 5.0, abs(r["dlugosc_krawedzi_brzegowych_m"] - r["obwod_dzialki_m"]) < 0.5 * r["obwod_dzialki_m"] * 0.05])
        r["ok"] = bool(ok)
        ok_all &= ok
        wyn["powierzchnie"][nazwa] = r
        print("%-30s pkt %6d trójk. %6d | pole %.2f (działka %.2f) | brzeg %.1f m (obwód %.1f) | CCW %s | %s" % (
            nazwa, len(P), len(F), r["suma_pol_trojkatow_m2"], r["pole_dzialki_m2"], r["dlugosc_krawedzi_brzegowych_m"], r["obwod_dzialki_m"], r["trojkaty_ccw_ok"], "OK" if ok else "BŁĄD"))
    # --- DXF vs LandXML
    doc = ezdxf.readfile(M.WY_DXF)
    aud = doc.audit()
    wyn["audyt_DXF_bledy"] = len(aud.errors)
    msp = doc.modelspace()
    for klucz, nazwa, warstwa, kol, opis in M.POWIERZCHNIE:
        P, F = surf[nazwa]
        faces = list(msp.query('3DFACE[layer=="%s"]' % warstwa))
        from scipy.spatial import cKDTree
        drzewo = cKDTree(np.column_stack([P[:, 2], P[:, 1], P[:, 3]]) - np.array([6.4e6, 5.6e6, 0]))
        dxf_v = np.array([tuple(e.dxf.vtx0) for e in faces]) - np.array([6.4e6, 5.6e6, 0])
        wspolne = float((drzewo.query(dxf_v)[0] < 0.001).mean())
        zgodne = (len(faces) == len(F)) and wspolne > 0.999
        wyn["powierzchnie"][nazwa]["dxf_trojkaty"] = len(faces)
        wyn["powierzchnie"][nazwa]["dxf_zgodny_z_landxml"] = bool(zgodne)
        ok_all &= zgodne
        print("DXF %-26s 3DFACE %6d (LandXML %6d) zgodność wierzchołków %.4f -> %s" % (warstwa, len(faces), len(F), wspolne, "OK" if zgodne else "BŁĄD"))
    # --- objętości z plików
    w, gm = S.licz(zapisz_geometrie=True)
    sg = gm["_siatka"]
    xs, ys, shape, cell = sg["xs"], sg["ys"], sg["shape"], sg["cell"]
    inG = sg["inG"].reshape(shape)
    Ac = cell * cell
    Zr = {}
    for klucz, nazwa, warstwa, kol, opis in M.POWIERZCHNIE:
        Pn, F = surf[nazwa]
        P = np.column_stack([Pn[:, 2], Pn[:, 1], Pn[:, 3]])
        Zr[klucz] = rasteryzuj(P, F - 1, xs, ys, None)
        print("  rasteryzacja %-30s %.0f s, komórek bez wartości w obrębie działki: %d" % (nazwa, time.time() - t0, int((inG & ~np.isfinite(Zr[klucz])).sum())))
        wyn["powierzchnie"][nazwa]["komorki_bez_wartosci_w_dzialce"] = int((inG & ~np.isfinite(Zr[klucz])).sum())
    wyn["objetosci"] = {}
    for k in ("A", "B"):
        d = np.where(inG, Zr["hum"] - Zr[k], 0.0)
        cut = float(np.nansum(np.clip(d, 0, None)) * Ac)
        fill = float(np.nansum(np.clip(-d, 0, None)) * Ac)
        bilans = float(sum(sum(v.values()) for v in w["warianty"][k]["wykop_m3"].values()))
        wyn["objetosci"][k] = {"wykop_z_plikow_m3": round(cut, 3), "wykop_bilans_m3": round(bilans, 3), "roznica_m3": round(cut - bilans, 3),
                               "roznica_proc": round(100 * (cut - bilans) / bilans, 4), "nasyp_ponad_teren_po_humusie_m3": round(fill, 3)}
        print("Objętość wykopu %s z plików: %.3f m3, bilans %.3f m3, różnica %.3f m3 (%.4f%%); powierzchnia po wykopie ponad terenem po humusie: %.3f m3" % (
            k, cut, bilans, cut - bilans, 100 * (cut - bilans) / bilans, fill))
    d = np.where(inG, Zr["ist"] - Zr["hum"], 0.0)
    wyn["objetosci"]["humus_i_nasyp"] = {"z_plikow_m3": round(float(np.nansum(d) * Ac), 3), "bilans_m3": round(w["humus_m3"] + w["nasyp_m3"], 3)}
    print("Humus + nasyp z plików: %.3f m3, bilans %.3f m3" % (wyn["objetosci"]["humus_i_nasyp"]["z_plikow_m3"], wyn["objetosci"]["humus_i_nasyp"]["bilans_m3"]))
    prog = 0.002 * 34000                             # 0,2% – dopuszczalna różnica między TIN a rastrem bilansu
    wyn["objetosci_ok"] = bool(all(abs(wyn["objetosci"][k]["roznica_m3"]) < prog for k in ("A", "B")))
    wyn["wynik"] = "OK" if (ok_all and wyn["objetosci_ok"] and wyn["audyt_DXF_bledy"] == 0) else "BŁĄD"
    print("WYNIK KONTROLI:", wyn["wynik"], "| audyt DXF: błędów", wyn["audyt_DXF_bledy"])
    kont = json.load(open(M.WY_KONTROLA, encoding="utf-8")) if os.path.exists(M.WY_KONTROLA) else {}
    kont["kontrola_niezalezna"] = wyn
    json.dump(kont, open(M.WY_KONTROLA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

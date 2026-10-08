"""
Kontrola geometrii użytkownika (*_checked) i położenia otworów.
Uruchom: python prace/weryfikacja/geometria_kontrola.py
Wynik na ekran + prace/weryfikacja/geometria_kontrola.json
"""
import json
import math
import os

import ezdxf
from shapely.geometry import LineString, Point, Polygon

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DU = os.path.join(REPO, "prace", "dane_wejsciowe_uzytkownika")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geometria_kontrola.json")


def wczytaj_pary(sciezka):
    pts = []
    for line in open(sciezka, encoding="utf-8"):
        p = line.split()
        if len(p) == 2:
            pts.append((float(p[0]), float(p[1])))
    return pts


def wczytaj_hale(sciezka):
    hale, nazwa = {}, None
    for line in open(sciezka, encoding="utf-8"):
        s = line.strip()
        if not s:
            continue
        if s.lower().startswith("hala"):
            nazwa = int(s[4:])
            hale[nazwa] = []
        else:
            e, n = map(float, s.split())
            hale[nazwa].append((e, n))
    return hale


# otwory DGI (karta informacyjna): nr -> (N=X, E=Y, H). Otwór 12: Y w źródle "643368,27" (uszkodzone)
OTWORY = {
    2: (5659002.2, 6433708.7, 124.70), 3: (5658972.6, 6433724.8, 124.80), 5: (5658920.1, 6433702.7, 125.00),
    7: (5658896.4, 6433678.7, 125.10), 9: (5658957.0, 6433679.0, 124.80), 10: (5658984.4, 6433680.5, 124.50),
    11: (5659015.9, 6433664.4, 124.40), 12: (5659037.4, None, 124.50), 14: (5659030.6, 6433620.1, 124.30),
    15: (5659002.8, 6433635.2, 124.30), 16: (5658980.3, 6433637.0, 124.60), 17: (5658959.8, 6433615.8, 124.80),
    18: (5658918.4, 6433636.0, 124.90), 20: (5658966.0, 6433587.1, 124.60), 21: (5658993.0, 6433578.9, 124.80),
    23: (5659037.1, 6433583.4, 124.50), 24: (5659055.7, 6433603.9, 124.40), 25: (5659058.6, 6433539.1, 124.40),
    26: (5659028.4, 6433553.7, 124.60), 27: (5659007.0, 6433529.5, 124.70), 29: (5658974.5, 6433530.1, 124.70),
    31: (5658968.6, 6433499.1, 125.00), 32: (5658995.0, 6433475.4, 124.90), 33: (5659013.3, 6433504.6, 124.80),
    36: (5659066.5, 6433470.2, 124.60), 38: (5659054.4, 6433439.8, 124.80), 39: (5659038.5, 6433412.3, 124.80),
    40: (5659026.3, 6433448.0, 124.90),
}
E12_KANDYDACI = {"6433682,7 (przesunięty przecinek)": 6433682.7, "6433688,2 (przyjęte w v1)": 6433688.2}


def main():
    wynik = {}
    hale = wczytaj_hale(os.path.join(DU, "wierzcholki_polilinii_hala1-8_checked.txt"))
    sc = wczytaj_pary(os.path.join(DU, "wierzcholki_polilinii_wykop_checked.txt"))
    gr = wczytaj_pary(os.path.join(DU, "wierzcholki_polilinii_granica_działki_checked.txt"))
    P_gr = Polygon(gr)
    P_sc = Polygon(sc)
    L_sc_otw = LineString(sc)  # ścianka bez odcinka zamykającego
    zamk = LineString([sc[-1], sc[0]])
    print("=== GRANICA: wierzchołków %d, pole %.2f m2, obwód %.2f m, poprawna=%s" % (len(gr), P_gr.area, P_gr.length, P_gr.is_valid))
    print("    różnica do pola oficjalnego 25 290,00: %.2f m2 (%.2f%%)" % (P_gr.area - 25290, (P_gr.area / 25290 - 1) * 100))
    print("=== ŚCIANKA: wierzchołków %d, pole po domknięciu %.2f m2, obwód domknięty %.2f m, długość linii otwartej %.2f m"
          % (len(sc), P_sc.area, P_sc.length, L_sc_otw.length))
    print("    odcinek zamykający: %.2f m, od (%.3f, %.3f) do (%.3f, %.3f)" % (zamk.length, *sc[-1], *sc[0]))
    print("    ścianka w granicy działki: %s; wystaje poza granicę: %.2f m2" % (P_gr.contains(P_sc), P_sc.difference(P_gr).area))
    wynik["granica"] = {"pole": round(P_gr.area, 2), "obwod": round(P_gr.length, 2)}
    wynik["scianka"] = {"pole_domkniete": round(P_sc.area, 2), "obwod_domkniety": round(P_sc.length, 2),
                        "dlugosc_otwarta": round(L_sc_otw.length, 2), "zamykajacy": round(zamk.length, 2)}
    suma = 0
    wynik["hale"] = {}
    print("=== HALE")
    for nr, pts in hale.items():
        P = Polygon(pts)
        suma += round(P.area, 2)
        boki = [math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
        az = math.degrees(math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0]))
        d_sc = P.exterior.distance(L_sc_otw)
        w_sc = P_sc.contains(P)
        poza = P.difference(P_sc).area
        przecina_zamk = P.intersects(zamk)
        w_gr = P_gr.contains(P)
        d_gr = P.exterior.distance(P_gr.exterior)
        print("  hala %d: wierzch. %d, pole %.2f, boki %s, kier. 1. boku %.2f°, min. odl. do ścianki %.2f m, "
              "w ściance=%s (poza: %.2f m2), przecina odcinek zamykający=%s, w granicy=%s, min. odl. do granicy %.2f m"
              % (nr, len(pts), P.area, "/".join("%.2f" % b for b in boki), az, d_sc, w_sc, poza, przecina_zamk, w_gr, d_gr))
        wynik["hale"][nr] = {"pole": round(P.area, 2), "odl_scianka": round(d_sc, 2), "poza_scianka_m2": round(poza, 2),
                             "przecina_zamykajacy": przecina_zamk, "odl_granica": round(d_gr, 2)}
    print("  RAZEM hale: %.2f m2" % suma)
    # nakładanie hal
    for a in hale:
        for b in hale:
            if a < b and Polygon(hale[a]).intersects(Polygon(hale[b])):
                print("  UWAGA: hale %d i %d nachodzą na siebie: %.2f m2" % (a, b, Polygon(hale[a]).intersection(Polygon(hale[b])).area))
    # porównanie z odczytem z rysunku projektanta (v1)
    g = json.load(open(os.path.join(REPO, "prace/obliczenia_v1/_skrypt/dane/geometria_G.json")))
    print("=== PORÓWNANIE z rysunkiem projektanta (v1, geometria_G.json)")
    for k, v in g["hale"].items():
        Pp, Pu = Polygon(v), Polygon(hale[int(k)])
        print("  hala %s: pole proj. %.2f vs użytk. %.2f (%+.2f%%), przesunięcie środka %.2f m, część wspólna %.1f%%"
              % (k, Pp.area, Pu.area, (Pu.area / Pp.area - 1) * 100, Pp.centroid.distance(Pu.centroid),
                 Pp.intersection(Pu).area / Pp.union(Pu).area * 100))
    Ps = Polygon(g["scianka"])
    print("  ścianka: proj. %.2f m2 / obwód %.2f vs użytk. %.2f / %.2f; część wspólna/suma %.1f%%; maks. odl. wierzchołków użytk. od linii proj. %.2f m"
          % (Ps.area, Ps.length, P_sc.area, P_sc.length, Ps.intersection(P_sc).area / Ps.union(P_sc).area * 100,
             max(Point(p).distance(Ps.exterior) for p in sc)))
    Pd = Polygon(g["dzialka"])
    print("  granica: proj. %.2f vs użytk. %.2f; maks. odl. wierzchołków użytk. od granicy proj. %.2f m"
          % (Pd.area, P_gr.area, max(Point(p).distance(Pd.exterior) for p in gr)))
    # zgodność plików txt z DXF
    print("=== ZGODNOŚĆ z DXF użytkownika")
    doc = ezdxf.readfile(os.path.join(DU, "siatka_10m_dz190_checked.dxf"))
    msp = doc.modelspace()
    for warstwa in ("HALE_GARAZOWE", "7_SCIANKA_ORIENTACYJNA", "A-granica inwest."):
        pl = [e for e in msp if e.dxf.layer == warstwa and e.dxftype() in ("LWPOLYLINE", "POLYLINE")]
        opis = []
        for e in pl:
            pts = [(p[0], p[1]) for p in (e.get_points("xy") if e.dxftype() == "LWPOLYLINE" else [v.dxf.location for v in e.vertices])]
            opis.append("%d wierzch.%s" % (len(pts), " zamknięta" if e.closed else " otwarta"))
        print("  %s: %d polilinii: %s" % (warstwa, len(pl), ", ".join(opis)))
    # otwory
    print("=== OTWORY względem granicy 1/90, ścianki i hal")
    wynik["otwory"] = {}
    for nr, (N, E, H) in OTWORY.items():
        if E is None:
            for opis, E12 in E12_KANDYDACI.items():
                p = Point(E12, N)
                print("  otwór 12 [%s]: w działce=%s, w ściance=%s, hala=%s, odl. od granicy %.1f m" %
                      (opis, P_gr.contains(p), P_sc.contains(p), [k for k, v in hale.items() if Polygon(v).contains(p)],
                       p.distance(P_gr.exterior)))
            continue
        p = Point(E, N)
        wd = P_gr.contains(p)
        wynik["otwory"][nr] = {"w_dzialce": wd, "w_sciance": P_sc.contains(p)}
        print("  otwór %2d: w działce=%-5s w ściance=%-5s hala=%s, odl. od granicy %.1f m" %
              (nr, wd, P_sc.contains(p), [k for k, v in hale.items() if Polygon(v).contains(p)], p.distance(P_gr.exterior)))
    json.dump(wynik, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

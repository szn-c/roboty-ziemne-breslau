"""
Kontrola DXF użytkownika v2 (siatka_10m_dz190_checked_v2.dxf):
- hale, granica, ścianka: porównanie z v1 (*_checked) i z geometrią skorygowaną do PZT (transformacja_uzytk_do_PZT.json),
- zieleń na gruncie / na stropie: zamknięcie, poprawność, pola, nakładanie, położenie względem hal i granicy,
  porównanie z tabelą "Bilans terenu" PZT.
Uruchom: python prace/weryfikacja/kontrola_dxf_v2.py   (wynik: ekran + kontrola_dxf_v2.json)
"""
import json
import math
import os

import ezdxf
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DU = os.path.join(REPO, "prace", "dane_wejsciowe_uzytkownika")
V1 = os.path.join(DU, "siatka_10m_dz190_checked.dxf")
V2 = os.path.join(DU, "siatka_10m_dz190_checked_v2.dxf")


def polilinie(msp, warstwa):
    out = []
    for e in msp:
        if e.dxf.layer != warstwa or e.dxftype() not in ("LWPOLYLINE", "POLYLINE"):
            continue
        if e.dxftype() == "LWPOLYLINE":
            pts = [(float(p[0]), float(p[1])) for p in e.get_points("xy")]
            bul = any(abs(p[4]) > 1e-9 for p in e.get_points("xyseb"))
        else:
            pts = [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in e.vertices]
            bul = any(abs(v.dxf.bulge) > 1e-9 for v in e.vertices)
        zamk = bool(e.closed) or (len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6)
        if zamk and math.dist(pts[0], pts[-1]) < 1e-6:
            pts = pts[:-1]
        out.append({"pts": pts, "zamknieta": zamk, "luki": bul, "handle": e.dxf.handle})
    return out


def main():
    m1 = ezdxf.readfile(V1).modelspace()
    m2 = ezdxf.readfile(V2).modelspace()
    T = json.load(open(os.path.join(HERE, "transformacja_uzytk_do_PZT.json")))
    wynik = {}
    # ---------------- hale
    h1 = [Polygon(p["pts"]) for p in polilinie(m1, "HALE_GARAZOWE")]
    h2l = polilinie(m2, "HALE_GARAZOWE")
    h2 = [Polygon(p["pts"]) for p in h2l]
    hT = {int(k): Polygon(v) for k, v in T["hale_po"].items()}
    print("=== HALE (v2): %d polilinii, zamknięte: %s, łuki: %s" % (len(h2), all(p["zamknieta"] for p in h2l), any(p["luki"] for p in h2l)))
    wynik["hale"] = {}
    for P in sorted(h2, key=lambda g: (-g.centroid.y // 40, g.centroid.x)):
        nr = min(hT, key=lambda k: hT[k].centroid.distance(P.centroid))
        Q = hT[nr]
        P1 = min(h1, key=lambda g: g.centroid.distance(P.centroid))
        maxd = max(Point(p).distance(Q.exterior) for p in P.exterior.coords)
        print("  hala %d: wierzch. %d, pole v2 %.2f | v1 %.2f | wg korekty do PZT %.2f ; przesunięcie środka v2–korekta %.3f m, "
              "maks. odl. wierzchołków v2 od obrysu po korekcie %.3f m" % (nr, len(P.exterior.coords) - 1, P.area, P1.area, Q.area,
                                                                             P.centroid.distance(Q.centroid), maxd))
        wynik["hale"][nr] = {"pole_v2": round(P.area, 2), "pole_korekta": round(Q.area, 2), "maks_odl": round(maxd, 3)}
    print("  RAZEM v2 %.2f | v1 %.2f | korekta %.2f" % (sum(p.area for p in h2), sum(p.area for p in h1), sum(p.area for p in hT.values())))
    # ---------------- granica
    g1 = polilinie(m1, "A-granica inwest.")[0]
    g2 = polilinie(m2, "A-granica inwest.")[0]
    G2, G1, GT = Polygon(g2["pts"]), Polygon(g1["pts"]), Polygon(T["granica_po"])
    print("=== GRANICA v2: wierzch. %d, zamknięta %s, pole %.2f (v1 %.2f, korekta %.2f, oficjalnie 25 290,00); maks. odl. wierzchołków v2 od granicy po korekcie %.3f m" % (
        len(g2["pts"]), g2["zamknieta"], G2.area, G1.area, GT.area, max(Point(p).distance(GT.exterior) for p in g2["pts"])))
    wynik["granica"] = {"pole_v2": round(G2.area, 2), "wierzcholki": g2["pts"]}
    # ---------------- ścianka
    s1 = polilinie(m1, "7_SCIANKA_ORIENTACYJNA")
    s2 = polilinie(m2, "7_SCIANKA_ORIENTACYJNA")
    print("=== ŚCIANKA v1: %s ; v2: %s" % ([len(p["pts"]) for p in s1], [len(p["pts"]) for p in s2]))
    sT = T["scianka_po"]
    for p in s2:
        L = LineString(p["pts"])
        same_v1 = [max(math.dist(a, b) for a, b in zip(p["pts"], q["pts"])) for q in s1 if len(q["pts"]) == len(p["pts"])]
        same_T = max(math.dist(a, b) for a, b in zip(p["pts"], sT)) if len(p["pts"]) == len(sT) else None
        print("  v2: %d wierzch., zamknięta %s, długość %.2f m; maks. różnica wierzchołków do v1 %s m; do ścianki po korekcie %s m" % (
            len(p["pts"]), p["zamknieta"], L.length, ["%.3f" % x for x in same_v1], "%.3f" % same_T if same_T is not None else "-"))
        wynik["scianka_v2"] = p["pts"]
    # ---------------- zieleń
    for warstwa, bilans in (("ZIELEN-NA-GRUNCIE", "6 443,06 (zieleń na gruncie rodzimym)"), ("ZIELEN-NA-STROPIE", "3 575,11 w tabeli / 3 975,11 z domknięcia")):
        pl = polilinie(m2, warstwa)
        polys, bledy = [], []
        for p in pl:
            if not p["zamknieta"]:
                bledy.append("otwarta (%d wierzch.)" % len(p["pts"]))
            if p["luki"]:
                bledy.append("ma łuki")
            P = Polygon(p["pts"])
            if not P.is_valid:
                bledy.append("niepoprawna (samoprzecięcie) pole %.2f" % P.area)
                P = P.buffer(0)
            polys.append(P)
        U = unary_union(polys)
        suma = sum(p.area for p in polys)
        H2 = unary_union(h2)
        print("=== %s: %d polilinii; suma pól %.2f m2; pole sumy (bez nakładania) %.2f m2; nakładanie %.2f m2 ; Bilans terenu PZT: %s" % (
            warstwa, len(pl), suma, U.area, suma - U.area, bilans))
        print("    błędy: %s" % (bledy if bledy else "brak"))
        print("    w obrysach hal: %.2f m2; poza halami: %.2f m2; poza granicą działki: %.2f m2" % (U.intersection(H2).area, U.difference(H2).area, U.difference(G2).area))
        pola = sorted([round(p.area, 2) for p in polys], reverse=True)
        print("    pola polilinii: %s" % pola)
        wynik[warstwa] = {"n": len(pl), "suma": round(suma, 2), "pole_sumy": round(U.area, 2), "w_halach": round(U.intersection(H2).area, 2),
                          "poza_halami": round(U.difference(H2).area, 2), "poza_granica": round(U.difference(G2).area, 2), "bledy": bledy}
    json.dump(wynik, open(os.path.join(HERE, "kontrola_dxf_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

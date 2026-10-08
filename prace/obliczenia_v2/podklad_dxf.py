"""
NOWY PODKŁAD DXF (v3) dla GstarCAD: plik użytkownika v2 + korekta geometrii do PZT + strefy i obrysy wykopów z obliczeń.
- warstwy użytkownika HALE_GARAZOWE, A-granica inwest., 7_SCIANKA_ORIENTACYJNA, ZIELEN-NA-GRUNCIE, ZIELEN-NA-STROPIE:
  przeliczone do PZT (skala 1,003663, obrót −0,0017°, przesunięcie ok. 0,7 m) – te same obiekty, poprawione położenie;
- stare warstwy wstępnej siatki (0_…8_) – wyłączone (nie usunięte);
- nowe warstwy BILANS_* – strefy z wektorowego PZT, rampy, zadaszone dojazdy, nasyp (mapa 4.3), otwory, obrysy wykopów A i B.
Wynik: wyniki/PODKLAD_dz190_v3.dxf
"""
import json
import math
import os

import ezdxf
import numpy as np
from shapely import wkt
from shapely.geometry import Polygon
from shapely.ops import unary_union

import dane as D
import silnik as S

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WY = os.path.join(REPO, "wyniki", "PODKLAD_dz190_v3.dxf")
WARSTWY_USER = ("HALE_GARAZOWE", "A-granica inwest.", "7_SCIANKA_ORIENTACYJNA", "ZIELEN-NA-GRUNCIE", "ZIELEN-NA-STROPIE")
STARE = ("0_SIATKA_10m", "1_WEZLY", "2_RZEDNE_TERENU", "3_GLEBOKOSC_WYKOPU", "4_HUMUS_m", "5_OTWORY", "6_KRZYZE_50m_DO_DOPASOWANIA", "8_OZNACZENIA_SIATKI")
NOWE = {  # nazwa: (kolor ACI, opis)
    "BILANS_ZIELEN_NA_GRUNCIE_PZT": (3, "zieleń na gruncie rodzimym – wypełnienie PZT (strefa Z)"),
    "BILANS_ZIELEN_NA_STROPIE_PZT": (92, "zieleń na stropie garażu – wypełnienie PZT"),
    "BILANS_ZADASZONE_DOJAZDY": (30, "zieleń na stropie poza obrysami hal = zadaszone dojazdy (strefa hal)"),
    "BILANS_OGRODY_DESZCZOWE": (4, "ogrody deszczowe (jak hale)"),
    "BILANS_RAMPY": (1, "pochylnie z murami (strefa R); strzałka: dół rampy"),
    "BILANS_NASYP_mapa_4.3": (6, "strefy nasypu niekontrolowanego z mapy 4.3 DGI"),
    "BILANS_OTWORY_1-90": (30, "otwory 2–24 i CPTU 10, 12, 18, 21, 24 (DGI)"),
    "BILANS_SCIANKA_ZAMKNIECIE": (8, "odcinek między końcami ścianki (podnóże skarpy od południa w wariancie B) – nie jest ścianką"),
    "BILANS_WYKOP_A_DNO": (5, "wariant A – krawędź dna wykopu 121,86 (obiekty + przestrzeń robocza 1,0 m)"),
    "BILANS_WYKOP_A_GORA": (150, "wariant A – górna krawędź skarp 1:1,5 (na terenie po zdjęciu humusu)"),
    "BILANS_WYKOP_B_DNO": (210, "wariant B – krawędź dna wykopu 121,86"),
    "BILANS_WYKOP_B_GORA": (230, "wariant B – górna krawędź wykopu"),
    "BILANS_OPISY": (7, "opisy i legenda"),
}


def main():
    T, f = D.transformacja()
    doc = ezdxf.readfile(D.V2)
    msp = doc.modelspace()
    # 1) korekta warstw użytkownika
    n = 0
    for e in msp:
        if e.dxf.layer not in WARSTWY_USER:
            continue
        if e.dxftype() == "LWPOLYLINE":
            pts = list(e.get_points("xyseb"))
            xy = f([(p[0], p[1]) for p in pts])
            e.set_points([(xy[i][0], xy[i][1], p[2], p[3], p[4]) for i, p in enumerate(pts)], format="xyseb")
            n += 1
        elif e.dxftype() in ("MTEXT", "TEXT"):
            p = e.dxf.insert
            q = f([(p.x, p.y)])[0]
            e.dxf.insert = (q[0], q[1], p.z)
            n += 1
    # 2) stare warstwy – wyłączone
    for nazwa in STARE:
        if nazwa in doc.layers:
            doc.layers.get(nazwa).off()
    # 3) nowe warstwy
    for nazwa, (kol, opis) in NOWE.items():
        if nazwa not in doc.layers:
            doc.layers.add(nazwa, color=kol)
        doc.layers.get(nazwa).description = opis
    st = json.load(open(os.path.join(D.DANE, "strefy.json"), encoding="utf-8"))
    geo = json.load(open(os.path.join(D.DANE, "geometria.json"), encoding="utf-8"))

    def rysuj(g, warstwa, minpole=0.5):
        gs = list(g.geoms) if hasattr(g, "geoms") else [g]
        k = 0
        for p in gs:
            if p.geom_type != "Polygon" or p.area < minpole:
                continue
            for ring in [p.exterior] + list(p.interiors):
                msp.add_lwpolyline(list(ring.coords)[:-1], close=True, dxfattribs={"layer": warstwa})
                k += 1
        return k
    rysuj(wkt.loads(st["zielen_na_gruncie"]), "BILANS_ZIELEN_NA_GRUNCIE_PZT")
    rysuj(wkt.loads(st["zielen_na_stropie"]), "BILANS_ZIELEN_NA_STROPIE_PZT")
    rysuj(wkt.loads(st["zadaszone_poza_halami"]), "BILANS_ZADASZONE_DOJAZDY", 1.0)
    rysuj(wkt.loads(st["ogrody_deszczowe"]), "BILANS_OGRODY_DESZCZOWE")
    for r in st["rampy"]:
        rysuj(wkt.loads(r["obrys"]), "BILANS_RAMPY")
        (xd, yd), (xg, yg) = r["dol"], r["gora"]
        msp.add_line((xg, yg), (xd, yd), dxfattribs={"layer": "BILANS_RAMPY"})
        msp.add_text("rampa: góra %.2f → dół %.2f" % (D.RAMPA_GORA, D.RAMPA_DOL), height=0.8,
                     dxfattribs={"layer": "BILANS_RAMPY", "insert": ((xd + xg) / 2 + 3, (yd + yg) / 2)})
    nas = json.load(open(os.path.join(D.DANE, "nasyp_strefy.json"), encoding="utf-8"))
    for s in nas["strefy"]:
        rysuj(Polygon(s["wierzcholki"]), "BILANS_NASYP_mapa_4.3")
        c = Polygon(s["wierzcholki"]).centroid
        msp.add_text("nasyp %.2f m" % s["grubosc_m"], height=0.8, dxfattribs={"layer": "BILANS_NASYP_mapa_4.3", "insert": (c.x, c.y)})
    oto = json.load(open(os.path.join(D.DANE, "otwory.json"), encoding="utf-8"))
    cp = json.load(open(os.path.join(D.DANE, "cptu.json"), encoding="utf-8"))
    for nr, o in oto.items():
        msp.add_circle((o["E"], o["N"]), 0.6, dxfattribs={"layer": "BILANS_OTWORY_1-90"})
        etyk = "otw. %s (H %.2f)%s" % (nr, o["H"], " + CPTU-%s" % nr if nr in cp else "")
        msp.add_text(etyk, height=0.9, dxfattribs={"layer": "BILANS_OTWORY_1-90", "insert": (o["E"] + 0.9, o["N"] + 0.3)})
    a, b = geo["odcinek_zamykajacy"]
    msp.add_line(tuple(a), tuple(b), dxfattribs={"layer": "BILANS_SCIANKA_ZAMKNIECIE", "linetype": "DASHED" if "DASHED" in doc.linetypes else "Continuous"})
    # 4) obrysy wykopów z silnika
    w, gm = S.licz(zapisz_geometrie=True)
    G = Polygon(geo["granica"])
    rysuj(gm["A"].intersection(G), "BILANS_WYKOP_A_GORA", 2.0)
    rysuj(gm["B"].intersection(G), "BILANS_WYKOP_B_GORA", 2.0)
    HALE = [Polygon(v) for v in geo["hale"].values()]
    obiekty = unary_union(HALE + [wkt.loads(st["zadaszone_poza_halami"])] + [wkt.loads(r["obrys"]) for r in st["rampy"]])
    P = Polygon(geo["scianka_otwarta"])
    dnoA = obiekty.buffer(S.PARAMETRY["przestrzen_robocza"], join_style=2).intersection(P.union(gm["A"]))
    rysuj(dnoA, "BILANS_WYKOP_A_DNO", 2.0)
    Hst = unary_union(HALE + [wkt.loads(st["zadaszone_poza_halami"])])
    dnoB = unary_union([P, Hst.buffer(S.PARAMETRY["przestrzen_robocza"], join_style=2).intersection(gm["B"])])
    rysuj(dnoB, "BILANS_WYKOP_B_DNO", 2.0)
    for nr, v in geo["hale"].items():
        c = Polygon(v).centroid
        msp.add_text("HALA %s – dno wykopu 121,86" % nr, height=1.5, dxfattribs={"layer": "BILANS_OPISY", "insert": (c.x - 10, c.y)})
    # legenda
    x0, y0 = G.bounds[2] + 10, G.bounds[3]
    msp.add_text("PODKŁAD v3 – bilans robót ziemnych dz. 1/90 (8.10.2026). Układ PL-2000/6, wysokości PL-KRON86-NH.", height=1.2,
                 dxfattribs={"layer": "BILANS_OPISY", "insert": (x0, y0)})
    msp.add_text("Warstwy HALE_GARAZOWE, A-granica inwest., 7_SCIANKA_ORIENTACYJNA, ZIELEN-*: przeliczone do PZT (skala 1,003663).", height=1.0,
                 dxfattribs={"layer": "BILANS_OPISY", "insert": (x0, y0 - 2.5)})
    for i, (nazwa, (kol, opis)) in enumerate(NOWE.items()):
        msp.add_text("%s – %s" % (nazwa, opis), height=0.9, dxfattribs={"layer": nazwa, "insert": (x0, y0 - 5.5 - 2.0 * i)})
    doc.header["$LASTSAVEDBY"] = "bilans_v2"
    doc.saveas(WY)
    print("zapisano", WY, "| przeliczonych obiektów użytkownika:", n)
    print("pola wykopu (górna krawędź): A %.2f m2, B %.2f m2; dno A %.2f m2, dno B %.2f m2" % (gm["A"].area, gm["B"].area, dnoA.area, dnoB.area))


if __name__ == "__main__":
    main()

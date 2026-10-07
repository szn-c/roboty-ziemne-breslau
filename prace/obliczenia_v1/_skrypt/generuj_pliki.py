"""
Generator plików wsadowych do Civil 3D - dz. 1/90 obr. Wojszyce, Wrocław.
Dane: DGI PGF Geoservice, XI-2025 (karty otworów zał. 5.x, tabela współrzędnych).
Układ: PL-2000 strefa 6 (EPSG:2177), wysokości PL-KRON86-NH.
Uwaga: X geodezyjne = Northing (N), Y geodezyjne = Easting (E).
"""
import csv
import math
import os

import ezdxf
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import MultiPoint, Point, Polygon, box
from shapely.ops import unary_union

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# nr: (X=N, Y=E, H, zwierciadło ustabilizowane [m ppt] lub None, uwaga)
OTWORY = {
    2: (5659002.2, 6433708.7, 124.70, 1.20, ""),
    3: (5658972.6, 6433724.8, 124.80, 1.50, ""),
    5: (5658920.1, 6433702.7, 125.00, 0.90, ""),
    7: (5658896.4, 6433678.7, 125.10, 1.20, ""),
    9: (5658957.0, 6433679.0, 124.80, 1.70, ""),
    10: (5658984.4, 6433680.5, 124.50, 1.30, "CPTU-10"),
    11: (5659015.9, 6433664.4, 124.40, 1.20, ""),
    12: (5659037.4, 6433688.2, 124.50, 1.30, "CPTU-12; Y odczytane z uszkodzonego pliku - SPRAWDZIC w DGI"),
    14: (5659030.6, 6433620.1, 124.30, 0.90, ""),
    15: (5659002.8, 6433635.2, 124.30, 1.40, ""),
    16: (5658980.3, 6433637.0, 124.60, 1.20, ""),
    17: (5658959.8, 6433615.8, 124.80, None, "brak zw. ustabilizowanego (nawiercone 1,9)"),
    18: (5658918.4, 6433636.0, 124.90, 3.30, "CPTU-18"),
    20: (5658966.0, 6433587.1, 124.60, 2.70, ""),
    21: (5658993.0, 6433578.9, 124.80, 3.00, "CPTU-21"),
    23: (5659037.1, 6433583.4, 124.50, 1.00, ""),
    24: (5659055.7, 6433603.9, 124.40, 3.70, "CPTU-24"),
}

# Warstwy: (strop, spąg [m ppt], kategoria, symbol, warstwa geol.-inż.)
# H = humus/gleba, N = nasyp, G = spoisty (gliny, pyły, piasek gliniasty), P = niespoisty
W = {
    2: [(0, .7, "H", "Gb", ""), (.7, 2.0, "G", "Gp", "IVc"), (2.0, 2.8, "P", "Pd", "Ia"),
        (2.8, 3.1, "G", "Gp", "IVd"), (3.1, 4.3, "P", "Pr+Z", "IIb"), (4.3, 6.5, "G", "Gp+Z", "IVd"),
        (6.5, 7.5, "G", "Gp+Z", "IVc"), (7.5, 10, "G", "Gp+Z", "IVd")],
    3: [(0, .6, "H", "Gb", ""), (.6, 1.3, "G", "Gp", "IVd"), (1.3, 1.6, "G", "Pg", "IVc"),
        (1.6, 2.0, "P", "Pd", "Ia"), (2.0, 2.8, "G", "Gp//Pd", "IVc"), (2.8, 10, "G", "Gp", "IVd")],
    5: [(0, .2, "N", "Nn", ""), (.2, .7, "H", "Gb", ""), (.7, 1.4, "G", "Gp", "IVc"),
        (1.4, 1.6, "P", "Pd", "Ia"), (1.6, 4.0, "G", "Gp", "IVc"), (4.0, 10, "G", "Gp+Z//Pd", "IVd")],
    7: [(0, .7, "H", "Gb", ""), (.7, 2.0, "G", "Gp//Ps", "IVb"), (2.0, 3.6, "G", "Gp", "IVc"),
        (3.6, 4.0, "P", "Ps", "IIb"), (4.0, 7.7, "G", "Gp//Pd", "IVd"), (7.7, 8.0, "P", "Pd", "Ia"),
        (8.0, 10, "G", "Gp+Z", "IVd")],
    9: [(0, .6, "H", "Gb", ""), (.6, 1.7, "G", "Gp+Z", "IVc"), (1.7, 2.2, "G", "Gp//Ps", "IVb"),
        (2.2, 3.2, "G", "Gp", "IVc"), (3.2, 4.4, "G", "Gp+Z", "IVd"), (4.4, 5.5, "P", "Ps+Z", "IIb"),
        (5.5, 10, "G", "Gp+Z", "IVd")],
    10: [(0, .5, "H", "Gb", ""), (.5, 2.7, "G", "Gp/Gp+Ps", "IVc"), (2.7, 4.5, "G", "Gp+Z", "IVd"),
         (4.5, 4.8, "P", "Pd", "Ia"), (4.8, 10, "G", "Gp+Z", "IVd")],
    11: [(0, .7, "H", "Gb", ""), (.7, 1.5, "G", "Gp", "IVc"), (1.5, 2.5, "P", "Pr+Z", "IIb"),
         (2.5, 3.0, "G", "Gp+Z", "IVd"), (3.0, 9.0, "P", "Po", "IIIa"), (9.0, 10, "G", "Gp+Z", "IVd")],
    12: [(0, .6, "H", "Gb+k", ""), (.6, 2.0, "G", "Gp+Z/Gp//Pg", "IVc"), (2.0, 2.7, "P", "Pr+Z", "IIb"),
         (2.7, 7.5, "G", "Gp+Z", "IVd"), (7.5, 10, "P", "Ps", "IIb")],
    14: [(0, .8, "H", "Gb", ""), (.8, 1.5, "P", "Ps", "IIb"), (1.5, 2.0, "P", "Ps//Gp", "IIb"),
         (2.0, 2.7, "G", "Gp+Z", "IVb"), (2.7, 3.0, "P", "Pr+Z", "IIb"), (3.0, 3.5, "G", "Gp+Z", "IVd"),
         (3.5, 3.7, "P", "Pr", "IIb"), (3.7, 5.5, "G", "Gp+Z", "IVd"), (5.5, 5.7, "P", "Ps", "IIb"),
         (5.7, 10, "G", "Gp+Z", "IVd")],
    15: [(0, .8, "H", "Gb", ""), (.8, 2.1, "G", "Gp+Z", "IVc"), (2.1, 10, "G", "Gp+Z", "IVd")],
    16: [(0, .5, "H", "Gb", ""), (.5, 2.7, "G", "Gp+Z", "IVc"), (2.7, 10, "G", "Gp+Z", "IVd")],
    17: [(0, .3, "N", "Nn", ""), (.3, .7, "H", "Gb", ""), (.7, 1.9, "G", "Gp+Z", "IVc"),
         (1.9, 2.3, "P", "Pd//Gp", "Ia"), (2.3, 3.1, "G", "Gp//Ps", "IVc"), (3.1, 3.5, "G", "Gp+Z", "IVd"),
         (3.5, 3.8, "P", "Ps", "IIb"), (3.8, 10, "G", "Gp+Z", "IVd")],
    18: [(0, .5, "H", "Gb", ""), (.5, 7.0, "G", "Gp/Gpz", "IVd"), (7.0, 8.7, "P", "Ps/Pd", "IIc"),
         (8.7, 10, "G", "Gp", "IVd")],
    20: [(0, .2, "N", "Nn", ""), (.2, .7, "H", "Gb", ""), (.7, 1.1, "P", "Ps//Pg", "IIb"),
         (1.1, 1.7, "G", "Gp", "IVd"), (1.7, 2.7, "P", "Pd+Z", "Ia"), (2.7, 3.6, "G", "Gp+Z/Gp", "IVd"),
         (3.6, 4.0, "P", "Pd", "Ia"), (4.0, 4.4, "G", "Gp", "IVd"), (4.4, 4.7, "P", "Ps", "IIb"),
         (4.7, 10, "G", "Gpz+Z", "IVd")],
    21: [(0, .8, "H", "Gb", ""), (.8, 2.8, "G", "Gp", "IVc"), (2.8, 10, "G", "Gp//Pd/Gp+Z/Gpz", "IVd")],
    23: [(0, .8, "H", "Gb", ""), (.8, 1.7, "P", "Ps", "IIb"), (1.7, 2.4, "G", "Gp+Z", "IVb"),
         (2.4, 2.8, "G", "Gp+Z", "IVc"), (2.8, 5.0, "G", "Gp+Z", "IVd"), (5.0, 6.0, "P", "Ps+Z", "IIb"),
         (6.0, 10, "G", "Gp+Z", "IVd")],
    24: [(0, .7, "H", "Gb", ""), (.7, 3.3, "G", "Gp/Gp//Pg", "IVd"), (3.3, 3.7, "G", "Gp//Ps", "IVc"),
         (3.7, 4.6, "G", "Gp+Z", "IVd"), (4.6, 5.0, "P", "Ps", "IIb"), (5.0, 9.5, "G", "Gpz//Ps/Pi//Pd", "IVd"),
         (9.5, 10, "P", "Ps", "IIb")],
}

POZIOMY_DNA = [119.0, 119.5, 120.0, 120.5, 121.0, 121.5, 122.0, 121.8, 121.9, 122.1, 121.97]  # dodane na koncu, by nie zmieniac numeracji
BUFOR_RAMKI = 30.0   # m - jak daleko poza otwory przedłużamy powierzchnie miąższości
KROK_RAMKI = 20.0    # m - odstęp punktów na ramce


def miazszosc(nr, kat):
    return round(sum(b - t for t, b, k, *_ in W[nr] if k == kat), 3)


def piasek_powyzej_rzednej(nr, rzedna):
    """Miąższość gruntów niespoistych (P) między spodem humusu a podaną rzędną dna wykopu."""
    H = OTWORY[nr][2]
    suma = 0.0
    for t, b, k, *_ in W[nr]:
        if k != "P":
            continue
        gora, dol = H - t, max(H - b, rzedna)
        if gora > dol:
            suma += gora - dol
    return round(suma, 3)


def sprawdz():
    for nr, warstwy in W.items():
        assert warstwy[0][0] == 0 and abs(warstwy[-1][1] - 10) < 1e-9, nr
        for a, b in zip(warstwy, warstwy[1:]):
            assert abs(a[1] - b[0]) < 1e-9, (nr, a, b)


def ramka():
    pts = MultiPoint([Point(v[1], v[0]) for v in OTWORY.values()])  # (E, N)
    minx, miny, maxx, maxy = pts.bounds
    r = box(minx - BUFOR_RAMKI, miny - BUFOR_RAMKI, maxx + BUFOR_RAMKI, maxy + BUFOR_RAMKI)
    obw = r.exterior
    n = max(4, int(math.ceil(obw.length / KROK_RAMKI)))
    return r, [obw.interpolate(i * obw.length / n) for i in range(n)]


def najblizszy(e, n, kandydaci=None):
    kandydaci = kandydaci or OTWORY
    return min(kandydaci, key=lambda k: (OTWORY[k][1] - e) ** 2 + (OTWORY[k][0] - n) ** 2)


def zapisz_pnezd(nazwa, start_nr, wartosci, z_ramka=True, opis="", podfolder=""):
    """wartosci: dict nr_otworu -> Z. Ramka: punkty z wartością najbliższego otworu."""
    folder = os.path.join(OUT, podfolder)
    os.makedirs(folder, exist_ok=True)
    sciezka = os.path.join(folder, nazwa)
    with open(sciezka, "w", newline="", encoding="ascii") as f:
        w = csv.writer(f)
        p = start_nr
        for nr, z in wartosci.items():
            N, E = OTWORY[nr][0], OTWORY[nr][1]
            w.writerow([p, f"{N:.2f}", f"{E:.2f}", f"{z:.3f}", f"{opis}OTW{nr}"])
            p += 1
        if z_ramka:
            _, rpts = ramka()
            p = start_nr + 100
            for pt in rpts:
                nr = najblizszy(pt.x, pt.y, list(wartosci))
                w.writerow([p, f"{pt.y:.2f}", f"{pt.x:.2f}", f"{wartosci[nr]:.3f}", f"{opis}RAMKA_z_OTW{nr}"])
                p += 1
    return sciezka


def main():
    sprawdz()
    folder_pl = "01_pliki_punktow_PNEZD"

    # 1. Otwory - rzędne terenu (tylko kontrola, NIE do budowy terenu)
    zapisz_pnezd("01_otwory_teren_kontrola.csv", 1000,
                 {nr: OTWORY[nr][2] for nr in OTWORY}, z_ramka=False, podfolder=folder_pl)
    # 2. Miąższość humusu
    hum = {nr: miazszosc(nr, "H") for nr in OTWORY}
    zapisz_pnezd("02_miazszosc_humus.csv", 2000, hum, opis="HUM_", podfolder=folder_pl)
    # 3. Miąższość nasypu
    nas = {nr: miazszosc(nr, "N") for nr in OTWORY}
    zapisz_pnezd("03_miazszosc_nasyp.csv", 3000, nas, opis="NAS_", podfolder=folder_pl)
    # 4. Humus + nasyp (cała warstwa zdejmowana z wierzchu)
    zapisz_pnezd("04_miazszosc_humus_plus_nasyp.csv", 4000,
                 {nr: hum[nr] + nas[nr] for nr in OTWORY}, opis="HN_", podfolder=folder_pl)
    # 5. Piaski powyżej rzędnej dna wykopu
    for i, rz in enumerate(POZIOMY_DNA):
        nazwa = f"05_piasek_nad_dnem_{rz:.2f}".replace(".", "_") + ".csv"
        zapisz_pnezd(nazwa, 5000 + i * 200,
                     {nr: piasek_powyzej_rzednej(nr, rz) for nr in OTWORY},
                     opis=f"PIA{int(rz*100)}_", podfolder=os.path.join(folder_pl, "05_piaski_nad_dnem_wykopu"))
    # 6. Zwierciadło wody (rzędna) - orientacyjnie
    zw = {nr: round(OTWORY[nr][2] - OTWORY[nr][3], 2) for nr in OTWORY if OTWORY[nr][3] is not None}
    zapisz_pnezd("06_zwierciadlo_wody_rzedna_orientacyjnie.csv", 8000, zw, opis="ZW_", podfolder=folder_pl)
    # 7. Powierzchnia ZERO (płaska, Z=0) - do liczenia objętości z miąższości
    r, _ = ramka()
    minx, miny, maxx, maxy = r.buffer(100).bounds
    with open(os.path.join(OUT, folder_pl, "07_powierzchnia_ZERO.csv"), "w", newline="", encoding="ascii") as f:
        w = csv.writer(f)
        for i, (e, n) in enumerate([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]):
            w.writerow([9000 + i, f"{n:.2f}", f"{e:.2f}", "0.000", "ZERO"])

    # 7b. Teren projektowany - PLASKI ZASTEPCZY (przekroj 2C: teren proj. 125,89 m npm) - do zamiany na prawdziwy plan wysokosciowy
    with open(os.path.join(OUT, folder_pl, "08_teren_projektowany_plaski_125_89.csv"), "w", newline="", encoding="ascii") as f:
        w = csv.writer(f)
        for i, (e, n) in enumerate([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]):
            w.writerow([9100 + i, f"{n:.2f}", f"{e:.2f}", "125.890", "TEREN_PROJ_ZASTEPCZY"])

    # 8. Zestawienie do Excela (średnik, przecinek dziesiętny)
    def pl(x):
        return "" if x is None else str(x).replace(".", ",")
    os.makedirs(os.path.join(OUT, "02_zestawienia_excel"), exist_ok=True)
    with open(os.path.join(OUT, "02_zestawienia_excel", "zestawienie_otworow.csv"), "w",
              newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Otwor", "X (Northing)", "Y (Easting)", "H [m npm]", "Nasyp [m]", "Humus [m]",
                    "Zw. wody ustab. [m ppt]"] + [f"Piasek nad rz. {rz} [m]" for rz in POZIOMY_DNA] + ["Uwagi"])
        for nr, (N, E, H, zwm, uw) in OTWORY.items():
            w.writerow([nr, pl(N), pl(E), pl(H), pl(nas[nr]), pl(hum[nr]), pl(zwm)]
                       + [pl(piasek_powyzej_rzednej(nr, rz)) for rz in POZIOMY_DNA] + [uw])
    with open(os.path.join(OUT, "02_zestawienia_excel", "profile_warstw.csv"), "w",
              newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Otwor", "Strop [m ppt]", "Spag [m ppt]", "Strop [m npm]", "Spag [m npm]",
                    "Kategoria (H/N/G/P)", "Symbol", "Warstwa geol.-inz."])
        for nr, warstwy in W.items():
            H = OTWORY[nr][2]
            for t, b, k, s, wg in warstwy:
                w.writerow([nr, pl(t), pl(b), pl(round(H - t, 2)), pl(round(H - b, 2)), k, s, wg])

    # 9. DXF kontrolny: otwory, opisy, wieloboki Thiessena, ramka
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.M
    msp = doc.modelspace()
    for nazwa, kolor in [("OTWORY", 1), ("OTWORY_OPIS", 7), ("THIESSEN", 3), ("RAMKA_POWIERZCHNI", 5),
                         ("OBRYS_OTWOROW", 4)]:
        doc.layers.add(nazwa, color=kolor)
    pts = np.array([[OTWORY[k][1], OTWORY[k][0]] for k in OTWORY])  # (E, N)
    far = 1e4
    vor = Voronoi(np.vstack([pts, [[pts[:, 0].mean() + dx, pts[:, 1].mean() + dy]
                                   for dx, dy in [(-far, -far), (far, -far), (far, far), (-far, far)]]]))
    thiessen = {}
    for i, nr in enumerate(OTWORY):
        reg = vor.regions[vor.point_region[i]]
        poly = Polygon([vor.vertices[j] for j in reg]).intersection(r)
        thiessen[nr] = poly
        msp.add_lwpolyline(list(poly.exterior.coords), close=True, dxfattribs={"layer": "THIESSEN"})
    for nr, (N, E, H, zwm, uw) in OTWORY.items():
        msp.add_circle((E, N), 0.75, dxfattribs={"layer": "OTWORY"})
        msp.add_point((E, N, H), dxfattribs={"layer": "OTWORY"})
        msp.add_text(f"{nr}  H={H:.2f}", height=1.5, dxfattribs={"layer": "OTWORY_OPIS"}).set_placement((E + 1.5, N + 1.0))
        msp.add_text(f"hum {hum[nr]:.2f}" + (f" nas {nas[nr]:.2f}" if nas[nr] else ""), height=1.2,
                     dxfattribs={"layer": "OTWORY_OPIS"}).set_placement((E + 1.5, N - 1.2))
    msp.add_lwpolyline(list(r.exterior.coords), close=True, dxfattribs={"layer": "RAMKA_POWIERZCHNI"})
    hull = MultiPoint([Point(p) for p in pts]).convex_hull
    msp.add_lwpolyline(list(hull.exterior.coords), close=True, dxfattribs={"layer": "OBRYS_OTWOROW"})
    # zasięg rysunku i widok startowy - bez tego program otwiera widok na 0,0
    from ezdxf import bbox as _bbox
    ext = _bbox.extents(msp, fast=True)
    doc.header["$EXTMIN"] = (ext.extmin.x, ext.extmin.y, 0)
    doc.header["$EXTMAX"] = (ext.extmax.x, ext.extmax.y, 0)
    doc.set_modelspace_vport(height=(ext.extmax.y - ext.extmin.y) * 1.1,
                             center=((ext.extmin.x + ext.extmax.x) / 2, (ext.extmin.y + ext.extmax.y) / 2))
    os.makedirs(os.path.join(OUT, "03_dxf_kontrolny"), exist_ok=True)
    doc.saveas(os.path.join(OUT, "03_dxf_kontrolny", "otwory_thiessen_dz190.dxf"))

    # Alternatywa: skrypt AutoCAD (.scr) rysujący to samo bezpośrednio w otwartym rysunku
    with open(os.path.join(OUT, "03_dxf_kontrolny", "rysuj_otwory.scr"), "w", encoding="ascii", newline="\r\n") as s:
        s.write("_OSMODE\n0\n")
        for nazwa, kolor in [("OTWORY", 1), ("OTWORY_OPIS", 7), ("THIESSEN", 3), ("RAMKA_POWIERZCHNI", 5)]:
            s.write(f"_-LAYER\n_M\n{nazwa}\n_C\n{kolor}\n\n\n")
        s.write("_-LAYER\n_S\nTHIESSEN\n\n")
        for poly in thiessen.values():
            s.write("_PLINE\n" + "".join(f"{x:.2f},{y:.2f}\n" for x, y in list(poly.exterior.coords)[:-1]) + "_C\n")
        s.write("_-LAYER\n_S\nRAMKA_POWIERZCHNI\n\n")
        s.write("_PLINE\n" + "".join(f"{x:.2f},{y:.2f}\n" for x, y in list(r.exterior.coords)[:-1]) + "_C\n")
        s.write("_-LAYER\n_S\nOTWORY\n\n")
        for nr, (N, E, H, *_r) in OTWORY.items():
            s.write(f"_CIRCLE\n{E:.2f},{N:.2f}\n0.75\n")
        s.write("_-LAYER\n_S\nOTWORY_OPIS\n\n")
        for nr, (N, E, H, *_r) in OTWORY.items():
            s.write(f"_-TEXT\n{E+1.5:.2f},{N+1.0:.2f}\n1.5\n0\nOTW {nr} H={H:.2f} hum={hum[nr]:.2f}\n")
        s.write("_ZOOM\n_E\n")

    # 10. Szacunek kontrolny (orientacyjny) w obrysie otworów
    A = hull.area
    v_h = sum(thiessen[nr].intersection(hull).area * hum[nr] for nr in OTWORY)
    v_n = sum(thiessen[nr].intersection(hull).area * nas[nr] for nr in OTWORY)
    print(f"Pole obrysu otworow: {A:.0f} m2")
    print(f"Humus (Thiessen) w obrysie: {v_h:.0f} m3, srednia wazona {v_h/A:.3f} m")
    print(f"Nasyp (Thiessen) w obrysie: {v_n:.0f} m3")
    print(f"Srednia arytm. humusu: {np.mean(list(hum.values())):.3f} m")
    for nr in OTWORY:
        print(nr, f"pole Thiessena w obrysie {thiessen[nr].intersection(hull).area:.0f} m2")


if __name__ == "__main__":
    main()

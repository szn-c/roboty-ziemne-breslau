"""
DANE WEJŚCIOWE do bilansu v2 (T4) – zapis do prace/dane/ (każda pozycja ze źródłem).

Geometria: DXF użytkownika v2 (hale, granica, ścianka) przeliczony do PZT (skala 1,003663, obrót −0,0017°,
  przesunięcie ok. 0,7 m; dopasowanie na 34 narożnikach hal, rms 1 mm – prace/weryfikacja/transformacja_uzytk_do_PZT.json).
Strefy: wypełnienia wektorowego PZT (prace/_odzyskane/PZT_wektorowy.pdf; prace/weryfikacja/pzt_strefy_widoczne.py).
Otwory: karty 5.1–5.17 DGI (profile z v1 – sprawdzone w T2, poprawka otw. 15), wilgotność z kart, woda z tab. 1 DGI.
CPTU 10, 12, 18, 21, 24: zał. 7 DGI. Nasyp: mapa 4.3 DGI. Teren: pomiar z PZT + otwory. Projekt: rzędne PZT.
Uruchom: python prace/obliczenia_v2/dane.py
"""
import csv
import json
import math
import os
import sys

import ezdxf
import numpy as np
from ezdxf import path as ezpath
from shapely import wkt
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WER = os.path.join(REPO, "prace", "weryfikacja")
DANE = os.path.join(REPO, "prace", "dane")
V2 = os.path.join(REPO, "prace", "dane_wejsciowe_uzytkownika", "siatka_10m_dz190_checked_v2.dxf")
sys.path.insert(0, WER)
sys.path.insert(0, os.path.join(REPO, "prace", "obliczenia_v1", "_skrypt"))

# ------------------------------------------------------------------ stałe projektu (źródła w komentarzach)
ZERO = 126.00              # ±0,00 = 126,00 m npm (PZT, przekroje terenowe)
DNO = 121.86               # d.k. płyty −4,04 (PW_*) − chudy beton 0,10 (przekrój B-B 2C) = 121,86
SPOD_PLYTY = -4.04         # względem ±0,00
CHUDY = 0.10
RAMPA_GORA = 125.80        # rzędna wlotu pochylni (PZT garaże: 125,76–125,83)
RAMPA_DOL = 122.85         # rzędna dołu pochylni (PZT garaże: 122,85, przed bramą 122,60)
RAMPA_POD = 0.71           # spód wykopu pod rampą = powierzchnia rampy − 0,71 m (jak pod posadzką garażu: 122,57 − 121,86)
MURY_RAMPY = 0.25          # obrys rampy z murami = kreskowanie + 0,25 m (Bilans: rampy z murami 553,77 m²)

# gęstości [t/m³]: tabela parametrów (zał. 8 DGI); piaski wg stanu wilgotności z karty (mw / w / nw), gliny – średnia z zakresu
GESTOSC = {
    "Ia": {"mw": 1.65, "w": 1.75, "nw": 1.90}, "IIa": {"mw": 1.65, "w": 1.75, "nw": 1.95},
    "IIb": {"mw": 1.70, "w": 1.85, "nw": 2.00}, "IIc": {"mw": 1.80, "w": 1.90, "nw": 2.05},
    "IIIa": {"mw": 1.80, "w": 1.90, "nw": 2.05}, "IIIb": {"mw": 1.85, "w": 2.00, "nw": 2.10},
    "IVa": 2.10, "IVb": 2.05, "IVc": 2.10, "IVd": 2.175,
}
GESTOSC_GLEBA, GESTOSC_NASYP = 1.60, 1.80   # brak w zał. 8 – założenie zaakceptowane przez użytkownika (8.10.2026)
KLASY = ("Ia", "IIa", "IIb", "IIc", "IIIa", "IIIb", "IVa", "IVb", "IVc", "IVd")
PIASKI = ("Ia", "IIa", "IIb", "IIc", "IIIa", "IIIb")
GLINY = ("IVa", "IVb", "IVc", "IVd")

# woda (DGI tab. 1): zwierciadło ustabilizowane [m ppt]; None = nie ustabilizowało się (podano nawiercone/sączenia)
WODA = {2: 1.2, 3: 1.5, 5: 0.9, 7: 1.2, 9: 1.7, 10: 1.3, 11: 1.2, 12: 1.3, 14: 0.9, 15: 1.4, 16: 1.2, 17: None,
        18: 5.8, 20: None, 21: None, 23: 1.0, 24: 3.7}
WODA_UWAGI = {17: "nawiercone 1,9 i 3,5 m ppt", 20: "sączenie 2,7; nawiercone 3,6 i 4,4 m ppt", 21: "sączenia 3,0 i 4,5 m ppt",
              18: "sączenia 3,3 i 5,4; nawiercone 7,0", 24: "sączenie 3,7; nawiercone 4,6"}
STRONA_KARTY = {2: 1, 3: 2, 5: 3, 7: 4, 9: 5, 10: 6, 11: 7, 12: 8, 14: 9, 15: 10, 16: 11, 17: 12, 18: 13, 20: 14, 21: 15, 23: 16, 24: 17}


def transformacja():
    T = json.load(open(os.path.join(WER, "transformacja_uzytk_do_PZT.json")))
    s, a = T["skala"], math.radians(T["obrot_deg"])
    cs, cd = np.array(T["srodek_uzytk"]), np.array(T["srodek_PZT"])
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return T, (lambda pts: [tuple(round(float(v), 3) for v in p) for p in (s * ((np.array(pts) - cs) @ R.T) + cd)])


def geometria_v2():
    """Hale, granica, ścianka z DXF v2, po korekcie do PZT."""
    T, f = transformacja()
    msp = ezdxf.readfile(V2).modelspace()
    txt, cur = {}, None
    for l in open(os.path.join(REPO, "prace", "dane_wejsciowe_uzytkownika", "wierzcholki_polilinii_hala1-8_checked.txt"), encoding="utf-8"):
        t = l.strip()
        if not t:
            continue
        if t.startswith("hala"):
            cur = int(t[4:]); txt[cur] = []
        else:
            txt[cur].append(tuple(map(float, t.split())))
    hale = {}
    for e in msp:
        if e.dxf.layer == "HALE_GARAZOWE" and e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points("xy")]
            nr = min(txt, key=lambda k: Polygon(txt[k]).centroid.distance(Polygon(pts).centroid))
            hale[nr] = f(pts)
    gr = [e for e in msp if e.dxf.layer == "A-granica inwest." and e.dxftype() == "LWPOLYLINE"][0]
    granica = f([(p[0], p[1]) for p in gr.get_points("xy")])
    sc = [e for e in msp if e.dxf.layer == "7_SCIANKA_ORIENTACYJNA" and e.dxftype() == "LWPOLYLINE"]
    assert len(sc) == 1 and len(sc[0]) == 11
    scianka = f([(p[0], p[1]) for p in sc[0].get_points("xy")])
    return {"hale": {str(k): hale[k] for k in sorted(hale)}, "granica": granica, "scianka_otwarta": scianka,
            "odcinek_zamykajacy": [scianka[-1], scianka[0]],
            "zrodlo": "DXF v2 użytkownika (identyczny z v1 dla hal, granicy, ścianki) przeliczony do PZT: skala %.6f, obrót %.5f°, rms %.3f m"
                      % (T["skala"], T["obrot_deg"], T["rms_m"])}


def strefy(geo):
    from pzt_strefy_widoczne import strefy_pzt
    S = strefy_pzt()
    G = Polygon(geo["granica"])
    H = unary_union([Polygon(v) for v in geo["hale"].values()])
    zad = S["widoczne"]["zielen_strop"].intersection(G).difference(H)
    zad = unary_union([g for g in (zad.geoms if hasattr(zad, "geoms") else [zad]) if g.area > 1.0])
    # pochylnie: skupiska kreskowania -> prostokąty + mury
    pk = S["pochylnie_kresk"]
    czesci = [g for g in (pk.geoms if hasattr(pk, "geoms") else [pk]) if g.area > 20]
    rampy = []
    Hz = unary_union([H, zad])
    for g in czesci:
        mr = g.minimum_rotated_rectangle
        xy = list(mr.exterior.coords)[:4]
        boki = [(xy[i], xy[(i + 1) % 4]) for i in range(4)]
        krotkie = sorted(boki, key=lambda b: math.dist(*b))[:2]
        sr = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in krotkie]
        dol = min(sr, key=lambda p: Hz.distance(LineString([p, p]).buffer(0.01)))
        gora = sr[1] if dol is sr[0] else sr[0]
        rampy.append({"obrys": wkt.dumps(mr.buffer(MURY_RAMPY, join_style=2), rounding_precision=3),
                      "kreskowanie_pole": round(g.area, 2), "dol": [round(v, 3) for v in dol], "gora": [round(v, 3) for v in gora],
                      "dlugosc": round(math.dist(dol, gora), 2)})
    out = {
        "zielen_na_gruncie": S["widoczne"]["zielen_grunt"].intersection(G),
        "ogrody_deszczowe": S["widoczne"]["ogrody_deszczowe"].intersection(G),
        "zielen_na_stropie": S["widoczne"]["zielen_strop"].intersection(G),
        "zadaszone_poza_halami": zad,
        "wiaty": S["widoczne"].get("sciany_pochylni", Polygon()).intersection(G),
        "geokrata_na_gruncie": S["widoczne"]["geokrata"].intersection(G),
    }
    pola = {k: round(v.area, 2) for k, v in out.items()}
    res = {k: wkt.dumps(v, rounding_precision=3) for k, v in out.items()}
    res["rampy"] = rampy
    res["pola"] = pola
    res["zrodlo"] = "wypełnienia wektorowego PZT (odzyskany z gita, commit 851b25a), widoczne części; rampy z kreskowania pochylni + mury 0,25 m"
    return res


def otwory():
    from generuj_pliki import OTWORY, W
    K = {k["nr"]: k for k in json.load(open(os.path.join(WER, "karty_otworow_odczyt.json"), encoding="utf-8"))}
    W = {k: list(v) for k, v in W.items()}
    # poprawka po T2: otwór 15 – granica IVc/IVd na 2,50 m (karta 5.10)
    W[15] = [(0, .8, "H", "Gb", ""), (.8, 2.5, "G", "Gp+Ż", "IVc"), (2.5, 10, "G", "Gp+Ż", "IVd")]
    out = {}
    for nr, (N, E, H, _zw, uw) in OTWORY.items():
        wl = [(g, t) for w in K[nr]["warstwy"] for g, t in w["wilg"]]
        warstwy = []
        for t, b, kat, sym, lay in W[nr]:
            wil = ""
            if kat == "P":
                w_in = [x for g, x in wl if t - 0.01 <= g <= b + 0.01]
                wil = w_in[0] if w_in else min(wl, key=lambda q: abs(q[0] - (t + b) / 2))[1]
            warstwy.append({"strop": t, "spag": b, "kat": kat, "symbol": sym.replace("Z", "Ż"), "warstwa": lay, "wilgotnosc": wil})
        out[str(nr)] = {"N": N, "E": E, "H": H, "woda_ustab_m_ppt": WODA[nr], "woda_uwagi": WODA_UWAGI.get(nr, ""),
                        "warstwy": warstwy, "zrodlo": "DGI zał. 5.x – karta otworu nr %d (str. %d PDF 5.1–5.28); współrzędne i H – karta informacyjna DGI%s"
                                                     % (nr, STRONA_KARTY[nr], "; E odtworzone z przekrojów IV-IV', XI-XI' i mapy 4.1 (w tabeli uszkodzone)" if nr == 12 else "")}
    return out


def cptu():
    C = json.load(open(os.path.join(WER, "cptu_odczyt.json"), encoding="utf-8"))
    out = {}
    for nr, rows in C.items():
        w = []
        for a, b, sym, lay in rows:
            kat = "H" if sym.startswith("Gb") else ("P" if lay in PIASKI else "G")
            w.append({"strop": a, "spag": b, "kat": kat, "symbol": sym, "warstwa": lay})
        out[nr] = {"przy_otworze": int(nr), "warstwy": w, "zrodlo": "DGI zał. 7 – tabela interpretacji CPTU-%s" % nr}
    return out


def main():
    os.makedirs(DANE, exist_ok=True)
    geo = geometria_v2()
    json.dump(geo, open(os.path.join(DANE, "geometria.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    st = strefy(geo)
    json.dump(st, open(os.path.join(DANE, "strefy.json"), "w", encoding="utf-8"), ensure_ascii=False)
    oto = otwory()
    json.dump(oto, open(os.path.join(DANE, "otwory.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cp = cptu()
    json.dump(cp, open(os.path.join(DANE, "cptu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nas = json.load(open(os.path.join(WER, "mapa43_nasyp.json")))
    gr = {str(k): v for k, v in {5: 0.20, 17: 0.30, 20: 0.20}.items()}
    for s in nas["strefy"]:
        s["grubosc_m"] = round(float(np.mean([gr[str(n)] for n in s["otwory"]])), 3)
    nas["zrodlo"] = "DGI mapa 4.3 (odzyskana z gita) – strefy 'miąższość 0,2–0,3 m'; grubość = średnia z otworów w strefie (karty 5.3, 5.12, 5.14)"
    json.dump(nas, open(os.path.join(DANE, "nasyp_strefy.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # teren istniejący i projektowany
    src = os.path.join(WER, "dane_odtworzone")
    with open(os.path.join(DANE, "teren_istniejacy.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.writer(fo); w.writerow(["E", "N", "z", "zrodlo"])
        for r in csv.DictReader(open(os.path.join(src, "eg_pomiar_PZT_czarne.csv"))):
            w.writerow([r["E"], r["N"], r["z"], "PZT – czarne rzędne pomiarowe (warstwa tekstowa)"])
        for nr, o in oto.items():
            w.writerow([o["E"], o["N"], o["H"], "otwór %s (karta informacyjna DGI)" % nr])
    with open(os.path.join(DANE, "teren_projektowany.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.writer(fo); w.writerow(["E", "N", "z", "zrodlo"])
        for r in csv.DictReader(open(os.path.join(src, "fg_projekt_PZT.csv"))):
            w.writerow([r["E"], r["N"], r["z"], "PZT – rzędne projektowane"])
    print("geometria: hale %.2f m2, granica %.2f m2, ścianka (linia otwarta) %.2f m" % (
        sum(Polygon(v).area for v in geo["hale"].values()), Polygon(geo["granica"]).area, LineString(geo["scianka_otwarta"]).length))
    print("strefy [m2]:", st["pola"])
    print("rampy:", [(r["kreskowanie_pole"], r["dlugosc"], round(wkt.loads(r["obrys"]).area, 2)) for r in st["rampy"]],
          "razem z murami %.2f" % sum(wkt.loads(r["obrys"]).area for r in st["rampy"]))
    print("otwory:", len(oto), "CPTU:", list(cp), "nasyp:", [(s["pole"], s["otwory"], s["grubosc_m"]) for s in nas["strefy"]])


if __name__ == "__main__":
    main()

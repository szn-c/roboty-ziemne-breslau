"""
Korekta geometrii użytkownika (*_checked) do PZT: podobieństwo (skala, obrót, przesunięcie) dopasowane
na 34 narożnikach hal (narożniki PZT = przecięcia zewnętrznej linii "obrys garażu" z wektorowego PZT).
Wymaga: pzt_wektor_hale_dopasowanie.json (uruchom najpierw pzt_wektor_hale_dopasowanie.py).
Wynik: transformacja_uzytk_do_PZT.json (parametry + granica, ścianka i hale po korekcie).
To jest WYNIK KONTROLI – geometria po korekcie obowiązuje dopiero po decyzji użytkownika.
"""
import json
import os

import numpy as np
from shapely.geometry import LineString, Polygon

import pzt_wektor_hale as W
from pzt_wektor_hale_dopasowanie import helmert

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    J = json.load(open(os.path.join(HERE, "pzt_wektor_hale_dopasowanie.json")))
    hale = W.wczytaj_hale()
    src, dst = [], []
    for nr, pts in hale.items():
        u = pts if Polygon(pts).exterior.is_ccw else pts[::-1]
        for p, q in zip(u, J[str(nr)]["narozniki_PZT_zewn"]):
            src.append(p); dst.append(tuple(q))
    s, kat, cs, cd, rms, f = helmert(src, dst)
    gr = [tuple(map(float, l.split())) for l in open(os.path.join(W.DU, "wierzcholki_polilinii_granica_działki_checked.txt"), encoding="utf-8") if l.strip()]
    sc = [tuple(map(float, l.split())) for l in open(os.path.join(W.DU, "wierzcholki_polilinii_wykop_checked.txt"), encoding="utf-8") if l.strip()]
    grT, scT = [tuple(p) for p in f(np.array(gr))], [tuple(p) for p in f(np.array(sc))]
    print("skala %.6f, obrót %+.5f°, przesunięcie środka (%+.2f, %+.2f) m, rms %.3f m (n=%d)" % (s, kat, cd[0] - cs[0], cd[1] - cs[1], rms, len(src)))
    print("granica %.2f -> %.2f m2; ścianka (domknięta) %.2f -> %.2f m2, linia otwarta %.2f -> %.2f m" % (
        Polygon(gr).area, Polygon(grT).area, Polygon(sc).area, Polygon(scT).area, LineString(sc).length, LineString(scT).length))
    json.dump({"skala": s, "obrot_deg": kat, "rms_m": rms, "srodek_uzytk": list(cs), "srodek_PZT": list(cd),
               "granica_po": [(round(x, 3), round(y, 3)) for x, y in grT], "scianka_po": [(round(x, 3), round(y, 3)) for x, y in scT],
               "hale_po": {nr: [(round(x, 3), round(y, 3)) for x, y in f(np.array(v))] for nr, v in hale.items()}},
              open(os.path.join(HERE, "transformacja_uzytk_do_PZT.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

"""
Odczyt kart otworów (zał. 5.1-5.28 DGI) z warstwy tekstowej PDF według położenia słów.
Wynik: prace/weryfikacja/karty_otworow_odczyt.json oraz tabela na ekran.

Układ karty (GeoStar): kolumna 4 = skala głębokości (1.0 ... 10.0),
kolumna 6 "Przelot" = spąg warstwy (napis tuż pod linią granicy),
kolumny 8-12 (symbol ISO, symbol PN, warstwa, wilgotność, stan) = środek warstwy,
kolumna 2 = woda: lewa podkolumna (x < 90) i prawa (x > 90).
"""
import json
import os
import re

import fitz

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF = os.path.join(REPO, "dokumentacja/01_geologiczno_inzynierska/załączniki graficzne/5.1 - 5.28 Karty otworów geol-inż.pdf")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "karty_otworow_odczyt.json")

NUM = re.compile(r"^\d+\.\d+$")


def odczytaj_strone(pg):
    ws = pg.get_text("words")
    tekst = " ".join(w[4] for w in ws)
    nr = int(re.search(r"numer\s+(\d+)", tekst).group(1))
    zal = re.search(r"Zał\.nr:\s*([\d.]+)", tekst).group(1).rstrip(".")
    rz = float(re.search(r"Rzędna:\s*([\d.]+)", tekst).group(1))
    data = re.search(r"wiercenia:\s*([\d.]+\s*r?)", tekst)
    # skala głębokości: napisy "1.0".."10.0" w kolumnie 4 (x ok. 131-147)
    skala = [(float(w[4]), (w[1] + w[3]) / 2) for w in ws
             if NUM.match(w[4]) and 125 < w[0] < 150 and w[1] > 190]
    skala.sort()
    (d1, y1), (d2, y2) = skala[0], skala[-1]
    b = (y2 - y1) / (d2 - d1)
    a = y1 - b * d1  # środek napisu "1.0" leży na linii 1,0 m
    gl = lambda y: (y - a) / b
    # spągi: kolumna "Przelot" (x ok. 195-220), górna krawędź napisu = granica
    spagi = sorted({float(w[4]) for w in ws if NUM.match(w[4]) and 193 < w[0] < 220 and w[1] > 190})
    granice = [0.0] + spagi
    warstwy = []
    for t, s in zip(granice, granice[1:]):
        warstwy.append({"strop": t, "spag": s, "opis": [], "iso": [], "pn": [], "warstwa": [], "wilg": [], "stan": []})

    def warstwa_dla(glebokosc):
        for w in warstwy:
            if w["strop"] - 1e-6 <= glebokosc < w["spag"] + 1e-6:
                return w
        return None

    kolumny = {"iso": (385, 420), "pn": (424, 450), "warstwa": (460, 490), "wilg": (500, 527), "stan": (535, 566)}
    linie_opisu = {}
    for w in ws:
        x0, y0, x1, y1, txt = w[:5]
        if y0 < 190 or y0 > 770:
            continue
        yc = (y0 + y1) / 2
        if 226 < x0 < 386:  # opis litologiczny
            linie_opisu.setdefault(round(y0, 0), []).append((x0, txt))
            continue
        for k, (xa, xb) in kolumny.items():
            if xa <= x0 < xb:
                ww = warstwa_dla(gl(yc))
                if ww is not None:
                    ww[k].append((round(gl(yc), 2), txt))
    # opis: każda linia przypisana do warstwy wg górnej krawędzi (opis zaczyna się na stropie)
    for y0, slowa in sorted(linie_opisu.items()):
        g = gl(y0) + 0.02
        ww = warstwa_dla(g)
        if ww is not None:
            ww["opis"].append(" ".join(t for _, t in sorted(slowa)))
    woda = {"lewa": [], "prawa": []}
    for w in ws:
        x0, y0, x1, y1, txt = w[:5]
        if NUM.match(txt) and 70 < x0 < 110 and y0 > 190:
            woda["lewa" if x0 < 90 else "prawa"].append((float(txt), round(gl(y0), 2)))
    return {"nr": nr, "zal": zal, "rzedna": rz, "data": data.group(1) if data else "",
            "warstwy": warstwy, "woda": woda, "skala_pt_na_m": round(b, 2)}


def main():
    d = fitz.open(PDF)
    karty = [odczytaj_strone(d[i]) | {"strona": i + 1} for i in range(d.page_count)]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(karty, f, ensure_ascii=False, indent=1)
    for k in karty:
        print(f"\n=== Otwór {k['nr']} (zał. {k['zal']}, str. {k['strona']}), H = {k['rzedna']:.2f}, "
              f"woda lewa (ustab.?) {k['woda']['lewa']}, prawa (nawierc.) {k['woda']['prawa']}")
        for w in k["warstwy"]:
            f = lambda key: "/".join(t for _, t in w[key])
            print(f"  {w['strop']:5.2f}-{w['spag']:5.2f}  {f('pn'):10s} {f('iso'):12s} {f('warstwa'):6s} "
                  f"{f('wilg'):6s} {f('stan'):10s} | {' '.join(w['opis'])}")


if __name__ == "__main__":
    main()

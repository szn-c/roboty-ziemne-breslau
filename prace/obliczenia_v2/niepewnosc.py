"""
Analiza wrażliwości (blok NIEPEWNOŚĆ arkusza): zmiana jednego założenia naraz, różnice głównych pozycji względem wyniku bazowego.
Wynik: niepewnosc.json
"""
import json
import os

import silnik

HERE = os.path.dirname(os.path.abspath(__file__))


def glowne(w):
    out = {"humus": w["humus_m3"], "nasyp": w["nasyp_m3"]}
    for k, r in w["warianty"].items():
        nat = {z: sum(v.values()) for z, v in r["wykop_m3"].items()}
        zap = sum(sum(r["zapotrzebowanie"][x].values()) for x in ("rodzimy_Z", "rodzimy_U", "rodzimy_R", "rodzimy_O"))
        out["wykop_" + k] = sum(nat.values())
        out["nadwyzka_" + k] = sum(nat.values()) - zap      # grunt rodzimy do wywozu (cały wykop przydatny – ustalenie 18)
        out["mroz_" + k] = sum(r["zapotrzebowanie"]["niewysadzinowy_U"].values())
    return out


PRZYPADKI = [
    ("teren +0,05 m (dokładność rzędnych PZT 0,1 m)", {"dz_teren": 0.05}),
    ("teren −0,05 m", {"dz_teren": -0.05}),
    ("humus +0,10 m (grubość z 17 otworów i 5 CPTU)", {"dz_humus": 0.10}),
    ("humus −0,10 m", {"dz_humus": -0.10}),
    ("przestrzeń robocza 0,5 m (A)", {"przestrzen_robocza": 0.5}),
    ("przestrzeń robocza 1,5 m (A)", {"przestrzen_robocza": 1.5}),
    ("skarpa 1:1,0", {"skarpa": 1.0}),
    ("skarpa 1:2,0", {"skarpa": 2.0}),
    ("spód wykopu pod rampą: powierzchnia − 0,50 m", {"rampa_pod": 0.50}),
    ("spód wykopu pod rampą: powierzchnia − 0,90 m", {"rampa_pod": 0.90}),
    ("raster 0,50 m (kontrola numeryczna)", {"cell": 0.50}),
]


def main():
    baza = glowne(silnik.licz())
    wyn = {"baza": baza, "przypadki": []}
    for opis, p in PRZYPADKI:
        g = glowne(silnik.licz(p))
        d = {k: round(g[k] - baza[k], 3) for k in baza}
        wyn["przypadki"].append({"opis": opis, "parametry": p, "roznice": d})
        print("%-50s " % opis + "  ".join("%s %+.0f" % (k, v) for k, v in d.items() if abs(v) >= 0.5))
    json.dump(wyn, open(os.path.join(HERE, "niepewnosc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("baza:", {k: round(v, 1) for k, v in baza.items()})


if __name__ == "__main__":
    main()

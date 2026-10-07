"""
Kontrola położenia geometrii użytkownika na rastrze PZT (bez oglądania obrazu).

1. Krzyże siatki współrzędnych co 50 m: położenie przewidziane transformacją v1 (PL-2000 -> strona PZT)
   porównane z położeniem wykrytym w rastrze (ciemne piksele ramion krzyża).
2. Granica działki (czerwona linia w legendzie) i obrysy hal (ciemnofioletowa linia "obrys projektowanej
   kondygnacji garażu podziemnego"): dla każdego boku liczony jest profil udziału pikseli danego koloru
   w funkcji przesunięcia prostopadłego (-3 m ... +3 m). Maksimum profilu = gdzie na PZT leży linia
   względem boku użytkownika.

Uruchom: python prace/weryfikacja/pzt_raster_kontrola.py
Wymaga: prace/weryfikacja/_cache/pzt_raster.npy (tworzy go sam, jeśli brak).
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CACHE = os.path.join(HERE, "_cache", "pzt_raster.npy")
PDF = os.path.join(REPO, "dokumentacja/04_projekt_zagospodarowania_i_architektura/6. PZT.pdf")
DU = os.path.join(REPO, "prace", "dane_wejsciowe_uzytkownika")

# transformacja v1 (wyciagnij_dane_z_pdf.py)
E0, N0 = 6433700.0, 5659050.0
X0, Y0, KAT, K = 2879.2, 309.7, 7.365944612743048, 72 / 0.0254 / 250
STR_W, STR_H = 4251.96826171875, 2590.8662109375


def wczytaj_raster():
    if not os.path.exists(CACHE):
        import pymupdf
        d = pymupdf.open(PDF)
        xref = d[0].get_images(full=True)[0][0]
        pix = pymupdf.Pixmap(d, xref)
        a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].copy()
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        np.save(CACHE, a)
    return np.load(CACHE)


A = wczytaj_raster()
SX, SY = A.shape[1] / STR_W, A.shape[0] / STR_H  # px na pt
c, s = math.cos(math.radians(KAT)), math.sin(math.radians(KAT))


def pl_do_px(E, N):
    dE, dN = E - E0, N - N0
    dx, dy = c * dE - s * dN, -s * dE - c * dN
    return (X0 + K * dx) * SX, (Y0 + K * dy) * SY


def px_na_m():
    return K * SX  # px na metr


def maska(nazwa):
    a = A.astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if nazwa == "czerwona":
        return (r > 170) & (g < 90) & (b < 100)
    if nazwa == "fiolet":
        return (r > 50) & (r < 150) & (g < 50) & (b > 25) & (b < 110) & (r > b)
    if nazwa == "ciemna":
        return (r < 110) & (g < 110) & (b < 110)
    raise ValueError(nazwa)


def profil_boku(M, p, q, zakres=3.0, krok=0.05, odstep=0.25, margines=0.15):
    """Udział pikseli maski wzdłuż odcinka p-q (PL-2000) przesuniętego o d [m] w lewo (+) / prawo (-)."""
    (e1, n1), (e2, n2) = p, q
    L = math.hypot(e2 - e1, n2 - n1)
    ue, un = (e2 - e1) / L, (n2 - n1) / L
    ne, nn = -un, ue  # normalna w lewo
    ts = np.arange(margines * L, (1 - margines) * L, odstep)
    wyn = []
    for d in np.arange(-zakres, zakres + 1e-9, krok):
        E = e1 + ue * ts + ne * d
        N = n1 + un * ts + nn * d
        xs, ys = pl_do_px(E, N)
        xi, yi = np.round(xs).astype(int), np.round(ys).astype(int)
        ok = (xi >= 0) & (yi >= 0) & (xi < M.shape[1]) & (yi < M.shape[0])
        wyn.append((round(float(d), 2), float(M[yi[ok], xi[ok]].mean()) if ok.any() else 0.0))
    return wyn


def najlepsze(profil):
    d, v = max(profil, key=lambda t: t[1])
    return d, v


def krzyze():
    """Przewidziane krzyże siatki 50 m w obrębie rysunku i wykryte środki (ciemne ramiona)."""
    M = maska("ciemna")
    wyn = []
    pm = px_na_m()
    for i in range(-6, 5):
        for j in range(-6, 3):
            E, N = E0 + 50 * i, N0 + 50 * j
            x, y = pl_do_px(E, N)
            if not (3000 < x < A.shape[1] - 200 and 200 < y < A.shape[0] - 200):
                continue
            # okno +-3 m; współrzędne lokalne w kierunkach E i N (w metrach)
            R = int(3 * pm)
            ys, xs = np.mgrid[int(y) - R:int(y) + R + 1, int(x) - R:int(x) + R + 1]
            m = M[ys, xs]
            if m.sum() < 20:
                continue
            dxp, dyp = (xs - x) / pm, (ys - y) / pm  # metry w osiach strony (y w dół)
            # osie siatki w układzie strony: kierunek E -> (c, -s) w (x, y) strony? z transformacji odwrotnej:
            # dx = c dE - s dN ; dy = -s dE - c dN  => wektor E na stronie = (c, -s), wektor N = (-s, -c)
            uE = dxp * c - dyp * s          # współrzędna wzdłuż E
            uN = -dxp * s - dyp * c         # współrzędna wzdłuż N
            # ramię wzdłuż E: piksele skupione przy stałym uN; ramię wzdłuż N: przy stałym uE
            h_n, kraw = np.histogram(uN[m], bins=60, range=(-3, 3))
            h_e, _ = np.histogram(uE[m], bins=60, range=(-3, 3))
            sr = (kraw[:-1] + kraw[1:]) / 2
            if h_n.max() < 8 or h_e.max() < 8:
                continue
            wyn.append({"E": E, "N": N, "przes_E_m": float(sr[np.argmax(h_e)]), "przes_N_m": float(sr[np.argmax(h_n)]),
                        "sila": int(min(h_n.max(), h_e.max()))})
    return wyn


def main():
    raport = {}
    print("Raster %d x %d px, %.4f px/pt, %.3f px/m (1 px = %.1f cm)" % (A.shape[1], A.shape[0], SX, px_na_m(), 100 / px_na_m()))
    print("\n=== 1. Krzyże siatki 50 m (przewidziane z transformacji v1 vs wykryte w rastrze)")
    kr = krzyze()
    for k in kr:
        print("  E=%d N=%d: przesunięcie wykrytego środka dE=%+.2f m, dN=%+.2f m (siła %d)" % (k["E"], k["N"], k["przes_E_m"], k["przes_N_m"], k["sila"]))
    if kr:
        print("  średnio dE=%+.2f m, dN=%+.2f m (n=%d)" % (np.mean([k["przes_E_m"] for k in kr]), np.mean([k["przes_N_m"] for k in kr]), len(kr)))
    raport["krzyze"] = kr

    gr = [tuple(map(float, l.split())) for l in open(os.path.join(DU, "wierzcholki_polilinii_granica_działki_checked.txt"), encoding="utf-8") if l.strip()]
    print("\n=== 2. Granica działki użytkownika vs czerwona linia PZT (przesunięcie + = w lewo od kierunku boku)")
    Mr = maska("czerwona")
    raport["granica"] = []
    for i in range(len(gr)):
        p, q = gr[i], gr[(i + 1) % len(gr)]
        L = math.dist(p, q)
        if L < 4:
            print("  bok %2d (%.1f m) – za krótki" % (i + 1, L))
            continue
        pr = profil_boku(Mr, p, q)
        d, v = najlepsze(pr)
        v0 = dict(pr)[0.0]
        print("  bok %2d (%.1f m): linia PZT przy d=%+.2f m (udział %.2f; przy d=0: %.2f)" % (i + 1, L, d, v, v0))
        raport["granica"].append({"bok": i + 1, "dl": round(L, 2), "d": d, "udzial": round(v, 3)})

    hale, cur = {}, None
    for l in open(os.path.join(DU, "wierzcholki_polilinii_hala1-8_checked.txt"), encoding="utf-8"):
        t = l.strip()
        if not t:
            continue
        if t.startswith("hala"):
            cur = int(t[4:]); hale[cur] = []
        else:
            hale[cur].append(tuple(map(float, t.split())))
    print("\n=== 3. Obrysy hal użytkownika vs fioletowa linia 'obrys kondygnacji garażu' na PZT")
    Mf = maska("fiolet")
    raport["hale"] = {}
    for nr, pts in hale.items():
        wyn = []
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            L = math.dist(p, q)
            if L < 4:
                continue
            pr = profil_boku(Mf, p, q)
            d, v = najlepsze(pr)
            wyn.append((i + 1, round(L, 2), d, round(v, 3), round(dict(pr)[0.0], 3)))
        raport["hale"][nr] = wyn
        print("  hala %d: " % nr + "; ".join("bok %d (%.1f m): d=%+.2f (udz. %.2f, przy 0: %.2f)" % w for w in wyn))
    json.dump(raport, open(os.path.join(HERE, "pzt_raster_kontrola.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

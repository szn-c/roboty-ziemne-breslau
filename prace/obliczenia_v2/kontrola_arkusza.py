"""
Niezależna kontrola arkusza: pozycje WYNIK liczone w Pythonie wprost z wyniki.json (bez formuł arkusza)
porównane z wartościami policzonymi z formuł biblioteką 'formulas'. Zwraca (liczba porównań, maks. różnica, wiersze).
"""
import json
import math
import os

import dane as D
import silnik as S

HERE = os.path.dirname(os.path.abspath(__file__))


def oczekiwane(wb_rej=None, decyzja=None):
    W = json.load(open(os.path.join(HERE, "wyniki.json"), encoding="utf-8"))
    r3 = lambda v: round(v + 0.0, 3)
    out = {}
    fund = 0.0
    for naz, (a, b, dk, ref) in S.ELEMENTY.items():
        h = ref - dk
        A1, A2 = a * b, (a + 1.0) * (b + 1.0)
        v1 = r3(h / 3 * (A1 + A2 + math.sqrt(A1 * A2)))
        fund += r3(v1 * sum(S.LICZBY[bn].get(naz, 0) for bn in S.LICZBY))
    fund = r3(fund)
    for war, col in (("A", "C"), ("B", "D")):
        w = W["warianty"][war]
        P = lambda z: r3(sum(w["wykop_m3"][z][k] for k in D.PIASKI))
        G = lambda z: r3(sum(w["wykop_m3"][z][k] for k in D.GLINY))
        h_zdj = r3(W["humus_m3"]); h_odk = min(h_zdj, r3(0.25 * 6443.06 * 1.10)); h_wyw = r3(h_zdj - h_odk)
        n_wyw = r3(W["nasyp_m3"])
        g_hal = r3(P("H") + G("H")); g_ogr = r3(P("O") + G("O")); g_odk = r3(sum(P(z) + G(z) for z in "RZU"))
        g_raz = r3(g_hal + g_ogr + g_odk)
        zz = lambda kl: r3(sum(r3(v) for v in w["zapotrzebowanie"][kl].values()))
        z_raz = r3(zz("rodzimy_Z") + zz("rodzimy_U") + zz("rodzimy_R"))
        z_mroz = zz("niewysadzinowy_U")
        d_wbud = decyzja[war] if decyzja else r3(min(g_odk, z_raz))
        x_gr = r3(g_raz - d_wbud); x_raz = r3(h_wyw + n_wyw + x_gr + fund)
        y_gr = r3(z_raz - d_wbud); y_raz = r3(y_gr + z_mroz)
        k1 = r3(h_zdj + n_wyw + g_raz + fund - (x_raz + h_odk + d_wbud))
        k2 = r3(z_raz + z_mroz - (d_wbud + y_gr + z_mroz))
        out.update({("h_zdj", col): h_zdj, ("h_odk", col): h_odk, ("h_wyw", col): h_wyw, ("n_wyw", col): n_wyw, ("g_hal", col): g_hal, ("g_ogr", col): g_ogr,
                    ("g_odk", col): g_odk, ("g_raz", col): g_raz, ("g_fund", col): fund, ("z_raz", col): z_raz, ("z_mroz", col): z_mroz,
                    ("x_gr", col): x_gr, ("x_raz", col): x_raz, ("y_gr", col): y_gr, ("y_mroz", col): z_mroz, ("y_raz", col): y_raz, ("k_1", col): k1, ("k_2", col): k2})
    return out


def propozycja():
    """Domyślna decyzja (poz. 5.4) = MIN(dostępne, zapotrzebowanie) z tych samych zaokrąglonych składników co arkusz."""
    oc = oczekiwane()
    return {"A": min(oc[("g_odk", "C")], oc[("z_raz", "C")]), "B": min(oc[("g_odk", "D")], oc[("z_raz", "D")])}


def porownaj(wart, rej):
    R = rej["WYNIK"]
    oc = oczekiwane()
    n, mx, wiersze = 0, 0.0, []
    for (kl, col), v in oc.items():
        a = wart.get(("WYNIK", "%s%d" % (col, R.adr[kl])))
        d = abs(float(a) - v) if a is not None else float("inf")
        n += 1; mx = max(mx, d)
        wiersze.append((kl, col, v, a, d))
    return n, mx, wiersze

"""Uproszczony bilans - JEDEN wariant: wykop w scianie szczelnej (caly obszar w scianke, sciany pionowe, dno 121,97).
Zalozenia uzytkownika: brak dowozu gruntu, caly grunt z wykopu nadaje sie do ponownego wbudowania.
Dane z modelu zaokraglone, wyniki zaokraglone (m3 do 100, tony do 1000).
Ten modul odwzorowuje wzory z arkusza Excel - sluzy do kontroli arkusza (kontrola/weryfikuj_prosty.py)."""
import math

from bilans_formuly import wczytaj

ZAL = dict(
    humus_potrzeba=1900.0,   # m3 humusu wracajacego do zieleni (6 443 m2 x 0,25 + geokrata, +10%)
    zakres_poza=1.0,         # czesc dzialki poza scianka, z ktorej zdejmuje sie humus
    przydatny=1.0,           # jaka czesc gruntu mineralnego z wykopu nadaje sie do wbudowania
    dno_zm=0.0,              # zmiana dna [m]
    fg_w=125.80, fg_poza=125.50, t=0.35,
    ks=dict(humus=1.25, nasyp=1.25, glina=1.30),
    ro=dict(humus=1.50, nasyp=1.80, glina=2.10),
)


def r(x, krok):
    """Zaokraglenie 'jak w Excelu' (polowka w gore) do wielokrotnosci kroku, np. 100 albo 1000."""
    return math.floor(x / krok + 0.5) * krok


def dane_zaokraglone(R=None):
    R = R or wczytaj()
    Z, s = R["zone"], R["scenariusze"]["B"]
    r10 = lambda v: r(v, 10)
    return dict(
        pole=r10(s["pole_wykopu"]), hale=r10(s["pole_hal_w_wykopie"]), Vb=r10(s["V_brutto"]), Vhn=r10(s["V_humus_nasyp_w_wykopie"]),
        pole_dz=25290.0, humus_W=r10(Z["humus_w_scianie"]), humus_poza=r10(Z["humus_poza_scianka"]),
        nasyp_W=r10(Z["nasyp_w_scianie"]), nasyp_poza=r10(Z["nasyp_poza_scianka"]),
        S0_poza=round(Z["srednia_S0_poza"], 2), dno0=R["DNO"])


def oblicz(D=None, z=None):
    D = D or dane_zaokraglone()
    z = dict(ZAL, **(z or {}))
    ks, ro = z["ks"], z["ro"]
    o = {}
    pole_poza = D["pole_dz"] - D["pole"]
    o["h_razem"] = D["humus_W"] + D["humus_poza"] * z["zakres_poza"]
    o["h_odkl"] = min(o["h_razem"], z["humus_potrzeba"])
    o["h_wyw"] = o["h_razem"] - o["h_odkl"]
    o["nas"] = D["nasyp_W"] + D["nasyp_poza"] * z["zakres_poza"]
    o["Vmin"] = (D["Vb"] - z["dno_zm"] * D["pole"]) - D["Vhn"]
    o["przyd"] = o["Vmin"] * z["przydatny"]
    F = z["fg_w"] - z["t"]
    Fo = z["fg_poza"] - z["t"]
    o["d1"] = (D["pole"] - D["hale"]) * (F - (D["dno0"] + z["dno_zm"]))
    o["d2"] = pole_poza * z["zakres_poza"] * max(0.0, Fo - D["S0_poza"])
    o["d"] = o["d1"] + o["d2"]
    o["m_odkl"] = min(o["przyd"], o["d"])
    o["m_nadw"] = o["Vmin"] - o["m_odkl"]
    o["brak"] = max(0.0, o["d"] - o["przyd"])
    o["wyw_luzem"] = o["h_wyw"] * ks["humus"] + o["nas"] * ks["nasyp"] + o["m_nadw"] * ks["glina"]
    o["wyw_tony"] = o["h_wyw"] * ro["humus"] + o["nas"] * ro["nasyp"] + o["m_nadw"] * ro["glina"]
    o["odkl_luzem"] = o["h_odkl"] * ks["humus"] + o["m_odkl"] * ks["glina"]
    # ---- to, co widzi uzytkownik (zaokraglone; sumy = sumy zaokraglonych pozycji)
    v = {}
    v["h_odkl"] = r(o["h_odkl"], 100)
    v["h_wyw"] = r(o["h_wyw"], 100)
    v["h_razem"] = v["h_odkl"] + v["h_wyw"]
    v["nas"] = r(o["nas"], 100)
    v["d"] = r(o["d"], 100)
    v["m_odkl"] = r(o["m_odkl"], 100)
    v["m_nadw"] = r(o["m_nadw"], 100)
    v["m_razem"] = v["m_odkl"] + v["m_nadw"]
    v["odkl"] = v["h_odkl"] + v["m_odkl"]
    v["wyw"] = v["h_wyw"] + v["nas"] + v["m_nadw"]
    v["wyw_luzem"] = r(o["wyw_luzem"], 100)
    v["wyw_tony"] = r(o["wyw_tony"], 1000)
    v["odkl_luzem"] = r(o["odkl_luzem"], 100)
    v["brak"] = r(o["brak"], 100)
    return o, v


if __name__ == "__main__":
    o, v = oblicz()
    for k, x in o.items():
        print("  %-10s %12.1f" % (k, x))
    print()
    for k, x in v.items():
        print("  WIDOCZNE %-10s %10.0f" % (k, x))

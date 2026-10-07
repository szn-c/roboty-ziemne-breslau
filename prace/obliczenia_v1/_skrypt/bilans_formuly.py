"""Bilans mas ziemnych z wynikow modelu (wyniki_bilans.json) i zalozen uzytkownika.
Te same wzory sa w arkuszu Excel (generuj_wynik_xlsx.py) - ten modul sluzy do kontroli arkusza i do podania liczb w opisie.
Wszystkie objetosci: m3 w gruncie rodzimym (w ziemi), chyba ze napisano inaczej."""
import json
import os

KAT = os.path.dirname(os.path.abspath(__file__))

ZALOZENIA = dict(
    dno_zm=0.0,                    # zmiana rzednej dna wzgledem 121,97 [m]; ujemna = glebiej
    zielen_grunt=6443.06,          # PZT, Bilans terenu: zielen na gruncie rodzimym [m2]
    zielen_geokrata=980.05,        # PZT: geokrata na gruncie [m2]
    gr_humus_zielen=0.25,          # m
    gr_humus_geokrata=0.10,        # m
    zielen_strop=3575.11 + 173.70, # PZT: zielen + geokrata na stropie garazu [m2]
    gr_humus_strop=0.0,            # m  (0 = na stropie uklada sie substrat z zewnatrz)
    zapas_humusu=0.10,
    zakres_humusu_poza=1.0,        # jaka czesc humusu z reszty dzialki (poza scianka) jest zdejmowana
    sprawnosc_piasku=0.90,
    udzial_gliny_suchej=0.0,
    fg_miedzy=125.77,              # m npm - srednia z 12 rzednych projektowych miedzy halami (PZT)
    fg_poza=125.52,                # m npm - srednia z 22 rzednych projektowych poza scianka (PZT)
    t_wierzch=0.35,                # m - humus / konstrukcja nawierzchni ponad gruntem z wykopu
    ks=dict(humus=1.25, nasyp=1.25, glina=1.30, piasek=1.15),
    ro=dict(humus=1.50, nasyp=1.80, glina=2.10, piasek=1.90),
)


def wczytaj():
    return json.load(open(os.path.join(KAT, "wyniki_bilans.json"), encoding="utf-8"))


def bilans(wariant, zal=None, R=None):
    z = dict(ZALOZENIA)
    z.update(zal or {})
    R = R or wczytaj()
    Z = R["zone"]
    s = R["scenariusze"][wariant]
    ks, ro = z["ks"], z["ro"]
    out = {}
    # ---- humus (niezalezny od wariantu)
    hum_w = Z["humus_w_scianie"]
    hum_poza = Z["humus_poza_scianka"] * z["zakres_humusu_poza"]
    hum = hum_w + hum_poza
    pop = z["zielen_grunt"] * z["gr_humus_zielen"] + z["zielen_geokrata"] * z["gr_humus_geokrata"] + z["zielen_strop"] * z["gr_humus_strop"]
    hum_odklad = min(hum, pop * (1 + z["zapas_humusu"]))
    hum_wywoz = hum - hum_odklad
    nas = Z["nasyp_w_scianie"] + Z["nasyp_poza_scianka"] * z["zakres_humusu_poza"]
    out.update(humus_w_scianie=hum_w, humus_poza=hum_poza, humus_razem=hum, humus_potrzeba=pop, humus_odklad=hum_odklad,
               humus_wywoz=hum_wywoz, nasyp=nas)
    # ---- wykop
    dno_zm = z["dno_zm"]
    dod = -dno_zm * s["pole_wykopu"]                       # dodatkowy (lub mniejszy) wykop przy zmianie dna
    Vb = s["V_brutto"] + dod
    Vhn = s["V_humus_nasyp_w_wykopie"]
    Vmin = Vb - Vhn
    psel = s["V_piasek_sel_suchy"] + s["V_piasek_sel_mokry"]
    pcien = s["V_piasek_cienki_suchy"] + s["V_piasek_cienki_mokry"]
    gsuch = s["V_glina_sucha"]
    gmokr = s["V_glina_mokra"] + dod                        # dodatkowa warstwa = glina pod zwierciadlem
    assert abs((psel + pcien + gsuch + gmokr) - Vmin) < 1.0, (psel + pcien + gsuch + gmokr, Vmin)
    re_p = psel * z["sprawnosc_piasku"]
    re_g = gsuch * z["udzial_gliny_suchej"]
    odklad_min = re_p + re_g
    wywoz_min = Vmin - odklad_min
    w_piasek = psel * (1 - z["sprawnosc_piasku"])
    w_glina = wywoz_min - w_piasek
    out.update(V_brutto=Vb, V_humus_nasyp_w_wykopie=Vhn, V_mineralny=Vmin, piasek_sel=psel, piasek_cienki=pcien,
               glina_sucha=gsuch, glina_mokra=gmokr, odklad_piasek=re_p, odklad_glina=re_g, odklad_min=odklad_min,
               wywoz_min=wywoz_min, wywoz_piasek=w_piasek, wywoz_glina=w_glina)
    # ---- zapotrzebowanie na grunt (zasypki + podniesienie terenu)
    F = z["fg_miedzy"] - z["t_wierzch"]
    dno = R["DNO"] + dno_zm
    zsr = s["srednia_z_wykopu"] + dno_zm
    d_wykop = s["pole_wykopu"] * (F - zsr) - s["pole_hal_w_wykopie"] * (F - dno)
    d_poza_wykopu = s["pole_w_scianie_poza_wykopem"] * (F - s["srednia_S0_poza_wykopem"])
    Fo = z["fg_poza"] - z["t_wierzch"]
    d_dzialka = Z["pole_poza_scianka_oficjalne"] * z["zakres_humusu_poza"] * max(0.0, Fo - Z["srednia_S0_poza"])
    D = d_wykop + d_poza_wykopu + d_dzialka
    import_ = max(0.0, D - odklad_min)
    out.update(zapotrz_wykop=d_wykop, zapotrz_w_scianie_poza_wykopem=d_poza_wykopu, zapotrz_poza_scianka=d_dzialka,
               zapotrzebowanie=D, import_=import_)
    # ---- razem
    out["odklad_razem"] = hum_odklad + odklad_min
    out["wywoz_razem"] = hum_wywoz + nas + wywoz_min
    # ---- luzem i tony
    loose = lambda h, n, g, p: h * ks["humus"] + n * ks["nasyp"] + g * ks["glina"] + p * ks["piasek"]
    tons = lambda h, n, g, p: h * ro["humus"] + n * ro["nasyp"] + g * ro["glina"] + p * ro["piasek"]
    out["wywoz_luzem"] = loose(hum_wywoz, nas, w_glina, w_piasek)
    out["wywoz_tony"] = tons(hum_wywoz, nas, w_glina, w_piasek)
    out["odklad_luzem"] = loose(hum_odklad, 0, re_g, re_p)
    out["odklad_tony"] = tons(hum_odklad, 0, re_g, re_p)
    out["wywoz_humus_luzem"] = hum_wywoz * ks["humus"]
    out["wywoz_humus_tony"] = hum_wywoz * ro["humus"]
    out["wywoz_min_luzem"] = w_glina * ks["glina"] + w_piasek * ks["piasek"]
    out["wywoz_min_tony"] = w_glina * ro["glina"] + w_piasek * ro["piasek"]
    out["import_luzem"] = import_ * 1.15
    return out


if __name__ == "__main__":
    R = wczytaj()
    for w in ("C15", "B", "A0"):
        o = bilans(w, R=R)
        print("=== wariant", w)
        for k, v in o.items():
            print("  %-34s %10.0f" % (k, v))

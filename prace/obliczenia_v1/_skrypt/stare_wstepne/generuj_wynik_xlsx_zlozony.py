"""Buduje arkusz 00_WYNIKI/BILANS_ROBOT_ZIEMNYCH_dz190.xlsx (wzory zywe - zmieniasz zolte pola, wynik przelicza sie sam)."""
import json
import os
import sys

import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bilans_formuly import ZALOZENIA, bilans, wczytaj  # noqa: E402
from eg_model import geometria, zbuduj  # noqa: E402
from generuj_pliki import OTWORY, OUT  # noqa: E402

R = wczytaj()
Z = R["zone"]
SC = R["scenariusze"]
KAT_WYNIK = os.path.join(OUT, "00_WYNIKI")
os.makedirs(KAT_WYNIK, exist_ok=True)
SCIEZKA = os.path.join(KAT_WYNIK, "BILANS_ROBOT_ZIEMNYCH_dz190.xlsx")

ZOLTY = PatternFill("solid", fgColor="FFF2CC")
SZARY = PatternFill("solid", fgColor="D9D9D9")
ZIELONY = PatternFill("solid", fgColor="E2EFDA")
JASNY = PatternFill("solid", fgColor="F2F2F2")
NIEB = PatternFill("solid", fgColor="DDEBF7")
B = Font(bold=True)
cienka = Side(style="thin", color="999999")
RAMKA = Border(left=cienka, right=cienka, top=cienka, bottom=cienka)
WRAP = Alignment(wrap_text=True, vertical="top")

wb = Workbook()

# =============================================================================== ZALOZENIA
wz = wb.active
wz.title = "ZALOZENIA"
for c, w in zip("ABCDEF", (5, 70, 16, 10, 16, 16)):
    wz.column_dimensions[c].width = w
wz.column_dimensions["G"].width = 90
wz["A1"] = "ZAŁOŻENIA – żółte pola możesz zmieniać, wyniki w arkuszu WYNIK przeliczą się same"
wz["A1"].font = Font(bold=True, size=13)
ZR = {}  # nazwa -> adres z nazwa arkusza


def zrow(r, klucz, opis, wart, jedn, uw, edytowalne=True, fmt="#,##0.00"):
    wz.cell(r, 1, r - 3)
    wz.cell(r, 2, opis).alignment = WRAP
    c = wz.cell(r, 3, wart)
    c.number_format = fmt
    c.border = RAMKA
    c.fill = ZOLTY if edytowalne else JASNY
    wz.cell(r, 4, jedn)
    wz.cell(r, 7, uw).alignment = WRAP
    ZR[klucz] = f"ZALOZENIA!$C${r}"


wz["B3"] = "A. DO WPISANIA / SPRAWDZENIA"
wz["B3"].font = B
zal = ZALOZENIA
zrow(4, "dno_zm", "Zmiana rzędnej dna wykopu względem 121,97 m npm (ujemna = głębiej)", zal["dno_zm"], "m",
     "Dno 121,97 = posadzka 122,57 − płyta 0,50 − chudy beton 0,10. Jeśli projekt konstrukcji przewiduje podsypkę pod chudziakiem, wpisz np. −0,20. Każde −0,10 m to ok. 1 600 m³ (wariant A) / 2 100 m³ (wariant B).")
zrow(5, "zielen_grunt", "Zieleń na gruncie rodzimym (wymaga humusu)", zal["zielen_grunt"], "m²", "PZT, tabela Bilans terenu: 6 443,06 m²")
zrow(6, "zielen_geokrata", "Geokrata na gruncie (wypełnienie humusem)", zal["zielen_geokrata"], "m²", "PZT: 980,05 m²")
zrow(7, "gr_humus_zielen", "Grubość humusu rozścielanego w zieleni", zal["gr_humus_zielen"], "m", "ZAŁOŻENIE: trawnik 0,15–0,20 m, krzewy/drzewa 0,40 m. Sprawdź w projekcie zieleni.")
zrow(8, "gr_humus_geokrata", "Grubość humusu w geokracie", zal["gr_humus_geokrata"], "m", "ZAŁOŻENIE")
zrow(9, "zielen_strop", "Zieleń na stropie garażu (z geokratą na stropie)", zal["zielen_strop"], "m²", "PZT: 3 575,11 + 173,70 m²")
zrow(10, "gr_humus_strop", "Grubość humusu z odkładu układanego na stropie garażu", zal["gr_humus_strop"], "m",
     "0 = na stropie idzie substrat kupiony. Jeśli projekt zieleni dopuszcza ziemię z budowy, wpisz np. 0,30 (= ok. +1 100 m³ na odkład).")
zrow(11, "zapas_humusu", "Zapas humusu na odkładzie", zal["zapas_humusu"], "", "straty, osiadanie", fmt="0%")
zrow(12, "zakres_humusu_poza", "Jaka część działki POZA ścianką też będzie odhumusowana", zal["zakres_humusu_poza"], "",
     "100% = cała działka 1/90. Jeśli pas poza ścianką zostaje nietknięty, wpisz 0%.", fmt="0%")
zrow(13, "sprawnosc_piasku", "Sprawność selektywnego wybrania piasku (reszta miesza się z gliną)", zal["sprawnosc_piasku"], "", "ZAŁOŻENIE", fmt="0%")
zrow(14, "udzial_gliny_suchej", "Jaka część SUCHEJ gliny (nad zwierciadłem wody) trafia na odkład do nasypów", zal["udzial_gliny_suchej"], "",
     "0% = cała glina na wywóz (bezpiecznie). Zmień dopiero po opinii geotechnika. Gliny mokre (pod zwierciadłem) nigdy nie są brane.", fmt="0%")
zrow(15, "fg_miedzy", "Rzędna terenu projektowanego między halami (średnia)", zal["fg_miedzy"], "m npm", "średnia z 12 rzędnych projektowych między halami na PZT (zakres 125,40–125,98)")
zrow(16, "fg_poza", "Rzędna terenu projektowanego poza ścianką (średnia)", zal["fg_poza"], "m npm", "średnia z 22 rzędnych na PZT (zakres 124,40–125,96; duży rozrzut – wartość orientacyjna)")
zrow(17, "t_wierzch", "Grubość warstw wierzchnich nie z wykopu (humus / konstrukcja nawierzchni)", zal["t_wierzch"], "m",
     "ZAŁOŻENIE: zieleń 0,25 m, nawierzchnie 0,45–0,55 m. Każde 0,10 m to ok. 2 000 m³ zapotrzebowania.")

wz["B19"] = "B. WSPÓŁCZYNNIKI PRZELICZENIOWE"
wz["B19"].font = B
for c, t in zip("CDEF", ("Humus", "Nasyp", "Glina", "Piasek")):
    wz[f"{c}20"] = t
    wz[f"{c}20"].font = B
    wz[f"{c}20"].fill = SZARY
wz["B21"] = "Współczynnik spulchnienia (m³ luzem / m³ w ziemi)"
wz["B22"] = "Gęstość w gruncie rodzimym [t/m³]"
for col, kk, kr in zip("CDEF", ("humus", "nasyp", "glina", "piasek"), ("humus", "nasyp", "glina", "piasek")):
    for r, v in ((21, zal["ks"][kk]), (22, zal["ro"][kr])):
        c = wz[f"{col}{r}"]
        c.value = v
        c.fill = ZOLTY
        c.border = RAMKA
        c.number_format = "0.00"
wz["G21"] = "wartości typowe – zweryfikuj z wykonawcą transportu"
wz["G22"] = "glina 2,0–2,25 i piaski 1,75–2,05 wg DGI; humus i nasyp – przyjęte typowo"
KS = {k: f"ZALOZENIA!${c}$21" for k, c in zip(("humus", "nasyp", "glina", "piasek"), "CDEF")}
RO = {k: f"ZALOZENIA!${c}$22" for k, c in zip(("humus", "nasyp", "glina", "piasek"), "CDEF")}

wz["B24"] = "C. Z MODELU (geometria z rysunku projektanta + otwory) – nie zmieniaj"
wz["B24"].font = B
zrow(25, "pole_W", "Pole w obrysie ścianki (wielokąt z rzutu zabezpieczenia)", round(Z["pole_scianki_wielokat"], 1), "m²", "obwód %.1f m (opis na rysunku: ok. 565 mb)" % Z["obwod_scianki"], False, "#,##0.0")
zrow(26, "pole_hal", "Pole 8 hal garażowych (obrys zewnętrzny)", round(Z["suma_hal"], 1), "m²", "hale 1–8: " + ", ".join("%.0f" % Z["pola_hal"][str(i)] for i in range(1, 9)), False, "#,##0.0")
zrow(27, "pole_dz", "Pole działki 1/90 (oficjalne)", Z["pole_dzialki_oficjalne"], "m²", "PZT, Bilans terenu. Granica z rysunku daje %.0f m² (+%.1f%%) – do obliczeń użyto wartości oficjalnej." % (Z["pole_dzialki_rysunek"], 100 * (Z["pole_dzialki_rysunek"] / Z["pole_dzialki_oficjalne"] - 1)), False, "#,##0.00")
zrow(28, "pole_poza", "Pole działki poza obrysem ścianki", f"={ZR['pole_dz'].split('!')[1]}-{ZR['pole_W'].split('!')[1]}", "m²", "pole działki minus pole w ściance", False, "#,##0.0")
zrow(29, "hum_W", "Humus w obrysie ścianki", round(Z["humus_w_scianie"], 0), "m³", "średnia grubość %.3f m (17 otworów, interpolacja w siatce 0,5 m)" % Z["srednia_grub_humusu_w_scianie"], False, "#,##0")
zrow(30, "hum_poza", "Humus na reszcie działki (poza ścianką) przy 100% zakresu", round(Z["humus_poza_scianka"], 0), "m³", "średnia grubość %.3f m × pole poza ścianką" % Z["srednia_grub_humusu_poza"], False, "#,##0")
zrow(31, "nas_W", "Nasyp niekontrolowany w obrysie ścianki", round(Z["nasyp_w_scianie"], 0), "m³", "tylko otwory 5, 17, 20 (0,2–0,3 m) – wynik bardzo niepewny (±50%)", False, "#,##0")
zrow(32, "nas_poza", "Nasyp niekontrolowany poza ścianką przy 100% zakresu", round(Z["nasyp_poza_scianka"], 0), "m³", "", False, "#,##0")
zrow(33, "S0_poza", "Średnia rzędna wierzchu gruntu mineralnego poza ścianką", round(Z["srednia_S0_poza"], 3), "m npm", "teren istniejący minus humus i nasyp", False, "0.000")
zrow(34, "dno0", "Rzędna dna wykopu bazowa", R["DNO"], "m npm", "", False, "0.00")
# formula C28 uses local refs
wz["C28"] = "=C27-C25"

# =============================================================================== DANE_MODEL
wd = wb.create_sheet("DANE_MODEL")
wd.column_dimensions["A"].width = 5
wd.column_dimensions["B"].width = 62
for c in "CDEF":
    wd.column_dimensions[c].width = 17
wd.column_dimensions["G"].width = 80
wd["A1"] = "DANE Z MODELU (raster 0,5 m) – wartości policzone programem, nie zmieniaj"
wd["A1"].font = Font(bold=True, size=13)
kol_war = {"C": "C15", "D": "B", "E": "A0", "F": "C10"}
naz_war = {"C": "A (skarpy 1:1,5)", "D": "B (cały obszar)", "E": "A0 (ściany pionowe)", "F": "A' (skarpy 1:1)"}
for c, n in naz_war.items():
    wd[f"{c}3"] = "Wariant " + n
    wd[f"{c}3"].font = B
    wd[f"{c}3"].fill = SZARY
    wd[f"{c}3"].alignment = Alignment(wrap_text=True, horizontal="center")
wd.row_dimensions[3].height = 32
wd["B3"] = "Wielkość"
wd["B3"].font = B
wd["B3"].fill = SZARY
DR = {}
pozycje = [
    ("pole", "Pole wykopu (rzut poziomy)", "pole_wykopu", "m²", "#,##0"),
    ("zsr", "Średnia rzędna powierzchni wykopu (dno + skarpy)", "srednia_z_wykopu", "m npm", "0.000"),
    ("hale", "Pole hal w wykopie", "pole_hal_w_wykopie", "m²", "#,##0"),
    ("gl", "Średnia głębokość wykopu od terenu istniejącego", "srednia_glebokosc", "m", "0.00"),
    ("Vb", "Wykop brutto: od terenu istniejącego do dna (z humusem i nasypem)", "V_brutto", "m³", "#,##0"),
    ("Vhn", "w tym humus i nasyp leżące w wykopie", "V_humus_nasyp_w_wykopie", "m³", "#,##0"),
    ("Vmin", "Grunt mineralny pod humusem do wykopania", "V_mineralny", "m³", "#,##0"),
    ("ps_s", "   piasek w grubych warstwach, nad zwierciadłem wody", "V_piasek_sel_suchy", "m³", "#,##0"),
    ("ps_m", "   piasek w grubych warstwach, pod zwierciadłem wody", "V_piasek_sel_mokry", "m³", "#,##0"),
    ("pc_s", "   piasek cienkich przewarstwień, nad zwierciadłem", "V_piasek_cienki_suchy", "m³", "#,##0"),
    ("pc_m", "   piasek cienkich przewarstwień, pod zwierciadłem", "V_piasek_cienki_mokry", "m³", "#,##0"),
    ("gs", "   glina nad zwierciadłem wody (sucha)", "V_glina_sucha", "m³", "#,##0"),
    ("gm", "   glina pod zwierciadłem wody (mokra)", "V_glina_mokra", "m³", "#,##0"),
    ("poza_pole", "Pole w ściance POZA wykopem (teren tylko podnoszony)", "pole_w_scianie_poza_wykopem", "m²", "#,##0"),
    ("poza_S0", "Średnia rzędna gruntu mineralnego tam", "srednia_S0_poza_wykopem", "m npm", "0.000"),
]
for i, (klucz, opis, pole, jedn, fmt) in enumerate(pozycje):
    r = 4 + i
    wd.cell(r, 1, i + 1)
    wd.cell(r, 2, opis)
    for c, w in kol_war.items():
        cell = wd[f"{c}{r}"]
        cell.value = round(SC[w][pole], 3)
        cell.number_format = fmt
        cell.border = RAMKA
        cell.fill = JASNY
    wd.cell(r, 7, jedn)
    DR[klucz] = r
wd["B20"] = "Wariant A/B/A0/A' – patrz arkusz WARIANTY. W wariantach ze skarpami skład gruntu liczony z ułamków dla pełnej głębokości (przybliżenie)."
wd["B20"].alignment = WRAP


def D(klucz, war):  # adres komorki w DANE_MODEL dla wariantu 'A' albo 'B'
    col = {"A": "C", "B": "D"}[war]
    return f"DANE_MODEL!${col}${DR[klucz]}"


# =============================================================================== WYNIK
ww = wb.create_sheet("WYNIK", 0)
ww.column_dimensions["A"].width = 74
ww.column_dimensions["B"].width = 19
ww.column_dimensions["C"].width = 19
ww.column_dimensions["D"].width = 8
ww.column_dimensions["E"].width = 80
ww["A1"] = "BILANS ROBÓT ZIEMNYCH – działka 1/90, obr. Wojszyce, Wrocław"
ww["A1"].font = Font(bold=True, size=15)
ww["A2"] = "Objętości w m³ w gruncie rodzimym (jak w ziemi), o ile nie napisano inaczej. Żółte założenia zmieniasz w arkuszu ZALOZENIA."
ww["A2"].font = Font(italic=True)
ww["A4"] = "WARIANT A – wykop pod halami: obrys hali + 1,0 m przestrzeni roboczej, dalej skarpa 1:1,5 (w obrębie ścianki). Realny wariant, jeśli ścianka jest tylko po obwodzie."
ww["A5"] = "WARIANT B – cały obszar w ściance wykopany do dna (górna granica). Tak czytany jest rzut zabezpieczenia: jeden wspólny wykop."
for c in ("A4", "A5"):
    ww[c].alignment = WRAP
    ww[c].font = B
ww.row_dimensions[4].height = 30
ww.row_dimensions[5].height = 30
for c, t in (("B", "Wariant A"), ("C", "Wariant B")):
    ww[f"{c}7"] = t
    ww[f"{c}7"].font = B
    ww[f"{c}7"].fill = SZARY
    ww[f"{c}7"].alignment = Alignment(horizontal="center")
ww["A7"] = ""
ww["D7"] = "jedn."
ww["E7"] = "Jak to liczymy / uwagi"
for c in ("D7", "E7"):
    ww[c].font = B
    ww[c].fill = SZARY

WR = {}


def wrow(r, klucz, opis, fA, fB=None, jedn="m³", uw="", styl=None, fmt="#,##0"):
    ww.cell(r, 1, opis)
    for col, f in (("B", fA), ("C", fB if fB is not None else fA)):
        c = ww[f"{col}{r}"]
        c.value = f
        c.number_format = fmt
        c.border = RAMKA
        c.fill = ZIELONY if styl != "info" else JASNY
    ww.cell(r, 4, jedn)
    ww.cell(r, 5, uw).alignment = WRAP
    if styl == "bold":
        ww.cell(r, 1).font = B
        ww[f"B{r}"].font = B
        ww[f"C{r}"].font = B
    WR[klucz] = r


def naglowek(r, tekst):
    ww.cell(r, 1, tekst).font = Font(bold=True, size=12)
    for col in "ABCDE":
        ww[f"{col}{r}"].fill = NIEB


def rr(klucz, col):
    return f"{col}{WR[klucz]}"


zr = ZR
naglowek(8, "1. HUMUS (cała działka; ta sama wartość w obu wariantach)")
wrow(9, "h_W", "Humus w obrysie ścianki", f"={zr['hum_W']}", uw="średnia grubość 0,61 m z 17 otworów")
wrow(10, "h_poza", "Humus z reszty działki (poza ścianką)", f"={zr['hum_poza']}*{zr['zakres_humusu_poza']}", uw="pole poza ścianką × zakres zdejmowania z ZALOZENIA")
wrow(11, "h_razem", "HUMUS DO ZEBRANIA – RAZEM", "=B9+B10", "=C9+C10", styl="bold")
wrow(12, "h_pot", "Potrzeba humusu do zieleni (z zapasem)",
     f"=({zr['zielen_grunt']}*{zr['gr_humus_zielen']}+{zr['zielen_geokrata']}*{zr['gr_humus_geokrata']}+{zr['zielen_strop']}*{zr['gr_humus_strop']})*(1+{zr['zapas_humusu']})",
     uw="pola zieleni z PZT × grubość rozścielenia × (1 + zapas)")
wrow(13, "h_odkl", "HUMUS NA ODKŁAD (do ponownego rozścielenia)", "=MIN(B11,B12)", "=MIN(C11,C12)", styl="bold", uw="tyle, ile się zużyje w zieleni")
wrow(14, "h_wyw", "HUMUS DO UTYLIZACJI / WYWOZU", "=B11-B13", "=C11-C13", styl="bold", uw="nadwyżka ponad potrzeby zieleni")
wrow(15, "nas", "NASYP NIEKONTROLOWANY – do utylizacji", f"={zr['nas_W']}+{zr['nas_poza']}*{zr['zakres_humusu_poza']}", uw="warstwa pod humusem w otworach 5, 17, 20; wynik bardzo niepewny")

naglowek(17, "2. RESZTA WYKOPU – grunt mineralny pod humusem i nasypem")
dz = zr["dno_zm"]
wrow(18, "Vb", "Wykop brutto: od terenu istniejącego do dna (razem z humusem)", f"={D('Vb','A')}-{dz}*{D('pole','A')}", f"={D('Vb','B')}-{dz}*{D('pole','B')}", styl="info", uw="dno 121,97 m npm (+ zmiana z ZALOZENIA)")
wrow(19, "Vhn", "   minus humus i nasyp leżące w wykopie (liczone wyżej)", f"={D('Vhn','A')}", f"={D('Vhn','B')}", styl="info")
wrow(20, "Vmin", "GRUNT MINERALNY DO WYKOPANIA", "=B18-B19", "=C18-C19", styl="bold")
wrow(21, "ps", "   w tym piasek w grubych warstwach (można wybrać osobno)", f"={D('ps_s','A')}+{D('ps_m','A')}", f"={D('ps_s','B')}+{D('ps_m','B')}", uw="warstwy piasku ≥ 0,5 m; po odwodnieniu nadają się do zasypek")
wrow(22, "pc", "   w tym piasek w cienkich przewarstwieniach (miesza się z gliną)", f"={D('pc_s','A')}+{D('pc_m','A')}", f"={D('pc_s','B')}+{D('pc_m','B')}")
wrow(23, "gs", "   w tym glina SUCHA (nad zwierciadłem wody)", f"={D('gs','A')}", f"={D('gs','B')}", uw="możliwa do rozważenia na nasypy nieobciążone – tylko za zgodą geotechnika")
wrow(24, "gm", "   w tym glina MOKRA (pod zwierciadłem wody)", f"={D('gm','A')}-{dz}*{D('pole','A')}", f"={D('gm','B')}-{dz}*{D('pole','B')}", uw="nie do ponownego wbudowania")
wrow(25, "kontrola", "   kontrola: suma składników minus grunt mineralny (ma być 0)", "=ROUND(B21+B22+B23+B24-B20,0)", "=ROUND(C21+C22+C23+C24-C20,0)", styl="info")
wrow(26, "odk_p", "NA ODKŁAD – piasek", f"=B21*{zr['sprawnosc_piasku']}", f"=C21*{zr['sprawnosc_piasku']}")
wrow(27, "odk_g", "NA ODKŁAD – glina sucha (tylko jeśli dopuszczona w ZALOZENIA)", f"=B23*{zr['udzial_gliny_suchej']}", f"=C23*{zr['udzial_gliny_suchej']}")
wrow(28, "odk_min", "NA ODKŁAD – grunt mineralny RAZEM", "=B26+B27", "=C26+C27", styl="bold")
wrow(29, "wyw_min", "DO UTYLIZACJI / WYWOZU – grunt mineralny", "=B20-B28", "=C20-C28", styl="bold", uw="gliny mokre, gliny suche (jeśli niedopuszczone), piasek zmieszany z gliną")

naglowek(31, "3. ZAPOTRZEBOWANIE NA GRUNT (zasypki + podniesienie terenu do rzędnych projektowych) – wartości orientacyjne")
F = f"({zr['fg_miedzy']}-{zr['t_wierzch']})"
Fo = f"({zr['fg_poza']}-{zr['t_wierzch']})"
dno_e = f"({zr['dno0']}+{dz})"
wrow(32, "d_w", "Zasypki w wykopie wokół hal (od dna do rzędnej proj. minus warstwy wierzchnie)",
     f"={D('pole','A')}*({F}-({D('zsr','A')}+{dz}))-{D('hale','A')}*({F}-{dno_e})",
     f"={D('pole','B')}*({F}-({D('zsr','B')}+{dz}))-{D('hale','B')}*({F}-{dno_e})",
     uw="nad halami nie liczymy gruntu (strop + warstwy proj.)")
wrow(33, "d_p", "Podniesienie terenu w ściance poza wykopem",
     f"={D('poza_pole','A')}*({F}-{D('poza_S0','A')})", f"={D('poza_pole','B')}*({F}-{D('poza_S0','B')})",
     uw="teren jest podnoszony o ok. 1,2 m względem istniejącego")
wrow(34, "d_d", "Podniesienie terenu poza ścianką (reszta działki)",
     f"={zr['pole_poza']}*{zr['zakres_humusu_poza']}*MAX(0,{Fo}-{zr['S0_poza']})", uw="bardzo orientacyjne (rzędne proj. poza ścianką mocno się różnią)")
wrow(35, "d_r", "ZAPOTRZEBOWANIE RAZEM", "=B32+B33+B34", "=C32+C33+C34", styl="bold")
wrow(36, "d_z", "   pokryte z własnego wykopu (odkład z poz. 2)", "=B28", "=C28", styl="info")
wrow(37, "imp", "GRUNT DO DOWIEZIENIA (import)", "=MAX(0,B35-B36)", "=MAX(0,C35-C36)", styl="bold", uw="np. piasek/pospółka z kopalni; m³ po zagęszczeniu w nasypie")

naglowek(39, "4. PODSUMOWANIE")
wrow(40, "s_odk", "RAZEM NA ODKŁAD (humus + grunt) [m³ w ziemi]", "=B13+B28", "=C13+C28", styl="bold")
wrow(41, "s_wyw", "RAZEM DO UTYLIZACJI / WYWOZU [m³ w ziemi]", "=B14+B15+B29", "=C14+C15+C29", styl="bold")
wrow(42, "s_wh", "   w tym humus", "=B14", "=C14", styl="info")
wrow(43, "s_wn", "   w tym nasyp niekontrolowany", "=B15", "=C15", styl="info")
wrow(44, "s_wm", "   w tym grunt mineralny", "=B29", "=C29", styl="info")
wrow(45, "w_p", "   (pomocniczo) piasek w wywozie = piasek niewybrany", f"=B21*(1-{zr['sprawnosc_piasku']})", f"=C21*(1-{zr['sprawnosc_piasku']})", styl="info")
wrow(46, "w_g", "   (pomocniczo) reszta gruntu mineralnego w wywozie (jak glina)", "=B29-B45", "=C29-C45", styl="info")
wrow(47, "s_wl", "RAZEM DO UTYLIZACJI / WYWOZU [m³ luzem]",
     f"=B14*{KS['humus']}+B15*{KS['nasyp']}+B46*{KS['glina']}+B45*{KS['piasek']}",
     f"=C14*{KS['humus']}+C15*{KS['nasyp']}+C46*{KS['glina']}+C45*{KS['piasek']}", styl="bold", uw="do planowania transportu (samochody)")
wrow(48, "s_wt", "RAZEM DO UTYLIZACJI / WYWOZU [tony]",
     f"=B14*{RO['humus']}+B15*{RO['nasyp']}+B46*{RO['glina']}+B45*{RO['piasek']}",
     f"=C14*{RO['humus']}+C15*{RO['nasyp']}+C46*{RO['glina']}+C45*{RO['piasek']}", jedn="t", styl="bold")
wrow(49, "s_ol", "RAZEM NA ODKŁADZIE [m³ luzem]",
     f"=B13*{KS['humus']}+B26*{KS['piasek']}+B27*{KS['glina']}", f"=C13*{KS['humus']}+C26*{KS['piasek']}+C27*{KS['glina']}", uw="wielkość hałd do zaplanowania na placu (teren poza ścianką jest ciasny)")
wrow(50, "s_ot", "RAZEM NA ODKŁADZIE [tony]",
     f"=B13*{RO['humus']}+B26*{RO['piasek']}+B27*{RO['glina']}", f"=C13*{RO['humus']}+C26*{RO['piasek']}+C27*{RO['glina']}", jedn="t")
wrow(51, "k_bil", "Kontrola bilansu: wykop+humus+nasyp = odkład + wywóz (ma być 0)",
     "=ROUND(B11+B15+B20-B40-B41,0)", "=ROUND(C11+C15+C20-C40-C41,0)", styl="info")

naglowek(53, "5. NIEPEWNOŚĆ – co ile zmienia wynik")
wrow(54, "n1", "Każde 10 cm głębokości wykopu (dno niżej/wyżej)", f"={D('pole','A')}*0.1", f"={D('pole','B')}*0.1", uw="np. podsypka pod chudziakiem, zagłębienia pod windy, rzędna dna")
wrow(55, "n2", "Model terenu istniejącego: ±0,02 m", f"={D('pole','A')}*0.02", f"={D('pole','B')}*0.02", uw="teren z pomiaru geodezyjnego (PZT) + otwory; siatka 10 m z rzutu była zawyżona o ok. 0,1 m")
wrow(56, "n3", "Humus: błąd średniej grubości ±0,03 m (1 odch. std.) – cała działka", f"=({zr['pole_W']}+{zr['pole_poza']}*{zr['zakres_humusu_poza']})*0.031", f"=({zr['pole_W']}+{zr['pole_poza']}*{zr['zakres_humusu_poza']})*0.031", uw="17 otworów, grubość 0,4–0,8 m; interpolacja nie poprawia średniej (brak korelacji przestrzennej)")
wrow(57, "n4", "Glina sucha, którą geotechnik może dopuścić do nasypów (potencjał)", "=B23", "=C23", uw="tyle mniej wywozu i tyle mniej importu, jeśli 100% zostanie wbudowane")
wb.move_sheet("ZALOZENIA", offset=0)
ww.freeze_panes = "B8"

# =============================================================================== WARIANTY
wv = wb.create_sheet("WARIANTY")
wv.column_dimensions["A"].width = 46
for c in "BCDE":
    wv.column_dimensions[c].width = 22
wv["A1"] = "PORÓWNANIE WARIANTÓW WYKOPU (ten sam model terenu, dno 121,97 m npm)"
wv["A1"].font = Font(bold=True, size=13)
hdr = ["", "A0: pod halami, ściany pionowe (teoretyczne minimum)", "A': skarpy 1:1", "A: skarpy 1:1,5 (użyte)", "B: cały obszar w ściance"]
for k, t in enumerate(hdr):
    c = wv.cell(3, 1 + k, t)
    c.font = B
    c.fill = SZARY
    c.alignment = Alignment(wrap_text=True, horizontal="center")
wv.row_dimensions[3].height = 48
wiersze = [("Pole wykopu [m²]", "pole_wykopu", "#,##0"), ("Średnia głębokość od terenu [m]", "srednia_glebokosc", "0.00"),
           ("Wykop brutto [m³]", "V_brutto", "#,##0"), ("w tym humus i nasyp [m³]", "V_humus_nasyp_w_wykopie", "#,##0"),
           ("Grunt mineralny [m³]", "V_mineralny", "#,##0")]
for i, (nazwa, klucz, fmt) in enumerate(wiersze):
    wv.cell(4 + i, 1, nazwa)
    for j, w in enumerate(("A0", "C10", "C15", "B")):
        c = wv.cell(4 + i, 2 + j, round(SC[w][klucz], 2))
        c.number_format = fmt
        c.border = RAMKA
wv["A10"] = ("Wariant A0 nie jest wykonalny bez dodatkowej obudowy wykopu (pionowe ściany gruntu spoistego i wody na 1,2–1,7 m p.p.t.). "
             "Dlatego za wariant A przyjęto skarpy 1:1,5 w obrębie ścianki. Rzeczywisty zakres zależy od technologii wykonawcy – "
             "ustal, czy wykopujecie cały obszar w ściance (B), czy tylko obszary pod halami (A).")
wv["A10"].alignment = WRAP
wv.merge_cells("A10:E12")

# =============================================================================== WEZLY_10m (kontrola metoda siatki kwadratow)
wn = wb.create_sheet("WEZLY_10m")
eg, _, _ = zbuduj(uzyj_trend=False)
Wp, HALE, PAR = geometria()
from oblicz_bilans import PRZESTRZEN_ROBOCZA  # noqa: E402
from shapely import contains_xy  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
import scipy.ndimage  # noqa: F401,E402

es = np.arange(6433570.0, 6433731.0, 10.0)
ns = np.arange(5658890.0, 5659061.0, 10.0)
EE, NN = np.meshgrid(es, ns)
e_ = EE.ravel()
n_ = NN.ravel()
eg_ = eg(e_, n_)
inW_ = contains_xy(Wp, e_, n_)
halls = unary_union(list(HALE.values()))
from shapely import distance as sdist, points as spoints  # noqa: E402
dist = sdist(spoints(e_, n_), halls)
# powierzchnia wykopu wariantu A: dno przy halach (+ przestrzen robocza), potem skarpa 1:1,5
zpit = R["DNO"] + np.maximum(0.0, dist - PRZESTRZEN_ROBOCZA) / 1.5
# hum / nas z modelu otworow
from oblicz_bilans import profil_otworu, Pola  # noqa: E402
prof = [profil_otworu(nr) for nr in OTWORY]
pola = Pola(prof, "tin")
hum_ = pola([p["h"] for p in prof], e_, n_)
nas_ = pola([p["n"] for p in prof], e_, n_)
wn.column_dimensions["A"].width = 8
for c in "BCDEFGHIJKLMN":
    wn.column_dimensions[c].width = 14
wn["A1"] = "KONTROLA METODĄ SIATKI KWADRATÓW 10 × 10 m (węzły co 10 m w układzie PL-2000; ID jak na rysunku DXF). Pokazuje, że wynik z rastra 0,5 m zgadza się z klasyczną metodą."
wn["A1"].font = B
hdrs = ["ID", "E (X) [m]", "N (Y) [m]", "Teren istn. [m npm]", "Humus [m]", "Nasyp [m]", "W ściance (1/0)", "Rzędna powierzchni wykopu A [m npm]",
        "W wykopie A (1/0)", "Głęb. B [m]", "Głęb. A [m]", "V brutto B [m³]", "V brutto A [m³]", "V humus+nasyp A [m³]"]
for k, t in enumerate(hdrs):
    c = wn.cell(3, 1 + k, t)
    c.font = B
    c.fill = SZARY
    c.alignment = Alignment(wrap_text=True, vertical="top")
wn.row_dimensions[3].height = 60
r0 = 4
idx_list = []
letter = lambda i: chr(ord("A") + i) if i < 26 else "A" + chr(ord("A") + i - 26)
for j, nv in enumerate(ns):
    for i, ev in enumerate(es):
        k = j * len(es) + i
        if not (inW_[k] or (dist[k] < 60 and Wp.buffer(12).contains(spoints([ev], [nv])[0]))):
            continue
        idx_list.append(k)
r = r0
for k in idx_list:
    i = int(round((e_[k] - es[0]) / 10)); j = int(round((n_[k] - ns[0]) / 10))
    inA = bool(inW_[k] and (zpit[k] < eg_[k] - hum_[k] - nas_[k]))
    wn.cell(r, 1, f"{letter(i)}{j + 1:02d}")
    wn.cell(r, 2, float(e_[k])).number_format = "0.0"
    wn.cell(r, 3, float(n_[k])).number_format = "0.0"
    wn.cell(r, 4, round(float(eg_[k]), 3)).number_format = "0.000"
    wn.cell(r, 5, round(float(hum_[k]), 3)).number_format = "0.000"
    wn.cell(r, 6, round(float(nas_[k]), 3)).number_format = "0.000"
    wn.cell(r, 7, int(inW_[k]))
    wn.cell(r, 8, round(float(zpit[k]), 3)).number_format = "0.000"
    wn.cell(r, 9, int(inA))
    wn.cell(r, 10, f"=G{r}*MAX(0,D{r}-({ZR['dno0']}+{dz}))").number_format = "0.000"
    wn.cell(r, 11, f"=I{r}*MAX(0,D{r}-(H{r}+{dz}))").number_format = "0.000"
    wn.cell(r, 12, f"=J{r}*100").number_format = "#,##0"
    wn.cell(r, 13, f"=K{r}*100").number_format = "#,##0"
    wn.cell(r, 14, f"=I{r}*MIN(K{r},E{r}+F{r})*100").number_format = "#,##0"
    r += 1
rl = r - 1
wn["P3"] = "WYNIK KONTROLI"
wn["P3"].font = B
wn["P4"] = "Liczba węzłów w ściance"
wn["Q4"] = f"=SUM(G{r0}:G{rl})"
wn["P5"] = "Współczynnik brzegu B = pole ścianki / (węzły × 100)"
wn["Q5"] = f"={ZR['pole_W']}/(Q4*100)"
wn["Q5"].number_format = "0.000"
wn["P6"] = "V brutto B z węzłów (po korekcie brzegu)"
wn["Q6"] = f"=SUM(L{r0}:L{rl})*Q5"
wn["P7"] = "V brutto B z modelu 0,5 m (arkusz WYNIK)"
wn["Q7"] = "=WYNIK!C18"
wn["P8"] = "Różnica"
wn["Q8"] = "=Q6/Q7-1"
wn["Q8"].number_format = "0.0%"
wn["P10"] = "Współczynnik brzegu A = pole wykopu A / (węzły × 100)"
wn["Q10"] = f"={D('pole','A')}/(SUM(I{r0}:I{rl})*100)"
wn["Q10"].number_format = "0.000"
wn["P11"] = "V brutto A z węzłów (po korekcie brzegu)"
wn["Q11"] = f"=SUM(M{r0}:M{rl})*Q10"
wn["P12"] = "V brutto A z modelu 0,5 m (arkusz WYNIK)"
wn["Q12"] = "=WYNIK!B18"
wn["P13"] = "Różnica"
wn["Q13"] = "=Q11/Q12-1"
wn["Q13"].number_format = "0.0%"
for cc in ("Q4", "Q6", "Q7", "Q11", "Q12"):
    wn[cc].number_format = "#,##0"
wn.column_dimensions["P"].width = 58
wn.column_dimensions["Q"].width = 16
wn.freeze_panes = "B4"

# =============================================================================== GEOMETRIA
wg = wb.create_sheet("GEOMETRIA")
geo = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dane", "geometria_G.json")))
wg["A1"] = "GEOMETRIA Z RYSUNKU PROJEKTANTA (układ PL-2000 strefa 6, metry; E = X w CAD, N = Y w CAD)"
wg["A1"].font = Font(bold=True, size=13)
wg["A2"] = ("Źródło: wektorowy rzut zabezpieczenia wykopu, zgrany z siatką współrzędnych 50 m narysowaną przez projektanta (odchyłka krzyży 1,4 cm). "
            "Twój szkic (ścianka i 8 hal) jest wszędzie o 3,7% mniejszy niż ten rysunek – patrz plik CZYTAJ_NAJPIERW.md.")
wg["A2"].alignment = WRAP
wg.merge_cells("A2:H3")
wg.row_dimensions[2].height = 30
col = 1
blocks = [("ŚCIANKA (11 wierzchołków)", geo["scianka"])] + [(f"HALA {k}", geo["hale"][str(k)]) for k in range(1, 9)] + [("GRANICA DZIAŁKI (rysunek)", geo["dzialka"][:-1] if geo["dzialka"][0] == geo["dzialka"][-1] else geo["dzialka"])]
rowp = 5
for nazwa, pts in blocks:
    wg.cell(rowp, 1, nazwa).font = B
    wg.cell(rowp, 2, "E [m]").font = B
    wg.cell(rowp, 3, "N [m]").font = B
    for k, (ev, nv) in enumerate(pts):
        wg.cell(rowp + 1 + k, 1, k + 1)
        wg.cell(rowp + 1 + k, 2, round(float(ev), 3)).number_format = "0.000"
        wg.cell(rowp + 1 + k, 3, round(float(nv), 3)).number_format = "0.000"
    from shapely.geometry import Polygon  # noqa: E402
    wg.cell(rowp, 5, "pole [m²]").font = B
    wg.cell(rowp, 6, round(Polygon(pts).area, 1))
    rowp += len(pts) + 3
wg.column_dimensions["A"].width = 30
for c in "BCDEF":
    wg.column_dimensions[c].width = 16

# =============================================================================== OTWORY
wo = wb.create_sheet("OTWORY")
hd = ["Otwór", "N [m]", "E [m]", "H terenu [m npm]", "Humus [m]", "Nasyp [m]", "Wierzch gr. mineralnego [m npm]", "Zwierciadło wody [m npm]",
      "Kolumna do dna 121,97 [m]", "Piasek gruby suchy", "Piasek gruby mokry", "Piasek cienki suchy", "Piasek cienki mokry", "Glina sucha", "Glina mokra", "Uwagi"]
for k, t in enumerate(hd):
    c = wo.cell(2, 1 + k, t)
    c.font = B
    c.fill = SZARY
    c.alignment = Alignment(wrap_text=True, vertical="top")
wo.row_dimensions[2].height = 48
wo["A1"] = "17 OTWORÓW DGI – rozkład gruntu w kolumnie od spodu humusu do dna wykopu (grubości w metrach)"
wo["A1"].font = B
for k, p in enumerate(R["otwory"]):
    r = 3 + k
    vals = [p["nr"], p["N"], p["E"], p["H"], p["h"], p["n"], p["ztop"], p["zw"], p["col"], p["piasek_sel_suchy"], p["piasek_sel_mokry"],
            p["piasek_cienki_suchy"], p["piasek_cienki_mokry"], p["glina_sucha"], p["glina_mokra"], OTWORY[p["nr"]][4]]
    for c, v in enumerate(vals):
        cell = wo.cell(r, 1 + c, round(v, 3) if isinstance(v, float) else v)
        if isinstance(v, float):
            cell.number_format = "0.00"
for c, w in zip("ABCDEFGHIJKLMNOP", (8, 13, 13, 11, 9, 9, 13, 13, 12, 10, 10, 10, 10, 10, 10, 60)):
    wo.column_dimensions[c].width = w
wo.freeze_panes = "B3"

wb.save(SCIEZKA)
print("zapisano", SCIEZKA, "| arkusze:", wb.sheetnames, "| wezlow:", len(idx_list))

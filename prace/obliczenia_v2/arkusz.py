"""
ARKUSZ EXCEL – bilans robót ziemnych dz. 1/90, warianty A i B (T8).
Wejście: wyniki.json (silnik.py), niepewnosc.json (niepewnosc.py), prace/dane/*.json.
Wyjście: wyniki/BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx – żywe formuły + wartości zapisane w komórkach (podgląd bez Excela).
Formaty: m² 0,00; m³ 0,000; t 0,000. Każda pozycja zaokrąglana w formule (ROUND), sumy z zaokrąglonych pozycji.
"""
import json
import os
import re
import shutil
import sys
import tempfile
import warnings
import zipfile

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

import dane as D
import silnik as S

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUTDIR = os.path.join(REPO, "wyniki")
PLIK = os.path.join(OUTDIR, "BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx")

F_M2, F_M3, F_T, F_P = "#,##0.00", "#,##0.000", "#,##0.000", "0.000"
ZOLTY = PatternFill("solid", fgColor="FFF2A8")
SZARY = PatternFill("solid", fgColor="EDEDED")
NAGL = PatternFill("solid", fgColor="D9E1F2")
ZIEL = PatternFill("solid", fgColor="E2EFDA")
CZER = PatternFill("solid", fgColor="FCE4D6")
B = Font(bold=True)
CIENKA = Side(style="thin", color="999999")
RAMKA = Border(left=CIENKA, right=CIENKA, top=CIENKA, bottom=CIENKA)
ZAWIJ = Alignment(wrap_text=True, vertical="top")


class Arkusz:
    """Pomocnik: wiersze z kluczami, żeby formuły odwoływały się do kluczy, a nie do numerów wierszy."""

    def __init__(self, wb, nazwa, kolumny, szer):
        self.ws = wb.create_sheet(nazwa)
        self.nazwa = nazwa
        self.r = 1
        self.adr = {}
        for i, w in enumerate(szer, start=1):
            self.ws.column_dimensions[get_column_letter(i)].width = w
        self.kol = kolumny

    def tytul(self, tekst, podtytul=None):
        self.ws.cell(self.r, 1, tekst).font = Font(bold=True, size=14)
        self.r += 1
        if podtytul:
            c = self.ws.cell(self.r, 1, podtytul); c.alignment = ZAWIJ
            self.ws.merge_cells(start_row=self.r, start_column=1, end_row=self.r, end_column=len(self.kol))
            self.ws.row_dimensions[self.r].height = 45
            self.r += 1
        self.r += 1

    def naglowek(self, teksty=None):
        for i, t in enumerate(teksty or self.kol, start=1):
            c = self.ws.cell(self.r, i, t); c.font = B; c.fill = NAGL; c.border = RAMKA; c.alignment = ZAWIJ
        self.ws.row_dimensions[self.r].height = 32
        self.r += 1

    def sekcja(self, tekst):
        c = self.ws.cell(self.r, 1, tekst); c.font = Font(bold=True, color="1F3864")
        self.r += 1

    def wiersz(self, klucz, wartosci, fmt=None, wypel=None, pogr=False):
        """wartosci: lista wartości/formuł od kolumny 1. Formuły mogą mieć {klucz:kolumna} lub {ARK!klucz:kolumna}."""
        for i, v in enumerate(wartosci, start=1):
            if v is None:
                continue
            if isinstance(v, str) and v.startswith("="):
                v = self.rozwin(v)
            c = self.ws.cell(self.r, i, v)
            c.border = RAMKA
            if isinstance(v, str) and not v.startswith("="):
                c.alignment = ZAWIJ
            if fmt and i >= 3 and not (isinstance(v, str) and not v.startswith("=")):
                c.number_format = fmt
            if wypel is not None and i in (wypel if isinstance(wypel, (list, tuple, set)) else (3, 4)):
                c.fill = ZOLTY
            if pogr:
                c.font = B
        if klucz:
            self.adr[klucz] = self.r
        self.r += 1

    REJESTR = {}

    def rozwin(self, f):
        def zam(m):
            ark, kl, kol = m.group(1), m.group(2), m.group(3)
            if ark:
                ark = ark[:-1]
                return "%s!%s%d" % (ark, kol, Arkusz.REJESTR[ark].adr[kl])
            return "%s%d" % (kol, self.adr[kl])
        return re.sub(r"\{([A-Z_]+!)?([A-Za-z0-9_]+):([A-Z]+)\}", zam, f)


def zbuduj():
    W = json.load(open(os.path.join(HERE, "wyniki.json"), encoding="utf-8"))
    N = json.load(open(os.path.join(HERE, "niepewnosc.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(D.DANE, "strefy.json"), encoding="utf-8"))
    kv2 = json.load(open(os.path.join(REPO, "prace", "weryfikacja", "kontrola_dxf_v2.json"), encoding="utf-8"))
    sys.path.insert(0, os.path.join(REPO, "prace", "weryfikacja"))
    from pzt_strefy_widoczne import polilinie_v2
    from shapely.ops import unary_union as _uu
    v2_luki = {w: round(_uu([g for _, g in polilinie_v2(w)]).area, 2) for w in ("ZIELEN-NA-GRUNCIE", "ZIELEN-NA-STROPIE")}
    wb = Workbook()
    wb.remove(wb.active)
    r3 = lambda v: round(float(v), 3)

    # =============================================================== ZALOZENIA
    Z = Arkusz(wb, "ZALOZENIA", ["Parametr", "Opis", "Wartość", "Jedn.", "Źródło / uwagi"], [30, 52, 14, 9, 70])
    Arkusz.REJESTR["ZALOZENIA"] = Z
    Z.tytul("ZAŁOŻENIA – dz. 1/90 Wojszyce", "Żółte pola: decyzje i założenia użytkownika – można je zmieniać, arkusz przeliczy się sam. Szare pola: parametry geometrii i stref – "
            "ich zmiana wymaga ponownego uruchomienia silnika (prace/obliczenia_v2/silnik.py).")
    Z.naglowek()
    Z.sekcja("Decyzje użytkownika (żółte)")
    Z.wiersz("pole_zieleni", ["Pole zieleni na gruncie rodzimym", "do wzoru na humus na odkład", 6443.06, "m²", "PZT – tabela Bilans terenu (decyzja użytkownika, USTALENIA pkt 4.3)"], F_M2, wypel=(3,))
    Z.wiersz("gr_humusu", ["Grubość humusu w zieleni", "warstwa humusu na terenach zielonych", 0.25, "m", "USTALENIA pkt 4.4"], F_M2, wypel=(3,))
    Z.wiersz("zapas", ["Zapas humusu", "doliczany do humusu na odkład", 0.10, "–", "decyzja użytkownika (10%)"], "0.00", wypel=(3,))
    Z.wiersz("ro_gleba", ["Gęstość gleby (humusu)", "do przeliczenia na tony", 1.60, "t/m³", "brak w tabeli 8 DGI – założenie zaakceptowane 8.10.2026"], F_P, wypel=(3,))
    Z.wiersz("ro_nasyp", ["Gęstość nasypu niekontrolowanego", "do przeliczenia na tony", 1.80, "t/m³", "brak w tabeli 8 DGI – założenie zaakceptowane 8.10.2026"], F_P, wypel=(3,))
    Z.wiersz("k_humus", ["Spulchnienie humusu", "tylko informacyjnie (objętość luzem)", 1.25, "–", "założenie (v1), zaakceptowane 8.10.2026"], "0.00", wypel=(3,))
    Z.wiersz("k_nasyp", ["Spulchnienie nasypu", "tylko informacyjnie", 1.25, "–", "jw."], "0.00", wypel=(3,))
    Z.wiersz("k_glina", ["Spulchnienie glin", "tylko informacyjnie", 1.30, "–", "jw."], "0.00", wypel=(3,))
    Z.wiersz("k_piasek", ["Spulchnienie piasków i pospółek", "tylko informacyjnie", 1.15, "–", "jw."], "0.00", wypel=(3,))
    Z.sekcja("Parametry wykopu i stref (szare – zmiana wymaga przeliczenia silnikiem)")
    p = W["parametry"]
    for kl, op, v, j, zr in (
            ("dno", "Dno wykopu (spód chudego betonu pod płytą)", p["dno"], "m npm", "d.k. płyty −4,04 (rzuty PW_1A…8B) − chudy beton 0,10 (przekrój B-B 2C); ±0,00 = 126,00"),
            ("prz_rob", "Przestrzeń robocza (wariant A)", p["przestrzen_robocza"], "m", "decyzja użytkownika 8.10.2026 (brak w dokumentacji)"),
            ("skarpa", "Nachylenie skarp 1:n (A; w B od południa)", p["skarpa"], "n", "decyzja użytkownika 8.10.2026"),
            ("konstr", "Konstrukcja nawierzchni (poza bilansem)", p["konstrukcja"], "m", "USTALENIA pkt 4.4"),
            ("mroz", "Strefa przemarzania pod nawierzchnią", p["przemarzanie"], "m", "decyzja użytkownika 8.10.2026 (DGI: 0,80 m – przyjęto bezpiecznie 1,00 m)"),
            ("substrat", "Substrat w ogrodach deszczowych (poza bilansem)", p["substrat_ogrod"], "m", "ustalenie 20; poniżej grunt rodzimy z odkładu"),
            ("rampa", "Spód wykopu pod rampą = powierzchnia rampy minus", p["rampa_pod"], "m", "założenie robocze (jak pod posadzką garażu 122,57 − 121,86); rampa liniowo 122,85 → 125,80"),
            ("raster", "Bok komórki rastra obliczeń", p["cell"], "m", "kontrola: raster 0,50 m daje różnice < 40 m³ (arkusz NIEPEWNOSC)"),
    ):
        Z.wiersz(kl, [op, "", v, j, zr], "0.00", wypel=None)
        for c in range(1, 6):
            Z.ws.cell(Z.r - 1, c).fill = SZARY
    Z.sekcja("Gęstości gruntów rodzimych – zał. 8 DGI (mw / w / nw = mało wilgotny / wilgotny / nawodniony)")
    for k in D.KLASY:
        g = D.GESTOSC[k]
        txt = ("%.2f / %.2f / %.2f (wg stanu z karty otworu)" % (g["mw"], g["w"], g["nw"])) if isinstance(g, dict) else ("%.3f (średnia z zakresu tabeli 8)" % g)
        Z.wiersz(None, ["Warstwa %s" % k, txt, None, "t/m³", "tabela parametrów geologiczno-inżynierskich (zał. 8 DGI)"])

    # =============================================================== OBLICZENIA (wartości z silnika)
    O = Arkusz(wb, "OBLICZENIA", ["Pozycja", "Opis", "Wariant A", "Wariant B", "Jedn.", "Źródło"], [34, 60, 16, 16, 8, 40])
    Arkusz.REJESTR["OBLICZENIA"] = O
    O.tytul("OBLICZENIA – wyniki silnika (raster 0,25 m)", "Wartości wyliczone programem prace/obliczenia_v2/silnik.py (wynik w wyniki.json). Arkusz WYNIK liczy z nich bilans formułami.")
    O.naglowek()
    wa, wb_ = W["warianty"]["A"], W["warianty"]["B"]
    O.sekcja("Zdjęcie wierzchnich warstw (całe 1/90, jednakowe w A i B)")
    O.wiersz("humus", ["humus", "humus (gleba) zdjęty z całej działki", W["humus_m3"], W["humus_m3"], "m³", "grubość z 17 otworów i 5 CPTU (TIN)"], F_M3)
    O.wiersz("nasyp", ["nasyp", "nasyp niekontrolowany (strefy z mapy 4.3 DGI)", W["nasyp_m3"], W["nasyp_m3"], "m³", "mapa 4.3: 759,28 m² × 0,25 + 350,30 m² × 0,20"], F_M3)
    O.sekcja("Wykop gruntu rodzimego wg stref (bez humusu, nasypu i fundamentów głębszych)")
    nazwy = {"H": "hale i zadaszone dojazdy (strefa hal)", "O": "ogrody deszczowe", "R": "rampy", "Z": "zieleń na gruncie", "U": "nawierzchnie (z geokratą i wiatami)"}
    for zn in ("H", "O", "R", "Z", "U"):
        for gr, kl in (("piaski", D.PIASKI), ("gliny", D.GLINY)):
            va = sum(wa["wykop_m3"][zn][k] for k in kl); vb = sum(wb_["wykop_m3"][zn][k] for k in kl)
            O.wiersz("w_%s_%s" % (zn, gr[0]), ["wykop %s – %s" % (zn, gr), "%s: %s" % (nazwy[zn], "piaski i pospółki" if gr == "piaski" else "gliny i pyły"), r3(va), r3(vb), "m³", "silnik"], F_M3)
            O.wiersz("m_%s_%s" % (zn, gr[0]), ["masa %s – %s" % (zn, gr), "masa tego gruntu (gęstości z zał. 8)", r3(wa["masa_t"][zn][gr]), r3(wb_["masa_t"][zn][gr]), "t", "silnik"], F_T)
    O.wiersz("wym_p", ["wymiana – piaski", "wymiana gruntu w strefie przemarzania (drogi, chodniki, plac, parkingi) – piaski (zawarte w strefie U)",
                        wa["wymiana_przemarzanie"]["piaski_m3"], wb_["wymiana_przemarzanie"]["piaski_m3"], "m³", "silnik (ustalenie 21)"], F_M3)
    O.wiersz("wym_g", ["wymiana – gliny", "jw. – gliny", wa["wymiana_przemarzanie"]["gliny_m3"], wb_["wymiana_przemarzanie"]["gliny_m3"], "m³", "silnik"], F_M3)
    O.wiersz("wym_m2", ["wymiana – pole", "pole wymiany", wa["wymiana_przemarzanie"]["m2"], wb_["wymiana_przemarzanie"]["m2"], "m²", "silnik"], F_M2)
    O.sekcja("Zapotrzebowanie na grunt (wbudowanie) – wg miejsca")
    obsz = {"wykop": "w wykopie", "poza_wykopem_w_sciance": "w ściance poza wykopem", "poza_wykopem_poza_scianka": "poza ścianką"}
    for kl, op in (("rodzimy_Z", "zieleń – grunt rodzimy pod humusem"), ("rodzimy_U", "nawierzchnie – grunt rodzimy poniżej 1,00 m"),
                   ("rodzimy_R", "rampy – grunt pod płytą rampy"), ("rodzimy_O", "ogrody deszczowe – grunt rodzimy pod substratem 0,30 m"), ("niewysadzinowy_U", "nawierzchnie – grunt niewysadzinowy 0,50–1,00 m (dowóz)"),
                   ("humus_warstwa_Z", "zieleń – warstwa humusu 0,25 m wg rastra (kontrola wzoru)")):
        for o, opo in obsz.items():
            O.wiersz("z_%s_%s" % (kl, o), ["%s" % kl, "%s – %s" % (op, opo), r3(wa["zapotrzebowanie"][kl][o]), r3(wb_["zapotrzebowanie"][kl][o]), "m³", "silnik"], F_M3)
    O.sekcja("Miejsca do zgłoszenia (poza wykopem nie kopiemy) – informacyjnie")
    for kl, op in (("U_grunt_rodzimy_w_strefie_przemarzania", "nawierzchnie: grunt rodzimy zostaje w strefie przemarzania (0,50–1,00 m)"),
                   ("U_konstrukcja_w_gruncie", "nawierzchnie: konstrukcja 0,50 m wchodzi w grunt rodzimy"),
                   ("Z_humus_ponad_grunt", "zieleń: warstwa humusu wchodzi w grunt rodzimy"),
                   ("O_substrat_ponad_grunt", "ogrody deszczowe: substrat 0,30 m wchodzi w grunt rodzimy")):
        ma = sum(v["m3"] for v in wa["konflikty"][kl].values()); mb = sum(v["m3"] for v in wb_["konflikty"][kl].values())
        pa = sum(v["m2"] for v in wa["konflikty"][kl].values()); pb = sum(v["m2"] for v in wb_["konflikty"][kl].values())
        O.wiersz("k_%s_m3" % kl, [kl, op + " – objętość", r3(ma), r3(mb), "m³", "silnik"], F_M3)
        O.wiersz("k_%s_m2" % kl, [kl, op + " – powierzchnia", round(pa, 2), round(pb, 2), "m²", "silnik"], F_M2)
    O.sekcja("Geometria wykopu")
    O.wiersz("pole_wykopu", ["pole wykopu", "pole dna i skarp (rzut)", round(wa["pole_wykopu_razem"], 2), round(wb_["pole_wykopu_razem"], 2), "m²", "silnik"], F_M2)
    O.wiersz("gleb_sr", ["głębokość średnia", "średnia głębokość wykopu gruntu rodzimego", wa["glebokosc_sr"], wb_["glebokosc_sr"], "m", "silnik"], F_M2)
    O.wiersz("poza_dz", ["wykop poza działką", "kontrola – powinno być 0", wa["wykop_poza_dzialka"]["m3"], wb_["wykop_poza_dzialka"]["m3"], "m³", "silnik"], F_M3)

    # =============================================================== FUNDAMENTY
    FU = Arkusz(wb, "FUNDAMENTY", ["Element", "a [m]", "b [m]", "h [m]", "V 1 szt. [m³]", "1A", "2C", "3A", "4B", "5A", "6A", "7A", "8B", "Razem szt.", "Razem [m³]"],
                [38, 8, 8, 8, 12, 6, 6, 6, 6, 6, 6, 6, 6, 10, 14])
    Arkusz.REJESTR["FUNDAMENTY"] = FU
    FU.tytul("FUNDAMENTY GŁĘBSZE – wykop poniżej dna 121,86 (osobna pozycja, wywóz)",
             "Rzuty fundamentów PW_1A…PW_8B (4IDEA, XI 2025). Bryła ścięta: spód a×b, góra (a+2·0,50)×(b+2·0,50) – obrys przerywany obniżenia na rzutach jest 0,50 m szerszy. "
             "h = różnica d.k. elementu i otoczenia (chudy beton 10 cm pod obydwoma). Liczby sztuk z rzutów; wymiary studzienek z opisów wymiarów (PW_1A).")
    FU.naglowek()
    FU.wiersz("skos", ["Poszerzenie górnej krawędzi (każda strona)", 0.50, None, None, None], "0.00", wypel=(2,))
    bud = ("1A", "2C", "3A", "4B", "5A", "6A", "7A", "8B")
    for i, (naz, (a, b, dk, ref)) in enumerate(S.ELEMENTY.items()):
        h = round(ref - dk, 3)
        row = FU.r
        f_v = "=ROUND(D{r}/3*(B{r}*C{r}+(B{r}+2*$B${s})*(C{r}+2*$B${s})+SQRT(B{r}*C{r}*(B{r}+2*$B${s})*(C{r}+2*$B${s}))),3)".format(r=row, s=FU.adr["skos"])
        cnt = [S.LICZBY[bn].get(naz, 0) for bn in bud]
        FU.wiersz("e%d" % i, [naz, a, b, h, f_v] + cnt + ["=SUM(F{r}:M{r})".format(r=row), "=ROUND(E{r}*N{r},3)".format(r=row)], None)
        for c in (2, 3, 4):
            FU.ws.cell(row, c).number_format = "0.000"
        FU.ws.cell(row, 5).number_format = F_M3; FU.ws.cell(row, 15).number_format = F_M3
    n_el = len(S.ELEMENTY)
    r0, r1 = FU.adr["e0"], FU.adr["e%d" % (n_el - 1)]
    FU.wiersz("razem", ["RAZEM fundamenty głębsze", None, None, None, None] + ["=SUM({c}{a}:{c}{b})".format(c=get_column_letter(6 + j), a=r0, b=r1) for j in range(8)]
              + ["=SUM(N{a}:N{b})".format(a=r0, b=r1), "=ROUND(SUM(O{a}:O{b}),3)".format(a=r0, b=r1)], F_M3, pogr=True)
    f = W["fundamenty"]
    vp = sum(f["klasy_m3"][k] for k in D.PIASKI); vg = sum(f["klasy_m3"][k] for k in D.GLINY)
    FU.r += 1
    FU.sekcja("Skład gruntu w wykopie fundamentów głębszych (silnik: profile otworów pod każdą halą)")
    FU.wiersz("f_udz_p", ["Udział piasków i pospółek", r3(vp / f["razem_m3"])], "0.000")
    FU.wiersz("f_ro_p", ["Gęstość średnia piasków", r3(f["masa_t"]["piaski"] / vp)], "0.000")
    FU.wiersz("f_ro_g", ["Gęstość średnia glin", r3(f["masa_t"]["gliny"] / vg)], "0.000")

    # =============================================================== WYNIK
    R = Arkusz(wb, "WYNIK", ["Nr", "Pozycja", "Wariant A", "Wariant B", "Jedn.", "Uwagi"], [6, 62, 18, 18, 8, 70])
    Arkusz.REJESTR["WYNIK"] = R
    R.tytul("BILANS ROBÓT ZIEMNYCH – działka 1/90 Wojszyce (Wrocław)",
            "Wariant A: wykop tylko pod garażami (hale + zadaszone dojazdy + rampy) + przestrzeń robocza 1,0 m + rozkop ze skarpą 1:1,5 (w obrębie ścianki; od południa skarpa) – rozkład w arkuszu WARIANT_A. "
            "Wariant B: cały obszar w ściance do dna 121,86 (ściany pionowe; od południa skarpa 1:1,5). Objętości w stanie rodzimym. Żółte pola – decyzja użytkownika.")
    R.naglowek(["Nr", "Pozycja", "Wariant A\nwykop pod garażami + rozkop", "Wariant B\ncały obszar w ściance", "Jedn.", "Uwagi"])
    OB = lambda kl, c: "{OBLICZENIA!%s:%s}" % (kl, c)
    def obl(klucze, c):
        return "+".join(OB(k, c) for k in klucze)
    def w2(klucz, nr, opis, fA, fB, jedn, uw, fmt=F_M3, wypel=None, pogr=False):
        R.wiersz(klucz, [nr, opis, fA, fB, jedn, uw], fmt, wypel=wypel, pogr=pogr)
    R.sekcja("1. HUMUS (gleba) – zdejmowany z całej działki")
    w2("h_zdj", "1.1", "Humus zdjęty z całej działki", "=ROUND(%s,3)" % OB("humus", "C"), "=ROUND(%s,3)" % OB("humus", "D"), "m³", "średnio %.2f m (17 otworów + 5 CPTU)" % W["humus_sr_grubosc"])
    f_odk = "=MIN({h_zdj:%s},ROUND({ZALOZENIA!gr_humusu:C}*{ZALOZENIA!pole_zieleni:C}*(1+{ZALOZENIA!zapas:C}),3))"
    w2("h_odk", "1.2", "Humus na odkład (do zieleni na gruncie)", f_odk % "C", f_odk % "D", "m³", "0,25 m × 6 443,06 m² × 1,10 (ZALOZENIA)")
    w2("h_wyw", "1.3", "Humus do wywozu (nadwyżka)", "=ROUND({h_zdj:C}-{h_odk:C},3)", "=ROUND({h_zdj:D}-{h_odk:D},3)", "m³", "")
    R.sekcja("2. NASYP NIEKONTROLOWANY")
    w2("n_wyw", "2.1", "Nasyp niekontrolowany – 100% do wywozu", "=ROUND(%s,3)" % OB("nasyp", "C"), "=ROUND(%s,3)" % OB("nasyp", "D"), "m³", "otwory 5, 17, 20; strefy z mapy 4.3")
    R.sekcja("3. GRUNT RODZIMY Z WYKOPU (bez humusu i nasypu)")
    w2("g_hal", "3.1", "Spod hal i zadaszonych dojazdów – na odkład", "=ROUND(%s,3)" % obl(["w_H_p", "w_H_g"], "C"), "=ROUND(%s,3)" % obl(["w_H_p", "w_H_g"], "D"), "m³", "ustalenie 18: grunt przydatny, użyty do zasypu (warunki – arkusz GRUNTY)")
    w2("g_ogr", "3.2", "Z ogrodów deszczowych – na odkład", "=ROUND(%s,3)" % obl(["w_O_p", "w_O_g"], "C"), "=ROUND(%s,3)" % obl(["w_O_p", "w_O_g"], "D"), "m³", "")
    w2("g_odk", "3.3", "Z pozostałych stref (zieleń, nawierzchnie, rampy) – na odkład", "=ROUND(%s,3)" % obl(["w_R_p", "w_R_g", "w_Z_p", "w_Z_g", "w_U_p", "w_U_g"], "C"),
       "=ROUND(%s,3)" % obl(["w_R_p", "w_R_g", "w_Z_p", "w_Z_g", "w_U_p", "w_U_g"], "D"), "m³", "w tym wymiana gruntu w strefie przemarzania (poz. 3.8)")
    w2("g_raz", "3.4", "RAZEM wykop gruntu rodzimego (cały na odkład)", "=ROUND({g_hal:C}+{g_ogr:C}+{g_odk:C},3)", "=ROUND({g_hal:D}+{g_ogr:D}+{g_odk:D},3)", "m³", "", pogr=True)
    w2("g_pias", "3.5", "   w tym piaski i pospółki (niewysadzinowe)", "=ROUND(%s,3)" % obl(["w_%s_p" % z for z in "HORZU"], "C"), "=ROUND(%s,3)" % obl(["w_%s_p" % z for z in "HORZU"], "D"), "m³", "warstwy Ia, IIa, IIb, IIc, IIIa")
    w2("g_glin", "3.6", "   w tym gliny i pyły (wysadzinowe)", "=ROUND(%s,3)" % obl(["w_%s_g" % z for z in "HORZU"], "C"), "=ROUND(%s,3)" % obl(["w_%s_g" % z for z in "HORZU"], "D"), "m³", "warstwy IVa, IVb, IVc, IVd")
    w2("g_fund", "3.7", "Fundamenty głębsze (pogrubienia, rdzenie, szyby, studzienki) – do wywozu", "=ROUND({FUNDAMENTY!razem:O},3)", "=ROUND({FUNDAMENTY!razem:O},3)", "m³", "osobna pozycja (ustalenie 13) – arkusz FUNDAMENTY")
    w2("g_wym", "3.8", "   w tym wymiana w strefie przemarzania pod drogami, chodnikami i parkingami", "=ROUND({OBLICZENIA!wym_p:C}+{OBLICZENIA!wym_g:C},3)",
       "=ROUND({OBLICZENIA!wym_p:D}+{OBLICZENIA!wym_g:D},3)", "m³", "ustalenie 21: wykop do 1,00 m pod nawierzchnią (zawarte w poz. 3.3)")
    R.sekcja("4. ZAPOTRZEBOWANIE NA GRUNT (wbudowanie)")
    w2("z_hum", "4.1", "Zieleń – humus 0,25 m (z odkładu)", "={h_odk:C}", "={h_odk:D}", "m³", "równe poz. 1.2")
    def zz(kl):
        return "=ROUND(%s,3)" % obl(["z_%s_%s" % (kl, o) for o in obsz], "C"), "=ROUND(%s,3)" % obl(["z_%s_%s" % (kl, o) for o in obsz], "D")
    w2("z_ziel", "4.2", "Zieleń – grunt rodzimy pod humusem (do dna wykopu lub do terenu po zdjęciu humusu)", *zz("rodzimy_Z"), "m³", "")
    w2("z_naw", "4.3", "Nawierzchnie – grunt rodzimy poniżej 1,00 m pod nawierzchnią", *zz("rodzimy_U"), "m³", "konstrukcja 0,50 m – poza bilansem")
    w2("z_ramp", "4.4", "Rampy – grunt pod płytą rampy", *zz("rodzimy_R"), "m³", "założenie: spód wykopu = powierzchnia rampy − 0,71 m")
    w2("z_ogr", "4.4a", "Ogrody deszczowe – grunt rodzimy pod substratem 0,30 m", *zz("rodzimy_O"), "m³", "ustalenie 20: substrat 0,30 m poza bilansem")
    w2("z_raz", "4.5", "RAZEM zapotrzebowanie na grunt rodzimy", "=ROUND({z_ziel:C}+{z_naw:C}+{z_ramp:C}+{z_ogr:C},3)", "=ROUND({z_ziel:D}+{z_naw:D}+{z_ramp:D}+{z_ogr:D},3)", "m³", "", pogr=True)
    w2("z_mroz", "4.6", "Nawierzchnie – grunt niewysadzinowy w strefie przemarzania (0,50–1,00 m)", *zz("niewysadzinowy_U"), "m³", "ustalenie 15: przemarzanie 1,00 m – grunt dowożony")
    R.sekcja("5. DECYZJA – PONOWNE WBUDOWANIE GRUNTU Z ODKŁADU (żółte pola)")
    w2("d_dost", "5.1", "Grunt rodzimy na odkładzie – dostępny (limit)", "={g_raz:C}", "={g_raz:D}", "m³", "równe poz. 3.4 (cały wykop, ustalenie 18)")
    w2("d_potr", "5.2", "Zapotrzebowanie na grunt rodzimy (limit)", "={z_raz:C}", "={z_raz:D}", "m³", "równe poz. 4.5")
    w2("d_prop", "5.3", "Propozycja: największe możliwe ponowne wbudowanie", "=MIN({d_dost:C},{d_potr:C})", "=MIN({d_dost:D},{d_potr:D})", "m³", "propozycja – decyzję podejmuje użytkownik")
    prop_a = min(sum(sum(wa["wykop_m3"][z].values()) for z in "RZU"), sum(sum(wa["zapotrzebowanie"][k].values()) for k in ("rodzimy_Z", "rodzimy_U", "rodzimy_R")))
    prop_b = min(sum(sum(wb_["wykop_m3"][z].values()) for z in "RZU"), sum(sum(wb_["zapotrzebowanie"][k].values()) for k in ("rodzimy_Z", "rodzimy_U", "rodzimy_R")))
    import kontrola_arkusza as KA0
    prop = KA0.propozycja()
    w2("d_wbud", "5.4", "PONOWNE WBUDOWANIE gruntu rodzimego z odkładu – DECYZJA", prop["A"], prop["B"], "m³", "wpisz własną wartość (≤ min z poz. 5.1 i 5.2)", wypel=(3, 4), pogr=True)
    w2("d_pias", "5.5", "Piaski z wykopu w strefie przemarzania zamiast dowozu – DECYZJA", 0, 0, "m³", "domyślnie 0 (ustalenie 15: grunt dowożony); max: poz. 5.6", wypel=(3, 4))
    w2("d_plim", "5.6", "   limit: piaski na odkładzie (pomniejszone o ich udział w poz. 5.4)", "=ROUND(MIN({z_mroz:C},{g_pias:C}*(1-{d_wbud:C}/{d_dost:C})),3)",
       "=ROUND(MIN({z_mroz:D},{g_pias:D}*(1-{d_wbud:D}/{d_dost:D})),3)", "m³", "")
    w2("d_kontr", "5.7", "Kontrola decyzji", '=IF(AND({d_wbud:C}<=MIN({d_dost:C},{d_potr:C})+0.0005,{d_pias:C}<={d_plim:C}+0.0005,{d_wbud:C}>=0,{d_pias:C}>=0),"OK","SPRAWDŹ")',
       '=IF(AND({d_wbud:D}<=MIN({d_dost:D},{d_potr:D})+0.0005,{d_pias:D}<={d_plim:D}+0.0005,{d_wbud:D}>=0,{d_pias:D}>=0),"OK","SPRAWDŹ")', "", "OK = decyzja mieści się w limitach", fmt=None)
    R.sekcja("6. WYNIK – WYWÓZ I DOWÓZ (m³ w stanie rodzimym)")
    w2("x_hum", "6.1", "WYWÓZ – humus (nadwyżka)", "={h_wyw:C}", "={h_wyw:D}", "m³", "")
    w2("x_nas", "6.2", "WYWÓZ – nasyp niekontrolowany", "={n_wyw:C}", "={n_wyw:D}", "m³", "")
    w2("x_gr", "6.3", "WYWÓZ – grunt rodzimy", "=ROUND({g_raz:C}-{d_wbud:C}-{d_pias:C},3)", "=ROUND({g_raz:D}-{d_wbud:D}-{d_pias:D},3)", "m³", "nadwyżka z odkładu")
    w2("x_fund", "6.4", "WYWÓZ – fundamenty głębsze", "={g_fund:C}", "={g_fund:D}", "m³", "")
    w2("x_raz", "6.5", "RAZEM DO WYWOZU", "=ROUND({x_hum:C}+{x_nas:C}+{x_gr:C}+{x_fund:C},3)", "=ROUND({x_hum:D}+{x_nas:D}+{x_gr:D}+{x_fund:D},3)", "m³", "", pogr=True)
    w2("y_gr", "6.6", "DOWÓZ – grunt do zasypu (brakująca część)", "=ROUND({z_raz:C}-{d_wbud:C},3)", "=ROUND({z_raz:D}-{d_wbud:D},3)", "m³", "grunt zasypowy, zagęszczalny")
    w2("y_mroz", "6.7", "DOWÓZ – grunt niewysadzinowy (strefa przemarzania pod nawierzchniami)", "=ROUND({z_mroz:C}-{d_pias:C},3)", "=ROUND({z_mroz:D}-{d_pias:D},3)", "m³", "np. piasek / pospółka")
    w2("y_raz", "6.8", "RAZEM DO DOWIEZIENIA", "=ROUND({y_gr:C}+{y_mroz:C},3)", "=ROUND({y_gr:D}+{y_mroz:D},3)", "m³", "poza bilansem: kruszywo konstrukcji nawierzchni 0,50 m; substrat na stropach, dachach i w ogrodach deszczowych", pogr=True)
    R.sekcja("7. KONTROLA BILANSU (musi być 0)")
    w2("k_1", "7.1", "Urobek − (wywóz + wbudowane z odkładu)", "=ROUND({h_zdj:C}+{n_wyw:C}+{g_raz:C}+{g_fund:C}-({x_raz:C}+{h_odk:C}+{d_wbud:C}+{d_pias:C}),3)",
       "=ROUND({h_zdj:D}+{n_wyw:D}+{g_raz:D}+{g_fund:D}-({x_raz:D}+{h_odk:D}+{d_wbud:D}+{d_pias:D}),3)", "m³", "")
    w2("k_2", "7.2", "Zapotrzebowanie − (z odkładu + dowóz)", "=ROUND({z_raz:C}+{z_mroz:C}-({d_wbud:C}+{d_pias:C}+{y_gr:C}+{y_mroz:C}),3)",
       "=ROUND({z_raz:D}+{z_mroz:D}-({d_wbud:D}+{d_pias:D}+{y_gr:D}+{y_mroz:D}),3)", "m³", "")
    R.sekcja("8. TONY – WYWÓZ")
    w2("t_hum", "8.1", "Humus", "=ROUND({x_hum:C}*{ZALOZENIA!ro_gleba:C},3)", "=ROUND({x_hum:D}*{ZALOZENIA!ro_gleba:C},3)", "t", "gęstość z ZALOZENIA", F_T)
    w2("t_nas", "8.2", "Nasyp", "=ROUND({x_nas:C}*{ZALOZENIA!ro_nasyp:C},3)", "=ROUND({x_nas:D}*{ZALOZENIA!ro_nasyp:C},3)", "t", "", F_T)
    mAll = lambda c: obl(["m_%s_%s" % (z, g) for z in "HORZU" for g in "pg"], c)
    mPp = lambda c: obl(["m_%s_p" % z for z in "HORZU"], c)
    f_tg = "=ROUND(({mall})-{{d_wbud:{c}}}*({mall})/{{g_raz:{c}}}-{{d_pias:{c}}}*({mp})/{{g_pias:{c}}},3)"
    w2("t_gr", "8.3", "Grunt rodzimy", f_tg.format(mall=mAll("C"), mp=mPp("C"), c="C"), f_tg.format(mall=mAll("D"), mp=mPp("D"), c="D"), "t",
       "masa z profili otworów (gęstości zał. 8) pomniejszona o wbudowaną część (gęstość średnia odkładu)", F_T)
    w2("t_fund", "8.4", "Fundamenty głębsze", "=ROUND({g_fund:C}*({FUNDAMENTY!f_udz_p:B}*{FUNDAMENTY!f_ro_p:B}+(1-{FUNDAMENTY!f_udz_p:B})*{FUNDAMENTY!f_ro_g:B}),3)",
       "=ROUND({g_fund:D}*({FUNDAMENTY!f_udz_p:B}*{FUNDAMENTY!f_ro_p:B}+(1-{FUNDAMENTY!f_udz_p:B})*{FUNDAMENTY!f_ro_g:B}),3)", "t", "", F_T)
    w2("t_raz", "8.5", "RAZEM WYWÓZ", "=ROUND({t_hum:C}+{t_nas:C}+{t_gr:C}+{t_fund:C},3)", "=ROUND({t_hum:D}+{t_nas:D}+{t_gr:D}+{t_fund:D},3)", "t", "", F_T, pogr=True)
    R.sekcja("9. OBJĘTOŚĆ WYWOZU LUZEM (po spulchnieniu – informacyjnie)")
    w2("l_hum", "9.1", "Humus", "=ROUND({x_hum:C}*{ZALOZENIA!k_humus:C},3)", "=ROUND({x_hum:D}*{ZALOZENIA!k_humus:C},3)", "m³", "")
    w2("l_nas", "9.2", "Nasyp", "=ROUND({x_nas:C}*{ZALOZENIA!k_nasyp:C},3)", "=ROUND({x_nas:D}*{ZALOZENIA!k_nasyp:C},3)", "m³", "")
    f_lg = "=ROUND(({{g_pias:{c}}}-{{d_wbud:{c}}}*{{g_pias:{c}}}/{{g_raz:{c}}}-{{d_pias:{c}}})*{{ZALOZENIA!k_piasek:C}}+({{g_glin:{c}}}-{{d_wbud:{c}}}*{{g_glin:{c}}}/{{g_raz:{c}}})*{{ZALOZENIA!k_glina:C}},3)"
    w2("l_gr", "9.3", "Grunt rodzimy (piaski × 1,15, gliny × 1,30)", f_lg.format(c="C"), f_lg.format(c="D"), "m³", "")
    w2("l_fund", "9.4", "Fundamenty głębsze", "=ROUND({g_fund:C}*({FUNDAMENTY!f_udz_p:B}*{ZALOZENIA!k_piasek:C}+(1-{FUNDAMENTY!f_udz_p:B})*{ZALOZENIA!k_glina:C}),3)",
       "=ROUND({g_fund:D}*({FUNDAMENTY!f_udz_p:B}*{ZALOZENIA!k_piasek:C}+(1-{FUNDAMENTY!f_udz_p:B})*{ZALOZENIA!k_glina:C}),3)", "m³", "")
    w2("l_raz", "9.5", "RAZEM WYWÓZ LUZEM", "=ROUND({l_hum:C}+{l_nas:C}+{l_gr:C}+{l_fund:C},3)", "=ROUND({l_hum:D}+{l_nas:D}+{l_gr:D}+{l_fund:D},3)", "m³", "", pogr=True)
    R.sekcja("10. INFORMACYJNIE – miejsca poza wykopem i poza drogami / chodnikami / parkingami, gdzie projekt wchodzi w grunt rodzimy (nie kopiemy, nie wliczone)")
    for kl, op in (("U_grunt_rodzimy_w_strefie_przemarzania", "Nawierzchnie: grunt rodzimy zostaje w strefie przemarzania 0,50–1,00 m"),
                   ("U_konstrukcja_w_gruncie", "Nawierzchnie: konstrukcja 0,50 m wchodzi w grunt rodzimy"),
                   ("Z_humus_ponad_grunt", "Zieleń: warstwa humusu 0,25 m wchodzi w grunt rodzimy"),
                   ("O_substrat_ponad_grunt", "Ogrody deszczowe: substrat 0,30 m wchodzi w grunt rodzimy")):
        w2("q_%s" % kl, "10", op, "={OBLICZENIA!k_%s_m3:C}" % kl, "={OBLICZENIA!k_%s_m3:D}" % kl, "m³", "powierzchnia: A %.2f m², B %.2f m² (OBLICZENIA)" % (
            sum(v["m2"] for v in wa["konflikty"][kl].values()), sum(v["m2"] for v in wb_["konflikty"][kl].values())))
    R.ws.freeze_panes = "C5"

    # =============================================================== WARIANT_A (jak liczony, porównanie z wcześniejszym arkuszem)
    RA = json.load(open(os.path.join(HERE, "rozklad_wariantu_A.json"), encoding="utf-8"))
    v1 = json.load(open(os.path.join(REPO, "prace", "obliczenia_v1", "_skrypt", "wyniki_bilans.json"), encoding="utf-8"))
    WA = Arkusz(wb, "WARIANT_A", ["Krok", "Co jest w wykopie", "Pole wykopu [m²]", "Wykop gruntu rodzimego [m³]", "Różnica do poprzedniego kroku [m³]", "Uwagi"], [6, 70, 16, 18, 18, 50])
    Arkusz.REJESTR["WARIANT_A"] = WA
    WA.tytul("WARIANT A – wykop tylko pod garażami + rozkop (jak w poprzednim arkuszu)",
             "Wykop: obrys hali (garażu) do dna 121,86 + przestrzeń robocza 1,0 m, dalej rozkop ze skarpą 1:1,5 aż do terenu po zdjęciu humusu. Przy ściance rozkop obcięty "
             "(za ścianką nie kopiemy), od południa skarpa swobodna. Między halami, gdzie skarpy się nie spotykają, teren zostaje (tylko zdjęty humus). "
             "Tak samo jak we wcześniejszym arkuszu (wariant C15 = 'A: skarpy 1:1,5'); doszły: rampy i zadaszone dojazdy do garaży oraz nowe ustalenia.")
    WA.naglowek()
    prev = None
    for i, rr in enumerate(RA):
        if rr["opis"].startswith("1b"):
            WA.r += 1
            WA.sekcja("Porównanie z wcześniejszym arkuszem (te same zasady co wcześniej, liczone obecnym modelem)")
            prev = RA[0]["wykop"]
        d = None if prev is None else round(rr["wykop"] - prev, 3)
        uw = {"1": "rdzeń wariantu A – jak wcześniej", "2": "zieleń na stropie poza obrysami hal = obiekty podziemne", "3": "4 pochylnie; spód = powierzchnia rampy − 0,71 m",
              "1b": "jak wcześniej: wykop obcięty prostym odcinkiem od południa", "1c": "bez ustalenia 21", "1d": "dno jak wcześniej (121,97)"}[rr["opis"].split(".")[0]]
        WA.wiersz("a%d" % i, [rr["opis"].split(".")[0], rr["opis"].split(". ", 1)[1], rr["pole"], rr["wykop"], d, uw], F_M3)
        WA.ws.cell(WA.r - 1, 3).number_format = F_M2
        prev = rr["wykop"]
    c15, a0 = v1["scenariusze"]["C15"], v1["scenariusze"]["A0"]
    WA.wiersz("v1c15", ["v1", "Wcześniejszy arkusz – wariant A (skarpy 1:1,5), geometria z rysunku projektanta, dno 121,97", round(c15["pole_wykopu"], 2), round(c15["V_mineralny"], 3),
                        None, "prace/obliczenia_v1 (scenariusz C15)"], F_M3)
    WA.ws.cell(WA.r - 1, 3).number_format = F_M2
    WA.wiersz("v1a0", ["v1", "Wcześniejszy arkusz – A0 (ściany pionowe, teoretyczne minimum)", round(a0["pole_wykopu"], 2), round(a0["V_mineralny"], 3), None, "nie do wykonania bez obudowy"], F_M3)
    WA.ws.cell(WA.r - 1, 3).number_format = F_M2
    WA.r += 1
    for t in ("Różnica między krokiem 1d a wcześniejszym arkuszem (ok. +1 500 m³) wynika z danych, nie z metody: obrysy przeliczone do PZT (hale +89 m², hala 2 większa o 11% niż w "
              "odczycie z rysunku projektanta), nowy model terenu (bez zawyżonej siatki 10 m) i grubość humusu z 17 otworów i 5 CPTU.",
              "Obecny wariant A (krok 3) jest w arkuszu WYNIK. Dno 121,86 zamiast 121,97 dodaje ok. 1 800 m³, rampy i zadaszone dojazdy ok. 1 300 m³."):
        WA.wiersz(None, ["", t])
        WA.ws.merge_cells(start_row=WA.r - 1, start_column=2, end_row=WA.r - 1, end_column=6)
        WA.ws.row_dimensions[WA.r - 1].height = 32

    # =============================================================== GRUNTY
    GR = Arkusz(wb, "GRUNTY", ["Warstwa", "Grunt (DGI)", "Ocena DGI", "Wysadzinowość", "Zieleń (pod humusem)", "Nawierzchnie poniżej 1,00 m", "Strefa przemarzania 0,50–1,00 m",
                               "Wykop A [m³]", "Wykop B [m³]", "Źródło"], [9, 34, 24, 16, 14, 16, 22, 14, 14, 40])
    Arkusz.REJESTR["GRUNTY"] = GR
    GR.tytul("GRUNTY – przydatność do ponownego wbudowania",
             "Kryteria: DGI rozdz. 10–11 i 19–21 (nośność, wysadzinowość, wrażliwość glin na zawilgocenie, roboty w porze suchej), projekt geotechniczny s. 12 (grunt z ukopu do makroniwelacji i zasypów niebudowlanych, warstwy ≤ 0,30 m, Is > 0,95), "
             "decyzja użytkownika 8.10.2026 (zieleń – wszystkie grunty rodzime; nawierzchnie – przemarzanie 1,00 m, w strefie przemarzania grunt dowożony; grunt spod hal – do zasypu, ustalenie 18). Gleba: tylko jako humus. Nasyp: nieprzydatny (wywóz).")
    GR.naglowek()
    opis = {"Ia": ("piaski drobne i pylaste, szg", "nośne", "niewysadzinowe / wątpliwe (Pπ)"), "IIa": ("piaski średnie, luźne (tylko CPTU-10)", "słabonośne (w podłożu)", "niewysadzinowe"),
            "IIb": ("piaski średnie i grube, szg", "nośne", "niewysadzinowe"), "IIc": ("piaski średnie, zg/bzg", "nośne", "niewysadzinowe"),
            "IIIa": ("pospółki, szg", "nośne", "niewysadzinowe"), "IIIb": ("pospółki, zg", "nośne", "niewysadzinowe"),
            "IVa": ("gliny piaszczyste, plastyczne (CPTU-18, CPTU-24)", "słabonośne", "wysadzinowe"), "IVb": ("gliny, tpl/pl", "obniżona nośność", "wysadzinowe"),
            "IVc": ("gliny, pyły, tpl", "nośne", "wysadzinowe"), "IVd": ("gliny piaszczyste (zwięzłe), pzw/zw", "nośne", "wysadzinowe")}
    for k in D.KLASY:
        va = sum(wa["wykop_m3"][z][k] for z in "HORZU"); vb = sum(wb_["wykop_m3"][z][k] for z in "HORZU")
        piasek = k in D.PIASKI
        GR.wiersz("k_" + k, [k, opis[k][0], opis[k][1], opis[k][2], "TAK", "TAK", "piasek z wykopu – możliwy (opcja 5.5)" if piasek else "NIE – dowóz",
                             r3(va), r3(vb), "DGI rozdz. 10, zał. 8; karty 5.x; CPTU (zał. 7)"], F_M3)
    GR.wiersz("k_raz", ["RAZEM", "", "", "", "", "", "", "=ROUND(SUM(H%d:H%d),3)" % (GR.adr["k_Ia"], GR.adr["k_IVd"]), "=ROUND(SUM(I%d:I%d),3)" % (GR.adr["k_Ia"], GR.adr["k_IVd"]), "równe poz. 3.4 WYNIK (kontrola w KONTROLE)"], F_M3, pogr=True)
    GR.ws.cell(GR.adr["k_raz"], 10).value = "kontrola z poz. 3.4 w arkuszu KONTROLE"
    GR.r += 1
    GR.sekcja("Uwagi")
    for t in ("Grunt spod hal (ustalenie 18): DGI, projekt geotechniczny i opinia nie zawierają przeciwwskazań do ponownego wbudowania gruntu rodzimego; projekt geotechniczny (s. 12) "
              "dopuszcza grunt z ukopu do makroniwelacji i zasypów niebudowlanych (warstwy ≤ 0,30 m, Is > 0,95). Warunki poniżej.",
              "Gliny (IV) przy zawilgoceniu pęcznieją i uplastyczniają się – składować i wbudowywać w porze suchej, chronić przed wodą (DGI rozdz. 19, 21).",
              "Badania lab. (zał. F): gliny twardoplastyczne, IL 0,01–0,08, wn 11,1–12,9% (blisko granicy plastyczności) – nadają się do zagęszczenia, brak badań Proctora.",
              "IVa (plastyczne) występuje tylko w cienkich wkładkach w CPTU-18 i CPTU-24 – ilościowo pomijalna; przy wbudowaniu oddzielić, jeśli zostanie stwierdzona.",
              "Woda: zwierciadło ustabilizowane 122,90–124,10 m npm (śr. 123,39), wahania ±0,5 m (DGI tab. 1) – urobek spod zwierciadła (piaski nawodnione) wymaga odsączenia na odkładzie."):
        GR.wiersz(None, ["", t])
        GR.ws.merge_cells(start_row=GR.r - 1, start_column=2, end_row=GR.r - 1, end_column=10)

    # =============================================================== STREFY
    ST = Arkusz(wb, "STREFY", ["Strefa", "Bilans terenu PZT [m²]", "PZT wektorowy [m²]", "Model (raster) [m²]", "DXF v2 użytkownika [m²]", "Zasada w bilansie"], [40, 16, 16, 16, 16, 60])
    Arkusz.REJESTR["STREFY"] = ST
    ST.tytul("STREFY – pola powierzchni", "PZT wektorowy: wypełnienia z odzyskanej wersji wektorowej PZT (widoczne części), przycięte do granicy działki. Model: komórki rastra 0,25 m po nadaniu strefom kolejności H > R > O > Z > U.")
    ST.naglowek()
    P_ = W["pola"]; pp = st["pola"]
    for kl, rows in (
        ("s_dz", ["Działka 1/90", 25290.00, round(P_["dzialka"], 2), round(P_["dzialka_raster"], 2), round(kv2["granica"]["pole_v2"], 2), "granica po korekcie do PZT"]),
        ("s_h", ["Hale (obrys kondygnacji garażu)", None, round(P_["hale_obrysy"], 2), None, round(sum(v["pole_v2"] for v in kv2["hale"].values()), 2), "strefa hal – wykop na odkład (ustalenie 18)"]),
        ("s_zs", ["Zieleń na stropie garażu", 3975.11, pp["zielen_na_stropie"], None, v2_luki["ZIELEN-NA-STROPIE"], "w tabeli PZT 3 575,11 – literówka (z domknięcia 3 975,11); strefa hal"]),
        ("s_zad", ["   w tym poza obrysami hal (zadaszone dojazdy)", None, pp["zadaszone_poza_halami"], round(P_["zadaszone_poza_halami"], 2), None, "strefa hal (obiekt podziemny)"]),
        ("s_H", ["Strefa H razem (hale + zadaszone dojazdy)", None, None, P_["H_hale_i_zadaszone"], None, "wykop na odkład (ustalenie 18); bez zasypu – na stropie dowożony substrat"]),
        ("s_R", ["Rampy (pochylnie z murami)", 553.77, round(sum(__import__("shapely").wkt.loads(r["obrys"]).area for r in st["rampy"]), 2), P_["R_rampy"], None, "wykop do spodu rampy, zasyp gruntem z odkładu"]),
        ("s_O", ["Ogrody deszczowe", 253.00, pp["ogrody_deszczowe"], P_["O_ogrody"], None, "substrat 0,30 m + grunt z odkładu (ustalenie 20)"]),
        ("s_Z", ["Zieleń na gruncie rodzimym", 6443.06, pp["zielen_na_gruncie"], P_["Z_zielen"], v2_luki["ZIELEN-NA-GRUNCIE"], "0,25 m humusu + grunt rodzimy"]),
        ("s_geo", ["Geokrata na gruncie (część nawierzchni)", 980.05, pp["geokrata_na_gruncie"], None, None, "jak nawierzchnie"]),
        ("s_wiat", ["Wiaty (część nawierzchni)", 143.15, pp["wiaty"], None, None, "jak nawierzchnie"]),
        ("s_U", ["Nawierzchnie i pozostałe (strefa U)", None, None, P_["U_nawierzchnie"], None, "0,50 m konstrukcji + 0,50 m gruntu niewysadzinowego + grunt rodzimy"]),
    ):
        ST.wiersz(kl, rows, F_M2)
    ST.wiersz("s_suma", ["Suma stref modelu (H + R + O + Z + U)", None, None, "=ROUND(D{a}+D{b}+D{c}+D{d}+D{e},2)".format(a=ST.adr["s_H"], b=ST.adr["s_R"], c=ST.adr["s_O"], d=ST.adr["s_Z"], e=ST.adr["s_U"]),
                          None, "musi być równa polu działki w rastrze"], F_M2, pogr=True)

    # =============================================================== NIEPEWNOSC
    NP = Arkusz(wb, "NIEPEWNOSC", ["Zmiana założenia", "Δ wykop rodzimy A [m³]", "Δ wykop rodzimy B [m³]", "Δ nadwyżka gruntu rodzimego (wywóz) [m³]", "Δ grunt niewysadzinowy [m³]", "Δ humus [m³]"], [52, 18, 18, 20, 18, 14])
    Arkusz.REJESTR["NIEPEWNOSC"] = NP
    NP.tytul("NIEPEWNOŚĆ – jak zmieniają się wyniki przy zmianie jednego założenia", "Wyniki główne liczone z najlepszych danych; tu – wrażliwość (silnik uruchomiony ponownie z jedną zmianą). Liczby główne w arkuszu WYNIK nie zawierają tych odchyłek.")
    NP.naglowek()
    for c in N["przypadki"]:
        d = c["roznice"]
        NP.wiersz(None, [c["opis"], d["wykop_A"], d["wykop_B"], d["nadwyzka_A"], d["mroz_A"], d["humus"]], F_M3)
    NP.r += 1
    NP.sekcja("Inne źródła niepewności (oszacowanie)")
    for t in ("Strefy z PZT: zieleń na gruncie w PZT 6 417,55 m² wobec 6 443,06 m² w tabeli (−0,40%); humus na odkład liczony z tabeli (decyzja użytkownika).",
              "Nasyp: zasięg z mapy 4.3 (1:1000, dopasowanie rms 0,76 m), grubość 0,2–0,3 m – możliwe ±100 m³.",
              "Fundamenty głębsze: wymiary studzienek odczytane z rysunku 1A i przyjęte dla wszystkich budynków; bryły z poszerzeniem 0,50 m – możliwe ±30% (±400 m³).",
              "Rampy: spód wykopu = powierzchnia rampy − 0,71 m (zmiana o ±0,2 m – wiersze wyżej); rampy i zadaszone dojazdy liczone jak garaż (ustalenie 19).",
              "Ogrody deszczowe: rzędna ogrodu z rzędnych projektowych otoczenia (brak rzędnych dna ogrodów na PZT) – możliwe ±100 m³.",
              "Warstwy gruntu między otworami: interpolacja liniowa (TIN) 17 otworów i 5 CPTU; wkładki piasków są nieciągłe – podział piaski/gliny ±20%.",
              "Spulchnienie i gęstości gleby i nasypu – założenia (tylko tony i objętości luzem)."):
        NP.wiersz(None, [t])
        NP.ws.merge_cells(start_row=NP.r - 1, start_column=1, end_row=NP.r - 1, end_column=6)
        NP.ws.row_dimensions[NP.r - 1].height = 30

    # =============================================================== KONTROLE
    K = Arkusz(wb, "KONTROLE", ["Kontrola", "Wariant A", "Wariant B", "Oczekiwane", "Wynik"], [62, 16, 16, 12, 12])
    Arkusz.REJESTR["KONTROLE"] = K
    K.tytul("KONTROLE")
    K.naglowek()
    def kontrola(kl, op, fa, fb, ocz="0"):
        K.wiersz(kl, [op, fa, fb, ocz, '=IF(AND(ABS(B{r}-{o})<0.0015,ABS(C{r}-{o})<0.0015),"OK","BŁĄD")'.format(r=K.r, o=ocz)], F_M3)
    kontrola("c1", "Bilans urobku = 0 (WYNIK 7.1)", "={WYNIK!k_1:C}", "={WYNIK!k_1:D}")
    kontrola("c2", "Bilans wbudowania = 0 (WYNIK 7.2)", "={WYNIK!k_2:C}", "={WYNIK!k_2:D}")
    kontrola("c3", "Suma klas w GRUNTY − poz. 3.4", "=ROUND({GRUNTY!k_raz:H}-{WYNIK!g_raz:C},3)", "=ROUND({GRUNTY!k_raz:I}-{WYNIK!g_raz:D},3)")
    kontrola("c4", "Piaski + gliny − poz. 3.4", "=ROUND({WYNIK!g_pias:C}+{WYNIK!g_glin:C}-{WYNIK!g_raz:C},3)", "=ROUND({WYNIK!g_pias:D}+{WYNIK!g_glin:D}-{WYNIK!g_raz:D},3)")
    kontrola("c5", "Suma stref modelu − pole działki w rastrze", "=ROUND({STREFY!s_suma:D}-{STREFY!s_dz:D},2)", "=ROUND({STREFY!s_suma:D}-{STREFY!s_dz:D},2)")
    kontrola("c6", "Wykop poza działką", "={OBLICZENIA!poza_dz:C}", "={OBLICZENIA!poza_dz:D}")
    K.wiersz("c7", ["Decyzja w limitach (WYNIK 5.7)", "={WYNIK!d_kontr:C}", "={WYNIK!d_kontr:D}", "OK", '=IF(AND(B{r}="OK",C{r}="OK"),"OK","SPRAWDŹ")'.format(r=K.r)])
    K.r += 1
    K.sekcja("Weryfikacja arkusza niezależnym silnikiem formuł (biblioteka 'formulas') – wpisywana po zapisie pliku")
    K.wiersz("v1", ["Liczba komórek z formułami przeliczonych i porównanych", None, None, None, None])
    K.wiersz("v2", ["Największa różnica: arkusz (formulas) vs obliczenie w Pythonie [m³]", None, None, None, None])
    return wb, Arkusz.REJESTR


def wpisz_wartosci(sciezka):
    """Przelicza formuły biblioteką 'formulas' i wpisuje wyniki jako wartości buforowane (<v>) – podgląd bez Excela pokazuje liczby."""
    import formulas
    warnings.filterwarnings("ignore")
    xl = formulas.ExcelModel().loads(sciezka).finish()
    sol = xl.calculate()
    pref = re.compile(r"^'\[" + re.escape(os.path.basename(sciezka)) + r"\]([^']+)'!([A-Z]+[0-9]+)$", re.I)
    wart = {}
    for k, v in sol.items():
        m = pref.match(str(k))
        if not m:
            continue
        val = v
        for _ in range(5):   # Ranges -> tablica -> pierwsza komórka
            if hasattr(val, "value"):
                val = val.value
            elif hasattr(val, "__len__") and not isinstance(val, str):
                val = val[0]
            else:
                break
        try:
            val = float(val)
        except (TypeError, ValueError):
            val = str(val)
        wart[(m.group(1).upper(), m.group(2))] = val
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(sciezka) as z_:
        z_.extractall(tmp)
    wbxml = open(os.path.join(tmp, "xl/workbook.xml"), encoding="utf-8").read()
    kolejnosc = re.findall(r'<sheet [^>]*name="([^"]+)"', wbxml)
    wpisane = set()
    for i, nazwa in enumerate(kolejnosc, start=1):
        p = os.path.join(tmp, "xl/worksheets/sheet%d.xml" % i)
        t = open(p, encoding="utf-8").read()

        def podmien(m):
            v = wart.get((nazwa.upper(), m.group(1)))
            if v is None:
                return m.group(0)
            wpisane.add((nazwa, m.group(1)))
            if isinstance(v, str):
                return '<c r="%s"%s t="str"><f>%s</f><v>%s</v></c>' % (m.group(1), re.sub(r'\st="[^"]*"', "", m.group(2)), m.group(3), v)
            return '<c r="%s"%s><f>%s</f><v>%s</v></c>' % (m.group(1), m.group(2), m.group(3), repr(round(float(v), 9)))
        t2 = re.sub(r'<c r="([A-Z]+[0-9]+)"([^>]*)><f>(.*?)</f><v\s*/></c>', podmien, t)
        t2 = re.sub(r'<c r="([A-Z]+[0-9]+)"([^>]*)><f>(.*?)</f><v>[^<]*</v></c>', podmien, t2)
        open(p, "w", encoding="utf-8").write(t2)
    os.remove(sciezka)
    with zipfile.ZipFile(sciezka, "w", zipfile.ZIP_DEFLATED) as z_:
        z_.write(os.path.join(tmp, "[Content_Types].xml"), "[Content_Types].xml")
        for root, _, files in os.walk(tmp):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, tmp)
                if rel != "[Content_Types].xml":
                    z_.write(full, rel)
    shutil.rmtree(tmp)
    return len(wpisane), wart


def przelicz(sciezka):
    """Wartości wszystkich formuł policzone biblioteką 'formulas' (bez zapisu)."""
    kopia = sciezka + ".tmp.xlsx"
    shutil.copy(sciezka, kopia)
    n, wart = wpisz_wartosci(kopia)
    os.remove(kopia)
    return wart


if __name__ == "__main__":
    from openpyxl import load_workbook
    import kontrola_arkusza as KA
    os.makedirs(OUTDIR, exist_ok=True)
    wb, rej = zbuduj()
    wb.save(PLIK)
    wart = przelicz(PLIK.replace(".xlsx", "") + ".xlsx")
    n_por, mx, wiersze = KA.porownaj({(k[0], k[1]): v for k, v in wart.items()}, rej)
    n_f = sum(1 for k in wart)
    wb2 = load_workbook(PLIK)
    ws = wb2["KONTROLE"]
    K = rej["KONTROLE"]
    ws.cell(K.adr["v1"], 2, n_por); ws.cell(K.adr["v1"], 4, "pozycji WYNIK"); ws.cell(K.adr["v1"], 5, "OK" if n_por > 0 else "BŁĄD")
    ws.cell(K.adr["v2"], 2, round(mx, 6)); ws.cell(K.adr["v2"], 4, "< 0,001"); ws.cell(K.adr["v2"], 5, "OK" if mx < 0.001 else "BŁĄD")
    wb2.save(PLIK)
    n, wart = wpisz_wartosci(PLIK)
    print("zapisano", PLIK, "– formuł z wartościami:", n, "| kontrola niezależna: %d pozycji, maks. różnica %.6f m3" % (n_por, mx))
    for kl, col, v, a, d in wiersze:
        if d >= 0.001:
            print("   RÓŻNICA", kl, col, v, a)

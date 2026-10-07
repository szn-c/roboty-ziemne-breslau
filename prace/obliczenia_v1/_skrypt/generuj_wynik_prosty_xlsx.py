"""Buduje UPROSZCZONY arkusz (JEDEN wariant: wykop w scianie szczelnej, bez dowozu gruntu):
   00_WYNIKI/BILANS_ROBOT_ZIEMNYCH_dz190.xlsx          - 3 arkusze: WYNIK, ZALOZENIA, OBLICZENIA (liczby zaokraglone)
Wzory sa zywe (zmieniasz zolte pola w ZALOZENIA). Dodatkowo wpisujemy policzone wartosci do komorek,
zeby liczby byly widoczne tez w podgladzie bez silnika Excela."""
import os
import re
import shutil
import sys
import tempfile
import warnings
import zipfile

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bilans_formuly import wczytaj  # noqa: E402
from bilans_prosty import ZAL, dane_zaokraglone  # noqa: E402
from generuj_pliki import OUT  # noqa: E402

R = wczytaj()
D = dane_zaokraglone(R)
KAT = os.path.join(OUT, "00_WYNIKI")
os.makedirs(KAT, exist_ok=True)
GLOWNY = os.path.join(KAT, "BILANS_ROBOT_ZIEMNYCH_dz190.xlsx")

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
ww = wb.active
ww.title = "WYNIK"
wz = wb.create_sheet("ZALOZENIA")
wo = wb.create_sheet("OBLICZENIA")

# ============================================================================================ ZALOZENIA
for c, w in zip("ABCDEF", (4, 66, 14, 9, 14, 14)):
    wz.column_dimensions[c].width = w
wz.column_dimensions["G"].width = 84
wz["A1"] = "ZAŁOŻENIA – zmieniasz tylko żółte pola, reszta przelicza się sama"
wz["A1"].font = Font(bold=True, size=13)
wz["A2"] = "Przyjęto: wykop w ściance szczelnej (cały obszar w ściance, ściany pionowe, bez skarp), bez dowozu gruntu, cały grunt z wykopu nadaje się do wbudowania."
wz["A2"].font = Font(italic=True)
ZR = {}


def zrow(r, klucz, opis, wart, jedn, uw, fmt="#,##0.00"):
    wz.cell(r, 1, r - 3)
    wz.cell(r, 2, opis).alignment = WRAP
    c = wz.cell(r, 3, wart)
    c.number_format = fmt
    c.border = RAMKA
    c.fill = ZOLTY
    wz.cell(r, 4, jedn)
    wz.cell(r, 7, uw).alignment = WRAP
    ZR[klucz] = f"ZALOZENIA!$C${r}"


zrow(4, "potrzeba", "Humus potrzebny do zieleni (ten wróci na teren = odkład)", ZAL["humus_potrzeba"], "m³",
     "6 443 m² zieleni × 0,25 m + geokrata + 10% zapasu (PZT, Bilans terenu). Zieleń na stropie garażu NIE jest wliczona – jeśli ma dostać humus z budowy, dopisz np. +1 100 m³ (3 750 m² × 0,30 m).", "#,##0")
zrow(5, "zakres", "Jaka część działki POZA ścianką też jest odhumusowana i podnoszona do rzędnej projektowej", ZAL["zakres_poza"], "",
     "100% = cała działka 1/90. Jeśli pas poza ścianką zostaje nietknięty, wpisz 0% (mniej humusu o ok. 2 700 m³ i mniej zasypek o ok. 3 500 m³).", "0%")
zrow(6, "przyd", "Jaka część gruntu z wykopu (pod humusem) nadaje się do ponownego wbudowania", ZAL["przydatny"], "",
     "Założenie: 100%. Grunt mokry spod zwierciadła wody wymaga odwodnienia i osuszenia, zanim trafi do nasypu – wpisz mniej, jeśli geotechnik tego nie dopuści.", "0%")
zrow(7, "dz", "Zmiana rzędnej dna względem 121,97 m npm (ujemna = głębiej)", ZAL["dno_zm"], "m",
     "Dno 121,97 = posadzka 122,57 − płyta 0,50 − chudy beton 0,10. Podsypka pod chudziakiem? Wpisz np. −0,20.")
zrow(8, "fgw", "Rzędna terenu projektowanego w ściance (średnia)", ZAL["fg_w"], "m npm", "z PZT, między halami 125,4–125,98. Wpływa na zapotrzebowanie na zasypki.")
zrow(9, "fgp", "Rzędna terenu projektowanego poza ścianką (średnia)", ZAL["fg_poza"], "m npm", "z PZT, duży rozrzut 124,4–125,96. Wpływa na zapotrzebowanie na zasypki.")
zrow(10, "t", "Grubość warstw wierzchnich, które nie są z wykopu (humus / nawierzchnia)", ZAL["t"], "m", "zieleń ok. 0,25 m, nawierzchnie 0,45–0,55 m. Wpływa na zapotrzebowanie na zasypki.")
wz["B12"] = "Współczynniki do przeliczeń"
wz["B12"].font = B
for c, t in zip("CDE", ("Humus", "Nasyp", "Grunt z wykopu")):
    wz[f"{c}12"] = t
    wz[f"{c}12"].font = B
    wz[f"{c}12"].fill = SZARY
    wz[f"{c}12"].alignment = Alignment(wrap_text=True, horizontal="center")
wz.row_dimensions[12].height = 30
wz["B13"] = "Spulchnienie (m³ luzem na 1 m³ w ziemi)"
wz["B14"] = "Gęstość w ziemi [t/m³]"
KS, RO = {}, {}
for col, k in zip("CDE", ("humus", "nasyp", "glina")):
    for r_, v, dic in ((13, ZAL["ks"][k], KS), (14, ZAL["ro"][k], RO)):
        c = wz[f"{col}{r_}"]
        c.value = v
        c.fill = ZOLTY
        c.border = RAMKA
        c.number_format = "0.00"
        dic[k] = f"ZALOZENIA!${col}${r_}"
wz["G13"] = "wartości typowe (grunt z wykopu to głównie gliny) – sprawdź z firmą transportową"

# ============================================================================================ OBLICZENIA
for c, w in zip("ABC", (76, 16, 70)):
    wo.column_dimensions[c].width = w
wo["A1"] = "OBLICZENIA (niezaokrąglone) – tu nic nie zmieniasz. Szare = dane z modelu, zielone = wzory."
wo["A1"].font = Font(bold=True, size=12)
RW = {}


def sekcja(r, tekst):
    wo.cell(r, 1, tekst).font = Font(bold=True, size=11)
    for col in "ABC":
        wo[f"{col}{r}"].fill = NIEB


def dane(r, klucz, opis, v, fmt="#,##0", uw=""):
    wo.cell(r, 1, opis)
    c = wo[f"B{r}"]
    c.value = v
    c.number_format = fmt
    c.fill = JASNY
    c.border = RAMKA
    wo.cell(r, 3, uw).alignment = WRAP
    RW[klucz] = r


def wzor(r, klucz, opis, f, fmt="#,##0", uw="", bold=False):
    wo.cell(r, 1, opis)
    c = wo[f"B{r}"]
    c.value = "=" + f
    c.number_format = fmt
    c.fill = ZIELONY
    c.border = RAMKA
    if bold:
        c.font = B
        wo.cell(r, 1).font = B
    wo.cell(r, 3, uw).alignment = WRAP
    RW[klucz] = r


z = ZR
sekcja(3, "A. Dane z modelu (zaokrąglone do 10 m² / 10 m³)")
dane(4, "pole", "Pole wykopu = pole w obrysie ścianki [m²]", D["pole"], uw="wielokąt z rysunku projektanta; obwód 563,5 m (na rysunku: ok. 565 mb)")
dane(5, "hale", "Pole 8 hal garażowych [m²]", D["hale"], uw="obrys zewnętrzny z rysunku projektanta")
dane(6, "Vb", "Wykop brutto: od terenu istniejącego do dna 121,97 [m³]", D["Vb"], uw="średnia głębokość 2,69 m; teren istniejący średnio 124,66 m npm")
dane(7, "Vhn", "   w tym humus i nasyp leżące w wykopie [m³]", D["Vhn"])
dane(8, "poleDz", "Pole działki 1/90, oficjalne [m²]", D["pole_dz"])
wzor(9, "polePoza", "Pole działki poza obrysem ścianki [m²]", "B8-B4")
dane(10, "hW", "Humus w obrysie ścianki [m³]", D["humus_W"], uw="średnia grubość 0,61 m (17 otworów)")
dane(11, "hP", "Humus poza ścianką, przy 100% zakresu [m³]", D["humus_poza"], uw="średnia grubość 0,57 m")
dane(12, "nW", "Nasyp niekontrolowany w ściance [m³]", D["nasyp_W"], uw="tylko otwory 5, 17, 20 – wynik bardzo niepewny (±50%)")
dane(13, "nP", "Nasyp niekontrolowany poza ścianką, przy 100% zakresu [m³]", D["nasyp_poza"])
dane(14, "S0p", "Średnia rzędna gruntu pod humusem poza ścianką [m npm]", D["S0_poza"], "0.00")
dane(15, "dno0", "Rzędna dna wykopu bazowa [m npm]", D["dno0"], "0.00")

sekcja(17, "B. Humus i nasyp")
wzor(18, "hRazem", "Humus do zebrania", "B10+B11*%s" % z["zakres"])
wzor(19, "hOdkl", "Humus na odkład", "MIN(B18,%s)" % z["potrzeba"], uw="tyle, ile wróci do zieleni")
wzor(20, "hWyw", "Humus do utylizacji", "B18-B19", uw="nadwyżka ponad potrzeby zieleni")
wzor(21, "nas", "Nasyp niekontrolowany (do utylizacji)", "B12+B13*%s" % z["zakres"])
sekcja(23, "C. Grunt z wykopu (pod humusem) – bilans z zapotrzebowaniem")
wzor(24, "Vmin", "Grunt z wykopu", "(B6-%s*B4)-B7" % z["dz"], uw="wykop brutto (z korektą dna) minus humus i nasyp")
wzor(25, "przyd", "Grunt przydatny do wbudowania", "B24*%s" % z["przyd"])
F = "(%s-%s)" % (z["fgw"], z["t"])
Fo = "(%s-%s)" % (z["fgp"], z["t"])
wzor(26, "d1", "Zasypki w wykopie wokół hal (bez pola hal)", "(B4-B5)*(%s-(B15+%s))" % (F, z["dz"]),
     uw="od dna wykopu do rzędnej projektowej minus warstwy wierzchnie; nad halami gruntu nie liczymy (strop + warstwy projektowe)")
wzor(27, "d2", "Podniesienie terenu poza ścianką", "B9*%s*MAX(0,%s-B14)" % (z["zakres"], Fo), uw="bardzo orientacyjne (rzędne projektowe poza ścianką mocno się różnią)")
wzor(28, "d", "Zapotrzebowanie na grunt razem", "B26+B27", bold=True)
wzor(29, "mOdkl", "Na odkład (ponownie wbudowany)", "MIN(B25,B28)", bold=True, uw="wykop pokrywa zapotrzebowanie, dowozu nie ma")
wzor(30, "mNadw", "Nadwyżka gruntu do utylizacji", "B24-B29", bold=True, uw="grunt z wykopu ponad zapotrzebowanie (albo nieprzydatny)")
wzor(31, "brak", "Brakuje gruntu (kontrola; wg założenia ma być 0)", "MAX(0,B28-B25)", uw="gdyby było więcej niż 0, trzeba by dowieźć albo mniej podnieść teren")
sekcja(33, "D. Luzem i tony")
wzor(34, "luzem", "Do utylizacji – m³ luzem", "B20*%s+B21*%s+B30*%s" % (KS["humus"], KS["nasyp"], KS["glina"]))
wzor(35, "tony", "Do utylizacji – tony", "B20*%s+B21*%s+B30*%s" % (RO["humus"], RO["nasyp"], RO["glina"]))
wzor(36, "odkLuzem", "Na odkładzie – m³ luzem (wielkość hałd)", "B19*%s+B29*%s" % (KS["humus"], KS["glina"]))
wzor(37, "kontrola", "Kontrola: humus + nasyp + grunt = odkład + utylizacja (ma być 0)", "ROUND(B18+B21+B24-(B19+B29)-(B20+B21+B30),0)")
wo.freeze_panes = "A3"

# ============================================================================================ WYNIK
for c, w in zip("ABC", (66, 18, 82)):
    ww.column_dimensions[c].width = w
ww["A1"] = "BILANS ROBÓT ZIEMNYCH – działka 1/90, Wojszyce (Wrocław)"
ww["A1"].font = Font(bold=True, size=15)
ww["A2"] = "Wykop w ściance szczelnej: cały obszar w ściance, ściany pionowe, dno 121,97 m npm. Bez dowozu gruntu; cały grunt z wykopu nadaje się do wbudowania."
ww["A2"].font = B
ww["A3"] = "Objętości w m³ w ziemi (nie luzem). Zaokrąglone: m³ do 100, tony do 1 000. Sumy = suma zaokrąglonych pozycji."
ww["A3"].font = Font(italic=True)
for c, t in (("B", "m³ w ziemi"), ("C", "Uwagi")):
    ww[f"{c}5"] = t
    ww[f"{c}5"].font = B
    ww[f"{c}5"].fill = SZARY
    ww[f"{c}5"].alignment = Alignment(horizontal="center" if c == "B" else "left")
ww["A5"].fill = SZARY
WR = {}


def wrow(r, klucz, opis, f, uw="", bold=False, fmt="#,##0"):
    ww.cell(r, 1, opis)
    c = ww[f"B{r}"]
    c.value = "=" + f
    c.number_format = fmt
    c.border = RAMKA
    c.fill = ZIELONY
    if bold:
        c.font = B
        ww.cell(r, 1).font = B
    ww.cell(r, 3, uw).alignment = WRAP
    WR[klucz] = r


def wsekcja(r, tekst):
    ww.cell(r, 1, tekst).font = Font(bold=True, size=12)
    for col in "ABC":
        ww[f"{col}{r}"].fill = NIEB


wsekcja(6, "HUMUS (cała działka 1/90)")
wrow(7, "hOdkl", "Humus na odkład (wraca do zieleni)", "ROUND(OBLICZENIA!B19,-2)", uw="tyle potrzeba do zieleni na gruncie (z zapasem)")
wrow(8, "hWyw", "Humus do utylizacji", "ROUND(OBLICZENIA!B20,-2)", uw="nadwyżka – dobry materiał, warto sprawdzić sprzedaż")
wrow(9, "hRazem", "Humus do zebrania – razem", "B7+B8", bold=True)
wrow(10, "nas", "Nasyp niekontrolowany – do utylizacji", "ROUND(OBLICZENIA!B21,-2)", uw="warstwa pod humusem w otworach 5, 17, 20; wynik bardzo niepewny")
wsekcja(11, "GRUNT Z WYKOPU (pod humusem)")
wrow(12, "d", "Zapotrzebowanie na zasypki i podniesienie terenu do rzędnej projektowej", "ROUND(OBLICZENIA!B28,-2)", uw="orientacyjnie – zależy od rzędnych projektowych i grubości warstw wierzchnich")
wrow(13, "mOdkl", "Na odkład (ponownie wbudowany)", "ROUND(OBLICZENIA!B29,-2)", uw="cały ten grunt trzeba przechować do czasu zasypywania")
wrow(14, "mNadw", "Nadwyżka do utylizacji", "ROUND(OBLICZENIA!B30,-2)", uw="grunt z wykopu ponad zapotrzebowanie")
wrow(15, "mRazem", "Grunt z wykopu – razem", "B13+B14", bold=True)
wsekcja(16, "RAZEM")
wrow(17, "odkl", "NA ODKŁAD", "B7+B13", bold=True)
wrow(18, "wyw", "DO UTYLIZACJI", "B8+B10+B14", bold=True, uw="humus + nasyp + nadwyżka gruntu")
wrow(19, "luzem", "   do utylizacji – m³ luzem", "ROUND(OBLICZENIA!B34,-2)", uw="do planowania transportu")
wrow(20, "tony", "   do utylizacji – tony", "ROUND(OBLICZENIA!B35,-3)")
wrow(21, "odkLuzem", "   na odkładzie – m³ luzem", "ROUND(OBLICZENIA!B36,-2)", uw="wielkość hałd; poza ścianką jest tylko ok. 4 600 m² – odkład się tam nie zmieści (etapowanie albo skład tymczasowy)")
wrow(22, "brak", "Brakuje gruntu (kontrola, wg założenia 0)", "ROUND(OBLICZENIA!B31,-2)", uw="dowozu nie ma; jeśli > 0, zapotrzebowanie przekracza wykop")
wsekcja(24, "CO ZMIENIA WYNIK (m³ w ziemi)")
wrow(25, "c1", "Każde 10 cm głębsze dno (np. podsypka): nadwyżka gruntu rośnie o", "ROUND(OBLICZENIA!B5*0.1,-2)", uw="wykop rośnie o ok. 2 100 m³, ale zasypki wokół hal też; przyrost nadwyżki to grunt spod hal")
wrow(26, "c2", "Teren projektowany 10 cm wyżej (albo warstwy wierzchnie 10 cm cieńsze): nadwyżka maleje o", "ROUND((OBLICZENIA!B4-OBLICZENIA!B5+OBLICZENIA!B9*%s)*0.1,-2)" % ZR["zakres"], uw="to najmniej pewne dane – patrz ZALOZENIA")
wrow(27, "c3", "Humus z budowy na stropie garażu (3 750 m² × 0,30 m): więcej na odkład o", "ROUND(3750*0.3,-2)", uw="o tyle mniej humusu do utylizacji")
wrow(28, "c4", "Pas poza ścianką nietknięty: mniej humusu o", "ROUND(OBLICZENIA!B11,-2)", uw="i mniej zasypek o ok. 3 500 m³ (wpisz 0% w ZALOZENIA)")
ww["A30"] = "Dokładność: humus ok. ±5%, wykop brutto ok. ±4%, nasyp niekontrolowany ±50%; zapotrzebowanie (a więc i nadwyżka) tylko rząd wielkości (±2 000 m³)."
ww["A31"] = "Nie ma w liczbach: rampy do garaży (ok. 500 m³), zagłębienia pod windy, odwodnienie wykopu, podsypka pod chudym betonem, zagęszczenie nasypów."
ww["A32"] = "Nadwyżka humusu i gruntu łącznie jest taka sama, niezależnie od tego, co z czego wbudujecie (humus 13 500 + nasyp 1 300 + grunt 8 100 = 22 900 m³)."
ww.freeze_panes = "A6"
wb.calculation.fullCalcOnLoad = True


# ============================================================================================ wartosci w komorkach
def policz_formuly(sciezka):
    """Zwraca slownik {(ARKUSZ, ADRES): wartosc} wyliczony biblioteka 'formulas' (niezalezny silnik niz Excel)."""
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
        try:
            val = v.value[0][0] if hasattr(v.value, "__len__") else v.value
            wart[(m.group(1).upper(), m.group(2))] = float(val)
        except Exception:
            pass
    return wart


def wpisz_wartosci(sciezka):
    """Wpisuje wyliczone wartosci jako wartosci buforowane (<v>) obok wzorow - podglad bez silnika Excela pokazuje liczby."""
    wart = policz_formuly(sciezka)
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(sciezka) as z_:
        z_.extractall(tmp)
    kolejnosc = re.findall(r'<sheet name="([^"]+)"', open(os.path.join(tmp, "xl/workbook.xml"), encoding="utf-8").read())
    n_wpis = 0
    for i, nazwa in enumerate(kolejnosc, start=1):
        p = os.path.join(tmp, f"xl/worksheets/sheet{i}.xml")
        t = open(p, encoding="utf-8").read()

        def podmien(m):
            v = wart.get((nazwa.upper(), m.group(1)))
            if v is None:
                return m.group(0)
            return f'<c r="{m.group(1)}"{m.group(2)}><f>{m.group(3)}</f><v>{repr(round(v, 9))}</v></c>'
        t2, n = re.subn(r'<c r="([A-Z]+[0-9]+)"([^>]*)><f>(.*?)</f><v\s*/></c>', podmien, t)
        open(p, "w", encoding="utf-8").write(t2)
        n_wpis += n
    os.remove(sciezka)
    with zipfile.ZipFile(sciezka, "w", zipfile.ZIP_DEFLATED) as z_:
        # [Content_Types].xml musi byc pierwszy
        z_.write(os.path.join(tmp, "[Content_Types].xml"), "[Content_Types].xml")
        for root, _, files in os.walk(tmp):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, tmp)
                if rel != "[Content_Types].xml":
                    z_.write(full, rel)
    shutil.rmtree(tmp)
    return n_wpis, len(wart)


if __name__ == "__main__":
    wb.save(GLOWNY)
    print("zapisano", GLOWNY)
    print("wpisano wartosci:", wpisz_wartosci(GLOWNY))

"""Arkusz bilansu robót ziemnych - wpisujesz wyniki z Civil 3D, arkusz liczy odkład / wywóz."""
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "02_zestawienia_excel")
os.makedirs(OUT, exist_ok=True)

ZOLTY = PatternFill("solid", fgColor="FFF2CC")
SZARY = PatternFill("solid", fgColor="D9D9D9")
ZIELONY = PatternFill("solid", fgColor="E2EFDA")
B = Font(bold=True)
cienka = Side(style="thin", color="999999")
RAMKA = Border(left=cienka, right=cienka, top=cienka, bottom=cienka)

wb = Workbook()
ws = wb.active
ws.title = "Bilans"
ws.column_dimensions["A"].width = 62
for c in "BCDE":
    ws.column_dimensions[c].width = 16
ws.column_dimensions["F"].width = 60


def wiersz(r, opis, wartosc=None, jedn="", uwaga="", wej=False, fmt="#,##0"):
    ws.cell(r, 1, opis)
    c = ws.cell(r, 2, wartosc)
    c.number_format = fmt
    c.border = RAMKA
    if wej:
        c.fill = ZOLTY
    ws.cell(r, 3, jedn)
    ws.cell(r, 6, uwaga).alignment = Alignment(wrap_text=True)


ws["A1"] = "BILANS ROBÓT ZIEMNYCH - dz. 1/90 obr. Wojszyce"
ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = "Żółte pola = wpisz wartości (z Civil 3D / z projektu). Reszta liczy się sama."
ws["A2"].font = Font(italic=True)

ws["A4"] = "A. DANE Z CIVIL 3D (objętości w gruncie rodzimym, m³)"
ws["A4"].font = B
wiersz(5, "V1 - humus na całym obszarze zdejmowania", None, "m³", "Krok 7.1 instrukcji: VOL_HUMUS, Fill, obrys ZAKRES_HUMUS", True)
wiersz(6, "V2 - nasyp na całym obszarze zdejmowania", None, "m³", "Krok 7.2: VOL_NASYP, Fill, obrys ZAKRES_HUMUS", True)
wiersz(7, "V3 - wykop liczony od istniejącego terenu", None, "m³", "Krok 7.3: VOL_WYKOP, Cut", True)
wiersz(8, "V4 - humus w obrysie wykopu (górna krawędź)", None, "m³", "Krok 7.4: VOL_HUMUS, Fill, obrys GORA_WYKOPU", True)
wiersz(9, "V5 - nasyp w obrysie wykopu (górna krawędź)", None, "m³", "Krok 7.4: VOL_NASYP, Fill, obrys GORA_WYKOPU", True)
wiersz(10, "V7 - piaski/pospółki w wykopie", None, "m³", "Krok 7.5: VOL_PIASEK_xxx, Fill, obrys DNO_WYKOPU", True)

ws["A12"] = "B. DANE Z PROJEKTU"
ws["A12"].font = B
wiersz(13, "Pole terenów zielonych do humusowania", None, "m²", "z PZT", True)
wiersz(14, "Grubość humusowania", 0.20, "m", "typowo 0,15-0,30 m - wg projektu zieleni", True, "0.00")
wiersz(15, "Zapas humusu na odkładzie", 0.10, "", "np. 10% na straty", True, "0%")
wiersz(16, "Zapotrzebowanie na grunt z wykopu (zasypki + podniesienie terenu do rzędnych proj.)", None, "m³", "zasypki przy ścianach garażu + nasypy do terenu proj. (przekrój 2C: 125,89 m npm). Z Civil 3D: Base=EG, Comparison=TEREN_PROJ, Fill, poza garażem; dolicz V1 (humus zdjęty spod nasypu)", True)
wiersz(17, "Udział piasków, które da się wybrać osobno (selektywnie)", 0.50, "", "cienkie przewarstwienia mieszają się z gliną - przyjmij ostrożnie", True, "0%")
wiersz(18, "Udział glin nadających się do ponownego wbudowania w nasypy", 0.0, "", "0% = wszystko na wywóz. Zmień dopiero po opinii geotechnika (gliny mokre spod zwierciadła wody zwykle wymagają osuszenia/stabilizacji)", True, "0%")

ws["A20"] = "C. PARAMETRY PRZELICZENIOWE"
ws["A20"].font = B
for col, t in zip("BCDE", ["Humus", "Nasyp", "Glina", "Piasek"]):
    ws[f"{col}21"] = t
    ws[f"{col}21"].font = B
    ws[f"{col}21"].fill = SZARY
ws["A22"] = "Współczynnik spulchnienia (m³ luzem / m³ rodzimy)"
ws["A23"] = "Gęstość objętościowa w gruncie rodzimym [t/m³]"
for col, ks, ro in zip("BCDE", [1.25, 1.25, 1.30, 1.15], [1.50, 1.80, 2.10, 1.90]):
    for r, v in ((22, ks), (23, ro)):
        c = ws[f"{col}{r}"]
        c.value = v
        c.fill = ZOLTY
        c.number_format = "0.00"
        c.border = RAMKA
ws["F22"] = "wartości typowe - zweryfikuj z wykonawcą"
ws["F23"] = "glina/piasek: zakresy z DGI (gliny 2,0-2,25; piaski 1,75-2,05); humus i nasyp - przyjęte typowo"

ws["A25"] = "D. WYNIKI"
ws["A25"].font = B
for col, tt in zip("BCD", ["m³ rodzime", "m³ luzem", "tony [Mg]"]):
    ws[f"{col}26"] = tt
    ws[f"{col}26"].font = B
    ws[f"{col}26"].fill = SZARY

wyniki = [
    # (opis, formuła, kolumna parametrów)
    ("Humus - NA ODKŁAD", "=MIN(B5,B13*B14*(1+B15))", "B"),                       # 27
    ("Humus - DO WYWOZU (nadmiar)", "=B5-B27", "B"),                              # 28
    ("Nasyp - DO WYWOZU / utylizacji", "=B6", "C"),                               # 29
    ("Grunt rodzimy w wykopie razem (V3-V4-V5)", "=B7-B8-B9", None),              # 30
    ("   w tym gliny (V3-V4-V5-V7)", "=B30-B10", "D"),                            # 31
    ("   w tym piaski/pospółki (V7)", "=B10", "E"),                               # 32
    ("Piaski możliwe do osobnego wybrania", "=B32*B17", "E"),                     # 33
    ("Piasek - NA ODKŁAD (do wbudowania)", "=MIN(B16,B33)", "E"),                 # 34
    ("Glina - NA ODKŁAD (do wbudowania, jeśli dopuszczona)", "=MIN(MAX(0,B16-B34),B31*B18)", "D"),  # 35
    ("Niedobór gruntu (dowóz)", "=MAX(0,B16-B34-B35)", None),                     # 36
    ("Gliny - DO WYWOZU", "=B31-B35", "D"),                                       # 37
    ("Piaski - DO WYWOZU (nadmiar + wymieszane z gliną)", "=B32-B34", "E"),       # 38
    ("RAZEM DO WYWOZU (humus + nasyp + gliny + piaski)", "=B28+B29+B37+B38", None),  # 39
]
r = 27
for opis, f, p in wyniki:
    ws.cell(r, 1, opis)
    c = ws.cell(r, 2, f)
    c.number_format = "#,##0"
    c.border = RAMKA
    c.fill = ZIELONY
    if p:
        ws.cell(r, 3, f"=B{r}*{p}22").number_format = "#,##0"
        ws.cell(r, 4, f"=B{r}*{p}23").number_format = "#,##0"
    r += 1
ws["C30"] = "=C31+C32"
ws["D30"] = "=D31+D32"
ws["C39"] = "=C28+C29+C37+C38"
ws["D39"] = "=D28+D29+D37+D38"
for cell in ("C30", "D30", "C39", "D39"):
    ws[cell].number_format = "#,##0"
for rr in (27, 34, 35, 39):
    ws.cell(rr, 1).font = B

ws["A41"] = "Kontrola: V4 musi być mniejsze od V1, a V5 od V2. Średnia grubość humusu = V1 / pole ZAKRES_HUMUS powinna wyjść ok. 0,55-0,70 m."
ws["A41"].font = Font(italic=True)
ws["A42"] = "Pole obszaru ZAKRES_HUMUS [m²]:"
ws["B42"].fill = ZOLTY
ws["B42"].border = RAMKA
ws["A43"] = "Średnia grubość humusu [m] = V1 / pole"
ws["B43"] = '=IF(B42>0,B5/B42,"")'
ws["B43"].number_format = "0.00"


# ===================== ARKUSZ 2: BILANS WSTĘPNY (dwa warianty) =====================
w2 = wb.create_sheet("Bilans wstępny")
w2.column_dimensions["A"].width = 72
w2.column_dimensions["B"].width = 20
w2.column_dimensions["C"].width = 20
w2.column_dimensions["D"].width = 70
w2["A1"] = "BILANS WSTĘPNY - garaże podziemne 8 hal + ścianka szczelna/berlińska (ok. 565 mb)"
w2["A1"].font = Font(bold=True, size=14)
w2["A2"] = "Szacunek z rzutu i przekroju 2C, do kontroli wyników z Civil 3D. Żółte pola = założenia, które możesz zmienić."
w2["A2"].font = Font(italic=True)

def w2row(r, opis, b=None, jedn="", uwaga="", wej=False, fmt="#,##0"):
    w2.cell(r, 1, opis)
    c = w2.cell(r, 2, b)
    c.number_format = fmt
    c.border = RAMKA
    if wej:
        c.fill = ZOLTY
    w2.cell(r, 3, jedn)
    w2.cell(r, 4, uwaga).alignment = Alignment(wrap_text=True)

w2["A4"] = "A. DANE WEJŚCIOWE"
w2["A4"].font = B
w2row(5, "Pole w obrysie ścianki (A_ring)", 19600, "m²", "szacunek z rzutu (±5%); zmierz polilinią wzdłuż ścianki w Civil 3D", True)
w2row(6, "Długość ścianki", 565, "m", "z opisu na rzucie; kontrola skali po obrysowaniu", True)
w2row(7, "Suma pól stref pożarowych 8 hal", 11001, "m²", "hala 1 ma na rzucie 0,00 - przyjęto 1390 m²", True)
w2row(8, "Pole dna wykopu pod halami z przestrzenią roboczą (wariant A)", 12564, "m²", "wnętrze hal + ściany 0,35 m + przestrzeń robocza 0,9 m, prostokąty 1,5:1", True)
w2row(9, "Pole zewnętrzne konstrukcji hal (płyta)", 11420, "m²", "wnętrze + ściany 0,35 m", True)
w2row(10, "Średnia rzędna istniejącego terenu", 124.65, "m npm", "średnia z 17 otworów po korekcie terenu +0,16 m", True, "0.00")
w2row(11, "Rzędna dna wykopu", 121.97, "m npm", "122,57 - płyta 0,50 - chudy beton 0,10", True, "0.00")
w2row(12, "Średnia rzędna terenu projektowanego", 125.80, "m npm", "przekrój 2C: 125,89; rzut: 125,56-125,83 przy rampach", True, "0.00")
w2row(13, "Rzędna wierzchu stropu nad halami (założenie)", 125.30, "m npm", "teren proj. minus ok. 0,5 m nadkładu - ZWERYFIKUJ z projektem", True, "0.00")
w2row(14, "Średnia grubość humusu", 0.63, "m", "z 17 otworów", True, "0.00")
w2row(15, "Średnia grubość nasypu niekontrolowanego", 0.03, "m", "nasyp tylko w otworach 5, 17, 20", True, "0.000")
w2row(16, "Udział piasków w gruncie pod humusem (do dna wykopu)", 0.19, "", "z otworów dla dna 121,97", True, "0%")
w2row(17, "Udział gruntu pod humusem poniżej zwierciadła wody", 0.53, "", "z 16 otworów, zwierciadło ustabilizowane; grunt mokry", True, "0%")
w2row(18, "Pole terenów zielonych do humusowania", 6000, "m²", "ZAŁOŻENIE - uzupełnij z PZT", True)
w2row(19, "Grubość humusowania", 0.25, "m", "wg projektu zieleni", True, "0.00")
w2row(20, "Zapas humusu na odkładzie", 0.10, "", "", True, "0%")
w2row(21, "Udział piasków możliwych do wybrania osobno", 0.50, "", "cienkie przewarstwienia mieszają się z gliną", True, "0%")
w2row(22, "Udział suchych glin dopuszczonych do wbudowania w nasypy", 0.0, "", "0% = wszystkie gliny na wywóz; zmień po opinii geotechnika", True, "0%")

w2["A24"] = "B. WYNIKI (m³ w gruncie rodzimym, o ile nie napisano inaczej)"
w2["A24"].font = B
w2["B25"] = "Wariant A: wykop tylko pod halami"
w2["C25"] = "Wariant B: cały obszar w ściance"
for c in ("B25", "C25"):
    w2[c].font = B
    w2[c].fill = SZARY
    w2[c].alignment = Alignment(wrap_text=True, horizontal="center")
w2.row_dimensions[25].height = 32

linie = [
    (26, "Pole wykopu [m²]", "=B8", "=B5", "#,##0"),
    (27, "Głębokość od średniego terenu [m]", "=$B$10-$B$11", "=$B$10-$B$11", "0.00"),
    (28, "Wykop brutto (teren istniejący do dna), ściany pionowe", "=B26*B27", "=C26*C27", "#,##0"),
    (29, "   w tym humus + nasyp leżący w wykopie", "=B26*($B$14+$B$15)", "=C26*($B$14+$B$15)", "#,##0"),
    (30, "   Grunt rodzimy pod humusem w wykopie", "=B28-B29", "=C28-C29", "#,##0"),
    (31, "      w tym piaski/pospółki", "=B30*$B$16", "=C30*$B$16", "#,##0"),
    (32, "      w tym gliny", "=B30-B31", "=C30-C31", "#,##0"),
    (33, "      w tym grunt poniżej zwierciadła wody (mokry)", "=B30*$B$17", "=C30*$B$17", "#,##0"),
    (35, "Humus z całego terenu robót (w ściance)", "=$B$5*$B$14", "=$B$5*$B$14", "#,##0"),
    (36, "Nasyp niekontrolowany (gruz, cegła) z całego terenu", "=$B$5*$B$15", "=$B$5*$B$15", "#,##0"),
    (37, "Humus NA ODKŁAD (zieleń + zapas)", "=MIN(B35,$B$18*$B$19*(1+$B$20))", "=MIN(C35,$B$18*$B$19*(1+$B$20))", "#,##0"),
    (38, "Humus DO WYWOZU / utylizacji", "=B35-B37", "=C35-C37", "#,##0"),
    (40, "Zapotrzebowanie: zasypki wokół i nad halami", "=MAX(0,B26*($B$12-$B$11)-$B$9*($B$13-$B$11))", "=MAX(0,C26*($B$12-$B$11)-$B$9*($B$13-$B$11))", "#,##0"),
    (41, "Zapotrzebowanie: nasyp poza wykopem (podniesienie terenu)", "=MAX(0,($B$5-B26)*($B$12-($B$10-$B$14-$B$15)))", "=MAX(0,($B$5-C26)*($B$12-($B$10-$B$14-$B$15)))", "#,##0"),
    (42, "Zapotrzebowanie razem", "=B40+B41", "=C40+C41", "#,##0"),
    (44, "Piasek NA ODKŁAD (zasypki przy halach)", "=MIN(B40,B31*$B$21)", "=MIN(C40,C31*$B$21)", "#,##0"),
    (45, "Glina NA ODKŁAD (nasypy niekonstrukcyjne, jeśli dopuszczona)", "=MIN(MAX(0,B42-B44),B32*(1-$B$17)*$B$22)", "=MIN(MAX(0,C42-C44),C32*(1-$B$17)*$B$22)", "#,##0"),
    (46, "GRUNT DO DOWIEZIENIA (import)", "=MAX(0,B42-B44-B45)", "=MAX(0,C42-C44-C45)", "#,##0"),
    (47, "Gliny DO WYWOZU", "=B32-B45", "=C32-C45", "#,##0"),
    (48, "Piaski DO WYWOZU", "=B31-B44", "=C31-C44", "#,##0"),
    (49, "Nasyp niekontrolowany DO WYWOZU / utylizacji", "=B36", "=C36", "#,##0"),
    (50, "Humus DO WYWOZU / utylizacji", "=B38", "=C38", "#,##0"),
    (51, "RAZEM DO WYWOZU [m³ rodzime]", "=B47+B48+B49+B50", "=C47+C48+C49+C50", "#,##0"),
    (52, "RAZEM DO WYWOZU [m³ luzem]", "=B47*Bilans!$D$22+B48*Bilans!$E$22+B49*Bilans!$C$22+B50*Bilans!$B$22", "=C47*Bilans!$D$22+C48*Bilans!$E$22+C49*Bilans!$C$22+C50*Bilans!$B$22", "#,##0"),
    (53, "RAZEM DO WYWOZU [tony]", "=B47*Bilans!$D$23+B48*Bilans!$E$23+B49*Bilans!$C$23+B50*Bilans!$B$23", "=C47*Bilans!$D$23+C48*Bilans!$E$23+C49*Bilans!$C$23+C50*Bilans!$B$23", "#,##0"),
    (55, "Czułość: każde 10 cm głębokości wykopu [m³]", "=B26*0.1", "=C26*0.1", "#,##0"),
]
for r, opis, fb, fc, fmt in linie:
    w2.cell(r, 1, opis)
    for col, f in ((2, fb), (3, fc)):
        c = w2.cell(r, col, f)
        c.number_format = fmt
        c.border = RAMKA
        c.fill = ZIELONY
for rr in (28, 30, 42, 46, 51):
    w2.cell(rr, 1).font = B
w2["D46"] = "Dowóz = zapotrzebowanie minus to, co da się wbudować z wykopu"
w2["D41"] = "Nasyp liczony od poziomu po zdjęciu humusu i nasypu niekontrolowanego"
w2["D40"] = "Przestrzeń wokół i nad halami od dna wykopu do terenu projektowanego minus objętość konstrukcji"
for d in ("D40", "D41", "D46"):
    w2[d].alignment = Alignment(wrap_text=True)
w2["A57"] = "Wariant B (cały obszar w ściance wykopany do dna) jest mało prawdopodobny: wywóz i dowóz są wtedy bardzo duże. Potwierdź z projektantem zakres wykopu."
w2["A57"].font = Font(italic=True)

wb.save(os.path.join(OUT, "bilans_robot_ziemnych.xlsx"))
print("ok")

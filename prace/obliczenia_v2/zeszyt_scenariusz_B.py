"""
ZESZYT2 – wersja z ilościami zgodnymi z bilansem, scenariusz B (wykop w obrębie całych ścian).
Wzór: plik użytkownika „Zeszyt2 - do sprawdzenia.xlsx" (kosztorys „Roboty ziemne"; widoczne kolumny: A, C, D, T = wcześniejsza suma budynków, AD = nowa).
Co się zmienia: tylko kolumna AD (wiersze 4–11) oraz dopisane: nagłówki w wierszu 1, kolumna AE z opisem źródła i blok „PODSTAWA – BILANS" (wiersze 13–29).
Liczby z arkusza bilansu (wyniki/BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx, zakładka WYNIK, kolumna D = wariant B); kolumny budynków (ukryte) bez zmian.
Tylko biblioteka standardowa (edycja XML w pliku xlsx – zachowuje formatowanie wzoru).
Uruchomienie (z katalogu głównego repo): python prace/obliczenia_v2/zeszyt_scenariusz_B.py
"""
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "Zeszyt2 - do sprawdzenia.xlsx")
BILANS = os.path.join(REPO, "wyniki", "BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx")
OUT = os.path.join(REPO, "wyniki", "Zeszyt2 - scenariusz B wg bilansu.xlsx")
M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


# ------------------------------------------------------------------------------------------------ odczyt bilansu (wariant B = kolumna D)
def wynik_bilansu():
    z = zipfile.ZipFile(BILANS)
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    path = None
    for s in wb.find("{%s}sheets" % M):
        if s.attrib["name"] == "WYNIK":
            path = "xl/" + rels[s.attrib["{%s}id" % R]].lstrip("/").replace("xl/", "")
    cells = {}
    for c in ET.fromstring(z.read(path)).iter("{%s}c" % M):
        if c.attrib.get("t") == "inlineStr":
            val = "".join(x.text or "" for x in c.iter("{%s}t" % M))
        else:
            v = c.find("{%s}v" % M)
            if v is None:
                continue
            val = v.text
        cells[c.attrib["r"]] = val
    out = {}
    for r in range(5, 70):
        nr = cells.get("A%d" % r)
        if nr and re.match(r"^\d+(\.\d+)?a?$", nr) and cells.get("D%d" % r) not in (None, ""):
            try:
                out.setdefault(nr, float(cells["D%d" % r]))
            except ValueError:
                pass
    return out


# ------------------------------------------------------------------------------------------------ układ arkusza
def build():
    b = wynik_bilansu()
    need = ["1.1", "1.2", "2.1", "3.4", "5.4", "6.3", "6.4", "6.5", "6.6", "6.7"]
    for k in need:
        if k not in b:
            sys.exit("brak pozycji %s w arkuszu bilansu" % k)
    r3 = lambda x: round(x + 0.0, 3)
    # blok podstawy (wiersze 13–29): (wiersz, opis, kind, wartość lub formuła, źródło)
    blok = [
        (14, "Humus zdjęty z całej działki", "in", b["1.1"], "Bilans WYNIK 1.1 (wariant B)."),
        (15, "Humus na odkład", "in", b["1.2"], "Bilans WYNIK 1.2: 0,25 m × 6 443,06 m² × 1,10."),
        (16, "Humus do wywozu", "f", "ROUND(AD14-AD15,3)", "Bilans WYNIK 1.3 (zdjęty − na odkład)."),
        (17, "Nasyp niekontrolowany – do wywozu", "in", b["2.1"], "Bilans WYNIK 2.1."),
        (18, "Wykop gruntu rodzimego (cały na odkład)", "in", b["3.4"], "Bilans WYNIK 3.4, wariant B."),
        (19, "Ponowne wbudowanie gruntu z odkładu", "in", b["5.4"], "Bilans WYNIK 5.4, wariant B."),
        (20, "Grunt rodzimy do wywozu", "f", "ROUND(AD18-AD19,3)", "Bilans WYNIK 6.3 (wykop − ponowne wbudowanie)."),
        (21, "Fundamenty głębsze – do wywozu", "in", b["6.4"], "Bilans WYNIK 6.4 (pogrubienia, rdzenie, szyby wind, studzienki)."),
        (22, "Dowóz – grunt niewysadzinowy (strefa przemarzania)", "in", b["6.7"], "Bilans WYNIK 6.7."),
        (23, "Dowóz – grunt do zasypu", "in", b["6.6"], "Bilans WYNIK 6.6 (cały grunt rodzimy wraca do zasypu)."),
        (24, "RAZEM DO WYWOZU (humus + nasyp + grunt + fundamenty)", "f", "ROUND(AD16+AD17+AD20+AD21,3)", "Bilans WYNIK 6.5."),
        (25, "RAZEM DO WYWOZU wg arkusza bilansu (do kontroli)", "in", b["6.5"], "Bilans WYNIK 6.5, wariant B."),
        (26, "Kontrola (musi być 0,000)", "f", "ROUND(AD24-AD25,3)", "Różnica wiersza 24 i 25."),
        (28, "Poza wzorem: wykop gruntu na odkład i zasypanie go z odkładu", "f", "AD19", "W kosztorysie nie ma na to pozycji. Bilans WYNIK 5.4."),
        (29, "Wykop razem (grunt + nasyp + fundamenty) − (wywóz + odkład)", "f", "ROUND(AD18+AD17+AD21-(AD6+AD28),3)", "Kontrola (musi być 0,000): cały wykop = część wywożona + część na odkład."),
    ]
    glowne = {   # kolumna AD, wiersze 4–11: (formuła, źródło)
        4: ("AD16", "Bilans WYNIK 6.1: humus do wywozu (zdjęty 15 274,147 − na odkład 1 771,842), m³."),
        5: ("AD15", "Bilans WYNIK 1.2: humus na odkład, m³."),
        6: ("ROUND(AD17+AD20+AD21,3)", "Bilans WYNIK 6.2 + 6.3 + 6.4: nasyp + grunt rodzimy + fundamenty głębsze (bez humusu)."),
        7: ("ROUND(AD6+AD4,3)", "Bilans WYNIK 6.5: razem do wywozu = wykop z wywozem + humus z wywozem (jak w kolumnach budynków: wiersz 7 = wiersz 6 + humus)."),
        8: ("AD6", "Jak pozycja 2: wykop z wywozem (bez humusu)."),
        10: ("ROUND(AD22+AD23,3)", "Bilans WYNIK 6.8: dowóz razem (grunt do zasypu + grunt niewysadzinowy)."),
        11: ("AD10", "Jak pozycja 5: grunt z dowozu."),
    }
    # wartości (do <v>) – ta sama logika co formuły
    v = {}
    inputs = {r: val for r, _, k, val, _ in blok if k == "in"}
    for r, val in inputs.items():
        v[r] = val
    v[16] = r3(v[14] - v[15]); v[20] = r3(v[18] - v[19])
    v[4] = v[16]; v[5] = v[15]
    v[6] = r3(v[17] + v[20] + v[21]); v[7] = r3(v[6] + v[4]); v[8] = v[6]
    v[10] = r3(v[22] + v[23]); v[11] = v[10]
    v[24] = r3(v[16] + v[17] + v[20] + v[21]); v[26] = r3(v[24] - v[25])
    v[28] = v[19]; v[29] = r3(v[18] + v[17] + v[21] - (v[6] + v[28]))
    return blok, glowne, v


def cell_num(ref, s, formula, val):
    f = "<f>%s</f>" % escape(formula) if formula else ""
    return '<c r="%s" s="%d">%s<v>%s</v></c>' % (ref, s, f, repr(round(val, 3)))


def cell_txt(ref, s, text):
    assert not text.startswith("="), text
    return '<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, s, escape(text))


def main():
    blok, glowne, v = build()
    zin = zipfile.ZipFile(SRC)
    parts = {n: zin.read(n) for n in zin.namelist()}
    # --- style: format 0,000 + dwa nowe style (żółte pole wejściowe, pole z formułą)
    st = parts["xl/styles.xml"].decode("utf-8")
    assert "<numFmts" not in st
    st = st.replace("<fonts ", '<numFmts count="1"><numFmt numFmtId="164" formatCode="#,##0.000"/></numFmts><fonts ', 1)
    n = int(re.search(r'<cellXfs count="(\d+)"', st).group(1))
    assert n == 29
    nowe = ('<xf numFmtId="164" fontId="1" fillId="4" borderId="3" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1"/>'      # 29 żółte pole z bilansu
            '<xf numFmtId="164" fontId="0" fillId="0" borderId="3" xfId="0" applyNumberFormat="1" applyBorder="1"/>')                                  # 30 formuła
    st = st.replace('<cellXfs count="29">', '<cellXfs count="31">', 1).replace("</cellXfs>", nowe + "</cellXfs>", 1)
    parts["xl/styles.xml"] = st.encode("utf-8")
    S_IN, S_F = 29, 30
    # --- arkusz
    sh = parts["xl/worksheets/sheet1.xml"].decode("utf-8")
    sh = sh.replace('<dimension ref="A2:AD11"/>', '<dimension ref="A1:AE29"/>').replace('spans="1:30"', 'spans="1:31"')
    sh = sh.replace('<col min="30" max="30" width="32.5546875" customWidth="1"/>',
                    '<col min="30" max="30" width="32.5546875" customWidth="1"/><col min="31" max="31" width="85" customWidth="1"/>')
    # wiersz 1 – nagłówki
    row1 = ('<row r="1" spans="1:31" ht="62" customHeight="1">' + cell_txt("T1", 2, "wcześniej (suma budynków)") +
            cell_txt("AD1", 2, "BILANS – scenariusz B (wykop w obrębie całych ścian), m3") + cell_txt("AE1", 2, "Skąd liczba (arkusz bilansu, zakładka WYNIK)") + "</row>")
    sh = sh.replace("<sheetData>", "<sheetData>" + row1, 1)
    # kolumna AD i notki AE w wierszach 4–11
    for r, (f, nota) in glowne.items():
        m = re.search(r'<c r="AD%d"[^>]*?(?:/>|>.*?</c>)' % r, sh, re.S)
        assert m, r
        sh = sh.replace(m.group(0), cell_num("AD%d" % r, S_F, f, v[r]), 1)
        sh = re.sub(r'(<row r="%d" [^>]*>.*?)(</row>)' % r, lambda mm: mm.group(1) + cell_txt("AE%d" % r, 5, nota) + mm.group(2), sh, count=1, flags=re.S)
    # blok podstawy
    rows = ['<row r="13" spans="1:31">' + '<c r="A13" s="9"/>' + cell_txt("C13", 10, "PODSTAWA – BILANS ROBÓT ZIEMNYCH, scenariusz B (m3, stan rodzimy)") +
            '<c r="D13" s="11"/><c r="T13" s="13"/><c r="AD13" s="15"/>' + cell_txt("AE13", 10, "Żółte pola – liczby z arkusza bilansu; pozostałe – formuły.") + "</row>"]
    for r, opis, kind, val, nota in blok:
        rows.append('<row r="%d" spans="1:31">' % r + cell_txt("C%d" % r, 5, opis) + cell_txt("D%d" % r, 23, "m3") +
                    (cell_num("AD%d" % r, S_IN, None, val) if kind == "in" else cell_num("AD%d" % r, S_F, val, v[r])) + cell_txt("AE%d" % r, 5, nota) + "</row>")
    sh = sh.replace("</sheetData>", "".join(rows) + "</sheetData>", 1)
    parts["xl/worksheets/sheet1.xml"] = sh.encode("utf-8")
    # --- skoroszyt: przeliczenie przy otwarciu, bez calcChain (Excel zbuduje go sam)
    wbx = parts["xl/workbook.xml"].decode("utf-8").replace('<calcPr calcId="191029"/>', '<calcPr calcId="191029" fullCalcOnLoad="1"/>')
    assert "fullCalcOnLoad" in wbx
    parts["xl/workbook.xml"] = wbx.encode("utf-8")
    del parts["xl/calcChain.xml"]
    ct = re.sub(r'<Override PartName="/xl/calcChain.xml"[^>]*/>', "", parts["[Content_Types].xml"].decode("utf-8"))
    parts["[Content_Types].xml"] = ct.encode("utf-8")
    rl = re.sub(r'<Relationship Id="rId5"[^>]*calcChain[^>]*/>', "", parts["xl/_rels/workbook.xml.rels"].decode("utf-8"))
    parts["xl/_rels/workbook.xml.rels"] = rl.encode("utf-8")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
        zo.writestr("[Content_Types].xml", parts.pop("[Content_Types].xml"))
        for n_, data in parts.items():
            zo.writestr(n_, data)
    print("zapisano", OUT, "| wiersze AD:", {r: v[r] for r in (4, 5, 6, 7, 8, 10, 11)})


if __name__ == "__main__":
    main()

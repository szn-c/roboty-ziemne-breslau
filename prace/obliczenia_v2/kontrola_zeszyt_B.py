"""
NIEZALEŻNA KONTROLA pliku „Zeszyt2 - scenariusz B wg bilansu.xlsx" (tylko biblioteka standardowa):
  1. struktura pakietu xlsx i poprawność XML wszystkich części, kolejność wierszy i komórek;
  2. przeliczenie WSZYSTKICH formuł własnym małym interpreterem (SUM, ROUND, + − × ÷) i porównanie z zapisanymi wartościami;
  3. porównanie kolumny AD z arkuszem bilansu (wariant B, zakładka WYNIK) – pozycja po pozycji;
  4. kolumny wcześniejsze (budynki, suma T) – bez zmian względem wzoru;
  5. brak tekstów zaczynających się od „=".
Uruchomienie: python prace/obliczenia_v2/kontrola_zeszyt_B.py
"""
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zeszyt_scenariusz_B as Z   # noqa: E402

M = Z.M


def wczytaj(path):
    z = zipfile.ZipFile(path)
    for n in z.namelist():
        if n.endswith(".xml") or n.endswith(".rels"):
            ET.fromstring(z.read(n))                       # poprawność XML
    root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        ss = ["".join(t.text or "" for t in si.iter("{%s}t" % M)) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("{%s}si" % M)]
    cells, formuly, kolej_ok = {}, {}, True
    ostatni_wiersz = 0
    for row in root.iter("{%s}row" % M):
        r = int(row.attrib["r"])
        kolej_ok &= r > ostatni_wiersz
        ostatni_wiersz = r
        ostatnia = 0
        for c in row.iter("{%s}c" % M):
            ref = c.attrib["r"]
            col = 0
            for ch in re.match(r"[A-Z]+", ref).group(0):
                col = col * 26 + ord(ch) - 64
            kolej_ok &= col > ostatnia and int(ref[len(re.match(r"[A-Z]+", ref).group(0)):]) == r
            ostatnia = col
            t = c.attrib.get("t")
            f = c.find("{%s}f" % M)
            v = c.find("{%s}v" % M)
            if t == "inlineStr":
                cells[ref] = "".join(x.text or "" for x in c.iter("{%s}t" % M))
            elif v is not None:
                cells[ref] = ss[int(v.text)] if t == "s" else float(v.text)
            if f is not None:
                formuly[ref] = f.text
    return z, cells, formuly, kolej_ok


def kol_do_nr(s):
    n = 0
    for ch in s:
        n = n * 26 + ord(ch) - 64
    return n


def nr_do_kol(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def licz(ref, cells, formuly, cache):
    if ref in cache:
        return cache[ref]
    if ref not in formuly:
        v = cells.get(ref, 0.0)
        cache[ref] = v if isinstance(v, float) else 0.0
        return cache[ref]
    expr = formuly[ref]

    def suma(m):
        a, b = m.group(1), m.group(2)
        ca, ra = re.match(r"([A-Z]+)(\d+)", a).groups()
        cb, rb = re.match(r"([A-Z]+)(\d+)", b).groups()
        tot = 0.0
        for c in range(kol_do_nr(ca), kol_do_nr(cb) + 1):
            for r in range(int(ra), int(rb) + 1):
                tot += licz("%s%d" % (nr_do_kol(c), r), cells, formuly, cache)
        return repr(tot)
    expr = re.sub(r"SUM\(([A-Z]+\d+):([A-Z]+\d+)\)", suma, expr)
    expr = re.sub(r"\b([A-Z]{1,2}\d+)\b", lambda m: repr(licz(m.group(1), cells, formuly, cache)), expr)
    val = float(eval(expr, {"__builtins__": {}}, {"ROUND": lambda x, n: round(x + 0.0, int(n))}))
    cache[ref] = val
    return val


def main():
    z, cells, formuly, kolej_ok = wczytaj(Z.OUT)
    _, cells0, formuly0, _ = wczytaj(Z.SRC)
    wyn = {"struktura_i_xml": True, "kolejnosc_wierszy_i_komorek": kolej_ok}
    print("pakiet xlsx: części %d, XML poprawny; kolejność wierszy i komórek %s" % (len(z.namelist()), "OK" if kolej_ok else "BŁĄD"))
    cache = {}
    bledy = []
    for ref, f in formuly.items():
        wart = licz(ref, cells, formuly, cache)
        zap = cells.get(ref)
        if not isinstance(zap, float) or abs(wart - zap) > 5e-7:
            bledy.append((ref, f, wart, zap))
    print("formuł w pliku: %d; przeliczone niezależnie; różnice z wartościami zapisanymi: %d" % (len(formuly), len(bledy)))
    for b in bledy:
        print("   RÓŻNICA", b)
    # AD vs bilans
    b = Z.wynik_bilansu()
    oczek = {4: ("6.1→1.3", None), 5: ("1.2", b["1.2"]), 6: ("6.2+6.3+6.4", round(b["2.1"] + b["6.3"] + b["6.4"], 3)), 7: ("6.5", b["6.5"]),
             8: ("6.2+6.3+6.4", round(b["2.1"] + b["6.3"] + b["6.4"], 3)), 10: ("6.8", round(b["6.6"] + b["6.7"], 3)), 11: ("6.8", round(b["6.6"] + b["6.7"], 3))}
    oczek[4] = ("1.1−1.2", round(b["1.1"] - b["1.2"], 3))
    print("\nPorównanie z arkuszem bilansu (wariant B):")
    ok = True
    for r, (zr, ov) in oczek.items():
        w = cells["AD%d" % r]
        zg = abs(w - ov) < 0.0006
        ok &= zg
        print("  AD%-2d = %12.3f | bilans %-12s %12.3f | różnica %+.3f %s" % (r, w, zr, ov, w - ov, "OK" if zg else "BŁĄD"))
    razem = cells["AD7"]
    print("  AD7 (wywóz razem) − bilans 6.5 = %+.3f; kontrola w pliku (AD26) = %.3f; (AD29) = %.3f" % (razem - b["6.5"], cells["AD26"], cells["AD29"]))
    ok &= abs(razem - b["6.5"]) < 0.0006 and cells["AD26"] == 0 and cells["AD29"] == 0
    # wzór bez zmian
    zmienione = [ref for ref in cells0 if not re.match(r"AD(4|5|6|7|8|10|11)$", ref) and cells.get(ref) != cells0[ref]]
    print("\nkomórki wzoru poza AD4–AD11 zmienione: %d %s" % (len(zmienione), zmienione[:5]))
    zm_f = [ref for ref in formuly0 if ref in formuly and formuly0[ref] != formuly[ref] and not ref.startswith("AD")]
    print("formuły wzoru (T4, T6, T7, T10) bez zmian:", "TAK" if not zm_f else "NIE %s" % zm_f)
    teksty_eq = [ref for ref, t in cells.items() if isinstance(t, str) and t.startswith("=")]
    print("teksty zaczynające się od „=”:", len(teksty_eq))
    wynik = ok and not bledy and kolej_ok and not zmienione and not zm_f and not teksty_eq
    print("\nWYNIK KONTROLI:", "OK" if wynik else "BŁĄD")
    sys.exit(0 if wynik else 1)


if __name__ == "__main__":
    main()

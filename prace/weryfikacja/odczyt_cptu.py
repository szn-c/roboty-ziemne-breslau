"""
Profile sondowań CPTU 10, 12, 18, 21, 24 (działka 1/90) z ekstraktu tekstu zał. 7 DGI (tabela "Strop / Spąg / Symbol / … / Nr warstwy").
Wynik: cptu_odczyt.json  {nr: [(strop, spąg, symbol, warstwa), ...]}
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EKS = os.path.join(REPO, "prace", "ekstrakty_tekstu", "7 Charakterystyki i wykresy CPTU.txt")
NR = (10, 12, 18, 21, 24)
WARSTWA = re.compile(r"^(Ia|Ib|IIa|IIb|IIc|IIIa|IIIb|IVa|IVb|IVc|IVd|V)$")
LICZBA = re.compile(r"^-?\d+[,.]\d+$")


def main():
    tekst = open(EKS, encoding="utf-8").read()
    strony = re.split(r"===== STRONA \d+ =====", tekst)
    wynik = {}
    for s in strony:
        m = re.search(r"Załącznik nr 7\.1\.\d+\s*\n[\s\n]*CPTU-(\d+)", s)
        if not m or int(m.group(1)) not in NR:
            continue
        nr = int(m.group(1))
        tok = [t.strip() for t in s.split("\n")]
        tok = [t for t in tok if t != ""]
        rows = []
        i = 0
        while i < len(tok) - 2:
            if LICZBA.match(tok[i]) and LICZBA.match(tok[i + 1]) and not LICZBA.match(tok[i + 2]) and not WARSTWA.match(tok[i + 2]):
                a, b = float(tok[i].replace(",", ".")), float(tok[i + 1].replace(",", "."))
                if b > a:
                    sym = tok[i + 2]
                    j = i + 3
                    war = ""
                    while j < len(tok) and j < i + 20:
                        if WARSTWA.match(tok[j]):
                            war = tok[j]; break
                        if LICZBA.match(tok[j]) and j + 2 < len(tok) and LICZBA.match(tok[j + 1]) and not LICZBA.match(tok[j + 2]) \
                                and float(tok[j].replace(",", ".")) == b:
                            break
                        j += 1
                    rows.append((a, b, sym, war))
                    i = j if war else i + 3
                    continue
            i += 1
        wynik[nr] = rows
    for nr in NR:
        print("CPTU-%d: %s" % (nr, "; ".join("%.2f–%.2f %s %s" % r for r in wynik.get(nr, []))))
    json.dump(wynik, open(os.path.join(HERE, "cptu_odczyt.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

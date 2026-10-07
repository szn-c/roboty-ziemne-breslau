"""Wyciaga tekst z dokumentow (PDF, DOC, DOCX) do plikow .txt w prace/ekstrakty_tekstu/.

Uzycie:  python wyciagnij_tekst_dokumentow.py            (przetwarza caly folder dokumentacja/)
         python wyciagnij_tekst_dokumentow.py plik.pdf   (jeden plik)
PDF: PyMuPDF (tekst strona po stronie; rysunki rastrowe nie maja tekstu).
DOC: odczyt tabeli fragmentow Worda (olefile), bez zewnetrznych programow.
DOCX: odczyt XML (zipfile).
Zaleznosci: pymupdf, olefile."""
import os
import re
import struct
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WYJ = REPO / "prace" / "ekstrakty_tekstu"


def z_pdf(sciezka):
    import pymupdf
    d = pymupdf.open(str(sciezka))
    return "".join(f"\n===== STRONA {i + 1} =====\n" + pg.get_text("text") for i, pg in enumerate(d))


def z_doc(sciezka):
    import olefile
    ole = olefile.OleFileIO(str(sciezka))
    wd = ole.openstream("WordDocument").read()
    flags = struct.unpack_from("<H", wd, 0x0A)[0]
    t = ole.openstream("1Table" if flags & 0x0200 else "0Table").read()
    fc_clx, lcb_clx = struct.unpack_from("<II", wd, 0x01A2)
    clx = t[fc_clx:fc_clx + lcb_clx]
    i = 0
    while clx[i] == 1:
        i += 3 + struct.unpack_from("<H", clx, i + 1)[0]
    lcb = struct.unpack_from("<I", clx, i + 1)[0]
    plc = clx[i + 5:i + 5 + lcb]
    n = (lcb - 4) // 12
    cps = struct.unpack_from("<%dI" % (n + 1), plc, 0)
    out = []
    for k in range(n):
        pcd = plc[(n + 1) * 4 + k * 8:(n + 1) * 4 + k * 8 + 8]
        fc = struct.unpack_from("<I", pcd, 2)[0]
        comp = bool(fc & 0x40000000)
        fc &= 0x3FFFFFFF
        cnt = cps[k + 1] - cps[k]
        if comp:
            out.append(wd[fc // 2:fc // 2 + cnt].decode("cp1250", errors="replace"))
        else:
            out.append(wd[fc:fc + 2 * cnt].decode("utf-16-le", errors="replace"))
    txt = "".join(out).replace("\r", "\n").replace("\x07", "\t").replace("\x0b", "\n").replace("\x0c", "\n")
    return re.sub(r"[\x00-\x08\x0e-\x1f]", "", txt)


def z_docx(sciezka):
    with zipfile.ZipFile(sciezka) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"</w:tc>", "\t", xml)
    return re.sub(r"<[^>]+>", "", xml)


def przetworz(sciezka):
    sciezka = Path(sciezka)
    rozsz = sciezka.suffix.lower()
    f = {".pdf": z_pdf, ".doc": z_doc, ".docx": z_docx}.get(rozsz)
    if f is None:
        return None
    txt = f(sciezka)
    WYJ.mkdir(parents=True, exist_ok=True)
    out = WYJ / (sciezka.stem + ".txt")
    out.write_text(txt, encoding="utf-8")
    return out, len(txt.strip())


if __name__ == "__main__":
    pliki = [Path(a) for a in sys.argv[1:]] or sorted((REPO / "dokumentacja").rglob("*"))
    for p in pliki:
        if p.is_file():
            r = przetworz(p)
            if r:
                print("%-80s -> %s (%d znakow)" % (str(p.relative_to(REPO)) if REPO in p.parents else str(p), r[0].name, r[1]))

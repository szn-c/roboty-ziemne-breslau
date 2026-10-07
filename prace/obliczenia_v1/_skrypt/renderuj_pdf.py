"""BEZPIECZNE renderowanie stron PDF do PNG - gwarantuje, ze obraz NIE przekroczy limitu.

Dlaczego: gdy w jednej rozmowie jest wiecej niz 20 obrazow, kazdy obraz (takze stary, z historii) musi miec
<= 2000 px na kazdym boku. Jeden wiekszy obraz blokuje cala sesje na stale (blad: "image dimensions exceed max
allowed size for many-image requests: 2000 pixels"). Duze rysunki w tym repo maja strony rzedu 1700-4300 pt
(1 pt = 1 px przy zoomie 1), wiec zwykle renderowanie "zoom 2" od razu przekracza limit.

Uzycie:
  python renderuj_pdf.py plik.pdf                                   # cala strona 1, dluzszy bok = 1500 px
  python renderuj_pdf.py plik.pdf --strona 3 --max 1200
  python renderuj_pdf.py plik.pdf --wycinek 1000 500 1800 1100      # wycinek w punktach strony (pt), powiekszony do --max
  python renderuj_pdf.py plik.pdf --kafelki 3x2                     # dzieli strone na 3 kolumny x 2 wiersze (osobne pliki)
  python renderuj_pdf.py --sprawdz obraz.png                        # sprawdza rozmiar DOWOLNEGO obrazu przed wczytaniem
Domyslne wyjscie: katalog _obrazy/ obok pliku skryptu (jest w .gitignore).
Zasada: NIE wczytuj obrazow > 1500 px i nie wiecej niz ok. 15 obrazow w jednej sesji. Najpierw czytaj tekst."""
import argparse
import os
import sys
from pathlib import Path

LIMIT_TWARDY = 2000       # px - powyzej tego sesja sie blokuje
DOMYSLNY_MAX = 1500       # px - bezpieczny zapas
MAX_ZOOM = 8.0            # nie powiekszaj ponad 8x (i tak nie ma wiecej szczegolow)
WYJ = Path(__file__).resolve().parent / "_obrazy"


def sprawdz(sciezka):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    w, h = Image.open(sciezka).size
    ok = max(w, h) <= DOMYSLNY_MAX
    print("%s: %d x %d px -> %s" % (sciezka, w, h, "OK" if ok else ("ZA DUZY (limit twardy %d, zalecane <= %d) - NIE WCZYTYWAC" % (LIMIT_TWARDY, DOMYSLNY_MAX))))
    return ok


def renderuj(pdf, strona=1, wycinek=None, max_px=DOMYSLNY_MAX, wyjscie=None):
    import pymupdf
    if max_px > LIMIT_TWARDY - 100:
        sys.exit("--max nie moze przekraczac %d px" % (LIMIT_TWARDY - 100))
    d = pymupdf.open(str(pdf))
    pg = d[strona - 1]
    clip = pymupdf.Rect(*wycinek) if wycinek else pg.rect
    zoom = min(max_px / max(clip.width, clip.height), MAX_ZOOM)
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    assert max(pix.width, pix.height) <= LIMIT_TWARDY, "blad: obraz za duzy"
    if wyjscie is None:
        WYJ.mkdir(exist_ok=True)
        wyjscie = WYJ / ("%s_s%d%s.png" % (Path(pdf).stem.replace(" ", "_")[:40], strona, "_w" if wycinek else ""))
    pix.save(str(wyjscie))
    print("%s: %d x %d px (zoom %.3f; wycinek strony [pt] %.0f %.0f %.0f %.0f)" % (wyjscie, pix.width, pix.height, zoom, clip.x0, clip.y0, clip.x1, clip.y1))
    return wyjscie


def kafelki(pdf, strona, n, m, max_px):
    import pymupdf
    pg = pymupdf.open(str(pdf))[strona - 1]
    r = pg.rect
    dx, dy = r.width / n, r.height / m
    out = []
    for j in range(m):
        for i in range(n):
            wyc = (r.x0 + i * dx, r.y0 + j * dy, r.x0 + (i + 1) * dx, r.y0 + (j + 1) * dy)
            wy = WYJ / ("%s_s%d_r%dk%d.png" % (Path(pdf).stem.replace(" ", "_")[:40], strona, j + 1, i + 1))
            WYJ.mkdir(exist_ok=True)
            out.append(renderuj(pdf, strona, wyc, max_px, wy))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--strona", type=int, default=1)
    ap.add_argument("--wycinek", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--max", type=int, default=DOMYSLNY_MAX, dest="max_px")
    ap.add_argument("--kafelki", help="np. 3x2 (kolumny x wiersze)")
    ap.add_argument("--wyjscie")
    ap.add_argument("--sprawdz", help="sprawdz rozmiar istniejacego obrazu")
    a = ap.parse_args()
    if a.sprawdz:
        sys.exit(0 if sprawdz(a.sprawdz) else 1)
    if not a.pdf:
        ap.error("podaj plik PDF albo --sprawdz obraz")
    if a.kafelki:
        n, m = [int(x) for x in a.kafelki.lower().split("x")]
        kafelki(a.pdf, a.strona, n, m, a.max_px)
    else:
        renderuj(a.pdf, a.strona, a.wycinek, a.max_px, a.wyjscie)

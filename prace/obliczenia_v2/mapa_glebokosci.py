"""
MAPY 2D dla wariantów A i B (układ PL-2000/6 – nakładają się na rysunki użytkownika):
  1. głębokość wykopu = teren po zdjęciu humusu i nasypu − powierzchnia po wykopie (klasy co 0,5 m),
  2. grubość wypełnienia = rzędna projektowa (PZT) − powierzchnia po wykopie, poza halami i zadaszonymi dojazdami
     (obejmuje warstwy konstrukcyjne: humus, konstrukcję nawierzchni, substrat, płytę rampy – to nie jest sam grunt rodzimy).
Wyniki: wyniki/MAPA_GLEBOKOSCI_dz190.dxf (warstwy MAPA_*), wyniki/MAPA_GLEBOKOSCI_dz190.png, prace/obliczenia_v2/mapa_glebokosci_kontrola.json
Uruchomienie: python mapa_glebokosci.py
"""
import json
import os

import ezdxf
import matplotlib
import numpy as np
from shapely import wkt
from shapely.geometry import Polygon
from shapely.ops import unary_union

import dane as D
import model3d as M
import silnik as S

matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from matplotlib.patches import PathPatch   # noqa: E402
from matplotlib.path import Path   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WY_DXF = os.path.join(REPO, "wyniki", "MAPA_GLEBOKOSCI_dz190.dxf")
WY_PNG = os.path.join(REPO, "wyniki", "MAPA_GLEBOKOSCI_dz190.png")
WY_JSON = os.path.join(HERE, "mapa_glebokosci_kontrola.json")
KRAWEDZIE = [0.02, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 6.0]       # m
KROK = 2                                                                # co 2. komórka rastra = 0,5 m


def etykiety_klas():
    return ["%.1f–%.1f m" % (a, b) if b < 6 else "ponad %.1f m" % a for a, b in zip(KRAWEDZIE[:-1], KRAWEDZIE[1:])]


def kolory(cmap, n):
    cm = plt.get_cmap(cmap)
    return [tuple(int(255 * v) for v in cm(0.15 + 0.8 * i / (n - 1))[:3]) for i in range(n)]


def wielokaty_klas(xs, ys, Z2d, maska2d):
    """Wielokąty klas z rastra (contourf) – dziury obsłużone przez XOR pierścieni."""
    Zm = np.where(maska2d, Z2d, np.nan)[::KROK, ::KROK]
    fig = plt.figure()
    cs = plt.contourf(xs[::KROK], ys[::KROK], Zm, levels=KRAWEDZIE, extend="neither")
    out = []
    for i in range(len(KRAWEDZIE) - 1):
        g = Polygon()
        for seg in cs.allsegs[i]:
            if len(seg) >= 4:
                g = g.symmetric_difference(Polygon(seg).buffer(0))
        out.append(g)
    plt.close(fig)
    return out


def main():
    geo = json.load(open(os.path.join(D.DANE, "geometria.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(D.DANE, "strefy.json"), encoding="utf-8"))
    w, gm = S.licz(zapisz_geometrie=True)
    sg = gm["_siatka"]
    xs, ys, shape, cell = sg["xs"], sg["ys"], sg["shape"], sg["cell"]
    A = cell * cell
    inG = sg["inG"].reshape(shape)
    mH = sg["mH"].reshape(shape)
    zs, zp = sg["zs"].reshape(shape), sg["zp"].reshape(shape)
    Z = {}
    for k in ("A", "B"):
        ze = sg[k]["ze"].reshape(shape)
        Z[k] = np.where(np.isfinite(ze), np.minimum(zs, ze), zs)
    G = Polygon(geo["granica"])
    HALE = [Polygon(v) for v in geo["hale"].values()]
    ZAD = wkt.loads(st["zadaszone_poza_halami"])
    kontrola = {"klasy": etykiety_klas(), "wykop": {}, "wypelnienie": {}}
    cut = {k: np.where(inG, np.clip(zs - Z[k], 0, None), 0.0) for k in Z}
    fill = {k: np.where(inG & ~mH, np.clip(zp - Z[k], 0, None), 0.0) for k in Z}
    nkl = len(KRAWEDZIE) - 1
    kol_cut, kol_fill = kolory("YlOrBr", nkl), kolory("Greens", nkl)
    poly = {}
    for k in Z:
        for nazwa, pole, klas_kol in (("wykop", cut[k], kol_cut), ("wypelnienie", fill[k], kol_fill)):
            masked = inG & (pole > KRAWEDZIE[0])
            poly[(k, nazwa)] = wielokaty_klas(xs, ys, pole, masked)
            tab = []
            for i in range(nkl):
                m = inG & (pole >= KRAWEDZIE[i]) & (pole < KRAWEDZIE[i + 1]) if i < nkl - 1 else inG & (pole >= KRAWEDZIE[i])
                if i == 0:
                    m = inG & (pole >= KRAWEDZIE[0]) & (pole < KRAWEDZIE[1])
                tab.append({"klasa": etykiety_klas()[i], "pole_m2": round(float(m.sum() * A), 2), "objetosc_m3": round(float(pole[m].sum() * A), 3)})
            kontrola[nazwa][k] = {"razem_pole_m2": round(float(sum(t["pole_m2"] for t in tab)), 2), "razem_objetosc_m3": round(float(sum(t["objetosc_m3"] for t in tab)), 3),
                                  "max_m": round(float(pole[inG].max()), 2), "klasy": tab}
            print("%s %s: pole %.2f m2, objętość %.3f m3, maks. %.2f m" % (nazwa, k, kontrola[nazwa][k]["razem_pole_m2"], kontrola[nazwa][k]["razem_objetosc_m3"], kontrola[nazwa][k]["max_m"]))
    # --- DXF
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 6
    msp = doc.modelspace()
    for nm, kol in (("MAPA_KONTEKST_GRANICA", 6), ("MAPA_KONTEKST_HALE", 1), ("MAPA_KONTEKST_ZADASZONE", 30), ("MAPA_KONTEKST_SCIANKA", 2), ("MAPA_KONTEKST_RAMPY", 2),
                    ("MAPA_OPISY", 7), ("MAPA_WYMIANA_PRZEMARZANIE", 40)):
        doc.layers.add(nm, color=kol)
    for k in Z:
        for nazwa, klas_kol in (("WYKOP", kol_cut), ("WYPELNIENIE", kol_fill)):
            for i in range(nkl):
                doc.layers.add("MAPA_%s_%s_%02d" % (k, nazwa, i + 1), color=7)
            doc.layers.add("MAPA_%s_%s_IZOLINIE" % (k, nazwa), color=8)
    for k in Z:
        for nazwa, klas_kol, klucz in (("WYKOP", kol_cut, "wykop"), ("WYPELNIENIE", kol_fill, "wypelnienie")):
            for i, g in enumerate(poly[(k, klucz)]):
                lay = "MAPA_%s_%s_%02d" % (k, nazwa, i + 1)
                for q in ([g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))):
                    if q.geom_type != "Polygon" or q.area < 0.5:
                        continue
                    q = q.simplify(0.05)
                    h = msp.add_hatch(dxfattribs={"layer": lay, "true_color": ezdxf.colors.rgb2int(klas_kol[i])})
                    h.paths.add_polyline_path(list(q.exterior.coords)[:-1], is_closed=True)
                    for ring in q.interiors:
                        h.paths.add_polyline_path(list(ring.coords)[:-1], is_closed=True)
                    msp.add_lwpolyline(list(q.exterior.coords)[:-1], close=True, dxfattribs={"layer": "MAPA_%s_%s_IZOLINIE" % (k, nazwa)})
        rys = gm[k + "_wymiana"].intersection(G)
        for q in ([rys] if rys.geom_type == "Polygon" else list(getattr(rys, "geoms", []))):
            if q.geom_type == "Polygon" and q.area > 0.5:
                msp.add_lwpolyline(list(q.exterior.coords)[:-1], close=True, dxfattribs={"layer": "MAPA_WYMIANA_PRZEMARZANIE"})
    msp.add_lwpolyline(list(G.exterior.coords)[:-1], close=True, dxfattribs={"layer": "MAPA_KONTEKST_GRANICA"})
    for h in HALE:
        msp.add_lwpolyline(list(h.exterior.coords)[:-1], close=True, dxfattribs={"layer": "MAPA_KONTEKST_HALE"})
    for q in (list(ZAD.geoms) if hasattr(ZAD, "geoms") else [ZAD]):
        if q.area > 1:
            msp.add_lwpolyline(list(q.exterior.coords)[:-1], close=True, dxfattribs={"layer": "MAPA_KONTEKST_ZADASZONE"})
    msp.add_lwpolyline(geo["scianka_otwarta"], dxfattribs={"layer": "MAPA_KONTEKST_SCIANKA"})
    for r in st["rampy"]:
        for q in ([wkt.loads(r["obrys"])] if wkt.loads(r["obrys"]).geom_type == "Polygon" else list(wkt.loads(r["obrys"]).geoms)):
            msp.add_lwpolyline(list(q.exterior.coords)[:-1], close=True, dxfattribs={"layer": "MAPA_KONTEKST_RAMPY"})
    x0, y0 = G.bounds[2] + 15, G.bounds[3]
    msp.add_text("MAPY 2D – głębokość wykopu (WYKOP) i grubość wypełnienia do rzędnej projektowej (WYPELNIENIE); warstwy MAPA_A_* i MAPA_B_*", height=1.6,
                 dxfattribs={"layer": "MAPA_OPISY", "insert": (x0, y0)})
    msp.add_text("Wykop: teren po zdjęciu humusu i nasypu − powierzchnia po wykopie. Wypełnienie: rzędna projektowa PZT − powierzchnia po wykopie, bez hal i zadaszonych dojazdów "
                 "(razem z warstwami konstrukcyjnymi, nie tylko grunt rodzimy).", height=1.0, dxfattribs={"layer": "MAPA_OPISY", "insert": (x0, y0 - 3)})
    yy = y0 - 7
    for nazwa, tytul, klas_kol in (("wykop", "WYKOP", kol_cut), ("wypelnienie", "WYPEŁNIENIE", kol_fill)):
        msp.add_text("%s – klasa [pole A m², B m²; objętość A m³, B m³]" % tytul, height=1.1, dxfattribs={"layer": "MAPA_OPISY", "insert": (x0, yy)})
        yy -= 2.6
        for i in range(nkl):
            ta, tb = kontrola[nazwa]["A"]["klasy"][i], kontrola[nazwa]["B"]["klasy"][i]
            lay = "MAPA_A_%s_%02d" % ("WYKOP" if nazwa == "wykop" else "WYPELNIENIE", i + 1)
            h = msp.add_hatch(dxfattribs={"layer": "MAPA_OPISY", "true_color": ezdxf.colors.rgb2int(klas_kol[i])})
            h.paths.add_polyline_path([(x0, yy - 0.2), (x0 + 3, yy - 0.2), (x0 + 3, yy + 1.6), (x0, yy + 1.6)], is_closed=True)
            msp.add_text("%s   [%.0f, %.0f m²;  %.0f, %.0f m³]" % (ta["klasa"], ta["pole_m2"], tb["pole_m2"], ta["objetosc_m3"], tb["objetosc_m3"]), height=0.9,
                         dxfattribs={"layer": "MAPA_OPISY", "insert": (x0 + 4, yy)})
            yy -= 2.4
        yy -= 3
    doc.saveas(WY_DXF)
    print("zapisano", WY_DXF, "%.1f MB" % (os.path.getsize(WY_DXF) / 1e6))
    # --- PNG
    fig, axs = plt.subplots(2, 2, figsize=(14.2, 13.8))
    minx, miny, maxx, maxy = G.bounds
    for r, (nazwa, klucz, klas_kol, tyt) in enumerate((("wykop", "wykop", kol_cut, "Głębokość wykopu"), ("wypelnienie", "wypelnienie", kol_fill, "Grubość wypełnienia do rzędnej projektowej"))):
        for c, k in enumerate(("A", "B")):
            ax = axs[r, c]
            ax.fill(*G.exterior.xy, color="0.96", lw=0)
            for i, g in enumerate(poly[(k, klucz)]):
                for q in ([g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))):
                    if q.geom_type != "Polygon" or q.area < 0.5:
                        continue
                    sciezki = [Path(np.array(q.exterior.coords))] + [Path(np.array(r.coords)) for r in q.interiors]
                    ax.add_patch(PathPatch(Path.make_compound_path(*sciezki), facecolor=tuple(v / 255 for v in klas_kol[i]), lw=0))
            ax.plot(*G.exterior.xy, color="purple", lw=0.8)
            for h in HALE:
                ax.plot(*h.exterior.xy, color="red", lw=0.9)
            ax.plot(*zip(*geo["scianka_otwarta"]), color="goldenrod", lw=1.6)
            rys = gm[k + "_wymiana"].intersection(G)
            for q in ([rys] if rys.geom_type == "Polygon" else list(getattr(rys, "geoms", []))):
                if q.geom_type == "Polygon" and q.area > 0.5:
                    ax.plot(*q.exterior.xy, color="black", lw=0.5)
            ax.set_aspect("equal"); ax.set_xlim(minx - 3, maxx + 3); ax.set_ylim(miny - 3, maxy + 3)
            ax.set_title("%s – wariant %s   (razem %.0f m³, maks. %.1f m)" % (tyt, k, kontrola[nazwa][k]["razem_objetosc_m3"], kontrola[nazwa][k]["max_m"]), fontsize=10)
            ax.tick_params(labelsize=7)
            ax.ticklabel_format(useOffset=False, style="plain")
    hand_c = [plt.Rectangle((0, 0), 1, 1, color=tuple(v / 255 for v in c)) for c in kol_cut]
    hand_f = [plt.Rectangle((0, 0), 1, 1, color=tuple(v / 255 for v in c)) for c in kol_fill]
    fig.legend(hand_c, etykiety_klas(), loc="lower left", ncol=5, fontsize=7, title="wykop", title_fontsize=7, bbox_to_anchor=(0.03, 0.0))
    fig.legend(hand_f, etykiety_klas(), loc="lower right", ncol=5, fontsize=7, title="wypełnienie (bez hal)", title_fontsize=7, bbox_to_anchor=(0.97, 0.0))
    fig.suptitle("czerwone – hale; złota – ścianka; fioletowa – granica działki; czarne kontury – wymiana gruntu w strefie przemarzania (poza wykopem)", fontsize=8, y=0.995)
    fig.tight_layout(rect=(0, 0.045, 1, 0.985))
    fig.savefig(WY_PNG, dpi=100)
    print("zapisano", WY_PNG)
    json.dump(kontrola, open(WY_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

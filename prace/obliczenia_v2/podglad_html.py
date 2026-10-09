"""
PODGLĄD 3D W PRZEGLĄDARCE – jeden plik HTML (Three.js r147 wbudowany, działa bez internetu i bez instalacji).
Zawartość (te same dane co MODEL3D_dz190.dxf / LandXML):
  - 5 etapów (powierzchnie z wyniki/MODEL3D_dz190_LandXML.xml): teren istniejący, po zdjęciu humusu i nasypu, po wykopie A, po wykopie B, stan końcowy (PZT);
  - garaże: hale i zadaszone dojazdy jako bryły (od spodu płyty 121,96 do rzędnej terenu projektowanego nad garażem – uproszczenie), rampy;
  - ścianka szczelna z grodzic po obwodzie wykopu (przebieg z geometria.json, głębokość ok. 8,0 m ppt wg projektu geotechnicznego s. 10);
  - poziom wody (średni ustabilizowany wg DGI 123,39 m npm, suwak w zakresie DGI 122,90–124,10) i zwierciadło ustabilizowane w otworach;
  - otwory DGI 2–24 (profile warstw) i sondowania CPTU 10, 12, 18, 21, 24 (profile z interpretacji, zał. 7 DGI).
Wynik: wyniki/MODEL3D_dz190_podglad.html
Uruchomienie: python podglad_html.py   (wymaga wcześniej: python model3d.py)
"""
import base64
import json
import math
import os

import numpy as np
from shapely import contains_xy, wkt
from shapely.geometry import LineString, Polygon

import dane as D
import model3d as M
import przekroje as PR
import silnik as S
from kontrola_modelu3d import czytaj_landxml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WY = os.path.join(REPO, "wyniki", "MODEL3D_dz190_podglad.html")
VENDOR = os.path.join(HERE, "_vendor", "three-0.147.0")
ZREF = 120.0
SPOD_PLYTY = 121.96          # d.k. płyty fundamentowej (−4,04; rzuty PW) – spód bryły garażu
GLEB_GRODZIC = 8.0           # PG s. 10: grodzice do maks. ok. 8,0 m poniżej istniejącego terenu
WODA_SR, WODA_MIN, WODA_MAX = 123.39, 122.90, 124.10   # DGI tab. 1 (zwierciadło ustabilizowane)


def b64(a, dt):
    return base64.b64encode(np.ascontiguousarray(a, dtype=dt).tobytes()).decode("ascii")


def zageszczone(coords, ds, zamkniety):
    ln = LineString(list(coords) + ([coords[0]] if zamkniety else []))
    n = max(int(math.ceil(ln.length / ds)), 1)
    return [(p.x, p.y) for p in (ln.interpolate(i * ln.length / n) for i in range(n + (0 if zamkniety else 1)))]


def main():
    geo = json.load(open(os.path.join(D.DANE, "geometria.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(D.DANE, "strefy.json"), encoding="utf-8"))
    oto = json.load(open(os.path.join(D.DANE, "otwory.json"), encoding="utf-8"))
    cpt = json.load(open(os.path.join(D.DANE, "cptu.json"), encoding="utf-8"))
    G = Polygon(geo["granica"])
    E0, N0 = math.floor(G.bounds[0]), math.floor(G.bounds[1])
    loc = lambda e, n: (round(e - E0, 3), round(n - N0, 3))
    w, gm = S.licz(zapisz_geometrie=True)
    sg = gm["_siatka"]
    xs, ys, shape = sg["xs"], sg["ys"], sg["shape"]
    fI = {k: M.interpolator(xs, ys, sg[k].reshape(shape)) for k in ("zt", "zs", "zp")}
    ev = lambda k, E, N: fI[k](np.column_stack([np.atleast_1d(N), np.atleast_1d(E)]))

    # --- powierzchnie z pliku LandXML (to, co dostaje Civil 3D)
    surf = czytaj_landxml(M.WY_XML)
    pow_ = []
    for klucz, nazwa, warstwa, kol, opis in M.POWIERZCHNIE:
        Pn, F = surf[nazwa]
        E, N, Z = Pn[:, 2], Pn[:, 1], Pn[:, 3]
        pos = np.column_stack([E - E0, Z - ZREF, -(N - N0)]).ravel()
        rec = {"klucz": klucz, "nazwa": nazwa, "opis": opis, "n": int(len(Pn)), "pos": b64(pos, "<f4"), "idx": b64((F - 1).ravel(), "<u2" if len(Pn) < 65535 else "<u4"),
               "idx32": len(Pn) >= 65535, "zmin": float(Z.min()), "zmax": float(Z.max())}
        if klucz in ("A", "B"):
            rec["gleb"] = b64(np.clip(ev("zs", E, N) - Z, 0, None), "<f4")
        pow_.append(rec)

    # --- garaże: hale + zadaszone dojazdy (bryły), rampy
    inG = sg["inG"]
    X, Y = np.meshgrid(xs, ys)
    xx, yy = X.ravel(), Y.ravel()

    def gora(poly):
        m = contains_xy(poly, xx, yy) & inG
        return float(np.median(sg["zp"][m])) if m.any() else 126.0
    garaze = []
    for nr, v in sorted(geo["hale"].items(), key=lambda t: int(t[0])):
        p = Polygon(v)
        garaze.append({"rodzaj": "hala", "nr": int(nr), "pts": [loc(*c) for c in list(p.exterior.coords)[:-1]], "zb": SPOD_PLYTY, "zt": round(gora(p), 2),
                       "c": loc(p.centroid.x, p.centroid.y), "pole": round(p.area, 2)})
    zad = wkt.loads(st["zadaszone_poza_halami"])
    for q in (list(zad.geoms) if hasattr(zad, "geoms") else [zad]):
        if q.geom_type == "Polygon" and q.area > 1.0:
            q = q.simplify(0.05)
            garaze.append({"rodzaj": "zadaszony dojazd", "nr": 0, "pts": [loc(*c) for c in list(q.exterior.coords)[:-1]], "zb": SPOD_PLYTY, "zt": round(gora(q), 2),
                           "c": loc(q.centroid.x, q.centroid.y), "pole": round(q.area, 2)})
    rampy = []
    for r in st["rampy"]:
        g = wkt.loads(r["obrys"])
        for q in (list(g.geoms) if hasattr(g, "geoms") else [g]):
            rampy.append({"pts": [loc(*c) for c in list(q.exterior.coords)[:-1]], "dol": loc(*r["dol"]), "gora": loc(*r["gora"]),
                          "zd": D.RAMPA_DOL, "zg": D.RAMPA_GORA})

    # --- ścianka szczelna (grodzice) wzdłuż otwartej linii ścianki
    wall = zageszczone(geo["scianka_otwarta"], 1.0, False)
    we, wn = np.array([p[0] for p in wall]), np.array([p[1] for p in wall])
    zt_w = ev("zt", we, wn)
    scianka = {"pts": [loc(e, n) for e, n in wall], "zt": [round(float(z), 3) for z in zt_w], "zb": [round(float(z) - GLEB_GRODZIC, 3) for z in zt_w],
               "dlugosc": round(LineString(geo["scianka_otwarta"]).length, 2)}
    a, b = geo["odcinek_zamykajacy"]
    zam = zageszczone([tuple(a), tuple(b)], 2.0, False)
    zamkniecie = {"pts": [loc(e, n) for e, n in zam], "z": [round(float(z), 3) for z in ev("zs", np.array([p[0] for p in zam]), np.array([p[1] for p in zam]))]}
    gr = zageszczone(list(G.exterior.coords)[:-1], 2.0, True)
    granica = {"pts": [loc(e, n) for e, n in gr], "z": [round(float(z), 3) for z in ev("zt", np.array([p[0] for p in gr]), np.array([p[1] for p in gr]))]}
    # górne krawędzie wykopów
    krawedzie = {}
    for k in ("A", "B"):
        g = gm[k].intersection(G)
        pier = []
        for q in (list(g.geoms) if hasattr(g, "geoms") else [g]):
            if q.geom_type != "Polygon" or q.area < 2:
                continue
            for ring in [q.exterior] + list(q.interiors):
                pp = zageszczone(list(ring.coords)[:-1], 2.0, True)
                zz = ev("zs", np.array([p[0] for p in pp]), np.array([p[1] for p in pp]))
                pier.append({"pts": [loc(e, n) for e, n in pp], "z": [round(float(z), 3) for z in zz]})
        krawedzie[k] = pier

    # --- otwory i CPTU (DGI)
    otwory = []
    for nr, o in sorted(oto.items(), key=lambda t: int(t[0])):
        otwory.append({"nr": nr, "p": loc(o["E"], o["N"]), "E": o["E"], "N": o["N"], "H": o["H"], "woda": o["woda_ustab_m_ppt"], "woda_uwagi": o.get("woda_uwagi", ""),
                       "warstwy": o["warstwy"], "zrodlo": o.get("zrodlo", ""),
                       "cptu": cpt[nr]["warstwy"] if nr in cpt else None, "cptu_zrodlo": cpt[nr].get("zrodlo", "") if nr in cpt else ""})

    pal = M.paleta("YlOrBr", len(M.KRAWEDZIE_GLEBOKOSCI) - 1)
    dane = {
        "E0": E0, "N0": N0, "ZREF": ZREF, "powierzchnie": pow_, "garaze": garaze, "rampy": rampy, "scianka": scianka, "zamkniecie": zamkniecie,
        "granica": granica, "krawedzie": krawedzie, "otwory": otwory,
        "granica_poly": [loc(*c) for c in list(G.exterior.coords)[:-1]],
        "woda": {"sr": WODA_SR, "min": WODA_MIN, "max": WODA_MAX},
        "dno": S.PARAMETRY["dno"], "spod_plyty": SPOD_PLYTY, "gleb_grodzic": GLEB_GRODZIC,
        "glebokosc_klasy": M.KRAWEDZIE_GLEBOKOSCI, "glebokosc_kolory": pal, "kolor_poza": M.KOLOR_POZA_WYKOPEM,
        "klasy_kolory": PR.KOLORY_KLAS, "klasy_opis": PR.OPIS_KLAS, "kolor_humus": PR.KOLOR_HUMUS, "kolor_nasyp": PR.KOLOR_NASYP,
        "bilans": {"A": round(sum(sum(v.values()) for v in w["warianty"]["A"]["wykop_m3"].values()), 3),
                   "B": round(sum(sum(v.values()) for v in w["warianty"]["B"]["wykop_m3"].values()), 3), "humus": w["humus_m3"], "nasyp": w["nasyp_m3"]},
    }
    js_dane = json.dumps(dane, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    three = open(os.path.join(VENDOR, "three.min.js"), encoding="utf-8").read()
    orbit = open(os.path.join(VENDOR, "OrbitControls.js"), encoding="utf-8").read()
    html = SZABLON.replace("/*THREE*/", three).replace("/*ORBIT*/", orbit).replace("/*DANE*/", js_dane).replace("/*APP*/", APP)
    open(WY, "w", encoding="utf-8").write(html)
    print("zapisano", WY, "%.2f MB" % (os.path.getsize(WY) / 1e6), "| powierzchnie:", [(p["nazwa"], p["n"]) for p in pow_],
          "| garaże:", len(garaze), "| rampy:", len(rampy), "| ścianka %.1f m" % scianka["dlugosc"], "| otwory:", len(otwory))


SZABLON = r"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<title>Model 3D robót ziemnych – dz. 1/90 Wojszyce</title>
<style>
 html,body{margin:0;height:100%;overflow:hidden;font-family:Segoe UI,Arial,sans-serif;font-size:13px;color:#1d2733}
 #scena{position:absolute;inset:0}
 #panel{position:absolute;top:8px;left:8px;width:290px;max-height:calc(100% - 16px);overflow:auto;background:rgba(255,255,255,.94);border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.2);padding:8px 10px}
 #panel h1{font-size:15px;margin:2px 0 6px}
 #panel h2{font-size:12px;margin:10px 0 3px;text-transform:uppercase;color:#4a5a6a;border-bottom:1px solid #d5dde5}
 #panel label{display:block;margin:2px 0;cursor:pointer}
 #panel .rz{display:flex;gap:4px;flex-wrap:wrap;margin:4px 0}
 #panel button{border:1px solid #9fb0c0;background:#f4f7fa;border-radius:4px;padding:2px 7px;cursor:pointer;font-size:12px}
 #panel button:hover{background:#dde7f0}
 #panel input[type=range]{width:100%}
 .maly{font-size:11px;color:#5a6a7a}
 #info{position:absolute;right:8px;bottom:8px;width:330px;max-height:55%;overflow:auto;background:rgba(255,255,255,.95);border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.2);padding:8px 10px;font-size:12px}
 #info table{border-collapse:collapse;width:100%}#info td,#info th{border-bottom:1px solid #e3e8ee;padding:1px 3px;text-align:left}
 #legenda{position:absolute;right:8px;top:8px;background:rgba(255,255,255,.94);border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.2);padding:6px 9px;font-size:11px;max-width:230px}
 .kw{display:inline-block;width:12px;height:10px;margin-right:5px;vertical-align:middle;border:1px solid #888}
 #etykiety{position:absolute;inset:0;pointer-events:none;overflow:hidden}
 .et{position:absolute;transform:translate(-50%,-100%);white-space:nowrap;font-size:11px;background:rgba(255,255,255,.78);padding:0 3px;border-radius:3px;color:#123}
 .et.hala{font-weight:bold;font-size:12px;color:#8a1010;z-index:3;background:rgba(255,255,255,.9)}
 .et.mniej{opacity:.85;font-size:10px}
 #polnoc{position:absolute;left:310px;top:12px;width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.9);box-shadow:0 1px 5px rgba(0,0,0,.25)}
 #polnoc div{position:absolute;inset:0;text-align:center;font-weight:bold;font-size:12px;line-height:14px}
 #ladowanie{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:18px;background:#eef2f5}
</style>
</head>
<body>
<div id="scena"></div>
<div id="etykiety"></div>
<div id="ladowanie">Wczytywanie modelu…</div>
<div id="polnoc" title="Północ"><div id="strzalka"><svg width="44" height="44" viewBox="0 0 44 44"><polygon points="22,4 28,24 22,20 16,24" fill="#b22"/><polygon points="22,40 28,24 22,28 16,24" fill="#999"/><text x="22" y="14" font-size="9" text-anchor="middle" fill="#fff">N</text></svg></div></div>
<div id="panel">
 <h1>Roboty ziemne – dz. 1/90 Wojszyce</h1>
 <div class="maly">Obrót: lewy przycisk myszy · przesuw: prawy · zoom: kółko. Kliknij w model, żeby zobaczyć rzędne w punkcie albo profil otworu.</div>
 <h2>Etapy (powierzchnie)</h2>
 <div id="etapy"></div>
 <div class="rz">Pokaż tylko: <button data-etap="ist">1</button><button data-etap="hum">2</button><button data-etap="A">3A</button><button data-etap="B">3B</button><button data-etap="kon">4</button></div>
 <label>Kolor powierzchni:
  <select id="kolor"><option value="auto">wykop wg głębokości, reszta jednolita</option><option value="rzedna">wszystkie wg rzędnej</option><option value="jednolity">jednolity</option></select></label>
 <label><input type="checkbox" id="siatka"> siatka trójkątów</label>
 <label>Przezroczystość powierzchni <input type="range" id="przezr" min="0" max="0.9" step="0.05" value="0"></label>
 <h2>Garaże i zabezpieczenie wykopu</h2>
 <label><input type="checkbox" id="garaze" checked> garaże (hale) – bryły</label>
 <label><input type="checkbox" id="zadaszone" checked> zadaszone dojazdy</label>
 <label><input type="checkbox" id="rampy" checked> rampy (pochylnie)</label>
 <label><input type="checkbox" id="scianka" checked> ścianka szczelna (grodzice)</label>
 <label><input type="checkbox" id="zamkniecie" checked> odcinek bez ścianki (skarpa od południa)</label>
 <label><input type="checkbox" id="krawA"> górna krawędź wykopu A</label>
 <label><input type="checkbox" id="krawB"> górna krawędź wykopu B</label>
 <label><input type="checkbox" id="granica" checked> granica działki</label>
 <h2>Woda i badania (DGI)</h2>
 <label><input type="checkbox" id="woda" checked> poziom wody: <b id="wodaTxt"></b> m npm</label>
 <input type="range" id="wodaPoz" step="0.01">
 <div class="maly">Średnie zwierciadło ustabilizowane 123,39 m npm; zakres w DGI 122,90–124,10 (wahania ±0,5 m).</div>
 <label><input type="checkbox" id="wodaOtw" checked> zwierciadło w otworach</label>
 <label><input type="checkbox" id="otwory" checked> otwory DGI (profile)</label>
 <label><input type="checkbox" id="cptu" checked> sondowania CPTU (profile)</label>
 <label><input type="checkbox" id="naWierzchu"> otwory widoczne przez powierzchnie</label>
 <div class="maly">Profile otworów są w gruncie – żeby je zobaczyć, zwiększ przezroczystość powierzchni albo zaznacz opcję wyżej.</div>
 <h2>Widok</h2>
 <label>Przewyższenie pionowe ×<b id="przewTxt"></b> <input type="range" id="przew" min="1" max="6" step="0.5" value="2"></label>
 <label><input type="checkbox" id="etyk" checked> etykiety</label>
 <div class="rz"><button id="wIzo">izometria</button><button id="wGora">z góry</button><button id="wPoludnie">od południa</button><button id="wZach">od zachodu</button></div>
 <h2>Bilans (dla porównania)</h2>
 <div class="maly" id="bilansTxt"></div>
 <h2>Uwagi</h2>
 <div class="maly">Garaże: bryła uproszczona – od spodu płyty 121,96 do rzędnej terenu projektowanego nad garażem (strop razem z warstwą zieleni). Ścianka: przebieg z obliczeń bilansu, głębokość ok. 8,0 m poniżej terenu istniejącego (projekt geotechniczny s. 10: „do maksymalnej głębokości około 8,0 m ppt", dokładna głębokość w dalszym etapie). Fundamenty głębsze (pogrubienia, rdzenie, studzienki) nie są pokazane. Profile otworów i CPTU wg DGI (karty otworów, zał. 7); CPTU narysowane 2,2 m na wschód od otworu (etykieta pod profilem), w którym wykonano sondowanie. Układ PL-2000/6, wysokości PL-KRON86-NH.</div>
</div>
<div id="legenda"></div>
<div id="info"><b>Kliknij w model</b><div class="maly">Pokażę rzędne wszystkich etapów w tym miejscu albo profil otworu.</div></div>
<script>/*THREE*/</script>
<script>/*ORBIT*/</script>
<script id="dane" type="application/json">/*DANE*/</script>
<script>/*APP*/</script>
</body>
</html>
"""

APP = r"""
(function(){
'use strict';
const DATA = JSON.parse(document.getElementById('dane').textContent);
const ZREF = DATA.ZREF, E0 = DATA.E0, N0 = DATA.N0;
const $ = id => document.getElementById(id);
const fmt = (v, d=2) => v.toFixed(d).replace('.', ',');
const fmtTys = v => { const s = v.toFixed(0); return s.replace(/\B(?=(\d{3})+(?!\d))/g, ' '); };
function dec(b, T){ const s = atob(b); const u = new Uint8Array(s.length); for (let i=0;i<s.length;i++) u[i]=s.charCodeAt(i); return new T(u.buffer); }
const rgb = c => new THREE.Color(c[0]/255, c[1]/255, c[2]/255);

// ---------------------------------------------------------------- scena
const kont = $('scena');
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(kont.clientWidth, kont.clientHeight);
kont.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe9eef3);
const camera = new THREE.PerspectiveCamera(40, kont.clientWidth/kont.clientHeight, 0.5, 6000);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.12; controls.screenSpacePanning = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a7a66, 0.75));
const sun = new THREE.DirectionalLight(0xffffff, 0.55); sun.position.set(-300, 500, 250); scene.add(sun);
const sun2 = new THREE.DirectionalLight(0xffffff, 0.2); sun2.position.set(300, 200, -300); scene.add(sun2);
const world = new THREE.Group(); scene.add(world);
const grupy = {};
function grupa(k){ if(!grupy[k]){ grupy[k] = new THREE.Group(); world.add(grupy[k]); } return grupy[k]; }
const etykiety = [];
function etykieta(tekst, x, y, z, klucz, cls){ const d = document.createElement('div'); d.className = 'et' + (cls?' '+cls:''); d.textContent = tekst; $('etykiety').appendChild(d); etykiety.push({d, x, y, z, klucz}); }
const pickable = [];

// ---------------------------------------------------------------- kolory
const KL = DATA.glebokosc_klasy, KK = DATA.glebokosc_kolory.map(rgb), KPOZA = rgb(DATA.kolor_poza);
function kolorGleb(g){ if (g < KL[0]) return KPOZA; for (let i=KL.length-2;i>=0;i--) if (g >= KL[i]) return KK[Math.min(i, KK.length-1)]; return KPOZA; }
const STOPS = [[121.5,[43,99,180]],[122.5,[80,170,200]],[123.3,[150,205,150]],[124.2,[235,225,140]],[125.0,[220,160,90]],[126.0,[170,95,60]],[127.0,[120,70,50]]];
function kolorRz(z){ if (z<=STOPS[0][0]) return rgb(STOPS[0][1]); for (let i=1;i<STOPS.length;i++){ if (z<=STOPS[i][0]){ const [z0,c0]=STOPS[i-1],[z1,c1]=STOPS[i]; const t=(z-z0)/(z1-z0); return rgb([c0[0]+(c1[0]-c0[0])*t, c0[1]+(c1[1]-c0[1])*t, c0[2]+(c1[2]-c0[2])*t]); } } return rgb(STOPS[STOPS.length-1][1]); }
const JEDN = {ist:[150,160,140], hum:[176,141,99], A:[214,150,70], B:[214,150,70], kon:[120,185,100]};
const NAZWY = {ist:'1. teren istniejący', hum:'2. po zdjęciu humusu i nasypu', A:'3A. po wykopie – wariant A', B:'3B. po wykopie – wariant B', kon:'4. stan końcowy (PZT)'};

// ---------------------------------------------------------------- powierzchnie
const POW = {};
DATA.powierzchnie.forEach((p, i) => {
  const pos = dec(p.pos, Float32Array);
  const idx = dec(p.idx, p.idx32 ? Uint32Array : Uint16Array);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  g.computeVertexNormals();
  const n = p.n, kol = new Float32Array(n*3);
  g.setAttribute('color', new THREE.BufferAttribute(kol, 3));
  const mat = new THREE.MeshLambertMaterial({vertexColors:true, side:THREE.DoubleSide, polygonOffset:true, polygonOffsetFactor:-0.6*i, polygonOffsetUnits:-2*i});
  const mesh = new THREE.Mesh(g, mat);
  mesh.userData = {typ:'powierzchnia', klucz:p.klucz};
  const wire = new THREE.Mesh(g, new THREE.MeshBasicMaterial({color:0x334455, wireframe:true, transparent:true, opacity:0.25}));
  wire.visible = false;
  const grp = grupa('pow_'+p.klucz); grp.add(mesh); grp.add(wire);
  POW[p.klucz] = {mesh, wire, geom:g, gleb: p.gleb ? dec(p.gleb, Float32Array) : null, pos};
  pickable.push(mesh);
});
function pokoloruj(){
  const tryb = $('kolor').value;
  for (const k in POW){
    const P = POW[k], c = P.geom.attributes.color, pos = P.pos;
    for (let i=0;i<c.count;i++){
      let col;
      if (tryb === 'rzedna') col = kolorRz(pos[i*3+1] + ZREF);
      else if (tryb === 'auto' && P.gleb) col = kolorGleb(P.gleb[i]);
      else col = rgb(JEDN[k]);
      c.setXYZ(i, col.r, col.g, col.b);
    }
    c.needsUpdate = true;
  }
  legenda();
}

// ---------------------------------------------------------------- bryły (garaże), rampy, woda
function v2(p){ return new THREE.Vector2(p[0], p[1]); }
function bryla(pts, zb, zt){
  let c = pts.map(v2); if (THREE.ShapeUtils.isClockWise(c)) c = c.reverse();
  const tr = THREE.ShapeUtils.triangulateShape(c, []), n = c.length, pos = [], idx = [];
  c.forEach(p => pos.push(p.x, zb-ZREF, -p.y)); c.forEach(p => pos.push(p.x, zt-ZREF, -p.y));
  tr.forEach(t => { idx.push(t[0]+n, t[1]+n, t[2]+n); idx.push(t[2], t[1], t[0]); });
  for (let i=0;i<n;i++){ const j=(i+1)%n; idx.push(i, j, j+n, i, j+n, i+n); }
  let g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx);
  g = g.toNonIndexed(); g.computeVertexNormals(); return g;
}
const matHala = new THREE.MeshLambertMaterial({color:0xb9bcc2, transparent:true, opacity:0.75, side:THREE.DoubleSide});
const matZad = new THREE.MeshLambertMaterial({color:0xd0b48a, transparent:true, opacity:0.82, side:THREE.DoubleSide});
const matKraw = new THREE.LineBasicMaterial({color:0x5a2020});
DATA.garaze.forEach(gz => {
  const g = bryla(gz.pts, gz.zb, gz.zt);
  const hala = gz.rodzaj === 'hala';
  const m = new THREE.Mesh(g, hala ? matHala : matZad);
  m.userData = {typ:'garaz', d:gz};
  const e = new THREE.LineSegments(new THREE.EdgesGeometry(g, 25), matKraw);
  const grp = grupa(hala ? 'garaze' : 'zadaszone'); grp.add(m); grp.add(e); pickable.push(m);
  if (hala) etykieta('HALA ' + gz.nr, gz.c[0], gz.c[1], gz.zt + 0.6, 'garaze', 'hala');
});
DATA.rampy.forEach(r => {
  let c = r.pts.map(v2); if (THREE.ShapeUtils.isClockWise(c)) c = c.reverse();
  const tr = THREE.ShapeUtils.triangulateShape(c, []), pos = [], idx = [];
  const ux = r.gora[0]-r.dol[0], uy = r.gora[1]-r.dol[1], L2 = ux*ux+uy*uy;
  c.forEach(p => { const t = Math.min(1, Math.max(0, ((p.x-r.dol[0])*ux + (p.y-r.dol[1])*uy)/L2)); const z = r.zd + t*(r.zg-r.zd) + 0.03; pos.push(p.x, z-ZREF, -p.y); });
  tr.forEach(t => idx.push(t[0], t[1], t[2]));
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({color:0xe8c33a, side:THREE.DoubleSide}));
  m.userData = {typ:'rampa', d:r}; grupa('rampy').add(m); pickable.push(m);
  const cx = (r.dol[0]+r.gora[0])/2, cy = (r.dol[1]+r.gora[1])/2;
  etykieta('rampa ' + fmt(r.zg) + ' – ' + fmt(r.zd), cx, cy, (r.zd+r.zg)/2 + 0.8, 'rampy');
});
// ścianka szczelna – pionowy pas
(function(){
  const s = DATA.scianka, pos = [], idx = [];
  s.pts.forEach((p, i) => { pos.push(p[0], s.zt[i]-ZREF, -p[1]); pos.push(p[0], s.zb[i]-ZREF, -p[1]); });
  for (let i=0;i<s.pts.length-1;i++){ const a=2*i; idx.push(a, a+1, a+3, a, a+3, a+2); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({color:0x4f6f8f, side:THREE.DoubleSide, transparent:true, opacity:0.9}));
  m.userData = {typ:'scianka', d:s}; grupa('scianka').add(m); pickable.push(m);
  const top = s.pts.map((p,i) => new THREE.Vector3(p[0], s.zt[i]-ZREF+0.02, -p[1]));
  grupa('scianka').add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(top), new THREE.LineBasicMaterial({color:0x1d3550})));
  const ymax = Math.max(...s.pts.map(p => p[1])), xs_ = s.pts.map(p => p[0]), xm = (Math.min(...xs_) + Math.max(...xs_)) / 2;
  let k = 0, best = 1e9; s.pts.forEach((p, i) => { if (p[1] > ymax - 15 && Math.abs(p[0] - xm) < best){ best = Math.abs(p[0] - xm); k = i; } });
  etykieta('ścianka szczelna (grodzice, ok. ' + fmt(DATA.gleb_grodzic,1) + ' m ppt)', s.pts[k][0], s.pts[k][1], s.zt[k] + 1.0, 'scianka');
})();
function linia(pts, z, kolor, klucz, przer){
  const v = pts.map((p,i) => new THREE.Vector3(p[0], z[i]-ZREF+0.05, -p[1]));
  const g = new THREE.BufferGeometry().setFromPoints(v);
  const m = przer ? new THREE.LineDashedMaterial({color:kolor, dashSize:2, gapSize:1.5}) : new THREE.LineBasicMaterial({color:kolor});
  const l = new THREE.Line(g, m); if (przer) l.computeLineDistances(); grupa(klucz).add(l); return l;
}
linia(DATA.zamkniecie.pts, DATA.zamkniecie.z, 0x7a2b8a, 'zamkniecie', true);
{ const z = DATA.zamkniecie, k = Math.floor(z.pts.length/2); etykieta('brak ścianki – skarpa 1:1,5', z.pts[k][0], z.pts[k][1], z.z[k] + 0.8, 'zamkniecie'); }
linia(DATA.granica.pts.concat([DATA.granica.pts[0]]), DATA.granica.z.concat([DATA.granica.z[0]]), 0x8a2be2, 'granica', false);
['A','B'].forEach(k => DATA.krawedzie[k].forEach(r => linia(r.pts.concat([r.pts[0]]), r.z.concat([r.z[0]]), k==='A'?0x1f5fbf:0x0f8f8f, 'kraw'+k, false)));
// woda – płaszczyzna w obrysie działki
const woda = (function(){
  let c = DATA.granica_poly.map(v2); if (THREE.ShapeUtils.isClockWise(c)) c = c.reverse();
  const tr = THREE.ShapeUtils.triangulateShape(c, []), pos = [], idx = [];
  c.forEach(p => pos.push(p.x, 0, -p.y)); tr.forEach(t => idx.push(t[0], t[1], t[2]));
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({color:0x2f7fd8, transparent:true, opacity:0.25, side:THREE.DoubleSide, depthWrite:false}));
  m.renderOrder = 10; m.userData = {typ:'woda'}; grupa('woda').add(m); return m;
})();

// ---------------------------------------------------------------- otwory i CPTU
const KLR = {}; for (const k in DATA.klasy_kolory) KLR[k] = rgb(DATA.klasy_kolory[k]);
function kolorWarstwy(w){ if (w.kat === 'H') return rgb(DATA.kolor_humus); if (w.kat === 'N') return rgb(DATA.kolor_nasyp); return KLR[w.warstwa] || new THREE.Color(0.6,0.6,0.6); }
const matProfile = [];
function profil(warstwy, x, y, H, r, klucz, info){
  warstwy.forEach(w => {
    const h = w.spag - w.strop; if (h <= 0) return;
    const g = new THREE.CylinderGeometry(r, r, h, 14);
    const mt = new THREE.MeshLambertMaterial({color:kolorWarstwy(w)}); matProfile.push(mt);
    const m = new THREE.Mesh(g, mt);
    m.position.set(x, H - (w.strop + w.spag)/2 - ZREF, -y);
    m.userData = {typ:'profil', info}; grupa(klucz).add(m); pickable.push(m);
  });
}
const matWodaOtw = new THREE.MeshBasicMaterial({color:0x0b50c8});
DATA.otwory.forEach(o => {
  const [x, y] = o.p;
  profil(o.warstwy, x, y, o.H, 0.8, 'otwory', o);
  etykieta('otw. ' + o.nr, x, y, o.H + 0.9, 'otwory', 'mniej');
  if (o.cptu){ const zk = o.H - Math.max(...o.cptu.map(l => l.spag)); profil(o.cptu, x + 2.2, y, o.H, 0.55, 'cptu', Object.assign({}, o, {jestCPTU:true})); etykieta('CPTU-' + o.nr, x + 2.2, y, zk - 0.3, 'cptu', 'mniej'); }
  if (o.woda !== null && o.woda !== undefined){
    const m = new THREE.Mesh(new THREE.CylinderGeometry(1.3, 1.3, 0.08, 20), matWodaOtw);
    m.position.set(x, o.H - o.woda - ZREF, -y); m.userData = {typ:'profil', info:o}; grupa('wodaOtw').add(m); pickable.push(m);
  }
});

// ---------------------------------------------------------------- etapy (UI)
const etapy = $('etapy');
['ist','hum','A','B','kon'].forEach(k => {
  const l = document.createElement('label');
  l.innerHTML = '<input type="checkbox" id="et_' + k + '"' + (k==='B' ? ' checked' : '') + '> ' + NAZWY[k];
  etapy.appendChild(l);
});
function widocznosc(){
  ['ist','hum','A','B','kon'].forEach(k => { grupy['pow_'+k].visible = $('et_'+k).checked; POW[k].wire.visible = $('siatka').checked; });
  ['garaze','zadaszone','rampy','scianka','zamkniecie','granica','woda','wodaOtw','otwory','cptu'].forEach(k => { if (grupy[k]) grupy[k].visible = $(k).checked; });
  grupa('krawA').visible = $('krawA').checked; grupa('krawB').visible = $('krawB').checked;
  const naWierzchu = $('naWierzchu').checked;
  matProfile.concat([matWodaOtw]).forEach(m => { m.depthTest = !naWierzchu; m.needsUpdate = true; });
  ['otwory','cptu','wodaOtw'].forEach(k => grupa(k).children.forEach(c => c.renderOrder = naWierzchu ? 20 : 0));
  const op = 1 - parseFloat($('przezr').value);
  for (const k in POW){ const m = POW[k].mesh.material; m.transparent = op < 0.999; m.opacity = op; m.depthWrite = op >= 0.999; m.needsUpdate = true; }
}
document.querySelectorAll('#panel input[type=checkbox]').forEach(c => c.addEventListener('change', widocznosc));
$('przezr').addEventListener('input', widocznosc);
document.querySelectorAll('[data-etap]').forEach(b => b.addEventListener('click', () => { ['ist','hum','A','B','kon'].forEach(k => $('et_'+k).checked = (k === b.dataset.etap)); widocznosc(); }));
$('kolor').addEventListener('change', pokoloruj);
// woda
$('wodaPoz').min = DATA.woda.min; $('wodaPoz').max = DATA.woda.max; $('wodaPoz').value = DATA.woda.sr;
function ustawWode(){ const z = parseFloat($('wodaPoz').value); woda.position.y = z - ZREF; $('wodaTxt').textContent = fmt(z); }
$('wodaPoz').addEventListener('input', ustawWode);
// przewyższenie
let przew = 2;
function ustawPrzew(){ const n = parseFloat($('przew').value); const cy = controls.target.y / przew; przew = n; world.scale.y = przew; controls.target.y = cy * przew; $('przewTxt').textContent = fmt(przew,1); }
$('przew').addEventListener('input', ustawPrzew);
// bilans
$('bilansTxt').innerHTML = 'Wykop gruntu rodzimego: A ' + fmtTys(DATA.bilans.A) + ' m³, B ' + fmtTys(DATA.bilans.B) + ' m³. Humus ' + fmtTys(DATA.bilans.humus) + ' m³, nasyp ' + fmtTys(DATA.bilans.nasyp) + ' m³. Szczegóły: arkusz BILANS_ROBOT_ZIEMNYCH_dz190_v2.xlsx.';

// ---------------------------------------------------------------- widoki
const box = new THREE.Box3().setFromObject(grupy['pow_ist']);
const srodek = box.getCenter(new THREE.Vector3()), rozm = box.getSize(new THREE.Vector3());
const R = Math.max(rozm.x, rozm.z);
function widok(dx, dy, dz){ const t = new THREE.Vector3(srodek.x, (124.0-ZREF)*przew, srodek.z); controls.target.copy(t); camera.position.set(t.x + dx*R, t.y + dy*R, t.z + dz*R); controls.update(); }
$('wIzo').onclick = () => widok(-0.75, 0.75, 0.85);
$('wGora').onclick = () => widok(0, 1.55, 0.001);
$('wPoludnie').onclick = () => widok(0, 0.35, 1.25);
$('wZach').onclick = () => widok(-1.25, 0.35, 0);

// ---------------------------------------------------------------- legenda
function legenda(){
  const tryb = $('kolor').value; let h = '';
  if (tryb === 'auto'){ h += '<b>Głębokość wykopu (3A, 3B)</b><br><span class="kw" style="background:rgb(' + DATA.kolor_poza.join(',') + ')"></span>poza wykopem<br>';
    for (let i=0;i<KL.length-1;i++){ const c = DATA.glebokosc_kolory[Math.min(i, DATA.glebokosc_kolory.length-1)]; h += '<span class="kw" style="background:rgb(' + c.join(',') + ')"></span>' + (KL[i+1] < 6 ? fmt(KL[i],1) + '–' + fmt(KL[i+1],1) + ' m' : 'ponad ' + fmt(KL[i],1) + ' m') + '<br>'; } }
  else if (tryb === 'rzedna'){ h += '<b>Rzędna [m npm]</b><br>'; STOPS.forEach(s => h += '<span class="kw" style="background:rgb(' + s[1].map(Math.round).join(',') + ')"></span>' + fmt(s[0],1) + '<br>'); }
  h += '<b>Grunt w otworach (DGI)</b><br><span class="kw" style="background:rgb(' + DATA.kolor_humus.join(',') + ')"></span>humus<br><span class="kw" style="background:rgb(' + DATA.kolor_nasyp.join(',') + ')"></span>nasyp niekontrolowany<br>';
  for (const k in DATA.klasy_kolory) h += '<span class="kw" style="background:rgb(' + DATA.klasy_kolory[k].join(',') + ')"></span>' + k + ' – ' + DATA.klasy_opis[k] + '<br>';
  h += '<span class="kw" style="background:#2f7fd8;opacity:.6"></span>poziom wody · <span class="kw" style="background:#0b50c8"></span>zwierciadło w otworze';
  $('legenda').innerHTML = h;
}

// ---------------------------------------------------------------- klik: rzędne w punkcie / profil otworu
const ray = new THREE.Raycaster(), mysz = new THREE.Vector2();
let start = null;
renderer.domElement.addEventListener('pointerdown', e => { start = [e.clientX, e.clientY]; });
renderer.domElement.addEventListener('pointerup', e => {
  if (!start || Math.hypot(e.clientX-start[0], e.clientY-start[1]) > 4) return;
  const r = renderer.domElement.getBoundingClientRect();
  mysz.set((e.clientX-r.left)/r.width*2-1, -(e.clientY-r.top)/r.height*2+1);
  ray.setFromCamera(mysz, camera);
  const widoczne = pickable.filter(o => { let p = o; while (p){ if (!p.visible) return false; p = p.parent; } return true; });
  const hit = ray.intersectObjects(widoczne, false)[0];
  if (!hit) return;
  const ud = hit.object.userData;
  if (ud.typ === 'profil'){ pokazProfil(ud.info); return; }
  const x = hit.point.x, y = -hit.point.z;
  let h = '<b>Punkt</b> E = ' + fmt(x+E0) + ', N = ' + fmt(y+N0) + '<br>';
  if (ud.typ === 'garaz') h += '<b>' + (ud.d.rodzaj === 'hala' ? 'Hala ' + ud.d.nr : 'Zadaszony dojazd') + '</b> – pole ' + fmt(ud.d.pole) + ' m², bryła ' + fmt(ud.d.zb) + ' – ' + fmt(ud.d.zt) + ' m npm (uproszczona)<br>';
  if (ud.typ === 'rampa') h += '<b>Rampa</b> ' + fmt(ud.d.zg) + ' – ' + fmt(ud.d.zd) + ' m npm; spód wykopu = powierzchnia − 0,71 m<br>';
  if (ud.typ === 'scianka') h += '<b>Ścianka szczelna</b> – długość ' + fmt(ud.d.dlugosc, 1) + ' m, grodzice ok. ' + fmt(DATA.gleb_grodzic,1) + ' m poniżej terenu (PG s. 10)<br>';
  h += '<table><tr><th>Etap</th><th>Rzędna [m npm]</th></tr>';
  const zz = {};
  ['ist','hum','A','B','kon'].forEach(k => {
    const rc = new THREE.Raycaster(new THREE.Vector3(x, 5000, -y), new THREE.Vector3(0,-1,0));
    const t = rc.intersectObject(POW[k].mesh, false)[0];
    if (t){ zz[k] = t.point.y / przew + ZREF; h += '<tr><td>' + NAZWY[k] + '</td><td>' + fmt(zz[k]) + '</td></tr>'; }
  });
  h += '</table>';
  if (zz.hum !== undefined){
    if (zz.ist !== undefined) h += 'Humus + nasyp: ' + fmt(zz.ist - zz.hum) + ' m<br>';
    if (zz.A !== undefined) h += 'Głębokość wykopu A: ' + fmt(Math.max(0, zz.hum - zz.A)) + ' m<br>';
    if (zz.B !== undefined) h += 'Głębokość wykopu B: ' + fmt(Math.max(0, zz.hum - zz.B)) + ' m<br>';
  }
  if (zz.kon !== undefined && zz.B !== undefined && ud.typ !== 'garaz') h += 'Od dna wykopu B do stanu końcowego: ' + fmt(Math.max(0, zz.kon - zz.B)) + ' m (z warstwami konstrukcyjnymi)';
  $('info').innerHTML = h;
});
function pokazProfil(o){
  const w = o.jestCPTU ? o.cptu : o.warstwy;
  let h = '<b>' + (o.jestCPTU ? 'Sondowanie CPTU-' : 'Otwór ') + o.nr + '</b> (DGI) – E ' + fmt(o.E,1) + ', N ' + fmt(o.N,1) + ', H = ' + fmt(o.H) + ' m npm<br>';
  if (o.woda !== null && o.woda !== undefined) h += 'Zwierciadło ustabilizowane: ' + fmt(o.woda) + ' m ppt = <b>' + fmt(o.H - o.woda) + ' m npm</b><br>';
  if (o.woda_uwagi) h += 'Woda: ' + o.woda_uwagi + '<br>';
  h += '<table><tr><th>od–do [m ppt]</th><th>rzędne [m npm]</th><th>grunt</th><th>warstwa</th></tr>';
  w.forEach(l => { const kat = l.kat === 'H' ? 'humus' : l.kat === 'N' ? 'nasyp' : (l.warstwa || ''); h += '<tr><td>' + fmt(l.strop) + '–' + fmt(l.spag) + '</td><td>' + fmt(o.H-l.strop) + '–' + fmt(o.H-l.spag) + '</td><td>' + (l.symbol || '') + (l.wilgotnosc ? ' (' + l.wilgotnosc + ')' : '') + '</td><td>' + kat + '</td></tr>'; });
  h += '</table><div class="maly">' + (o.jestCPTU ? o.cptu_zrodlo : o.zrodlo) + '</div>';
  $('info').innerHTML = h;
}

// ---------------------------------------------------------------- pętla
const v = new THREE.Vector3();
function rysujEtykiety(){
  const on = $('etyk').checked, W = kont.clientWidth, H = kont.clientHeight;
  for (const e of etykiety){
    const g = grupy[e.klucz];
    if (!on || !g || !g.visible){ e.d.style.display = 'none'; continue; }
    v.set(e.x, (e.z - ZREF) * przew, -e.y).project(camera);
    if (v.z > 1 || v.z < -1){ e.d.style.display = 'none'; continue; }
    e.d.style.display = 'block'; e.d.style.left = ((v.x+1)/2*W) + 'px'; e.d.style.top = ((1-v.y)/2*H) + 'px';
  }
}
function petla(){ requestAnimationFrame(petla); controls.update(); renderer.render(scene, camera); rysujEtykiety(); $('strzalka').style.transform = 'rotate(' + controls.getAzimuthalAngle() + 'rad)'; }
function ustawKamere(){ const W = kont.clientWidth, H = kont.clientHeight; camera.aspect = W/H; const off = W > 900 ? -Math.round($('panel').offsetWidth/2) : 0; camera.setViewOffset(W, H, off, 0, W, H); camera.updateProjectionMatrix(); renderer.setSize(W, H); }
window.addEventListener('resize', ustawKamere); ustawKamere();

// start
world.scale.y = przew; $('przewTxt').textContent = fmt(przew,1);
ustawWode(); pokoloruj(); widocznosc(); widok(-0.75, 0.75, 0.85);
$('ladowanie').style.display = 'none';
window.__model = {POW, grupy, pickable, etykiety, renderer, scene, camera, controls};   // do testów automatycznych
petla();
})();
"""


if __name__ == "__main__":
    main()

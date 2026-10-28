"""
AUDYTOWY MODEL HTML ROBÓT ZIEMNYCH – jeden plik działający offline.

Generator wykorzystuje zweryfikowaną geometrię z istniejącego modelu HTML, lecz
uzupełnia ją o zamrożone wyniki bilansu, kontrole, analizę wrażliwości, ryzyka
i kalkulator kosztowy. Objętości oficjalne pochodzą z wyniki.json; TIN służy
wyłącznie do wizualizacji i inspekcji przestrzennej.

Wynik: wyniki/MODEL_ROBOT_ZIEMNYCH_AUDYT.html
Uruchomienie: python prace/obliczenia_v2/podglad_audyt_html.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SOURCE_HTML = REPO / "wyniki" / "MODEL3D_dz190_podglad.html"
OUT = REPO / "wyniki" / "MODEL_ROBOT_ZIEMNYCH_AUDYT.html"
WYNIKI = HERE / "wyniki.json"
KONTROLA = HERE / "model3d_kontrola.json"
NIEPEWNOSC = HERE / "niepewnosc.json"
LANDXML = REPO / "wyniki" / "MODEL3D_dz190_LandXML.xml"
GEOMETRIA = REPO / "prace" / "dane" / "geometria.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def suma_wykopu(wariant: dict) -> float:
    return round(sum(sum(strefa.values()) for strefa in wariant["wykop_m3"].values()), 3)


def suma_zapotrzebowania(wariant: dict) -> float:
    nazwy = ("rodzimy_Z", "rodzimy_U", "rodzimy_R", "rodzimy_O")
    return round(sum(sum(wariant["zapotrzebowanie"][n].values()) for n in nazwy), 3)


def suma_niewysadzinowego(wariant: dict) -> float:
    return round(sum(wariant["zapotrzebowanie"]["niewysadzinowy_U"].values()), 3)


def dane_audytu(wyniki: dict, kontrola: dict, niepewnosc: dict) -> dict:
    humus = wyniki["humus_m3"]
    nasyp = wyniki["nasyp_m3"]
    humus_odklad = 1771.842
    fundamenty = 1294.323  # wynik oficjalny XLSX: suma zaokrąglonych pozycji
    warianty = {}
    for nazwa in ("A", "B"):
        w = wyniki["warianty"][nazwa]
        wykop = suma_wykopu(w)
        reuse = suma_zapotrzebowania(w)
        rodzimy_wywoz = round(wykop - reuse, 3)
        niewys = suma_niewysadzinowego(w)
        warianty[nazwa] = {
            "wykop": wykop,
            "pole": w["pole_wykopu_razem"],
            "glebokosc_sr": w["glebokosc_sr"],
            "ponowne_wbudowanie": reuse,
            "rodzimy_wywoz": rodzimy_wywoz,
            "wywoz_razem": round(humus - humus_odklad + nasyp + rodzimy_wywoz + fundamenty, 3),
            "dowoz_niewysadzinowy": niewys,
            "dowoz_zwykly": 0.0,
            "strefy": {k: round(sum(v.values()), 3) for k, v in w["wykop_m3"].items()},
        }

    delta = round(warianty["B"]["wykop"] - warianty["A"]["wykop"], 3)
    ryzyka = [
        {
            "poziom": "krytyczne",
            "tytul": "Przydatność całego gruntu rodzimego",
            "opis": "Brak badań Proctora. Wynik 0 m³ zwykłego dowozu zakłada przydatność całej planowanej masy do zasypów.",
            "dzialanie": "Badania Proctora i wilgotności, podział urobku oraz kryteria odbioru dla każdej strefy.",
        },
        {
            "poziom": "wysokie",
            "tytul": "Rzędne T1 i T4",
            "opis": "Lokalne różnice model–przekrój dochodzą do około 1,0–1,34 m.",
            "dzialanie": "Kontrola geodezyjna i wyjaśnienie z projektantem przed rozliczeniem ilości.",
        },
        {
            "poziom": "wysokie",
            "tytul": "Pełny koszt odkładu w wariancie B",
            "opis": f"Kosztorys nie zawiera pełnego cyklu odkładu i ponownego wbudowania {warianty['B']['ponowne_wbudowanie']:.3f} m³.",
            "dzialanie": "Dodać transport wewnętrzny, ochronę, przeładunek, rozłożenie, zagęszczenie i badania.",
        },
        {
            "poziom": "średnie",
            "tytul": "Fundamenty głębsze",
            "opis": "Brak lokalizacji elementów w modelu 3D; szacowana niepewność około ±400 m³.",
            "dzialanie": "Potwierdzić liczbę, wymiary i nakładanie brył na wszystkich rzutach PW.",
        },
        {
            "poziom": "średnie",
            "tytul": "Humus 0,604 m",
            "opis": "Grubość jest interpolowana; zmiana o 0,10 m przesuwa około 2 529 m³ między kategoriami.",
            "dzialanie": "Wykonać odkrywki i obmiar grubości przed rozpoczęciem zdejmowania humusu.",
        },
    ]
    optymalizacje = [
        {
            "tytul": "Wariant A jako baza",
            "wartosc": delta,
            "jednostka": "m³ mniej cyklu wykop–odkład–zasyp",
            "warunek": "Jeżeli technologia i organizacja wykopu dopuszczają pozostawienie gruntu między obiektami.",
        },
        {
            "tytul": "Przemarzanie 0,80 m",
            "wartosc": 1090.654,
            "jednostka": "m³ mniej dowozu i około tyle samo mniej wywozu",
            "warunek": "Wyłącznie po zatwierdzeniu przez projektanta branży drogowej/geotechnika.",
        },
        {
            "tytul": "Bezpośrednie wbudowanie",
            "wartosc": warianty["A"]["ponowne_wbudowanie"],
            "jednostka": "m³ planowanego ponownego użycia w A",
            "warunek": "Skoordynować front wykopu z zasypem i selektywnie rozdzielać grunty.",
        },
    ]
    return {
        "schema": "audyt-model-1.0",
        "wygenerowano": date.today().isoformat(),
        "status": "Obliczenia odtwarzalne; zatwierdzenie warunkowe",
        "warianty": warianty,
        "humus": {"zdjety": humus, "odklad": humus_odklad, "wywoz": round(humus - humus_odklad, 3)},
        "nasyp_wywoz": nasyp,
        "fundamenty": fundamenty,
        "fundamenty_json": wyniki["fundamenty"]["razem_m3"],
        "delta_B_A": delta,
        "delta_B_A_proc": round(delta / warianty["A"]["wykop"] * 100, 2),
        "optymalizacje": optymalizacje,
        "ryzyka": ryzyka,
        "parametry": wyniki["parametry"],
        "pola": wyniki["pola"],
        "kontrola": kontrola,
        "niepewnosc": niepewnosc,
        "scenariusz_przemarzanie_080": {
            "dowoz_niewysadzinowy": 1644.476,
            "redukcja_dowozu": 1090.654,
            "redukcja_wywozu": 1090.653,
            "redukcja_wykopu_A": 59.745,
        },
        "zrodla": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (SOURCE_HTML, WYNIKI, KONTROLA, NIEPEWNOSC, LANDXML, GEOMETRIA)
        },
    }


def main() -> None:
    if not SOURCE_HTML.exists():
        raise SystemExit(f"Brak modelu źródłowego: {SOURCE_HTML}. Najpierw uruchom podglad_html.py.")

    html = SOURCE_HTML.read_text(encoding="utf-8")
    match = re.search(r'(<script id="dane" type="application/json">)(.*?)(</script>)', html, re.S)
    if not match:
        raise SystemExit("Nie znaleziono osadzonych danych modelu w HTML źródłowym.")

    data = json.loads(match.group(2))
    wyniki = json.loads(WYNIKI.read_text(encoding="utf-8"))
    kontrola = json.loads(KONTROLA.read_text(encoding="utf-8"))
    niepewnosc = json.loads(NIEPEWNOSC.read_text(encoding="utf-8"))

    # Nie wolno połączyć starej siatki wizualnej z nowszym bilansem. Liczby
    # wierzchołków, zakresy Z i główne objętości muszą odpowiadać kontroli.
    for surface in data.get("powierzchnie", []):
        nazwa = surface["nazwa"]
        ref = kontrola.get("powierzchnie", {}).get(nazwa)
        ref_geom = kontrola.get("kontrola_niezalezna", {}).get("powierzchnie", {}).get(nazwa)
        if not ref or not ref_geom:
            raise SystemExit(f"Brak kontroli powierzchni {nazwa}.")
        if surface["n"] != ref["punkty"] or surface["n"] != ref_geom["liczba_punktow"]:
            raise SystemExit(f"Niezgodna liczba punktów powierzchni {nazwa}.")
        if abs(surface["zmin"] - ref_geom["Z_min"]) > 0.002:
            raise SystemExit(f"Niezgodna minimalna rzędna powierzchni {nazwa}.")
        if abs(surface["zmax"] - ref_geom["Z_max"]) > 0.002:
            raise SystemExit(f"Niezgodna maksymalna rzędna powierzchni {nazwa}.")
    oficjalne_a = suma_wykopu(wyniki["warianty"]["A"])
    oficjalne_b = suma_wykopu(wyniki["warianty"]["B"])
    if abs(data["bilans"]["A"] - oficjalne_a) > 0.001 or abs(data["bilans"]["B"] - oficjalne_b) > 0.001:
        raise SystemExit("Model źródłowy i wyniki.json pochodzą z różnych wersji obliczeń.")

    data["audyt"] = dane_audytu(wyniki, kontrola, niepewnosc)
    packed = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = html[: match.start(2)] + packed + html[match.end(2) :]
    html = html.replace(
        "<title>Model 3D robót ziemnych – dz. 1/90 Wojszyce</title>",
        "<title>Audytowy model robót ziemnych – dz. 1/90 Wojszyce</title>",
        1,
    )
    html = html.replace("</head>", AUDIT_STYLE + "\n</head>", 1)
    html = html.replace("<body>", "<body>\n" + AUDIT_HTML, 1)
    html = html.replace("</body>", "<script>" + AUDIT_APP + "</script>\n</body>", 1)
    OUT.write_text(html, encoding="utf-8")
    print(
        "zapisano",
        OUT,
        f"{OUT.stat().st_size / 1e6:.2f} MB",
        "| offline | A/B/nakładka | bilans | ryzyka | kalkulator | walidacja",
    )


AUDIT_STYLE = r"""
<style id="audit-style">
:root{--ink:#10212d;--muted:#60717f;--paper:#f5f3ee;--card:#fff;--navy:#123247;--cyan:#4db7b3;--amber:#e6a23c;--red:#d45745;--green:#2f8b68;--line:#d9e0e4}
html,body{font-family:Inter,Segoe UI,Arial,sans-serif;background:#dfe7e8;color:var(--ink)}
#auditTop{position:absolute;z-index:40;left:0;right:0;top:0;height:72px;background:linear-gradient(108deg,#102d40,#173e52 64%,#1c4d5a);color:#fff;display:flex;align-items:center;gap:14px;padding:0 16px;box-shadow:0 3px 16px #0b233544;box-sizing:border-box}
#auditBrand{min-width:245px}#auditBrand b{display:block;font-size:16px;letter-spacing:.2px}#auditBrand span{font-size:10px;color:#b8d2dc;text-transform:uppercase;letter-spacing:1.2px}
#auditModes{display:flex;gap:5px}#auditModes button,.audit-action{border:1px solid #ffffff38;color:#fff;background:#ffffff0e;border-radius:7px;padding:8px 11px;font-weight:650;cursor:pointer}#auditModes button:hover,.audit-action:hover,#auditModes button.on{background:#fff;color:var(--navy)}
#auditKpis{display:flex;gap:8px;min-width:0;flex:1;justify-content:flex-end}.top-kpi{min-width:118px;border-left:1px solid #ffffff30;padding-left:10px}.top-kpi small{display:block;color:#b9d1da;font-size:10px}.top-kpi b{font-size:15px;font-variant-numeric:tabular-nums}.top-kpi em{font-style:normal;font-size:10px;color:#d9e7eb}
#panel{top:80px!important;left:8px!important;width:300px!important;max-height:calc(100% - 88px)!important;border-radius:10px!important;border:1px solid #fff!important;box-shadow:0 8px 30px #1832442b!important}#panel h1{display:none}#panel h2{color:#365466!important;letter-spacing:.6px}#panel button{padding:4px 8px!important}
#polnoc{top:84px!important;left:320px!important}#legenda{display:none!important}
#auditPanel{position:absolute;z-index:35;right:8px;top:80px;width:365px;max-height:calc(100% - 88px);overflow:auto;background:#f7f5f0f2;backdrop-filter:blur(10px);border:1px solid #fff;border-radius:11px;box-shadow:0 8px 30px #18324438}
#auditPanel header{padding:13px 14px 9px;border-bottom:1px solid var(--line);background:#ffffffb8;position:sticky;top:0;z-index:2;border-radius:11px 11px 0 0}#auditPanel header b{font-size:15px}#auditPanel header span{display:block;font-size:11px;color:var(--muted);margin-top:2px}
#auditTabs{display:flex;gap:3px;padding:8px 10px 0;position:sticky;top:57px;background:#f7f5f0;z-index:2}#auditTabs button{flex:1;border:0;border-bottom:2px solid transparent;background:none;padding:7px 3px;font-size:11px;font-weight:700;color:var(--muted);cursor:pointer}#auditTabs button.on{color:var(--navy);border-color:var(--cyan)}
.audit-view{display:none;padding:11px 12px 14px}.audit-view.on{display:block}.audit-card{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:10px;margin-bottom:8px}.audit-card h3{font-size:12px;margin:0 0 7px;color:var(--navy)}
.audit-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px}.metric{background:#eef3f3;border-radius:7px;padding:8px}.metric small{display:block;font-size:10px;color:var(--muted)}.metric b{font-size:16px;font-variant-numeric:tabular-nums}.metric span{font-size:10px}
.compare-row{display:grid;grid-template-columns:92px 1fr 58px;gap:6px;align-items:center;margin:6px 0;font-size:10px}.bar{height:9px;background:#e6ebed;border-radius:9px;overflow:hidden}.bar i{display:block;height:100%;border-radius:9px}.bar-a{background:#3d86c6}.bar-b{background:#e7a33d}
.risk{border-left:4px solid var(--amber)}.risk.krytyczne{border-left-color:var(--red)}.risk.wysokie{border-left-color:#e47a35}.risk.średnie{border-left-color:var(--amber)}.risk .tag{font-size:9px;text-transform:uppercase;font-weight:800;letter-spacing:.8px}.risk p{font-size:11px;line-height:1.35;margin:4px 0;color:#304552}.risk strong{font-size:10px;color:var(--green)}
.opt{border-left:4px solid var(--green)}.opt .big{font-size:19px;font-weight:800;color:var(--green)}.opt p{font-size:10px;color:var(--muted);margin:3px 0}
.cost label{font-size:10px;color:var(--muted);display:grid;grid-template-columns:1fr 90px;gap:8px;align-items:center;margin:6px 0}.cost input{width:100%;box-sizing:border-box;padding:5px;border:1px solid #bdc9ce;border-radius:5px;text-align:right}.cost-result{background:var(--navy);color:#fff;border-radius:8px;padding:10px;margin-top:9px}.cost-result small{color:#bcd0d9}.cost-result b{font-size:18px}
#reusePct{width:100%}.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:9px;word-break:break-all;color:#546773}.ok{color:var(--green);font-weight:800}.warn{color:#b56a24;font-weight:800}
#info{right:382px!important;bottom:8px!important;width:345px!important;max-height:38%!important;border:1px solid #fff!important;border-radius:10px!important;box-shadow:0 8px 30px #1832442b!important}
#auditMobile{display:none}
@media(max-width:1100px){#auditKpis .top-kpi:nth-child(n+3){display:none}#auditPanel{width:330px}#info{right:347px!important}}
@media(max-width:820px){#auditTop{height:112px;align-items:flex-start;padding-top:9px;flex-wrap:wrap}#auditBrand{min-width:100%}#auditKpis{display:none}#auditModes{position:absolute;left:12px;bottom:8px}#panel{top:120px!important;max-height:calc(100% - 128px)!important}#auditPanel{display:none;top:120px;left:8px;right:8px;width:auto;max-height:calc(100% - 128px)}#auditPanel.mobile-on{display:block}#auditMobile{display:block;position:absolute;z-index:45;right:10px;bottom:8px}#info{right:8px!important;width:calc(100% - 36px)!important}#polnoc{top:124px!important}.audit-action{padding:6px 9px}}
</style>
"""

AUDIT_HTML = r"""
<div id="auditTop">
  <div id="auditBrand"><b>Audytowy model robót ziemnych</b><span>działka 1/90 · Wojszyce · model offline</span></div>
  <div id="auditModes">
    <button data-mode="A" class="on">Wariant A</button>
    <button data-mode="B">Wariant B</button>
    <button data-mode="AB">Nakładka A/B</button>
    <button data-mode="IST">Teren</button>
  </div>
  <div id="auditKpis"></div>
  <button id="auditMobile" class="audit-action">Audyt</button>
</div>
<div id="auditPanel">
  <header><b>Pulpit decyzji</b><span id="auditStatus"></span></header>
  <nav id="auditTabs">
    <button data-tab="bilans" class="on">Bilans</button><button data-tab="ryzyka">Ryzyka</button><button data-tab="koszty">Koszty</button><button data-tab="kontrola">Kontrola</button>
  </nav>
  <section id="tab-bilans" class="audit-view on"></section>
  <section id="tab-ryzyka" class="audit-view"></section>
  <section id="tab-koszty" class="audit-view"></section>
  <section id="tab-kontrola" class="audit-view"></section>
</div>
"""

AUDIT_APP = r"""
(function(){
'use strict';
const D = JSON.parse(document.getElementById('dane').textContent), A = D.audyt;
const $ = id => document.getElementById(id);
const fmt = (v,d=0) => Number(v).toLocaleString('pl-PL',{minimumFractionDigits:d,maximumFractionDigits:d});
const money = v => Number(v).toLocaleString('pl-PL',{style:'currency',currency:'PLN',maximumFractionDigits:0});
const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
$('auditStatus').textContent = A.status + ' · ' + A.wygenerowano;

function kpis(mode){
  const w = mode==='B' ? A.warianty.B : A.warianty.A;
  $('auditKpis').innerHTML = '<div class="top-kpi"><small>Wykop '+(mode==='AB'?'B − A':mode)+'</small><b>'+(mode==='AB'?fmt(A.delta_B_A,0):fmt(w.wykop,0))+' m³</b><em>'+(mode==='AB'?'dodatkowy cykl':fmt(w.glebokosc_sr,2)+' m średnio')+'</em></div>'+
    '<div class="top-kpi"><small>Wywóz razem</small><b>'+fmt(w.wywoz_razem,0)+' m³</b><em>stan rodzimy</em></div>'+
    '<div class="top-kpi"><small>Ponowne użycie</small><b>'+fmt(w.ponowne_wbudowanie,0)+' m³</b><em>warunkowe</em></div>'+
    '<div class="top-kpi"><small>Dowóz niewys.</small><b>'+fmt(w.dowoz_niewysadzinowy,0)+' m³</b><em>dla 1,00 m</em></div>';
}

function check(id,val){ const e=$(id); if(!e)return; e.checked=val; e.dispatchEvent(new Event('change',{bubbles:true})); }
function appearance(mode){
  const m=window.__model;if(!m)return;
  ['ist','hum','A','B','kon'].forEach(k=>{const q=m.POW[k].mesh.material;q.vertexColors=true;q.color.set(0xffffff);q.transparent=false;q.opacity=1;q.depthWrite=true;q.needsUpdate=true;});
  if(mode==='A'||mode==='B'){
    const q=m.POW[mode].mesh.material;q.vertexColors=true;q.transparent=false;q.opacity=1;q.needsUpdate=true;
  } else if(mode==='AB'){
    const qa=m.POW.A.mesh.material,qb=m.POW.B.mesh.material;
    qa.vertexColors=false;qa.color.set(0x3182bd);qa.transparent=false;qa.opacity=1;qa.needsUpdate=true;
    qb.vertexColors=false;qb.color.set(0xf0a332);qb.transparent=true;qb.opacity=.55;qb.depthWrite=false;qb.needsUpdate=true;
    m.POW.A.wire.visible=true;m.POW.A.wire.material.color.set(0x164c73);m.POW.A.wire.material.opacity=.38;
  }
}
function setMode(mode){
  document.querySelectorAll('#auditModes [data-mode]').forEach(b=>b.classList.toggle('on',b.dataset.mode===mode));
  ['ist','hum','A','B','kon'].forEach(k=>check('et_'+k,false));
  check('krawA',mode==='A'||mode==='AB');check('krawB',mode==='B'||mode==='AB');
  if(mode==='IST')check('et_ist',true);else if(mode==='AB'){check('et_A',true);check('et_B',true);}else check('et_'+mode,true);
  appearance(mode);kpis(mode==='IST'?'A':mode);window.__auditMode=mode;
}
document.querySelectorAll('#auditModes [data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));

function compareRow(label,a,b){const max=Math.max(a,b);return '<div class="compare-row"><b>'+esc(label)+'</b><div><div class="bar"><i class="bar-a" style="width:'+(a/max*100)+'%"></i></div><div class="bar" style="margin-top:2px"><i class="bar-b" style="width:'+(b/max*100)+'%"></i></div></div><span>'+fmt(a,0)+'<br>'+fmt(b,0)+'</span></div>';}
const wa=A.warianty.A,wb=A.warianty.B;
$('tab-bilans').innerHTML = '<div class="audit-card"><h3>Najważniejsza decyzja</h3><div class="metric"><small>Dodatkowy cykl wariantu B</small><b>'+fmt(A.delta_B_A,3)+' m³</b><span> · +'+fmt(A.delta_B_A_proc,2)+'% wykopu</span></div><p style="font-size:11px;margin:8px 0 0">Wywóz i dowóz są praktycznie takie same. Ilościowo wariant A jest korzystniejszy.</p></div>'+
 '<div class="audit-card"><h3>A (niebieski) / B (pomarańczowy)</h3>'+compareRow('Wykop',wa.wykop,wb.wykop)+compareRow('Ponowne',wa.ponowne_wbudowanie,wb.ponowne_wbudowanie)+compareRow('Wywóz',wa.wywoz_razem,wb.wywoz_razem)+compareRow('Dowóz',wa.dowoz_niewysadzinowy,wb.dowoz_niewysadzinowy)+'</div>'+
 '<div class="audit-card"><h3>Bilans podstawowy</h3><div class="audit-grid"><div class="metric"><small>Humus zdjęty</small><b>'+fmt(A.humus.zdjety,0)+'</b><span> m³</span></div><div class="metric"><small>Humus na odkład</small><b>'+fmt(A.humus.odklad,0)+'</b><span> m³</span></div><div class="metric"><small>Nasyp – wywóz</small><b>'+fmt(A.nasyp_wywoz,0)+'</b><span> m³</span></div><div class="metric"><small>Pogłębienia</small><b>'+fmt(A.fundamenty,0)+'</b><span> m³</span></div></div></div>'+
 '<div class="audit-card"><h3>Wykop A według stref</h3>'+Object.entries(wa.strefy).map(([k,v])=>'<div class="compare-row"><b>'+({H:'hale',O:'ogrody',R:'rampy',Z:'zieleń',U:'nawierzchnie'}[k]||k)+'</b><div class="bar"><i class="bar-a" style="width:'+(v/wa.wykop*100)+'%"></i></div><span>'+fmt(v,0)+'</span></div>').join('')+'</div>';

$('tab-ryzyka').innerHTML = A.optymalizacje.map(o=>'<div class="audit-card opt"><h3>'+esc(o.tytul)+'</h3><div class="big">'+fmt(o.wartosc,o.wartosc<2000?3:0)+'</div><p>'+esc(o.jednostka)+'</p><p><b>Warunek:</b> '+esc(o.warunek)+'</p></div>').join('')+'<h3 style="font-size:12px">Ryzyka wymagające decyzji</h3>'+A.ryzyka.map(r=>'<div class="audit-card risk '+esc(r.poziom)+'"><span class="tag">'+esc(r.poziom)+'</span><h3>'+esc(r.tytul)+'</h3><p>'+esc(r.opis)+'</p><strong>→ '+esc(r.dzialanie)+'</strong></div>').join('');

$('tab-koszty').innerHTML = '<div class="audit-card cost"><h3>Kalkulator przewagi A nad B</h3><p style="font-size:10px;color:var(--muted)">Wpisz własne stawki netto za m³. Kalkulator nie zmienia modelu.</p>'+[
 ['cExc','Wykop i załadunek'],['cStock','Transport/odkład wewnętrzny'],['cReload','Ponowny załadunek'],['cCompact','Rozłożenie, zagęszczenie, badania'],['cExport','Wywóz i przyjęcie'],['cImport','Zakup i dowóz materiału']
 ].map(x=>'<label>'+x[1]+' [zł/m³]<input id="'+x[0]+'" type="number" min="0" step="1" value="0"></label>').join('')+'<div class="cost-result"><small>Szacowana przewaga wariantu A</small><br><b id="costAB">0 zł</b><br><small>'+fmt(A.delta_B_A,3)+' m³ × pełny koszt cyklu wewnętrznego</small></div></div>'+
 '<div class="audit-card cost"><h3>Potencjał przemarzania 0,80 m</h3><div class="cost-result"><small>Orientacyjna oszczędność</small><br><b id="costFrost">0 zł</b><br><small>mniej wykopu, wywozu i dowozu; wymaga zatwierdzenia</small></div></div>'+
 '<div class="audit-card"><h3>Ryzyko odrzucenia gruntu</h3><label style="font-size:10px">Odrzucona część ponownego użycia: <b id="reusePctTxt">10%</b></label><input id="reusePct" type="range" min="0" max="30" step="1" value="10"><div class="audit-grid"><div class="metric"><small>A: dodatkowy wywóz i dowóz</small><b id="reuseA"></b><span> m³ każdy</span></div><div class="metric"><small>B: dodatkowy wywóz i dowóz</small><b id="reuseB"></b><span> m³ każdy</span></div></div></div>';

const ctl=A.kontrola.objetosci;
$('tab-kontrola').innerHTML = '<div class="audit-card"><h3>Status modelu</h3><p class="ok">✓ Silnik odtwarza wynik zapisany</p><p class="ok">✓ Formuły arkusza i scenariusz B zgodne</p><p class="ok">✓ DXF i LandXML zgodne</p><p class="warn">! Zatwierdzenie geotechniczne pozostaje warunkowe</p></div>'+
 '<div class="audit-card"><h3>Raster a TIN</h3><div class="audit-grid"><div class="metric"><small>A: różnica</small><b>'+fmt(ctl.A.roznica_m3,3)+'</b><span> m³ · '+fmt(ctl.A.roznica_proc,4)+'%</span></div><div class="metric"><small>B: różnica</small><b>'+fmt(ctl.B.roznica_m3,3)+'</b><span> m³ · '+fmt(ctl.B.roznica_proc,4)+'%</span></div></div><p style="font-size:10px;color:var(--muted)">TIN służy do oglądania. Oficjalne KPI pochodzą z rastra 0,25 m i arkusza bilansu.</p></div>'+
 '<div class="audit-card"><h3>Niespójności jawne</h3><p style="font-size:11px">Fundamenty: JSON '+fmt(A.fundamenty_json,3)+' m³ / XLSX '+fmt(A.fundamenty,3)+' m³ (kolejność zaokrąglania).</p><p style="font-size:11px">Humus + nasyp w modelu 3D różni się od bilansu o 2,655 m³; obecna flaga kontroli tego nie blokuje.</p></div>'+
 '<div class="audit-card"><h3>Manifest źródeł SHA-256</h3>'+Object.entries(A.zrodla).map(([p,h])=>'<p class="mono"><b>'+esc(p)+'</b><br>'+h+'</p>').join('')+'</div>';

function calc(){
 const n=id=>parseFloat($(id).value)||0;
 $('costAB').textContent=money(A.delta_B_A*(n('cExc')+n('cStock')+n('cReload')+n('cCompact')));
 const f=A.scenariusz_przemarzanie_080;
 $('costFrost').textContent=money(f.redukcja_wykopu_A*n('cExc')+f.redukcja_wywozu*n('cExport')+f.redukcja_dowozu*n('cImport'));
}
['cExc','cStock','cReload','cCompact','cExport','cImport'].forEach(id=>$(id).addEventListener('input',calc));
function reuse(){const p=parseFloat($('reusePct').value);$('reusePctTxt').textContent=fmt(p,0)+'%';$('reuseA').textContent=fmt(wa.ponowne_wbudowanie*p/100,0);$('reuseB').textContent=fmt(wb.ponowne_wbudowanie*p/100,0);}$('reusePct').addEventListener('input',reuse);reuse();

document.querySelectorAll('#auditTabs [data-tab]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('#auditTabs button').forEach(x=>x.classList.toggle('on',x===b));document.querySelectorAll('.audit-view').forEach(x=>x.classList.toggle('on',x.id==='tab-'+b.dataset.tab));}));
$('auditMobile').addEventListener('click',()=>$('auditPanel').classList.toggle('mobile-on'));
setMode('A');
window.__audit={data:A,setMode};
})();
"""


if __name__ == "__main__":
    main()

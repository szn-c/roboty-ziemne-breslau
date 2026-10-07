// Odczyt pliku DWG (AutoCAD/GstarCAD) do zwyklego JSON - bez AutoCAD. Python (ezdxf) nie czyta DWG.
// Uzycie (w sandboxie NODE_OPTIONS jest uszkodzone, wiec go wylaczamy):
//   cd prace/obliczenia_v1/_skrypt/odczyt_dwg
//   env -u NODE_OPTIONS npm install --no-audit --no-fund
//   env -u NODE_OPTIONS node odczyt_dwg.mjs plik.dwg wyjscie.json [warstwa1,warstwa2,...]
// Wynik: warstwy z liczba obiektow, polilinie (wierzcholki E,N), okregi, punkty i teksty z wybranych warstw.
// Uwaga: plik z rozszerzeniem .dxf moze byc w rzeczywistosci DWG (pierwsze bajty "AC10..."). Sprawdz: head -c 6 plik
import { LibreDwg, Dwg_File_Type } from '@mlightcad/libredwg-web';
import fs from 'fs';
const [,, wejscie, wyjscie, warstwyTekst] = process.argv;
if (!wejscie || !wyjscie) { console.error('uzycie: node odczyt_dwg.mjs plik.dwg wyjscie.json [warstwy,po,przecinku]'); process.exit(2); }
const wybrane = warstwyTekst ? new Set(warstwyTekst.split(',')) : null;
const buf = fs.readFileSync(wejscie);
const lib = await LibreDwg.create();
const data = lib.dwg_read_data(new Uint8Array(buf).buffer, Dwg_File_Type.DWG);
if (!data) { console.error('nie udalo sie odczytac pliku'); process.exit(1); }
const db = lib.convert(data);
const ents = db.entities || [];
const warstwy = {};
for (const e of ents) { const w = e.layer || '?'; warstwy[w] = warstwy[w] || {}; warstwy[w][e.type] = (warstwy[w][e.type] || 0) + 1; }
const ok = e => !wybrane || wybrane.has(e.layer);
const wynik = {
  plik: wejscie, obiektow: ents.length, warstwy,
  polilinie: ents.filter(e => e.type === 'LWPOLYLINE' && ok(e)).map(e => ({ warstwa: e.layer, zamknieta: !!((e.flag || 0) & 1), wierzcholki: (e.vertices || []).map(v => [v.x, v.y]) })),
  okregi: ents.filter(e => e.type === 'CIRCLE' && ok(e)).map(e => ({ warstwa: e.layer, srodek: [e.center.x, e.center.y], promien: e.radius })),
  punkty: ents.filter(e => e.type === 'POINT' && ok(e)).map(e => ({ warstwa: e.layer, xyz: [e.position.x, e.position.y, e.position.z] })),
  teksty: ents.filter(e => e.type === 'TEXT' && ok(e)).map(e => ({ warstwa: e.layer, tekst: e.text, xy: [e.startPoint.x, e.startPoint.y] })),
};
fs.writeFileSync(wyjscie, JSON.stringify(wynik, null, 1));
console.log('zapisano', wyjscie, '| obiektow', ents.length, '| warstw', Object.keys(warstwy).length);
lib.dwg_free(data);

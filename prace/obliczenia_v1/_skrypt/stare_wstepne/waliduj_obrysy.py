"""Walidacja obrysow przekazanych przez uzytkownika (scianka + 8 hal).

Sprawdza: pola, obwody, czy hale sa wewnatrz scianki, odleglosci miedzy halami,
zgodnosc z polami stref pozarowych z rzutu, poprawnosc geometrii.
Wynik drukowany zwiezle (zeby nie byl obciety).
"""
import itertools
from shapely.geometry import Polygon
from dane_uzytkownika import SCIANKA_UZ, HALE_UZ, STREFY_POZ

sc = Polygon(SCIANKA_UZ)
print("=== SCIANKA ===")
print(f"poprawny: {sc.is_valid}   pole = {sc.area:9.1f} m2   obwod = {sc.length:7.1f} m")

print("\n=== HALE (pole z obrysu vs pole strefy pozarowej z rzutu) ===")
hale = {}
for nr, pts in HALE_UZ.items():
    p = Polygon(pts)
    hale[nr] = p
    sp = STREFY_POZ.get(nr)
    sp_txt = f"{sp:8.2f}" if sp else "   brak "
    ratio = f"{p.area / sp:5.3f}" if sp else "  -  "
    wew = sc.contains(p)
    dist = sc.exterior.distance(p)
    print(f"hala {nr}: poprawna={p.is_valid!s:5}  pole={p.area:8.2f}  strefa={sp_txt}  stosunek={ratio}  "
          f"w scianie={wew!s:5}  odl. do scianki={dist:5.2f} m")

print("\n=== SUMA ===")
suma = sum(p.area for p in hale.values())
print(f"suma pol 8 hal = {suma:.1f} m2   (udzial w polu scianki: {100*suma/sc.area:.1f}%)")

print("\n=== ODLEGLOSCI MIEDZY HALAMI (<= 15 m) ===")
for a, b in itertools.combinations(hale, 2):
    d = hale[a].distance(hale[b])
    if d <= 15:
        print(f"hala {a} - hala {b}: {d:6.2f} m")

print("\n=== NAKLADANIE SIE HAL ===")
bylo = False
for a, b in itertools.combinations(hale, 2):
    inter = hale[a].intersection(hale[b]).area
    if inter > 0.01:
        bylo = True
        print(f"UWAGA: hala {a} nachodzi na hale {b} o {inter:.2f} m2")
if not bylo:
    print("brak nakladania")

print("\n=== WYMIARY HAL (bok1 x bok2) ===")
for nr, pts in HALE_UZ.items():
    import math
    d = [math.dist(pts[i], pts[(i + 1) % 4]) for i in range(4)]
    print(f"hala {nr}: boki = {d[0]:.2f}, {d[1]:.2f}, {d[2]:.2f}, {d[3]:.2f} m")

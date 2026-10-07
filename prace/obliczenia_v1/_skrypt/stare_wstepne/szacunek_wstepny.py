"""Wstepny szacunek objetosci wykopu pod 8 garazy (na podstawie rzutu 'Schemat zbiorczy garazy' i przekroju 2C).
To tylko kontrola rzedu wielkosci - wlasciwe liczby da model w Civil 3D."""
import math
hale = {1: 1390.0, 2: 1096.72, 3: 1392.35, 4: 1474.97, 5: 1390.71, 6: 1390.55, 7: 1390.55, 8: 1475.33}  # m2 strefy pozarowej; hala 1 = zalozone (na rzucie 0,00)
TEREN = 124.65          # srednia rzedna istn. terenu z 17 otworow
DNO = 122.57 - 0.50 - 0.10   # posadzka - plyta 0,50 - chudy beton 0,10
HUM, NAS = 0.63, 0.03   # srednia grubosc humusu i nasypu [m]
PIASEK = 0.20           # udzial piaskow w gruncie pod humusem (srednia z otworow dla dna ~121,9)
ASPEKT = 1.5            # stosunek dluzszego do krotszego boku hali (zalozenie)
def licz(offset, skarpa):
    d = TEREN - DNO
    sum_dol = sum_gora = V = 0
    for A in hale.values():
        b = math.sqrt(A / ASPEKT); a = ASPEKT * b
        ab = (a + 2 * offset) * (b + 2 * offset)
        s = skarpa * d
        at = (a + 2 * offset + 2 * s) * (b + 2 * offset + 2 * s)
        am = (a + 2 * offset + s) * (b + 2 * offset + s)
        V += d / 6 * (ab + 4 * am + at)
        sum_dol += ab; sum_gora += at
    return d, sum_dol, sum_gora, V
print("Suma stref pozarowych (hala 1 zalozona 1390):", round(sum(hale.values())), "m2")
for nazwa, off, sk in [("A: obudowa pionowa, offset 1,25 m od wnetrza", 1.25, 0), ("B: skarpy 1:1, offset 1,25 m", 1.25, 1.0), ("C: skarpy 1:1,5, offset 1,25 m", 1.25, 1.5)]:
    d, ad, ag, V = licz(off, sk)
    hum = (HUM + NAS) * ag
    czysty = V - hum
    print(f"{nazwa}\n  glebokosc {d:.2f} m | pole dna {ad:,.0f} m2 | pole gory {ag:,.0f} m2 | wykop razem {V:,.0f} m3 | w tym humus+nasyp {hum:,.0f} | grunt pod humusem {czysty:,.0f} | w tym piaski ok. {czysty*PIASEK:,.0f} | gliny ok. {czysty*(1-PIASEK):,.0f}")
print("Czulosc: kazde 10 cm glebokosci =", round(0.1 * sum(hale.values()) * 1.15), "m3 (ok.)")

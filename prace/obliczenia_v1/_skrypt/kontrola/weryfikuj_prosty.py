"""Kontrola uproszczonego arkusza: (1) wartosci zapisane w pliku (jak w podgladzie) = kod w Pythonie,
(2) formuly przeliczone od nowa niezaleznym silnikiem = wartosci zapisane, (3) sumy w tabeli dodaja sie dokladnie."""
import os, sys, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from openpyxl import load_workbook
from bilans_prosty import oblicz, dane_zaokraglone
from generuj_wynik_prosty_xlsx import policz_formuly, GLOWNY
D = dane_zaokraglone()
o, v = oblicz(D)
V = load_workbook(GLOWNY, data_only=True)
F = load_workbook(GLOWNY)
ws = V['WYNIK']
mapa = {7:'h_odkl',8:'h_wyw',9:'h_razem',10:'nas',12:'d',13:'m_odkl',14:'m_nadw',15:'m_razem',17:'odkl',18:'wyw',19:'wyw_luzem',20:'wyw_tony',21:'odkl_luzem',22:'brak'}
bad = 0
for r, k in mapa.items():
    x = ws[f'B{r}'].value
    if x is None or abs(x - v[k]) > 0.5:
        bad += 1; print('ROZNICA (zapisane vs Python)', r, k, x, v[k])
print('1) zapisane wartosci vs kod Python: rozbieznosci =', bad)
wart = policz_formuly(GLOWNY)
bad2 = 0; n = 0
for sh in F.sheetnames:
    for row in F[sh].iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('='):
                n += 1
                sv = V[sh][c.coordinate].value; fv = wart.get((sh.upper(), c.coordinate))
                if sv is None or fv is None or abs(sv - fv) > 1e-6 * max(1, abs(fv)):
                    bad2 += 1; print('ROZNICA (zapisane vs przeliczone)', sh, c.coordinate, sv, fv)
print('2) formul sprawdzonych:', n, ' rozbieznosci =', bad2)
g = lambda r: ws[f'B{r}'].value
assert g(9) == g(7) + g(8) and g(15) == g(13) + g(14) and g(17) == g(7) + g(13) and g(18) == g(8) + g(10) + g(14), 'sumy'
print('3) sumy w tabeli dodaja sie dokladnie: OK')
print('4) kontrola bilansu OBLICZENIA!B37 =', V['OBLICZENIA']['B37'].value)
print('   bilans masy: zebrane', round(o['h_razem']+o['nas']+o['Vmin']), ' = odklad+utylizacja', round(o['h_odkl']+o['m_odkl']+o['h_wyw']+o['nas']+o['m_nadw']))

import sys, os, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'/projects/sandbox/civil3d_roboty_ziemne_dz190/_skrypt')
import formulas
from bilans_formuly import bilans, wczytaj
P='/projects/sandbox/civil3d_roboty_ziemne_dz190/00_WYNIKI/BILANS_ROBOT_ZIEMNYCH_dz190.xlsx'
xl=formulas.ExcelModel().loads(P).finish()
sol=xl.calculate()
def val(sheet,cell):
    k="'[%s]%s'!%s"%(os.path.basename(P),sheet.upper(),cell)
    v=sol[k].value
    return float(v[0][0]) if hasattr(v,'__len__') else float(v)
R=wczytaj()
mapa={ # wiersz WYNIK -> klucz bilans()
 9:'humus_w_scianie',10:'humus_poza',11:'humus_razem',12:'humus_potrzeba',13:'humus_odklad',14:'humus_wywoz',15:'nasyp',
 20:'V_mineralny',21:'piasek_sel',22:'piasek_cienki',23:'glina_sucha',24:'glina_mokra',26:'odklad_piasek',28:'odklad_min',29:'wywoz_min',
 32:'zapotrz_wykop',33:'zapotrz_w_scianie_poza_wykopem',34:'zapotrz_poza_scianka',35:'zapotrzebowanie',37:'import_',
 40:'odklad_razem',41:'wywoz_razem',47:'wywoz_luzem',48:'wywoz_tony',49:'odklad_luzem',50:'odklad_tony'}
bad=0
for col,war in (('B','C15'),('C','B')):
    o=bilans(war,R=R)
    for r,k in mapa.items():
        x=val('WYNIK',f'{col}{r}'); y=o[k]
        if k=='humus_potrzeba': y=y*(1+0.10)   # w arkuszu wiersz 12 zawiera zapas
        ok=abs(x-y)<=max(1.0,1e-6*abs(y))
        if not ok:
            bad+=1; print('ROZNICA',col,r,k,x,y)
    print('kolumna',col,'wariant',war,'| kontrola wiersz25=',val('WYNIK',f'{col}25'),' wiersz51=',val('WYNIK',f'{col}51'))
print('rozbieznosci:',bad)
for c in ('Q4','Q5','Q6','Q7','Q8','Q10','Q11','Q12','Q13'):
    print('WEZLY',c,round(val('WEZLY_10m',c),4))

import sys, os, warnings
warnings.filterwarnings('ignore')
import formulas
from openpyxl import load_workbook
P='/projects/sandbox/civil3d_roboty_ziemne_dz190/00_WYNIKI/BILANS_ROBOT_ZIEMNYCH_dz190.xlsx'
xl=formulas.ExcelModel().loads(P).finish(); sol=xl.calculate()
ws=load_workbook(P)['WYNIK']
def val(cell):
    k="'[%s]WYNIK'!%s"%(os.path.basename(P),cell); v=sol[k].value
    return float(v[0][0]) if hasattr(v,'__len__') else float(v)
for r in range(8,58):
    a=ws.cell(r,1).value
    if a is None: continue
    try: b=val(f'B{r}'); c=val(f'C{r}')
    except Exception: b=c=None
    if b is None or (ws.cell(r,2).value is None): print('\n'+str(a)); continue
    print('%-78s %10.0f %10.0f'%(str(a)[:78],b,c))

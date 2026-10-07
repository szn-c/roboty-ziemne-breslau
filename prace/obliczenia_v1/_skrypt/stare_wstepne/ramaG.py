"""Uklad G = siatka wspolrzednych PL-2000 narysowana przez projektanta (krzyze co 50 m).
Rzut wektorowy zabezpieczenia: skala 1:1270 (A4), krzyze siatki -> dopasowanie najmniejszych kwadratow."""
import json, math
import numpy as np

CROSSES = [(30.0,201.72),(30.0,313.32),(30.0,424.8),(141.6,201.72),(141.6,313.32),(141.6,424.8),(141.6,536.4),
           (253.2,201.72),(253.2,313.32),(253.2,424.8),(253.2,536.4),(364.68,201.72),(364.68,313.32),(364.68,424.8),
           (364.68,536.4),(364.68,647.88),(476.28,313.32),(476.28,424.8),(476.28,536.4),(476.28,647.88)]
E0,N0 = 6433700.0, 5659050.0
def _fit():
    A=[];B=[]
    for x,y in CROSSES:
        i=round((x-364.68)/111.5); j=round((y-201.72)/111.5)
        E=50.0*i; N=-50.0*j       # E-E0, N-N0
        A.append([E,0,1,0]);B.append(x)     # x = s*E' + x0 (zakladamy obrot 0)
        A.append([0,-N*-1,0,1]);B.append(y) # y = y0 - s*N' ; N' = -50 j -> y = y0 + s*50 j
    A=np.array(A,float);B=np.array(B,float)
    # niezalezne s w x i y -> dopasuj wspolnie: x = x0 + s*E', y = y0 - s*N'
    A2=[];B2=[]
    for x,y in CROSSES:
        i=round((x-364.68)/111.5); j=round((y-201.72)/111.5)
        Ep=50.0*i; Np=-50.0*j
        A2.append([Ep,1,0]);B2.append(x)
        A2.append([-Np,0,1]);B2.append(y)
    sol,*_=np.linalg.lstsq(np.array(A2),np.array(B2),rcond=None)
    res=np.array(A2)@sol-np.array(B2)
    return sol,res
_sol,_res=_fit()
S_VEC, X0_VEC, Y0_VEC = _sol
def vec_to_G(x,y):
    return (E0+(x-X0_VEC)/S_VEC, N0-(y-Y0_VEC)/S_VEC)
def G_to_vec(E,N):
    return (X0_VEC+S_VEC*(E-E0), Y0_VEC-S_VEC*(N-N0))
if __name__=='__main__':
    print('skala rzutu = %.5f pt/m (1:%.1f), x0=%.3f y0=%.3f ; rms residuum krzyzy = %.3f pt = %.3f m'%(S_VEC,72/0.0254/S_VEC,X0_VEC,Y0_VEC,math.sqrt((_res**2).mean()),math.sqrt((_res**2).mean())/S_VEC))
    print('krzyz z etykieta (364.68,201.72) ->',vec_to_G(364.68,201.72))

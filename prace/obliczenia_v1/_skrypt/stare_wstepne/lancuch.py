import math, json
from shapely.geometry import Polygon

def line_int(a,b):
    (x1,y1),(x2,y2)=a; (x3,y3),(x4,y4)=b
    den=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    if abs(den)<1e-9: return None
    t=((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/den
    return (x1+t*(x2-x1), y1+t*(y2-y1))

def ang(p,q): return math.atan2(q[1]-p[1], q[0]-p[0])

def chain_polygon(S, start_dir_up=True, maxgap=9.0, corner_deg=2.0, simplify_tol=0.08, verbose=True):
    rest=[tuple(map(tuple,s)) for s in S]
    cur=min(rest,key=lambda s:(s[0][0]+s[1][0])/2); rest.remove(cur)
    if cur[0][1]>cur[1][1]: cur=(cur[1],cur[0])          # na zachodzie jedziemy ku polnocy
    chain=[cur]
    while rest:
        e=chain[-1][1]; best=None
        for s in rest:
            for flip in (False,True):
                p,q=(s[1],s[0]) if flip else s
                d=math.dist(e,p)
                if best is None or d<best[0]: best=(d,s,(p,q))
        d,s,(p,q)=best
        if verbose and d>maxgap: print('UWAGA: duza przerwa %.2f m przy (%.1f, %.1f)'%(d,e[0],e[1]))
        chain.append((p,q)); rest.remove(s)
    if verbose: print('lancuch:',len(chain),' domkniecie %.2f m'%math.dist(chain[-1][1],chain[0][0]))
    V=[]; n=len(chain)
    for i in range(n):
        A=chain[i]; B=chain[(i+1)%n]
        V+=[A[0],A[1]]
        da=abs((math.degrees(ang(*B)-ang(*A))+180)%360-180)
        gap=math.dist(A[1],B[0])
        if da>corner_deg and gap>0.3:
            X=line_int(A,B)
            if X and math.dist(X,A[1])<maxgap and math.dist(X,B[0])<maxgap: V.append(X)
    out=[]
    for p in V:
        if out and math.dist(p,out[-1])<0.05: continue
        out.append(p)
    ch=True
    while ch and len(out)>3:
        ch=False
        for i in range(len(out)):
            a,b,c=out[i-1],out[i],out[(i+1)%len(out)]
            ab=(c[0]-a[0],c[1]-a[1]); L=math.hypot(*ab)
            if L<1e-9: continue
            dist=abs(ab[0]*(b[1]-a[1])-ab[1]*(b[0]-a[0]))/L
            if dist<simplify_tol: out.pop(i); ch=True; break
    return out

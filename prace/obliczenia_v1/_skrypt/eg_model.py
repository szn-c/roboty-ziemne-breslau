"""Model istniejacego terenu (EG) dla dz. 1/90.
Zrodla: (1) 17 otworow DGI, (2) czarne rzedne pomiarowe z PZT (mapa geodezyjna), (3) siatka 10 m rzednych z rzutu zabezpieczenia
(szara; ma stale zawyzenie ok. +0,1 m i pojedyncze literowki -> odfiltrowana i skorygowana wzgledem pomiaru).
"""
import csv, json, os
import numpy as np
from scipy.spatial import cKDTree
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
from shapely.geometry import Polygon
from shapely import contains_xy
from generuj_pliki import OTWORY

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dane') + os.sep
E0, N0 = 6433650.0, 5658975.0


def _rd(fn):
    with open(D + fn) as f:
        return np.array([(float(x['E']), float(x['N']), float(x['z'])) for x in csv.DictReader(f)])


def geometria():
    g = json.load(open(D + 'geometria_G.json'))
    return Polygon(g['scianka']), {int(k): Polygon(v) for k, v in g['hale'].items()}, Polygon(g['dzialka'])


def _clean(P, r, k):
    tr = cKDTree(P[:, :2]); keep = []
    for p in P:
        d, idx = tr.query(p[:2], k=min(k + 1, len(P)))
        keep.append(abs(p[2] - np.median(P[idx[1:], 2])) <= r)
    return P[np.array(keep)]


def _huber_plane(x, y, z, iters=30, c=1.5):
    A = np.c_[np.ones(len(x)), x - E0, y - N0]
    w = np.ones(len(z))
    for _ in range(iters):
        coef, *_ = np.linalg.lstsq(A * w[:, None], z * w, rcond=None)
        r = z - A @ coef
        s = 1.4826 * np.median(abs(r - np.median(r))) + 1e-9
        w = np.minimum(1, c * s / np.maximum(abs(r), 1e-9)) ** 0.5
    return coef, s


def zbuduj(uzyj_trend=True, tylko_pomiar=False, tylko_siatka=False, buf=25.0, verbose=False):
    W, HALE, PAR = geometria()
    PB = PAR.buffer(buf)
    sel = lambda P: P[contains_xy(PB, P[:, 0], P[:, 1])]
    grid = _clean(sel(_rd('eg_siatka10m_z_rzutu_zabezpieczenia.csv')), 0.30, 8)
    pzt = _clean(sel(_rd('eg_pomiar_PZT_czarne.csv')), 0.30, 6)
    bh = np.array([(E, N, h) for nr, (N, E, h, zw, uw) in OTWORY.items()])
    S = np.vstack([bh, pzt])
    fg = LinearNDInterpolator(grid[:, :2], grid[:, 2])
    inside = contains_xy(W.buffer(8), S[:, 0], S[:, 1])
    res = S[:, 2] - fg(S[:, 0], S[:, 1]); m = inside & ~np.isnan(res)
    coef, s = _huber_plane(S[m, 0], S[m, 1], res[m])
    if not uzyj_trend:
        coef = np.array([np.median(res[m]), 0, 0])
    corr = lambda x, y: coef[0] + coef[1] * (x - E0) + coef[2] * (y - N0)
    g2 = grid.copy(); g2[:, 2] = g2[:, 2] + corr(g2[:, 0], g2[:, 1])
    if tylko_pomiar:
        P = S
    elif tylko_siatka:
        P = grid
    else:
        P = np.vstack([S, g2])
    # usun duplikaty bardzo blisko siebie (<0.5 m)
    tr = cKDTree(P[:, :2]); keep = np.ones(len(P), bool)
    for i, j in tr.query_pairs(0.5):
        if keep[i] and keep[j]:
            keep[j] = False
    P = P[keep]
    lin = LinearNDInterpolator(P[:, :2], P[:, 2]); nn = NearestNDInterpolator(P[:, :2], P[:, 2])

    def eg(x, y):
        x = np.asarray(x, float); y = np.asarray(y, float)
        z = lin(x, y)
        bad = np.isnan(z)
        if bad.any():
            z[bad] = nn(x[bad], y[bad])
        return z
    info = dict(n_siatka=len(grid), n_pomiar=len(pzt), n_otwory=len(bh), korekta_stala=float(coef[0]),
                korekta_dE_100m=float(coef[1] * 100), korekta_dN_100m=float(coef[2] * 100), rozrzut_MAD=float(s), n_dopasowania=int(m.sum()))
    return eg, info, P

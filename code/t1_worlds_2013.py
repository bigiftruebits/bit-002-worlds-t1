"""T1's 2013 Worlds (Season 3), left out of the analysis window (2014-2025): games, wins, expected wins with
ratings frozen on the event's first day, and the Worlds total with 2013 added (Riccardo, 11 Oct 2026).

    python t1_worlds_2013.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd
from elo import *; from backtest_params import PARAMS, SCALE
g = prep(); reg = team_regions(g)
gm = g[g.tournament == 'Season 3 World Championship']; st = gm.dt.min()
e = Elo(**PARAMS); e.run(g, reg, until=st)
rows = []
for r in gm.itertuples():
    d = e.eff(r.t1) - e.eff(r.t2)
    for team, dd, win in ((r.t1, d, r.win1), (r.t2, -d, 1 - r.win1)):
        if team == 'T1': rows.append(dict(t1=r.t1, t2=r.t2, d=dd, p=1 / (1 + 10 ** (-dd / SCALE)), win=win))
D = pd.DataFrame(rows); D.to_csv('../data/t1_worlds_2013.csv', index=False)
print(f'2013: {len(D)} games, {int(D.win.sum())} won, {D.p.sum():.1f} expected, excess {D.win.sum() - D.p.sum():.1f}')

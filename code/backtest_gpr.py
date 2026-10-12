"""backtest_gpr.py

    python backtest_gpr.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, random
from sim import *; from history import main_event; from teams2026 import CODE2NAME
snap={2024:'2024-09-27',2025:'2025-10-06'}
for y in (2024,2025):
    ev=main_event(y); d=pd.read_csv(f'../raw/not_redistributed/gpr_{y}_worlds_history.csv'); d=d[d.date.str.startswith(snap[y])]
    gp={CODE2NAME.get(c,c):v for c,v in zip(d.code,d.gpr)}; elo={t:gp[t] for t in ev['teams']}
    for scale in (400,480):
        def one(rng):
            W=World(elo,{},scale=scale,rng=rng); q,_=swiss(W,ev['round1']); return swiss_knockout(W,q)
        ch,_=run_many(one,40000,seed=1); N=40000
        top=sorted(((t,c/N) for t,c in ch.items()),key=lambda x:-x[1])[:5]
        print(y,scale,'champ',ev['champion'],round(ch[ev['champion']]/N,4),'| top',[(t,round(p,3)) for t,p in top])

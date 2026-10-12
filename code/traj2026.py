"""Elo of the 20 Worlds 2026 candidates through the 2026 season (weekly snapshots).

    python traj2026.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, random
from elo import *; from teams2026 import REGION, LATE_RESULTS
from backtest_params import PARAMS
g=prep(); reg=team_regions(g)
extra=[]
for r in LATE_RESULTS:
    a,b,s1,s2,dt=r[:5]
    seq=list(r[5]) if len(r)>5 else [1]*s1+[0]*s2
    if len(r)<=5: random.Random(0).shuffle(seq)
    for i,w in enumerate(seq): extra.append(dict(dt=pd.Timestamp(dt)+pd.Timedelta(minutes=40*i),tournament='late',match_id='late',t1=a,t2=b,win1=w,t_region='Brazil' if a in ('LOUD','LØS','FURIA') else 'North America',league=''))
g=pd.concat([g,pd.DataFrame(extra)]).sort_values('dt').reset_index(drop=True)
e=Elo(**PARAMS)
dates=pd.date_range('2026-01-12','2026-10-10',freq='7D').append(pd.DatetimeIndex(['2026-10-10 23:59']))
e.run(g,reg,until=dates[0]); prev=dates[0]; rows=[]
for d in dates:
    e.run(g[(g.dt>=prev)],reg,until=d); prev=d
    for t in REGION: rows.append(dict(date=d,team=t,elo=e.eff(t),played=e.last.get(t,pd.Timestamp(0))>=pd.Timestamp('2026-01-01')))
T=pd.DataFrame(rows); T.to_csv('../data/traj2026.csv',index=False)
print(T[T.date==T.date.max()].sort_values('elo',ascending=False).round(0).to_string(index=False))
print(T[T.team=='Gen.G'].elo.round(0).tolist()[:6])

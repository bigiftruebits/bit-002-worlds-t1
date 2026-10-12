"""Re-run the champion-odds backtest and the T1 residual with lolproelo.com ratings instead of ours.

    python published_backtest.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
from sim import *; from history import main_event
T=pd.read_csv('../data/compare_published_ratings.csv'); D=pd.read_csv('../data/compare_published_games.csv')
N=30000; rows=[]
for y in range(2014,2026):
    ev=main_event(y); t=T[T.year==y].set_index('team')
    for col,scale in (('ours',480),('lpe',526),('lpe',400)):
        elo=t[col].to_dict()
        if any(pd.isna(v) for v in elo.values()):
            fill=np.nanmin(list(elo.values())); elo={k:(fill if pd.isna(v) else v) for k,v in elo.items()}
        def one(rng):
            W=World(elo,{},scale=scale,rng=rng)
            if ev['format']=='groups': return group_knockout(W,group_stage(W,ev['groups']))
            q,_=swiss(W,ev['round1']); return swiss_knockout(W,q)
        ch,_=run_many(one,N,seed=y)
        fav=max(ch,key=ch.get)
        rows.append(dict(year=y,ratings=f'{col}@{scale}',champion=ev['champion'],p_champ=ch[ev['champion']]/N,favourite=fav,p_fav=ch[fav]/N))
B=pd.DataFrame(rows); B.to_csv('../data/published_backtest.csv',index=False)
print(B.pivot(index=['year','champion'],columns='ratings',values='p_champ').round(3).to_string())
for r,b in B.groupby('ratings'):
    p=b.set_index('year').p_champ; print(r,'T1 2023-25 three-peat: 1 in',round(1/(p[2023]*p[2024]*p[2025])),'| favourite won',(b.favourite==b.champion).sum(),'of 12')
# T1 residual at Worlds under each rating
long=pd.concat([D.assign(team=D.t1,win=D.win1,s=1),D.assign(team=D.t2,win=1-D.win1,s=-1)])
for c,scale in (('ours',480),('lpe',526)):
    x=long.dropna(subset=['d_'+c]); p=1/(1+10**(-(x.s*x['d_'+c])/scale)); x=x.assign(p=p)
    t=x[x.team=='T1']; ex=t.win.sum()-t.p.sum(); z=ex/np.sqrt((t.p*(1-t.p)).sum())
    print(f'T1 at Worlds with {c}: {len(t)} games, {t.win.sum()} wins vs {t.p.sum():.1f} expected, excess {ex:+.1f}, z={z:.2f}')

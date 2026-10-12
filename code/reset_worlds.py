"""Does resetting Elo every season predict Worlds better? Ratings frozen at each main-event start.
Variants: carry share of team rating (vs region mean) and of region offset (vs global mean).

    python reset_worlds.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, random
from elo import *; from history import main_event; from sim import *
from backtest_params import PARAMS
from scipy.optimize import minimize_scalar
g=prep(); reg=team_regions(g)
VARIANTS=[('Full reset (teams and regions)',0.0,0.0),('Reset teams, keep regions',0.0,0.91),('Keep 30%',0.3,0.91),
          ('Keep 63% (our model)',0.63,0.91),('No reset',1.0,1.0)]
EV={y:main_event(y) for y in range(2014,2026)}
rows=[]; champ=[]
for lab,c,cr in VARIANTS:
    D=[]; ratings={}
    for y,ev in EV.items():
        e=Elo(**dict(PARAMS,carry=c,carry_reg=cr)); e.run(g,reg,until=ev['start'])
        ratings[y]={t:e.eff(t) for t in ev['teams']}
        gm=g[(g.dt>=ev['start'])&g.tournament.str.contains(f'{y} Season World Championship')]
        for r in gm.itertuples(): D.append((y,ratings[y][r.t1]-ratings[y][r.t2],r.win1))
    D=pd.DataFrame(D,columns=['y','d','w'])
    nll=lambda s: -np.mean(D.w*np.log(1/(1+10**(-D.d/s)))+(1-D.w)*np.log(1-1/(1+10**(-D.d/s))))
    s=minimize_scalar(nll,bounds=(100,3000),method='bounded').x
    # champion log-score via simulation
    ls=[]
    for y,ev in EV.items():
        elo=ratings[y]
        def one(rng):
            W=World(elo,{},scale=s,rng=rng)
            if ev['format']=='groups': return group_knockout(W,group_stage(W,ev['groups']))
            q,_=swiss(W,ev['round1']); return swiss_knockout(W,q)
        ch,_=run_many(one,10000,seed=y); ls.append(np.log(max(ch[ev['champion']],1)/10000))
    rows.append(dict(variant=lab,worlds_games=len(D),favourite_won=((D.d>0)==(D.w==1)).mean(),log_loss=nll(s),best_scale=s,
                     champion_log_score=np.mean(ls),geo_mean_p_champion=np.exp(np.mean(ls))))
    print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv('../data/reset_worlds.csv',index=False)

"""backtest.py

    python backtest.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, random, json, sys
from elo import *; from sim import *; from history import main_event
from backtest_params import PARAMS, SCALE
N=int(sys.argv[1]) if len(sys.argv)>1 else 20000
g=prep(); reg=team_regions(g)
rows=[]; teamrows=[]
for y in range(2014,2026):
    ev=main_event(y)
    e=Elo(**PARAMS); e.run(g,reg,until=ev['start'])
    elo={t:e.eff(t) for t in ev['teams']}; region={t:e.home.get(t) for t in ev['teams']}
    missing=[t for t in ev['teams'] if t not in e.r]
    def one(rng):
        W=World(elo,region,scale=SCALE,rng=rng)
        if ev['format']=='groups': return group_knockout(W,group_stage(W,ev['groups']))
        q,_=swiss(W,ev['round1']); return swiss_knockout(W,q)
    champs,stage=run_many(one,N,seed=y)
    pr={t:champs[t]/N for t in ev['teams']}
    fav=max(pr,key=pr.get); rank=sorted(pr.values(),reverse=True).index(pr[ev['champion']])+1
    rows.append(dict(year=y,champion=ev['champion'],p_champ=pr[ev['champion']],champ_rank=rank,champ_elo_rank=sorted(elo.values(),reverse=True).index(elo[ev['champion']])+1,
                     favourite=fav,p_fav=pr[fav],runner_up=ev['runner_up'],p_final_pair=None,missing=missing))
    for t in ev['teams']:
        st=stage[t]; reached=lambda lvl: sum(v for k,v in st.items() if k in lvl)/N
        actual='W' if t==ev['champion'] else 'F' if t==ev['runner_up'] else 'SF' if t in ev['semis'] else 'QF' if t in ev['quarters'] else 'G'
        teamrows.append(dict(year=y,team=t,region=region[t],elo=elo[t],p_win=pr[t],p_final=reached({'W','F'}),p_semi=reached({'W','F','SF'}),p_ko=reached({'W','F','SF','QF'}),actual=actual))
    print(rows[-1])
pd.DataFrame(rows).to_csv('../data/backtest_years.csv',index=False); pd.DataFrame(teamrows).to_csv('../data/backtest_teams.csv',index=False)

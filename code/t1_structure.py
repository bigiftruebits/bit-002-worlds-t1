"""IF informed by tournament structure: for every Worlds T1 played (2015-2025), simulate the real main-event
format and record T1's chance of winning and of doing at least as well as it did, with no bonus, with the
bonus fitted only on earlier years (forward, from bonus_oos.py) and with the full-sample bonus (177).

    python t1_structure.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
from elo import *; from sim import *; from history import main_event
from backtest_params import PARAMS, SCALE
N=20000; FWD={2015:0,2016:373,2017:194,2019:72,2021:63,2022:89,2023:102,2024:149,2025:176}; FULL=177
ORDER=['G','QF','SF','F','W']
g=prep(); reg=team_regions(g); rows=[]
for y in sorted(FWD):
    ev=main_event(y)
    if 'T1' not in ev['teams']: continue
    e=Elo(**PARAMS); e.run(g,reg,until=ev['start'])
    base={t:e.eff(t) for t in ev['teams']}; region={t:e.home.get(t) for t in ev['teams']}
    actual='W' if ev['champion']=='T1' else 'F' if ev['runner_up']=='T1' else 'SF' if 'T1' in ev['semis'] else 'QF' if 'T1' in ev['quarters'] else 'G'
    out=dict(year=y,actual=actual)
    for lab,b in [('none',0),('forward',FWD[y]),('full',FULL)]:
        elo=dict(base); elo['T1']+=b
        def one(rng):
            W=World(elo,region,scale=SCALE,rng=rng)
            if ev['format']=='groups': return group_knockout(W,group_stage(W,ev['groups']))
            q,_=swiss(W,ev['round1']); return swiss_knockout(W,q)
        champs,stage=run_many(one,N,seed=y)
        st=stage['T1']; lvl=lambda s: ORDER.index(s)
        atleast=sum(v for k,v in st.items() if lvl(k)>=lvl(actual))/N + (st.get('G',0)/N if actual=='G' else 0)
        # stages: 'G' never recorded in run_many for eliminated teams -> P(at least G)=1
        atleast=1.0 if actual=='G' else sum(v for k,v in st.items() if lvl(k)>=lvl(actual))/N
        exact=(st.get(actual,0)/N) if actual!='G' else 1-sum(st.values())/N
        out[f'p_win_{lab}']=champs['T1']/N; out[f'p_atleast_{lab}']=atleast; out[f'p_exact_{lab}']=exact
    rows.append(out); print(out,flush=True)
D=pd.DataFrame(rows); D.to_csv('../data/t1_structure.csv',index=False)
for lab in ['none','forward','full']:
    print(lab,'prod P(at least actual)=%.3g'%D[f'p_atleast_{lab}'].prod(),' loglik stages=%.2f'%np.log(D[f'p_exact_{lab}']).sum(),
          ' 3-peat=%.3g'%D[D.year>=2023][f'p_win_{lab}'].prod())

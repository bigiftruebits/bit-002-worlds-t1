"""tune.py

    python tune.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import numpy as np, pandas as pd, json
from elo import *
g=prep(); reg=team_regions(g)
s_all=g.win1.values; yr=g.dt.dt.year.values
def evaluate(par):
    e=Elo(**par); rec=e.run(g,reg,record=True)
    idx,p,cross=map(np.array,zip(*rec)); s=s_all[idx]; y=yr[idx]
    p=np.clip(p,1e-6,1-1e-6); l=-(s*np.log(p)+(1-s)*np.log(1-p))
    tr=(y>=2014)&(y<=2019); te=(y>=2020)
    return dict(tr_cross=l[tr&cross].mean(),tr_all=l[tr].mean(),te_cross=l[te&cross].mean(),te_all=l[te].mean())
rng=np.random.default_rng(0); res=[]
base=dict(K=24,K_intl=32,K_reg=8,carry=0.75,carry_reg=0.85,new_pen=60)
res.append((base,evaluate(base)))
for i in range(150):
    par=dict(K=float(rng.uniform(10,50)),K_intl=float(rng.uniform(10,80)),K_reg=float(rng.uniform(0,30)),
             carry=float(rng.uniform(0.3,1)),carry_reg=float(rng.uniform(0.5,1)),new_pen=float(rng.uniform(0,150)))
    res.append((par,evaluate(par)))
df=pd.DataFrame([{**p,**m} for p,m in res])
df['obj']=df.tr_cross+df.tr_all
df=df.sort_values('obj'); df.to_csv('../data/tune_results.csv',index=False)
print(df.head(10).round(3).to_string()); print(df[df.index==0].round(3).to_string())

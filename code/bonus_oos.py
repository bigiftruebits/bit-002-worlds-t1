"""bonus_oos.py

    python bonus_oos.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
from backtest_params import SCALE
from scipy.optimize import minimize_scalar
D=pd.read_csv('../data/intl_games_static.csv'); D=D[D.kind=='Worlds']
L=pd.concat([D.assign(team=D.t1,win=D.win1,d=D['diff']),D.assign(team=D.t2,win=1-D.win1,d=-D['diff'])])
w=L[L.team=='T1']
P=lambda d: 1/(1+10**(-d/SCALE))
ll=lambda x,b: -np.sum(x.win*np.log(P(x.d+b))+(1-x.win)*np.log(1-P(x.d+b)))
tot0=tot1=0; rows=[]
for y in sorted(w.year.unique()):
    past=w[w.year<y]; cur=w[w.year==y]
    if past.empty: continue
    b=minimize_scalar(lambda b:ll(past,b),bounds=(-300,600),method='bounded').x
    rows.append((y,round(b),len(cur),round(ll(cur,0),2),round(ll(cur,b),2))); tot0+=ll(cur,0); tot1+=ll(cur,b)
print(pd.DataFrame(rows,columns=['year','bonus_from_past','games','nll_no_bonus','nll_with_bonus']).to_string(index=False))
print('total out-of-sample NLL: no bonus',round(tot0,2),' with bonus',round(tot1,2))
b_pre23=minimize_scalar(lambda b:ll(w[w.year<2023],b),bounds=(-300,600),method='bounded').x
print('bonus using 2015-2022 only:',round(b_pre23))

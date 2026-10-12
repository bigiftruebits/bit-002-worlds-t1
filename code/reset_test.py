"""How much of last season's rating to keep? Compare full reset, partial (tuned), and no reset.

    python reset_test.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import numpy as np, pandas as pd
from elo import *; from backtest_params import PARAMS
g=prep(); reg=team_regions(g); s_all=g.win1.values; yr=g.dt.dt.year.values; mon=g.dt.dt.month.values
wc=g.tournament.str.contains('Season World Championship').values
rows=[]
for carry in [0.0,0.25,0.5,0.63,0.8,1.0]:
    par=dict(PARAMS,carry=carry); e=Elo(**par); rec=e.run(g,reg,record=True)
    idx,p,cross=map(np.array,zip(*rec)); s=s_all[idx]; y=yr[idx]; m=mon[idx]
    p=np.clip(p,1e-6,1-1e-6); l=-(s*np.log(p)+(1-s)*np.log(1-p)); ok=y>=2014
    rows.append(dict(carry=carry,all=l[ok].mean(),first_2_months=l[ok&(m<=2)].mean(),cross_region=l[ok&cross].mean(),worlds=l[ok&wc[idx]].mean()))
print(pd.DataFrame(rows).round(4).to_string(index=False))

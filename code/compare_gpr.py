"""compare_gpr.py

    python compare_gpr.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
from elo import *; from history import main_event; from teams2026 import CODE2NAME
from backtest_params import PARAMS, SCALE
from scipy.optimize import minimize_scalar
g=prep(); reg=team_regions(g)
snap={2024:'2024-09-27',2025:'2025-10-06'}
rows=[]; tabs=[]
for y in (2024,2025):
    ev=main_event(y); e=Elo(**PARAMS); e.run(g,reg,until=ev['start'])
    d=pd.read_csv(f'../raw/not_redistributed/gpr_{y}_worlds_history.csv'); d=d[d.date.str.startswith(snap[y])]
    gp={CODE2NAME.get(c,c):v for c,v in zip(d.code,d.gpr)}
    miss=[t for t in ev['teams'] if t not in gp]; print(y,'missing in GPR map',miss)
    tab=pd.DataFrame([(y,t,e.eff(t),gp.get(t)) for t in ev['teams']],columns=['year','team','ours','gpr']); tabs.append(tab)
    print(tab[['ours','gpr']].corr(method='spearman').iloc[0,1], 'sd ours',tab.ours.std(),'sd gpr',tab.gpr.std())
    gm=g[(g.dt>=ev['start'])&g.tournament.str.contains(f'{y} Season World Championship/Main')]
    for r in gm.itertuples(): rows.append((y,e.eff(r.t1)-e.eff(r.t2),gp[r.t1]-gp[r.t2],r.win1))
d=pd.DataFrame(rows,columns=['y','d_ours','d_gpr','win'])
def nll(diff,s): p=1/(1+10**(-diff/s)); return -np.mean(d.win*np.log(p)+(1-d.win)*np.log(1-p))
for c,s in (('d_ours',SCALE),('d_gpr',400)):
    best=minimize_scalar(lambda x:nll(d[c],x),bounds=(50,3000),method='bounded')
    print(c,len(d),'nll@default',round(nll(d[c],s),4),'best scale',round(best.x),round(best.fun,4),'acc',((d[c]>0)==(d.win==1)).mean().round(3))
pd.concat(tabs).to_csv('../data/ours_vs_gpr_2024_2025.csv',index=False)

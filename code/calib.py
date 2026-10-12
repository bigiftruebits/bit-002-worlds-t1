"""calib.py

    python calib.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
from elo import *; from history import main_event
from backtest_params import PARAMS
g=prep(); reg=team_regions(g); rows=[]
for y in range(2014,2026):
    ev=main_event(y); e=Elo(**PARAMS); e.run(g,reg,until=ev['start'])
    end=ev['start']+pd.Timedelta(days=40)
    gm=g[(g.dt>=ev['start'])&(g.dt<end)&(g.tournament.str.contains(f'{y} Season World Championship'))]
    for r in gm.itertuples():
        d=e.eff(r.t1)-e.eff(r.t2); rows.append((y,d,r.win1,'KO' if False else ''))
d=pd.DataFrame(rows,columns=['year','diff','win','x'])
d.to_csv('../data/worlds_games_static.csv',index=False)
from scipy.optimize import minimize_scalar
def nll(s,dd): p=1/(1+10**(-dd['diff']/s)); return -np.mean(dd.win*np.log(p)+(1-dd.win)*np.log(1-p))
for lab,dd in [('all',d),('2014-19',d[d.year<2020]),('2020-25',d[d.year>=2020])]:
    r=minimize_scalar(lambda s:nll(s,dd),bounds=(100,3000),method='bounded'); print(lab,len(dd),'best scale',round(r.x),'nll',round(r.fun,4),'nll@400',round(nll(400,dd),4))
d['p']=1/(1+10**(-d['diff']/400)); d['fav_p']=np.maximum(d.p,1-d.p); d['fav_win']=np.where(d.p>=0.5,d.win,1-d.win)
d['bin']=pd.cut(d.fav_p,[0.5,0.6,0.7,0.8,0.9,1])
print(d.groupby('bin',observed=True).agg(n=('win','size'),pred=('fav_p','mean'),actual=('fav_win','mean')).round(3))

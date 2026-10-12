"""Over/under-performance at Worlds vs pre-tournament Elo, per team and per region (game level, 2014-2025).

    python residuals.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
from elo import *; from history import main_event
from backtest_params import PARAMS, SCALE
g=prep(); reg=team_regions(g); rows=[]
for y in range(2014,2026):
    ev=main_event(y); e=Elo(**PARAMS); e.run(g,reg,until=ev['start'])
    gm=g[(g.dt>=ev['start'])&g.tournament.str.contains(f'{y} Season World Championship')]
    for r in gm.itertuples():
        p=1/(1+10**(-(e.eff(r.t1)-e.eff(r.t2))/SCALE))
        rows+= [(y,r.t1,e.home.get(r.t1),r.win1,p),(y,r.t2,e.home.get(r.t2),1-r.win1,1-p)]
d=pd.DataFrame(rows,columns=['year','team','region','win','p']); d.to_csv('../data/worlds_team_games.csv',index=False)
d['res']=d.win-d.p; d['var']=d.p*(1-d.p)
t=d.groupby('team').agg(games=('win','size'),wins=('win','sum'),exp=('p','sum'),var=('var','sum'),years=('year','nunique'))
t['excess']=t.wins-t.exp; t['z']=t.excess/np.sqrt(t['var'])
print(t[t.games>=30].sort_values('z',ascending=False).round(2).head(12).to_string()); print(t[t.games>=30].sort_values('z').round(2).head(6).to_string())
r=d.groupby('region').agg(games=('win','size'),wins=('win','sum'),exp=('p','sum'),var=('var','sum')); r['excess']=r.wins-r.exp; r['z']=r.excess/np.sqrt(r['var'])
print(r.sort_values('z').round(2).to_string())
print(d[d.team=='T1'].groupby('year').agg(g=('win','size'),w=('win','sum'),e=('p','sum')).round(1).T.to_string())

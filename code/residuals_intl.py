"""Is T1's over-performance Worlds-specific? Compare residuals at Worlds vs other international events,
using ratings frozen at each event's start. Also fit a 'Worlds bonus' for T1 in Elo points.

    python residuals_intl.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
from elo import *; from backtest_params import PARAMS, SCALE
from scipy.optimize import minimize_scalar
g=prep(); reg=team_regions(g)
intl=g[g.t_region.isin(INTL)].copy()
intl['event']=intl.tournament.str.replace(r'/(Main Event|Play-In|Group Stage|Knockout Stage|Bracket Stage|Rumble Stage)$','',regex=True)
starts=intl.groupby('event').dt.min().sort_values()
starts=starts[starts>='2014-01-01']
rows=[]
for ev,st in starts.items():
    e=Elo(**PARAMS); e.run(g,reg,until=st)
    gm=intl[intl.event==ev]
    kind='Worlds' if 'Season World Championship' in ev else 'MSI' if 'Mid-Season Invitational' in ev else 'Other intl'
    for r in gm.itertuples():
        d=e.eff(r.t1)-e.eff(r.t2); rows.append((ev,kind,st.year,r.t1,r.t2,e.home.get(r.t1),e.home.get(r.t2),d,r.win1))
D=pd.DataFrame(rows,columns=['event','kind','year','t1','t2','r1','r2','diff','win1']); D.to_csv('../data/intl_games_static.csv',index=False)
long=pd.concat([D.assign(team=D.t1,reg=D.r1,win=D.win1,d=D['diff']),D.assign(team=D.t2,reg=D.r2,win=1-D.win1,d=-D['diff'])])
long['p']=1/(1+10**(-long.d/SCALE)); long['var']=long.p*(1-long.p)
def summ(x): return pd.Series(dict(games=len(x),wins=x.win.sum(),exp=x.p.sum(),excess=x.win.sum()-x.p.sum(),z=(x.win.sum()-x.p.sum())/np.sqrt(x['var'].sum())))
print('T1 by event type'); print(long[long.team=='T1'].groupby('kind').apply(summ).round(2))
print('Korean teams except T1'); print(long[(long.reg=='KR')&(long.team!='T1')].groupby('kind').apply(summ).round(2))
print('Chinese teams'); print(long[(long.reg=='CN')].groupby('kind').apply(summ).round(2))
# Worlds bonus for T1 (Elo points added in Worlds games only)
w=long[(long.team=='T1')&(long.kind=='Worlds')]
nll=lambda b: -np.sum(w.win*np.log(1/(1+10**(-(w.d+b)/SCALE)))+(1-w.win)*np.log(1-1/(1+10**(-(w.d+b)/SCALE))))
b=minimize_scalar(nll,bounds=(-300,600),method='bounded').x
# profile-likelihood 95% interval
grid=np.arange(-100,500,1); L=np.array([nll(x) for x in grid]); ci=grid[L<=nll(b)+1.92]
print('T1 Worlds bonus (Elo pts):',round(b),'95% CI',ci.min(),ci.max())
# leave-one-year-out stability
for y in sorted(w.year.unique()):
    ww=w[w.year!=y]; f=lambda b: -np.sum(ww.win*np.log(1/(1+10**(-(ww.d+b)/SCALE)))+(1-ww.win)*np.log(1-1/(1+10**(-(ww.d+b)/SCALE))))
    print('  without',y,round(minimize_scalar(f,bounds=(-300,600),method='bounded').x))

"""A 'clutch' yardstick for T1's Worlds bonus: how much do teams beat their pre-game rating in domestic playoffs
(and finals) compared with the regular season? Bonus in Elo points per team (ML), 2014-2025, tier-1 leagues.
Pre-game ratings come from the same Elo run (record=True), so this is not frozen like the Worlds test.

    python clutch.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, re
from elo import *; from backtest_params import PARAMS, SCALE
from scipy.optimize import minimize_scalar
g=prep(); reg=team_regions(g)
e=Elo(**PARAMS); rec=e.run(g,reg,record=True)
R=pd.DataFrame(rec,columns=['idx','p','cross']).set_index('idx'); G=g.join(R)
G=G[(G.dt>='2014-01-01')&(G.dt<'2026-01-01')&(~G.cross.astype(bool))]
G['po']=G.tournament.str.contains(r'Playoffs|Regional Finals|Finals',regex=True)
long=pd.concat([G.assign(team=G.t1,win=G.win1,pp=G.p),G.assign(team=G.t2,win=1-G.win1,pp=1-G.p)])
long['d']=-SCALE*np.log10(1/long.pp-1)   # rating gap implied by p (scale 480)
def fitb(x):
    nll=lambda b:-np.sum(x.win*np.log(1/(1+10**(-(x.d+b)/SCALE)))+(1-x.win)*np.log(1-1/(1+10**(-(x.d+b)/SCALE))))
    r=minimize_scalar(nll,bounds=(-600,600),method='bounded'); gr=np.arange(-600,601,2); L=np.array([nll(v) for v in gr]); ci=gr[L<=r.fun+1.92]
    return r.x,ci.min(),ci.max()
rows=[]
for t,x in long[long.po].groupby('team'):
    if len(x)<60: continue
    b,lo,hi=fitb(x); rows.append(dict(team=t,league=x.league.mode()[0],po_games=len(x),excess=(x.win-x.pp).sum(),z=(x.win-x.pp).sum()/np.sqrt((x.pp*(1-x.pp)).sum()),bonus=b,lo=lo,hi=hi))
C=pd.DataFrame(rows).sort_values('bonus',ascending=False); C.to_csv('../data/clutch_playoffs.csv',index=False)
print(C.round(1).head(12).to_string(index=False)); print('...'); print(C.round(1).tail(5).to_string(index=False))
print('teams',len(C),'median bonus %.0f'%C.bonus.median(),'sd %.0f'%C.bonus.std(),'90th pct %.0f'%C.bonus.quantile(.9),'max %.0f'%C.bonus.max())
t=C[C.team=='T1']; print('T1 rank',(C.bonus>=t.bonus.iloc[0]).sum(),'of',len(C))

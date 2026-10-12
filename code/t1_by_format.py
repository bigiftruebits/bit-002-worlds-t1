"""Where in the tournament mechanism does T1's Worlds over-performance sit? Residuals (wins - expected, ratings
frozen at event start) split by series length (Bo1/Bo3/Bo5, inferred from each match's games), by stage
(knockout vs earlier), and by game position inside a series. Worlds vs MSI. Also a bonus fitted per series length.

    python t1_by_format.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
import re
from elo import *; from backtest_params import PARAMS, SCALE
from scipy.optimize import minimize_scalar
g=prep(); reg=team_regions(g)
intl=g[g.t_region.isin(INTL)].copy()
intl['event']=intl.tournament.str.replace(r'/(Main Event|Play-In|Group Stage|Knockout Stage|Bracket Stage|Rumble Stage)$','',regex=True)
intl=intl.sort_values('dt'); intl['gno']=intl.groupby('match_id').cumcount()+1
w1=intl.groupby('match_id').apply(lambda m: max(m.win1.sum(),(1-m.win1).sum()) if (m.t1==m.t1.iloc[0]).all() else None)
# winners' wins per match, robust to side swaps: count wins per team name
def bo(m):
    wins={}
    for r in m.itertuples(): w=r.t1 if r.win1==1 else r.t2; wins[w]=wins.get(w,0)+1
    k=max(wins.values()); return 2*k-1
B=intl.groupby('match_id').apply(bo).rename('bo'); intl=intl.join(B,on='match_id')
intl['ngames']=intl.groupby('match_id').match_id.transform('size')
starts=intl.groupby('event').dt.min(); starts=starts[starts>='2014-01-01'].sort_values()
rows=[]
for ev,st in starts.items():
    kind='Worlds' if 'Season World Championship' in ev else 'MSI' if 'Mid-Season Invitational' in ev else None
    if kind is None: continue
    e=Elo(**PARAMS); e.run(g,reg,until=st)
    for r in intl[intl.event==ev].itertuples():
        for team,opp,win,sgn in ((r.t1,r.t2,r.win1,1),(r.t2,r.t1,1-r.win1,-1)):
            if team!='T1': continue
            d=e.eff(team)-e.eff(opp); p=1/(1+10**(-d/SCALE))
            ko=bool(re.search(r'Knockout|Bracket',r.tournament)) or ('Main Event' in r.tournament and r.bo==5)
            rows.append(dict(kind=kind,year=st.year,event=ev,stage=r.tournament.split('/')[-1],bo=r.bo,gno=r.gno,ngames=r.ngames,ko=ko,d=d,p=p,win=win))
D=pd.DataFrame(rows); D.to_csv('../data/t1_by_format.csv',index=False)
def summ(x): return pd.Series(dict(games=len(x),wins=x.win.sum(),exp=x.p.sum(),excess=x.win.sum()-x.p.sum(),z=(x.win.sum()-x.p.sum())/np.sqrt((x.p*(1-x.p)).sum())))
print(D.groupby(['kind','bo']).apply(summ).round(2))
print(D.groupby(['kind','ko']).apply(summ).round(2))
D['pos']=np.where(D.gno==1,'game 1',np.where(D.gno==D.bo,'deciding game','other'))
print(D[D.bo>1].groupby(['kind','pos']).apply(summ).round(2))
def fit(x):
    nll=lambda b:-np.sum(x.win*np.log(1/(1+10**(-(x.d+b)/SCALE)))+(1-x.win)*np.log(1-1/(1+10**(-(x.d+b)/SCALE))))
    b=minimize_scalar(nll,bounds=(-400,800),method='bounded').x; gr=np.arange(-400,800); L=np.array([nll(v) for v in gr]); ci=gr[L<=nll(b)+1.92]
    return round(b),ci.min(),ci.max()
for k in ['Worlds','MSI']:
    for b in sorted(D.bo.unique()):
        x=D[(D.kind==k)&(D.bo==b)]
        if len(x)>5: print(k,'Bo%d'%b,len(x),'bonus',fit(x))
# test: is the Worlds bonus different between Bo5 and shorter? LR test of separate vs common bonus
x=D[D.kind=='Worlds']
def nllb(x,b): return -np.sum(x.win*np.log(1/(1+10**(-(x.d+b)/SCALE)))+(1-x.win)*np.log(1-1/(1+10**(-(x.d+b)/SCALE))))
bc=minimize_scalar(lambda b:nllb(x,b),bounds=(-400,800),method='bounded')
s5=minimize_scalar(lambda b:nllb(x[x.bo==5],b),bounds=(-400,800),method='bounded'); s1=minimize_scalar(lambda b:nllb(x[x.bo<5],b),bounds=(-400,800),method='bounded')
from scipy.stats import chi2
lr=2*(bc.fun-(s5.fun+s1.fun)); print('LR Bo5 vs shorter at Worlds: %.2f, p=%.3f'%(lr,chi2.sf(lr,1)))

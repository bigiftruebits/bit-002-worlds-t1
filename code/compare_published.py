"""Compare our pre-Worlds Elo with published ratings: lolproelo.com (as-of the day before each main event, 2014-2026)
and Riot's Global Power Rankings (elo and gprScore fields, 2024-2026).

    python compare_published.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, random
from scipy.optimize import minimize_scalar
from scipy.stats import spearmanr, pearsonr
from elo import *; from history import main_event; from sim import *
from teams2026 import CODE2NAME, REGION as R26
from backtest_params import PARAMS, SCALE
LPE_FIX={'Albus NoX Luna':'Albus NoX Luna','Griffin':'Griffin (Korean Team)','Evil Geniuses':'Evil Geniuses.NA','Unicorns of Love':'Unicorns of Love.CIS',
         'Dplus Kia':'Dplus KIA','Ninjas in Pyjamas':'Ninjas in Pyjamas.CN','KOI':'Movistar KOI'}
if __name__=='__main__':
    L=pd.read_csv('../raw/not_redistributed/lolproelo/lolproelo_preworlds.csv'); L['team']=L.name.map(lambda n: canon(LPE_FIX.get(n,n)))
    g=prep(); reg=team_regions(g)
    snap={2024:'2024-09-27',2025:'2025-10-06',2026:'2026-10-01'}
    def gpr(y):
        f={2024:'2024_worlds',2025:'2025_worlds',2026:'2026_current'}[y]
        d=pd.read_csv(f'../raw/not_redistributed/gpr_{f}_history.csv'); d=d[d.date.str.startswith(snap[y])]
        return {CODE2NAME.get(c,c):(e,s) for c,e,s in zip(d.code,d.elo,d.gpr)}
    tabs=[]; games=[]
    for y in range(2014,2027):
        if y<2026:
            ev=main_event(y); teams=ev['teams']; until=ev['start']
        else:
            teams=list(R26); until=None; ev=None
        e=Elo(**PARAMS); 
        if until is not None: e.run(g,reg,until=until)
        else: e.run(g,reg)
        lp=L[L.year==y].drop_duplicates('team').set_index('team').elo
        G=gpr(y) if y>=2024 else {}
        tab=pd.DataFrame(dict(year=y,team=teams,ours=[e.eff(t) for t in teams],lpe=[lp.get(t,np.nan) for t in teams],
                              gpr_elo=[G.get(t,(np.nan,np.nan))[0] for t in teams],gpr_score=[G.get(t,(np.nan,np.nan))[1] for t in teams]))
        tabs.append(tab)
        if ev is not None:
            gm=g[(g.dt>=ev['start'])&g.tournament.str.contains(f'{y} Season World Championship')]
            T=tab.set_index('team')
            for r in gm.itertuples():
                if r.t1 in T.index and r.t2 in T.index:
                    games.append(dict(year=y,t1=r.t1,t2=r.t2,win1=r.win1,**{f'd_{c}':T.loc[r.t1,c]-T.loc[r.t2,c] for c in ['ours','lpe','gpr_elo','gpr_score']}))
    T=pd.concat(tabs); D=pd.DataFrame(games)
    T.to_csv('../data/compare_published_ratings.csv',index=False); D.to_csv('../data/compare_published_games.csv',index=False)
    # 1. agreement
    print('== Rank agreement with our Elo (Worlds participants, Spearman rho)')
    rows=[]
    for y,t in T.groupby('year'):
        r=dict(year=y,n=t.lpe.notna().sum(),rho_lpe=spearmanr(t.ours,t.lpe,nan_policy='omit')[0])
        if t.gpr_score.notna().any(): r.update(rho_gpr_score=spearmanr(t.ours,t.gpr_score,nan_policy='omit')[0],rho_gpr_elo=spearmanr(t.ours,t.gpr_elo,nan_policy='omit')[0],rho_lpe_gpr=spearmanr(t.lpe,t.gpr_score,nan_policy='omit')[0])
        r['sd_ours']=t.ours.std(); r['sd_lpe']=t.lpe.std(); rows.append(r)
    A=pd.DataFrame(rows); print(A.round(2).to_string(index=False)); A.to_csv('../data/compare_agreement.csv',index=False)
    # 2. predictive accuracy on Worlds games (ratings frozen at event start)
    def nll(diff,win,s): p=np.clip(1/(1+10**(-diff/s)),1e-9,1-1e-9); return -np.mean(win*np.log(p)+(1-win)*np.log(1-p))
    print('\n== Worlds main-event games, log-loss (lower is better); scale fitted per system on the same games')
    for lab,sub,cols in [('2014-2025, ours vs lolproelo',D.dropna(subset=['d_lpe']),['ours','lpe']),
                         ('2024-2025, all four',D[D.year>=2024].dropna(),['ours','lpe','gpr_elo','gpr_score'])]:
        print(lab,'games',len(sub))
        for c in cols:
            x=sub['d_'+c]; s=minimize_scalar(lambda s:nll(x,sub.win1,s),bounds=(50,5000),method='bounded').x
            acc=((x>0)==(sub.win1==1)).mean()
            print(f'   {c:10s} nll@400={nll(x,sub.win1,400):.4f}  best scale={s:5.0f} nll={nll(x,sub.win1,s):.4f}  favourite won {acc:.1%}')
    # per-period, ours vs lpe
    for a,b in [(2014,2019),(2020,2025)]:
        sub=D[(D.year>=a)&(D.year<=b)].dropna(subset=['d_lpe'])
        print(f'   {a}-{b}: ours {nll(sub.d_ours,sub.win1,SCALE):.4f} (scale {SCALE}) | lpe {nll(sub.d_lpe,sub.win1,400):.4f} (400)  n={len(sub)}')
    
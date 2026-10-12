"""Bradley–Terry vs our Elo (Riccardo, 10 Oct 2026). For each Worlds 2014–2025: fit a Bradley–Terry model
(logistic, one strength per team, ridge penalty, games weighted by exp(-age/half-life)) on all games in the
`window` days before the event starts; predict every game of that Worlds with strengths frozen on day one, as
for Elo. Compare log loss, Brier score and accuracy with Elo's frozen predictions (out/intl_games_static.csv),
and redo T1's Worlds residual. Elo is the online, one-pass approximation of the same model; BT fits all games
jointly, so information flows backwards in time and through every region link at once.

    python bt_compare.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, scipy.sparse as sp, itertools, sys
from sklearn.linear_model import LogisticRegression
from elo import prep
from backtest_params import SCALE
g=prep(); D=pd.read_csv('../data/intl_games_static.csv'); W=D[D.kind=='Worlds'].copy()
intl=g[g.tournament.str.contains('Season World Championship')].copy()
intl['event']=intl.tournament.str.replace(r'/(Main Event|Play-In|Group Stage|Knockout Stage|Bracket Stage|Rumble Stage)$','',regex=True)
starts=intl.groupby('event').dt.min(); starts=starts[starts>='2014-01-01']
def fit(train,start,H,C):
    teams=sorted(set(train.t1)|set(train.t2)); ix={t:i for i,t in enumerate(teams)}; n=len(train)
    r=np.r_[np.arange(n),np.arange(n)]; c=np.r_[train.t1.map(ix).values,train.t2.map(ix).values]; v=np.r_[np.ones(n),-np.ones(n)]
    X=sp.csr_matrix((v,(r,c)),shape=(n,len(teams))); y=train.win1.values
    age=(start-train.dt).dt.days.values; w=0.5**(age/H); w=w*len(w)/w.sum()   # normalised: C keeps its meaning
    m=LogisticRegression(C=C,fit_intercept=False,max_iter=2000).fit(X,y,sample_weight=w)
    return dict(zip(teams,m.coef_[0]*SCALE/np.log(10)))   # in Elo-like points
def run(window,H,C):
    rows=[]
    for ev,st in starts.items():
        tr=g[(g.dt<st)&(g.dt>=st-pd.Timedelta(days=window))]
        s=fit(tr,st,H,C); gm=intl[intl.event==ev]
        for x in gm.itertuples():
            d=s.get(x.t1,np.nan)-s.get(x.t2,np.nan); rows.append((ev,st.year,x.t1,x.t2,d,x.win1))
    return pd.DataFrame(rows,columns=['event','year','t1','t2','d','win1']).dropna()
def score(d,win):
    p=1/(1+10**(-d/SCALE)); p=np.clip(p,1e-6,1-1e-6)
    return dict(logloss=-np.mean(win*np.log(p)+(1-win)*np.log(1-p)),brier=np.mean((p-win)**2),acc=np.mean((p>0.5)==(win==1)),n=len(win))
def t1(df):
    L=pd.concat([df.assign(team=df.t1,win=df.win1,dd=df.d),df.assign(team=df.t2,win=1-df.win1,dd=-df.d)])
    L=L[L.team=='T1']; p=1/(1+10**(-L.dd/SCALE)); return dict(games=len(L),wins=L.win.sum(),exp=round(p.sum(),1),excess=round(L.win.sum()-p.sum(),1),z=round((L.win.sum()-p.sum())/np.sqrt((p*(1-p)).sum()),2))
elo=W.rename(columns={'diff':'d'})
print('Elo (ours):',{k:round(v,4) for k,v in score(elo.d.values,elo.win1.values).items()},'T1',t1(elo))
res=[]
for window,H,C in itertools.product((365,730),(90,180,365,10**6),(3,10,30,100,1000)):
    b=run(window,H,C); sc=score(b.d.values,b.win1.values); res.append(dict(window=window,half_life=H,C=C,**sc,**{'T1_'+k:v for k,v in t1(b).items()}))
    print(res[-1],flush=True)
pd.DataFrame(res).to_csv('../data/bt_vs_elo.csv',index=False)

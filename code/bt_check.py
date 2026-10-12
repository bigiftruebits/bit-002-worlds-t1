"""Follow-up to bt_compare.py: is BT's smaller T1 residual because its 1–2 year window lets T1's own past
Worlds games raise T1's strength? Same best setting (730-day window, half-life 365, C=100), with and without
past Worlds games in the training data, and with a current-season-only window (as our Elo's seasonal reset).

    python bt_check.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
exec(open('bt_compare.py').read().split("elo=W.rename")[0])
def run2(window,H,C,drop_worlds=False,season=False):
    rows=[]
    for ev,st in starts.items():
        lo=pd.Timestamp(st.year,1,1) if season else st-pd.Timedelta(days=window)
        tr=g[(g.dt<st)&(g.dt>=lo)]
        if drop_worlds: tr=tr[~tr.tournament.str.contains('Season World Championship')]
        s=fit(tr,st,H,C); gm=intl[intl.event==ev]
        for x in gm.itertuples(): rows.append((ev,st.year,x.t1,x.t2,s.get(x.t1,np.nan)-s.get(x.t2,np.nan),x.win1))
    return pd.DataFrame(rows,columns=['event','year','t1','t2','d','win1']).dropna()
out=[]
for lab,kw in [('BT 2y, all games',{}),('BT 2y, past Worlds removed',dict(drop_worlds=True)),('BT season only',dict(season=True)),('BT season only, C=1000',dict(season=True,C=1000))]:
    C=kw.pop('C',100); b=run2(730,365,C,**kw); sc=score(b.d.values,b.win1.values); tt=t1(b)
    out.append(dict(model=lab,**{k:round(float(v),4) for k,v in sc.items()},**{'T1_'+k:v for k,v in tt.items()})); print(out[-1],flush=True)
elo=W.rename(columns={'diff':'d'}); out.append(dict(model='Elo (ours)',**{k:round(float(v),4) for k,v in score(elo.d.values,elo.win1.values).items()},**{'T1_'+k:v for k,v in t1(elo).items()}))
pd.DataFrame(out).to_csv('../data/bt_check.csv',index=False); print(out[-1])

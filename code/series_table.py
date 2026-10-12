"""Attach Leaguepedia match ids to data/intl_games_static.csv (same row order as residuals_intl.py) and build a
series table for Worlds and MSI: series length from the winner's game wins, chance of winning from frozen ratings.

    python series_table.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
from elo import *; from sim import p_series; from backtest_params import SCALE
g=prep(); intl=g[g.t_region.isin(INTL)].copy()
intl['event']=intl.tournament.str.replace(r'/(Main Event|Play-In|Group Stage|Knockout Stage|Bracket Stage|Rumble Stage)$','',regex=True)
starts=intl.groupby('event').dt.min().sort_values(); starts=starts[starts>='2014-01-01']
order=pd.concat([intl[intl.event==ev] for ev in starts.index])
D=pd.read_csv('../data/intl_games_static.csv'); assert len(D)==len(order) and (D.t1.values==order.t1.values).all()
D['match_id']=order.match_id.values; D['stage']=order.tournament.str.split('/').str[-1].values
rows=[]
for mid,m in D.groupby('match_id',sort=False):
    a,b=m.t1.iloc[0],m.t2.iloc[0]
    wa=sum((r.t1==a)==(r.win1==1) for r in m.itertuples()); wb=len(m)-wa
    da=m['diff'].iloc[0] if m.t1.iloc[0]==a else -m['diff'].iloc[0]
    ra=m.r1.iloc[0]; rb=m.r2.iloc[0]; bo=2*max(wa,wb)-1
    rows.append(dict(event=m.event.iloc[0],kind=m.kind.iloc[0],year=m.year.iloc[0],stage=m.stage.iloc[0],match_id=mid,a=a,b=b,ra=ra,rb=rb,bo=bo,wa=wa,wb=wb,p_game_a=1/(1+10**(-da/SCALE))))
S=pd.DataFrame(rows); S['p_series_a']=[p_series(p,b) for p,b in zip(S.p_game_a,S.bo)]
S.to_csv('../data/intl_series.csv',index=False); print(len(S),'series'); print(S.bo.value_counts())

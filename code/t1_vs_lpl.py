"""Korea vs China series (Bo3/Bo5) at Worlds, ratings frozen at each event's start (data/intl_series.csv):
T1's record against LPL teams vs the chance of it, and the other LCK teams'. Plus T1's 2023-25 knockout path.

    python t1_vs_lpl.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np
S=pd.read_csv('../data/intl_series.csv'); S=S[(S.kind=='Worlds')&(S.bo>=3)]
kc=S[((S.ra=='KR')&(S.rb=='CN'))|((S.ra=='CN')&(S.rb=='KR'))].copy()
f=kc.ra=='KR'
kc['kr']=np.where(f,kc.a,kc.b); kc['cn']=np.where(f,kc.b,kc.a); kc['p']=np.where(f,kc.p_series_a,1-kc.p_series_a)
kc['won']=np.where(f,kc.wa>kc.wb,kc.wb>kc.wa); kc['score']=[f'{max(x,y)}-{min(x,y)}' if w else f'{min(x,y)}-{max(x,y)}' for x,y,w in zip(kc.wa,kc.wb,kc.won)]
kc.to_csv('../data/lck_vs_lpl_series.csv',index=False)
def pb(p,k):
    d=np.array([1.0])
    for q in p: d=np.convolve(d,[1-q,q])
    return d
for nm,x in [('T1, all stages',kc[kc.kr=='T1']),('T1, main event',kc[(kc.kr=='T1')&(kc.stage!='Play-In')]),('T1 2023-25, all stages',kc[(kc.kr=='T1')&(kc.year>=2023)]),('other LCK',kc[kc.kr!='T1'])]:
    d=pb(x.p.values,0); w=int(x.won.sum())
    tail=d[w:].sum() if nm.startswith('T1') else d[:w+1].sum()
    print(f"{nm}: {w}/{len(x)} won, expected {x.p.sum():.2f}, underdog in {(x.p<0.5).sum()}, min {x.p.min():.3f}, tail P={tail:.3g} (1 in {1/tail:,.0f})")
print(kc[kc.kr=='T1'][['year','stage','cn','bo','score','p']].round(3).to_string(index=False))

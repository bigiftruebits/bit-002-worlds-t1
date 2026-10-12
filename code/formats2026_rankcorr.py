"""How well does each format's final order follow the ratings? (Riccardo, 9 Oct 2026)
For every simulated tournament, each team's result = series won, ties broken by fewer series lost (a single game counts as a series of one),
so a knockout result is the round reached, a Swiss record 3-0 beats 3-2, and a league result is the table. Spearman correlation between that result and
the pre-tournament rating, averaged over tournaments (ties get average ranks). Ratings alone, this year's 16 teams.

    python formats2026_rankcorr.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import random, numpy as np, pandas as pd
from scipy.stats import spearmanr, kendalltau
import formats as F
from sim import World
from backtest_params import SCALE
N=4000
elo,region=F.fields()[2026]
class RankWorld(World):
    def __init__(s,*a,**k): super().__init__(*a,**k); s.won={}; s.lost={}
    def play(s,a,b,bo):
        r=super().play(a,b,bo); s.won[r[0]]=s.won.get(r[0],0)+1; s.lost[r[1]]=s.lost.get(r[1],0)+1; return r
SEL=['Swiss + Bo5 knockouts (2023-26)','Groups + Bo5 knockouts (2014-22)','Single elimination Bo5, random','Single elimination Bo5, seeded',
     'Double elimination Bo5, seeded','Double round-robin league, Bo1','Swiss + Bo1 knockouts','Swiss + Bo3 knockouts','Swiss + Bo7 knockouts','League + playoffs, Bo1 then Bo5']
teams=list(elo); e=np.array([elo[t] for t in teams]); top4=set(sorted(teams,key=lambda t:-elo[t])[:4])
rows=[]
for name in SEL:
    rng=random.Random(7); P=None; rho=[]; tau=[]; t4=[]
    for _ in range(N):
        W=RankWorld(elo,region,scale=SCALE,rng=rng); F.W0=W
        if P is None: P=F.pots(list(elo))
        F.FORMATS[name](W,list(elo),P)
        sc=lambda t: W.won.get(t,0)-0.01*W.lost.get(t,0); w=np.array([sc(t) for t in teams]); rho.append(spearmanr(e,w)[0]); tau.append(kendalltau(e,w)[0])
        best=sorted(teams,key=lambda t:-sc(t))[:4]; t4.append(len(top4&set(best))/4)
    rows.append(dict(format=name,spearman=np.mean(rho),spearman_sd=np.std(rho),kendall=np.mean(tau),top4_in_top4=np.mean(t4)))
    print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv('../data/formats2026_rankcorr.csv',index=False)

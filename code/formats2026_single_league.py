"""Single round-robin league (each team plays every other once, 15 games each, Bo1) vs the double round-robin
in Figure 3 (Riccardo, 11 Oct 2026). Title odds with ratings alone and with T1's Worlds bonus (40,000 tournaments),
rank correlation of the final table with ratings (4,000), same seeds and method as formats2026_bonus/rankcorr.

    python formats2026_single_league.py      (about 3 minutes)

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import random, numpy as np, pandas as pd
from collections import Counter
from scipy.stats import spearmanr
import formats as F
from sim import World
from backtest_params import SCALE
class RankWorld(World):   # as in formats2026_rankcorr.py
    def __init__(s,*a,**k): super().__init__(*a,**k); s.won={}; s.lost={}
    def play(s,a,b,bo):
        r=super().play(a,b,bo); s.won[r[0]]=s.won.get(r[0],0)+1; s.lost[r[1]]=s.lost.get(r[1],0)+1; return r
elo0,region=F.fields()[2026]; N=40000; NR=4000
rows=[]
for rounds in (1,2):
    for b in (0,177):
        elo=dict(elo0); elo['T1']+=b; rng=random.Random(7); ch=Counter()
        for _ in range(N):
            W=World(elo,region,scale=SCALE,rng=rng); ch[F.league(W,list(elo),rounds=rounds)]+=1
        for t in ('Gen.G','Bilibili Gaming','Hanwha Life Esports','T1'): rows.append(dict(rounds=rounds,bonus=b,team=t,p=ch[t]/N))
    teams=list(elo0); e=np.array([elo0[t] for t in teams]); rng=random.Random(7); rho=[]
    for _ in range(NR):
        W=RankWorld(elo0,region,scale=SCALE,rng=rng); F.league(W,teams,rounds=rounds)
        w=np.array([W.won.get(t,0)-0.01*W.lost.get(t,0) for t in teams]); rho.append(spearmanr(e,w)[0])
    rows.append(dict(rounds=rounds,bonus=-1,team='spearman',p=np.mean(rho)))
D=pd.DataFrame(rows); D.to_csv('../data/formats2026_single_league.csv',index=False); print(D.to_string(index=False))

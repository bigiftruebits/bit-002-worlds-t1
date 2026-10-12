"""What each format costs and buys (Riccardo's review, 9 Oct 2026): length, predictable games, close high-stakes
series, and for the league how early the title is decided. This year's 16 Swiss-stage teams, ratings alone.

    python formats2026_tradeoffs.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import random, itertools, numpy as np, pandas as pd
from collections import Counter
import formats as F
from sim import World, p_game, p_series
from backtest_params import SCALE
N=8000
elo,region=F.fields()[2026]
class LogWorld(World):
    def __init__(s,*a,**k): super().__init__(*a,**k); s.log=[]
    def play(s,a,b,bo):
        p=p_game(s.elo[a],s.elo[b],s.scale); s.log.append((max(p,1-p),bo,max(p_series(p,bo),1-p_series(p,bo)))); return super().play(a,b,bo)
SEL=['Swiss + Bo5 knockouts (2023-26)','Swiss + Bo3 knockouts','Swiss + Bo7 knockouts','Double elimination Bo5, seeded','Groups + Bo5 knockouts (2014-22)',
     'Single elimination Bo5, random','Single elimination Bo5, seeded','Double round-robin league, Bo1','League + playoffs, Bo1 then Bo5']
rows=[]
for name in SEL:
    rng=random.Random(7); P=None; G=PR=CL=FR=0.0
    for _ in range(N):
        W=LogWorld(elo,region,scale=SCALE,rng=rng); F.W0=W
        if P is None: P=F.pots(list(elo))
        F.FORMATS[name](W,list(elo),P)
        g=W.games; G+=g
        # games are weighted by expected length via W.games; per-series weights from sim's own length cache
        ser=W.log
        PR+=sum(1 for pf,bo,ps in ser if pf>=0.75)/len(ser)          # share of matchups that are mismatches (fav wins a game >=75%)
        CL+=sum(1 for pf,bo,ps in ser if bo>=3 and ps<=0.65)          # close series (Bo3+), fav wins series <=65%
        FR+=np.mean([pf for pf,bo,ps in ser[:8]])                     # first round: favourite's single-game chance
    rows.append(dict(format=name,games=G/N,mismatch_share=PR/N,close_series=CL/N,first_round_fav=FR/N)); print(rows[-1],flush=True)
# league: when is the title decided? circle-method double round robin, 30 rounds of 8 games
teams=list(elo); n=len(teams); rounds=[]
arr=teams[:]
for r in range(n-1):
    rounds.append([(arr[i],arr[n-1-i]) for i in range(n//2)]); arr=[arr[0]]+[arr[-1]]+arr[1:-1]
rounds=rounds+[[(b,a) for a,b in rd] for rd in rounds]
rng=random.Random(3); left=[]; open_last=0
for _ in range(N):
    W=World(elo,region,scale=SCALE,rng=rng); w=Counter({t:0 for t in teams}); clinched=None
    for ri,rd in enumerate(rounds):
        for a,b in rd: w[W.play(a,b,1)[0]]+=1
        rem=len(rounds)-ri-1; top=w.most_common(2)
        if clinched is None and top[0][1]>top[1][1]+rem: clinched=rem
    left.append(clinched if clinched is not None else 0); open_last+= (clinched is None or clinched==0)
L=np.array(left)
rows.append(dict(format='league clinch',rounds_left_mean=L.mean(),rounds_left_median=float(np.median(L)),p_open_to_last_round=open_last/N,p_clinched_3plus_early=(L>=3).mean()))
print(rows[-1])
pd.DataFrame(rows).to_csv('../data/formats2026_tradeoffs.csv',index=False)

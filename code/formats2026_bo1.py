"""Football-style comparison (Riccardo, 9 Oct 2026): this year's Swiss stage, then single-game (Bo1) knockouts,
as in a football World Cup's knockout rounds. Ratings alone and with T1's Worlds bonus. 40k runs each.

    python formats2026_bo1.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, random
from collections import Counter
import formats as F
from sim import World
from backtest_params import SCALE
elo0,region=F.fields()[2026]; N=40000; rows=[]
for b in (0,177):
    elo=dict(elo0); elo['T1']+=b; rng=random.Random(7); P=None; ch=Counter(); tot=cg=0.0
    for _ in range(N):
        W=World(elo,region,scale=SCALE,rng=rng); F.W0=W
        if P is None: P=F.pots(list(elo0))
        c=F.FORMATS['Swiss + Bo1 knockouts'](W,list(elo),P); ch[c]+=1; tot+=W.games; cg+=W.team_games.get(c,0)
    for t in elo: rows.append(dict(bonus=b,team=t,p=ch[t]/N,games=tot/N,games_by_champion=cg/N))
    print(b,{k:round(v/N,3) for k,v in ch.most_common(5)},round(tot/N,1),round(cg/N,1),flush=True)
pd.DataFrame(rows).to_csv('../data/formats2026_bo1.csv',index=False)

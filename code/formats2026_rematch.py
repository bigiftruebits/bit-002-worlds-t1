"""How often is the final a rematch of a series already played in the same tournament? (Riccardo, 11 Oct 2026:
double elimination, as at MSI, can repeat the final.) This year's 16 Swiss teams, ratings alone, 10,000 tournaments,
same seed and field as formats2026_bonus.py. Prints the share per format; for double elimination also the share of finals that replay the upper-bracket final (added 11 Oct).

    python formats2026_rematch.py      (a few minutes)

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import random, pandas as pd
import formats as F
from sim import World
from backtest_params import SCALE
elo,region=F.fields()[2026]; N=10000
class LogWorld(World):
    def __init__(s,*a,**k): super().__init__(*a,**k); s.log=[]
    def play(s,a,b,bo):
        r=super().play(a,b,bo); s.log.append(frozenset((a,b))); return r
SEL=['Swiss + Bo5 knockouts (2023-26)','Groups + Bo5 knockouts (2014-22)','Single elimination Bo5, seeded','Double elimination Bo5, seeded','League + playoffs, Bo1 then Bo5']
rows=[]
for name in SEL:
    rng=random.Random(7); P=None; rem=0; ubf=0
    for _ in range(N):
        W=LogWorld(elo,region,scale=SCALE,rng=rng); F.W0=W
        if P is None: P=F.pots(list(elo))
        F.FORMATS[name](W,list(elo),P); fin=W.log[-1]; rem+= fin in W.log[:-1]
        if name.startswith('Double elimination'): ubf+= fin==W.log[-3]   # 16-team DE: upper-bracket final is the third-last series
    rows.append(dict(format=name,final_is_rematch=rem/N,final_replays_upper_final=(ubf/N if name.startswith('Double elimination') else None))); print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv('../data/formats2026_rematch.csv',index=False)

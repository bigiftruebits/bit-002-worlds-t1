"""TRUE beat: 2026 title odds per format with the IF beat's corrected ratings (T1 + Worlds bonus),
and the plain-Elo special case (bonus = 0). Also the bonus CI for the Verdict range.

    python formats2026_bonus.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, random, sys
from collections import Counter
import formats as F
from sim import World
from backtest_params import SCALE
BONUS=177; CI=(102,255)
elo0,region=F.fields()[2026]
SEL=['Swiss + Bo5 knockouts (2023-26)','Swiss + Bo3 knockouts','Swiss + Bo7 knockouts','Groups + Bo5 knockouts (2014-22)',
     'Single elimination Bo5, random','Single elimination Bo5, seeded','Double round-robin league, Bo1','Double elimination Bo5, seeded','League + playoffs, Bo1 then Bo5']
N=int(sys.argv[1]) if len(sys.argv)>1 else 40000
GAMES=[]
def run(elo,name,seed=7):
    rng=random.Random(seed); P=None; ch=Counter(); tot=0.0; champ_g=0.0
    for _ in range(N):
        W=World(elo,region,scale=SCALE,rng=rng); F.W0=W
        if P is None: P=F.pots(list(elo0))
        c=F.FORMATS[name](W,list(elo),P); ch[c]+=1; tot+=W.games; champ_g+=W.team_games.get(c,0)
    GAMES.append(dict(format=name,games_per_tournament=tot/N,games_by_champion=champ_g/N))
    return ch
rows=[]
for b in (0,CI[0],BONUS,CI[1]):
    elo=dict(elo0); elo['T1']+=b
    for name in (SEL if b in (0,BONUS) else SEL[:1]):
        ch=run(elo,name)
        for t in elo: rows.append(dict(bonus=b,format=name,team=t,p=ch[t]/N))
        print(b,name,{k:round(v/N,3) for k,v in ch.most_common(4)},flush=True)
pd.DataFrame(rows).to_csv('../data/formats2026_bonus.csv',index=False)
pd.DataFrame(GAMES).drop_duplicates('format').to_csv('../data/formats2026_games.csv',index=False); print(pd.DataFrame(GAMES).drop_duplicates('format').round(1).to_string(index=False))

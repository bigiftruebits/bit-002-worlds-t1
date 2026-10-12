"""Match quality per format: average rating of the two teams per matchup (series, unweighted) and per game, and share between two top-8 teams.
Plain ratings (no bonus), this year's 16 Swiss teams, 20,000 tournaments per format.

    python formats2026_quality.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, random
import formats as F
from sim import World
from backtest_params import SCALE
elo,region=F.fields()[2026]
top8=set(sorted(elo,key=lambda t:-elo[t])[:8]); field_mean=sum(elo.values())/len(elo)
SEL=['Swiss + Bo5 knockouts (2023-26)','Swiss + Bo3 knockouts','Swiss + Bo7 knockouts','Groups + Bo5 knockouts (2014-22)',
     'Single elimination Bo5, random','Single elimination Bo5, seeded','Double round-robin league, Bo1','Double elimination Bo5, seeded','League + playoffs, Bo1 then Bo5']
rows=[]
for name in SEL:
    rng=random.Random(11); P=None; G=E=TG=S=ES=TS=FS=FG=0.0; N=20000
    for _ in range(N):
        W=World(elo,region,scale=SCALE,rng=rng); W.top=top8; F.W0=W
        if P is None: P=F.pots(list(elo))
        F.FORMATS[name](W,list(elo),P); G+=W.games; E+=W.elo_games; TG+=W.top_games; S+=W.series; ES+=W.elo_series; TS+=W.top_series; FS+=W.fav_series; FG+=W.fav_games
    rows.append(dict(format=name,games=G/N,matchups=S/N,avg_elo_matchup=ES/S,matchup_above_field_mean=ES/S-field_mean,share_top8_matchups=TS/S,fav_game_p_matchup=FS/S,fav_game_p_game=FG/G,avg_elo=E/G,above_field_mean=E/G-field_mean,share_top8_vs_top8=TG/G))
    print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv('../data/formats2026_quality.csv',index=False)
print('field mean',round(field_mean,1))

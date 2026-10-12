"""How often is the MSI final a replay of an upper-bracket series? (Riccardo, 11 Oct 2026)
MSI bracket stage since 2023: 8 teams, double elimination, every series Bo5, no bracket reset.
1) Real MSI 2023-2026 brackets, from data/games_clean.parquet.
2) Simulation of the real MSI 2026 bracket (pairs as drawn), ratings on the eve (traj2026.csv), 100,000 runs.
3) Same bracket shape with this year's Worlds top 8 by rating, seeded 1v8, 4v5 | 2v7, 3v6, 100,000 runs.

    python msi_final_rematch.py      (a few minutes)

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import random, pandas as pd
from collections import Counter
from sim import World
from backtest_params import SCALE
import formats as F
# 1) real brackets
g=pd.read_parquet('../data/games_clean.parquet')
real=[]
for y in (2023,2024,2025,2026):
    m=g[g.tournament==f'{y} Mid-Season Invitational']
    s=m.groupby('match_id').agg(t1=('t1','first'),t2=('t2','first')).reset_index()
    pair=lambda mid: frozenset(s.set_index('match_id').loc[mid,['t1','t2']])
    fin=pair(f'{y} Mid-Season Invitational_Finals_1')
    ubs={pair(f'{y} Mid-Season Invitational_Bracket Round 2_{i}') for i in (1,2)}
    ubf=pair(f'{y} Mid-Season Invitational_Bracket Round 4_1')
    real.append(dict(year=y,final=' vs '.join(sorted(fin)),replay_of=('upper final' if fin==ubf else 'upper semi-final' if fin in ubs else 'none')))
R=pd.DataFrame(real); print(R.to_string(index=False))
# 2-3) simulation
def de8(W,qf,bo=5):
    ub1=[W.play(a,b,bo) for a,b in qf]
    ubs=[W.play(ub1[0][0],ub1[1][0],bo),W.play(ub1[2][0],ub1[3][0],bo)]
    ubf=W.play(ubs[0][0],ubs[1][0],bo)
    lb1=[W.play(ub1[0][1],ub1[1][1],bo)[0],W.play(ub1[2][1],ub1[3][1],bo)[0]]
    lb2=[W.play(lb1[0],ubs[1][1],bo)[0],W.play(lb1[1],ubs[0][1],bo)[0]]
    lb3=W.play(lb2[0],lb2[1],bo)[0]; lbf=W.play(lb3,ubf[1],bo)[0]
    fin=frozenset((ubf[0],lbf))
    return 'upper final' if fin==frozenset(ubf[:2]) else 'upper semi-final' if fin in {frozenset(x[:2]) for x in ubs} else 'none'
N=100000; out=[]
T=pd.read_csv('../data/traj2026.csv',parse_dates=['date']); e=T[T.date<='2026-07-02 23:59'].sort_values('date').groupby('team').tail(1).set_index('team').elo.to_dict()
qf26=[('Hanwha Life Esports','Team Secret Whales'),('Top Esports','G2 Esports'),('FURIA','LYON'),('T1','Bilibili Gaming')]
elo,region=F.fields()[2026]; top=sorted(elo,key=lambda t:-elo[t])[:8]; qfw=[(top[0],top[7]),(top[3],top[4]),(top[1],top[6]),(top[2],top[5])]
for name,ratings,qf in [('MSI 2026 bracket, ratings on 2 July',e,qf26),("Worlds 2026 top 8, seeded",elo,qfw)]:
    rng=random.Random(7); c=Counter()
    for _ in range(N): c[de8(World(ratings,{t:'' for t in ratings},scale=SCALE,rng=rng),qf)]+=1
    for k in ('upper final','upper semi-final','none'): out.append(dict(case=name,replay_of=k,share=c[k]/N))
S=pd.DataFrame(out); print(S.to_string(index=False))
R.to_csv('../data/msi_final_rematch_real.csv',index=False); S.to_csv('../data/msi_final_rematch_sim.csv',index=False)

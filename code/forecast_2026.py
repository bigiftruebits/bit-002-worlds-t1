"""Forecast Worlds 2026 (play-in 15-18 Oct, final 14 Nov) from every result up to the CBLOL final of 10 Oct 2026.
All regional qualifiers are decided; the play-in uses the real draw (FURIA v MVK Esports, Cloud9 v Karmine Corp,
double elimination, Bo5). Swiss round-1 pairings are still drawn by the simulator (the real draw comes after the play-in).

    python forecast_2026.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, random, sys
from collections import Counter, defaultdict
from elo import *; from sim import *; from teams2026 import *
from backtest_params import PARAMS, SCALE

def our_elo():
    g=prep(); reg=team_regions(g)
    extra=[]
    for r in LATE_RESULTS:
        a,b,s1,s2,dt=r[:5]
        if len(r)>5: seq=list(r[5])                       # game order known
        else: seq=[1]*s1+[0]*s2; random.Random(0).shuffle(seq)
        tr='Brazil' if a in ('LOUD','LØS','FURIA') else 'North America'
        for i,w in enumerate(seq): extra.append(dict(dt=pd.Timestamp(dt)+pd.Timedelta(minutes=40*i),tournament='late',match_id='late',t1=a,t2=b,win1=w,t_region=tr,league=''))
    g=pd.concat([g,pd.DataFrame(extra)]).sort_values('dt').reset_index(drop=True)
    e=Elo(**PARAMS); e.run(g,reg)
    return {t:e.eff(t) for t in REGION}

def gpr_elo(field='gpr',date='2026-10-01'):
    d=pd.read_csv('../raw/not_redistributed/gpr_2026_current_history.csv'); d=d[d.date.str.startswith(date)]
    m={CODE2NAME[c]:v for c,v in zip(d.code,d[field]) if c in CODE2NAME}
    return {t:m[t] for t in REGION}

def one_tournament(rng,elo,scale,log=None):
    W=World(elo,REGION,scale=scale,rng=rng)
    # --- remaining regional matches ---
    # all decided: TL 3-1 LYON (LCS final, 4 Oct), LØS 3-2 FURIA (CBLOL final, 10 Oct)
    lcs1,lcs2,lcs3='Team Liquid','LYON','Cloud9'
    cb1,cb2='LØS','FURIA'
    # --- play-in, real draw of 10 Oct: FURIA v MVK, Cloud9 v Karmine Corp; double elimination, Bo5 ---
    pi=['FURIA','MVK Esports','Cloud9','Karmine Corp']
    piw=double_elim4(W,pi)
    pools=[['Gen.G',"Anyone's Legend",lcs1,'G2 Esports'],
           ['Team Secret Whales',cb1,'Hanwha Life Esports','Bilibili Gaming'],
           [lcs2,'Movistar KOI','T1','Top Esports'],
           ['CTBC Flying Oyster','Invictus Gaming','Dplus KIA',piw]]
    same=lambda a,b: REGION[a]==REGION[b]
    r1=cross_pairing(pools[0],pools[3],rng,forbid=same)+cross_pairing(pools[1],pools[2],rng,forbid=same)
    q,rec=swiss(W,r1)
    champ,res=swiss_knockout(W,q)
    stage={t:'Swiss' for t in rec}; stage.update(res)
    for t in pi:
        if t!=piw: stage[t]='Play-In'
    stage['_lcs']=(lcs1,lcs2,lcs3); stage['_cb']=(cb1,cb2)
    return champ,stage

def forecast(elo,scale,N=100000,seed=2026):
    rng=random.Random(seed); out=defaultdict(Counter); seeds=Counter()
    for _ in range(N):
        c,st=one_tournament(rng,elo,scale)
        seeds[('LCS',)+st.pop('_lcs')]+=1; seeds[('CBLOL',)+st.pop('_cb')]+=1
        for t,s in st.items(): out[t][s]+=1
    rows=[]
    for t in REGION:
        s=out[t]; rows.append(dict(team=t,region=REGION[t],elo=round(elo[t]),
           p_attend=sum(s.values())/N, p_swiss=(sum(s.values())-s['Play-In'])/N,
           p_knockouts=sum(s[k] for k in ('QF','SF','F','W'))/N, p_semis=sum(s[k] for k in ('SF','F','W'))/N,
           p_final=(s['F']+s['W'])/N, p_win=s['W']/N))
    return pd.DataFrame(rows).sort_values('p_win',ascending=False).reset_index(drop=True), seeds

def with_bonus(elo,team='T1',b=177):
    e=dict(elo); e[team]+=b; return e

if __name__=='__main__':
    N=int(sys.argv[1]) if len(sys.argv)>1 else 100000
    pd.set_option('display.width',200)
    ours=our_elo(); fo,seeds=forecast(ours,SCALE,N); fo.to_csv('../data/forecast2026_our_elo.csv',index=False)
    print('OUR ELO'); print(fo.round(3).to_string())
    import os
    if os.path.exists('../raw/not_redistributed/gpr_2026_current_history.csv'):   # Riot's rankings: not redistributed
        gp=gpr_elo('gpr'); fg,_=forecast(gp,400,N); fg.to_csv('../data/forecast2026_gpr.csv',index=False)
        print('GPR SCORE (scale 400)'); print(fg.round(3).to_string())
    else: print('GPR comparison skipped: recollect the Global Power Rankings (DATA_MANIFEST.md)')
    fb,_=forecast(with_bonus(ours),SCALE,N); fb.to_csv('../data/forecast2026_our_elo_T1bonus.csv',index=False)
    print('OUR ELO + T1 WORLDS BONUS'); print(fb.round(3).to_string())
    print({k:v/N for k,v in seeds.most_common(10)})

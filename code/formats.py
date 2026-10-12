"""Does the tournament format reward the best team?
Same 16-team field, same ratings, different formats. Run on each Worlds main-event field 2014-2026.

    python formats.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, random, math, itertools, sys
from collections import Counter
from sim import *
from backtest_params import SCALE

def pots(field):                      # 4 pots of 4 by rating
    s=sorted(field,key=lambda t:-W0.elo[t]); return [s[i:i+4] for i in range(0,16,4)]

def draw_groups(W,P):
    for _ in range(2000):
        cols=[p[:] for p in P]; [W.rng.shuffle(c) for c in cols]
        groups=[[cols[k][i] for k in range(4)] for i in range(4)]
        if all(len({W.region[t] for t in g})==4 for g in groups): return groups
    return groups

def swiss_variant(W,P,bo_rule):
    same=lambda a,b: W.region[a]==W.region[b]
    r1=cross_pairing(P[0],P[3],W.rng,forbid=same)+cross_pairing(P[1],P[2],W.rng,forbid=same)
    rec={t:[0,0] for p in r1 for t in p}; played=set(); q={}; pairs=r1
    for rnd in range(1,6):
        for a,b in pairs:
            dec=rec[a][0]==2 or rec[a][1]==2
            bo={'worlds':3 if dec else 1,'all1':1,'all3':3}[bo_rule]
            w,l=W.play(a,b,bo); rec[w][0]+=1; rec[l][1]+=1; played.add(frozenset((a,b)))
            if rec[w][0]==3: q[w]=f'3-{rec[w][1]}'
        if rnd==5: break
        pools={}
        for t,(w,l) in rec.items():
            if w<3 and l<3: pools.setdefault((w,l),[]).append(t)
        pairs=[]
        for k in sorted(pools): pairs+=random_pairing(pools[k],W.rng,forbid=lambda a,b:frozenset((a,b)) in played)
    return q

def bracket(W,qf,bo=5):
    sf=[W.play(a,b,bo)[0] for a,b in qf]
    f=[W.play(sf[0],sf[1],bo)[0],W.play(sf[2],sf[3],bo)[0]]
    return W.play(f[0],f[1],bo)[0]

def ko_from_swiss(W,q,bo=5):
    t30=[t for t,r in q.items() if r=='3-0']; t31=[t for t,r in q.items() if r=='3-1']; t32=[t for t,r in q.items() if r=='3-2']
    for x in (t30,t31,t32): W.rng.shuffle(x)
    rest=t31+t32[2:]; W.rng.shuffle(rest)
    return bracket(W,[(t30[0],t32[0]),(rest[0],rest[1]),(t30[1],t32[1]),(rest[2],rest[3])],bo)

def ko_from_groups(W,top2,bo=5):
    n=4
    while True:
        perm=list(range(n)); W.rng.shuffle(perm)
        if any(perm[i]==i for i in range(n)): continue
        qf=[(top2[i][0],top2[perm[i]][1]) for i in range(n)]; W.rng.shuffle(qf)
        grp={t:i for i,(a,b) in enumerate(top2) for t in (a,b)}
        if len({grp[t] for m in qf[:2] for t in m})==4: return bracket(W,qf,bo)

def bracket_order(W,field,seeded=True):
    """16 teams in first-round order (pairs i,i+1). Seeded: 1v16, 8v9, ... ; random: random draw. Same-region pairs avoided."""
    s=sorted(field,key=lambda t:-W.elo[t])
    same=lambda a,b: W.region[a]==W.region[b]
    if seeded:
        order=[1,16,8,9,5,12,4,13,3,14,6,11,7,10,2,15]; s=[s[i-1] for i in order]
        for i in range(0,16,2):
            if same(s[i],s[i+1]):
                for d in (2,-2,4,-4,6,-6,8,-8,10,-10,12,-12,14,-14):
                    j=i+d
                    if 0<=j<16 and not same(s[i],s[j+1]) and not same(s[j],s[i+1]):
                        s[i+1],s[j+1]=s[j+1],s[i+1]; break
        return s
    pairs=random_pairing(list(field),W.rng,forbid=same); return [t for p in pairs for t in p]

def double_elim(W,order,bo=5):
    """Full double elimination for 2^k teams, all series Bo`bo`, no bracket reset in the grand final (as at MSI).
    Upper-bracket losers drop into the lower bracket in reverse order, to delay rematches. 16 teams: 30 series.
    Added 9 Oct 2026 (Riccardo: a single double-elimination tree, no Swiss stage)."""
    r=[W.play(order[i],order[i+1],bo) for i in range(0,len(order),2)]
    ub=[x[0] for x in r]; L=[x[1] for x in r]
    lb=[W.play(L[i],L[i+1],bo)[0] for i in range(0,len(L),2)]
    while len(ub)>1:
        r=[W.play(ub[i],ub[i+1],bo) for i in range(0,len(ub),2)]
        ub=[x[0] for x in r]; L=[x[1] for x in r][::-1]
        lb=[W.play(lb[i],L[i],bo)[0] for i in range(len(lb))]
        if len(lb)>1: lb=[W.play(lb[i],lb[i+1],bo)[0] for i in range(0,len(lb),2)]
    return W.play(ub[0],lb[0],bo)[0]

def single_elim(W,field,seeded=True,bo=5):
    """16-team bracket, Bo5. Seeded: 1v16, 8v9, ... (top seeds meet late). Random: random draw.
    Both avoid same-region first-round matches, as Worlds does (added 9 Oct 2026, Riccardo's review)."""
    s=sorted(field,key=lambda t:-W.elo[t])
    same=lambda a,b: W.region[a]==W.region[b]
    if seeded:
        order=[1,16,8,9,5,12,4,13,3,14,6,11,7,10,2,15]; s=[s[i-1] for i in order]
        # fix same-region pairs by swapping the lower-seeded team with the lower seed of the nearest pair that allows it
        for i in range(0,16,2):
            if same(s[i],s[i+1]):
                for d in (2,-2,4,-4,6,-6,8,-8,10,-10,12,-12,14,-14):
                    j=i+d
                    if 0<=j<16 and not same(s[i],s[j+1]) and not same(s[j],s[i+1]):
                        s[i+1],s[j+1]=s[j+1],s[i+1]; break
    else:
        pairs=random_pairing(list(field),W.rng,forbid=same); s=[t for p in pairs for t in p]
    r=s
    while len(r)>1: r=[W.play(r[i],r[i+1],bo)[0] for i in range(0,len(r),2)]
    return r[0]

def double_elim8(W,qf,bo=5):
    """8-team double elimination, all Bo5 (MSI-style bracket stage). qf: 4 first-round pairs, halves [0,1] and [2,3]."""
    ub1=[W.play(a,b,bo) for a,b in qf]                       # (winner, loser)
    ubs=[W.play(ub1[0][0],ub1[1][0],bo),W.play(ub1[2][0],ub1[3][0],bo)]
    ubf=W.play(ubs[0][0],ubs[1][0],bo)
    lb1=[W.play(ub1[0][1],ub1[1][1],bo)[0],W.play(ub1[2][1],ub1[3][1],bo)[0]]
    lb2=[W.play(lb1[0],ubs[1][1],bo)[0],W.play(lb1[1],ubs[0][1],bo)[0]]   # cross to delay rematches
    lb3=W.play(lb2[0],lb2[1],bo)[0]
    lbf=W.play(lb3,ubf[1],bo)[0]
    return W.play(ubf[0],lbf,bo)[0]

def de_from_swiss(W,q,bo=5):
    t30=[t for t,r in q.items() if r=='3-0']; t31=[t for t,r in q.items() if r=='3-1']; t32=[t for t,r in q.items() if r=='3-2']
    for x in (t30,t31,t32): W.rng.shuffle(x)
    rest=t31+t32[2:]; W.rng.shuffle(rest)
    return double_elim8(W,[(t30[0],t32[0]),(rest[0],rest[1]),(t30[1],t32[1]),(rest[2],rest[3])],bo)

def league(W,field,rounds=2):
    wins=Counter({t:0 for t in field})
    for _ in range(rounds):
        for a,b in itertools.combinations(field,2): wins[W.play(a,b,1)[0]]+=1
    top=max(wins.values()); c=[t for t in field if wins[t]==top]
    return c[0] if len(c)==1 else tiebreak(W,c)[0]

def league_playoffs(W,field,top=8,bo=5):
    """League then playoffs, as in the NBA (and, with a double-elimination bracket, the LCK): one round-robin of single
    games, then the top `top` by wins (ties broken at random) play a seeded single-elimination bracket, 1v8, 4v5, 2v7, 3v6,
    Bo`bo`. Added 9 Oct 2026 (Riccardo)."""
    wins={t:0 for t in field}
    for a,b in itertools.combinations(field,2): wins[W.play(a,b,1)[0]]+=1
    order=sorted(field,key=lambda t:(-wins[t],W.rng.random()))[:top]
    r=[order[i-1] for i in (1,8,4,5,2,7,3,6)]
    while len(r)>1: r=[W.play(r[i],r[i+1],bo)[0] for i in range(0,len(r),2)]
    return r[0]

FORMATS={
 'Groups + Bo5 knockouts (2014-22)': lambda W,F,P: ko_from_groups(W,group_stage(W,draw_groups(W,P))),
 'Swiss + Bo5 knockouts (2023-26)':  lambda W,F,P: ko_from_swiss(W,swiss_variant(W,P,'worlds')),
 'Swiss, every match Bo1':           lambda W,F,P: ko_from_swiss(W,swiss_variant(W,P,'all1')),
 'Swiss, every match Bo3':           lambda W,F,P: ko_from_swiss(W,swiss_variant(W,P,'all3')),
 'Swiss + Bo3 knockouts':            lambda W,F,P: ko_from_swiss(W,swiss_variant(W,P,'worlds'),bo=3),
 'Swiss + Bo7 knockouts':            lambda W,F,P: ko_from_swiss(W,swiss_variant(W,P,'worlds'),bo=7),
 'Swiss + Bo1 knockouts':            lambda W,F,P: ko_from_swiss(W,swiss_variant(W,P,'worlds'),bo=1),   # football-style single-game knockouts (9 Oct)
 'Groups played Bo3 + Bo5 knockouts':lambda W,F,P: ko_from_groups(W,group_stage(W,draw_groups(W,P),rounds=1,bo=3)),
 'Single elimination Bo5, seeded':   lambda W,F,P: single_elim(W,F,True),
 'Single elimination Bo5, random':   lambda W,F,P: single_elim(W,F,False),
 'Double round-robin league, Bo1':   lambda W,F,P: league(W,F),
 'Swiss + double-elimination knockouts': lambda W,F,P: de_from_swiss(W,swiss_variant(W,P,'worlds')),
 'Double elimination Bo5, seeded':   lambda W,F,P: double_elim(W,bracket_order(W,F,True)),
 'League + playoffs, Bo1 then Bo5':  lambda W,F,P: league_playoffs(W,F),
}

def fields():
    from elo import Elo, prep, team_regions; from history import main_event; from backtest_params import PARAMS
    g=prep(); reg=team_regions(g); out={}
    for y in range(2014,2026):
        ev=main_event(y); e=Elo(**PARAMS); e.run(g,reg,until=ev['start'])
        out[y]=({t:e.eff(t) for t in ev['teams']},{t:e.home.get(t) for t in ev['teams']})
    from forecast_2026 import our_elo
    from teams2026 import REGION
    o=our_elo(); f26=['Gen.G',"Anyone's Legend",'Team Liquid','G2 Esports','Team Secret Whales','LØS','Hanwha Life Esports','Bilibili Gaming',
                      'LYON','Movistar KOI','T1','Top Esports','CTBC Flying Oyster','Invictus Gaming','Dplus KIA','Karmine Corp']
    out[2026]=({t:o[t] for t in f26},{t:REGION[t] for t in f26})
    return out

if __name__=='__main__':
    N=int(sys.argv[1]) if len(sys.argv)>1 else 20000
    rows=[]
    for y,(elo,region) in fields().items():
        F=list(elo); rank={t:i+1 for i,t in enumerate(sorted(F,key=lambda t:-elo[t]))}
        for name,fn in FORMATS.items():
            rng=random.Random(abs(hash((y,name)))%2**32); globals()['W0']=World(elo,region,scale=SCALE,rng=rng); P=pots(F)
            ch=Counter(fn(W0,F,P) for _ in range(N))
            p=np.array([ch[t]/N for t in F]); r=np.array([rank[t] for t in F])
            H=-sum(x*math.log(x) for x in p if x>0)
            rows.append(dict(year=y,format=name,p_best=float(p[r==1][0]),p_top2=float(p[r<=2].sum()),p_top4=float(p[r<=4].sum()),
                             mean_rank=float((p*r).sum()),eff_contenders=math.exp(H)))
        print(y,'done',flush=True)
    R=pd.DataFrame(rows); R.to_csv('../data/formats_by_year.csv',index=False)
    S=R.groupby('format')[['p_best','p_top2','p_top4','mean_rank','eff_contenders']].mean().sort_values('p_best',ascending=False)
    S.to_csv('../data/formats_summary.csv'); print(S.round(3).to_string())

"""Monte Carlo simulator for League of Legends Worlds formats (2014-2026).
Game win probability from Elo; series probabilities computed exactly from the game probability
(games treated as independent).

    python sim.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import numpy as np, itertools, random
from collections import Counter, defaultdict

def p_game(e1,e2,scale=400.): return 1/(1+10**(-(e1-e2)/scale))
def p_series(p,bo):
    """P(win a best-of-`bo` series) with independent games of win prob p (first to (bo+1)/2)."""
    from math import comb
    k=(bo+1)//2
    return sum(comb(k-1+j,j)*p**k*(1-p)**j for j in range(k))

def series_len(p,bo):
    """Expected number of games in a best-of-`bo` series (first to (bo+1)/2), games independent with win prob p."""
    from math import comb
    k=(bo+1)//2; e=0.0
    for j in range(k):          # winner takes k, loser j
        e+=(k+j)*comb(k-1+j,j)*(p**k*(1-p)**j+(1-p)**k*p**j)
    return e

class World:
    def __init__(self,elo,region,scale=400.,rng=None):
        self.elo=elo; self.region=region; self.scale=scale
        self.rng=rng or random.Random()
        self._c={}; self._l={}; self.games=0.0; self.team_games={}; self.elo_games=0.0; self.top_games=0.0; self.top=set(); self.series=0; self.elo_series=0.0; self.top_series=0; self.fav_series=0.0; self.fav_games=0.0
    def pwin(self,a,b,bo):
        k=(a,b,bo)
        if k not in self._c: self._c[k]=p_series(p_game(self.elo[a],self.elo[b],self.scale),bo)
        return self._c[k]
    def play(self,a,b,bo):
        k=(a,b,bo)
        if k not in self._l: self._l[k]=series_len(p_game(self.elo[a],self.elo[b],self.scale),bo)
        pg=p_game(self.elo[a],self.elo[b],self.scale); pf=max(pg,1-pg); self.fav_series+=pf
        g=self._l[k]; self.fav_games+=g*pf; self.series+=1; self.elo_series+=(self.elo[a]+self.elo[b])/2; self.top_series+=(a in self.top and b in self.top); self.games+=g; self.elo_games+=g*(self.elo[a]+self.elo[b])/2; self.top_games+=g*(a in self.top and b in self.top); self.team_games[a]=self.team_games.get(a,0)+g; self.team_games[b]=self.team_games.get(b,0)+g
        return (a,b) if self.rng.random()<self.pwin(a,b,bo) else (b,a)   # (winner, loser)

# ---------- pairing helpers ----------
def random_pairing(teams,rng,forbid=lambda a,b:False,tries=200):
    """Random perfect matching of teams avoiding forbidden pairs (falls back to allowing them)."""
    for _ in range(tries):
        t=teams[:]; rng.shuffle(t); pairs=[]; ok=True
        while t:
            a=t.pop(0); opts=[b for b in t if not forbid(a,b)]
            if not opts: ok=False; break
            b=rng.choice(opts); t.remove(b); pairs.append((a,b))
        if ok: return pairs
    t=teams[:]; rng.shuffle(t); return [(t[i],t[i+1]) for i in range(0,len(t),2)]

def cross_pairing(A,B,rng,forbid=lambda a,b:False,tries=500):
    for _ in range(tries):
        b=B[:]; rng.shuffle(b)
        if not any(forbid(x,y) for x,y in zip(A,b)): return list(zip(A,b))
    b=B[:]; rng.shuffle(b); return list(zip(A,b))

# ---------- Swiss stage (2023+) ----------
def swiss(W,round1_pairs,bo_rule='worlds'):
    """16-team Swiss, first to 3 wins advance. round1_pairs: list of 8 pairs.
    Matches where either team can advance/be eliminated are Bo3, others Bo1.
    From round 2 pairings are drawn randomly within record pools, avoiding rematches."""
    rec={t:[0,0] for p in round1_pairs for t in p}; played=set(); qualified={}
    pairs=round1_pairs
    for rnd in range(1,6):
        for a,b in pairs:
            dec= rec[a][0]==2 or rec[a][1]==2
            w,l=W.play(a,b,3 if dec else 1)
            rec[w][0]+=1; rec[l][1]+=1; played.add(frozenset((a,b)))
            if rec[w][0]==3: qualified[w]=f'3-{rec[w][1]}'
        if rnd==5: break
        pools=defaultdict(list)
        for t,(w,l) in rec.items():
            if w<3 and l<3: pools[(w,l)].append(t)
        pairs=[]
        for k in sorted(pools):
            pairs+=random_pairing(pools[k],W.rng,forbid=lambda a,b:frozenset((a,b)) in played)
    return qualified, rec

def swiss_knockout(W,qualified):
    """QF: 3-0 teams face 3-2 teams, 3-1 teams face the rest; the two 3-0 teams go to opposite halves."""
    rng=W.rng
    t30=[t for t,r in qualified.items() if r=='3-0']; t31=[t for t,r in qualified.items() if r=='3-1']; t32=[t for t,r in qualified.items() if r=='3-2']
    rng.shuffle(t30); rng.shuffle(t31); rng.shuffle(t32)
    opp30=t32[:2]; rest=t31+t32[2:]; rng.shuffle(rest)
    qf=[(t30[0],opp30[0]),(rest[0],rest[1]),(t30[1],opp30[1]),(rest[2],rest[3])]   # halves: [0,1] and [2,3]
    return bracket8(W,qf)

def bracket8(W,qf):
    r={}
    sf=[W.play(a,b,5)[0] for a,b in qf]
    for a,b in qf:
        for t in (a,b): r[t]='QF'
    f=[W.play(sf[0],sf[1],5),W.play(sf[2],sf[3],5)]
    for t in sf: r[t]='SF'
    for w,l in f: r[w]='F'
    champ,ru=W.play(f[0][0],f[1][0],5); r[champ]='W'
    return champ,r

# ---------- group stage (2014-2022) ----------
def tiebreak(W,teams):
    """Order tied teams with Bo1 tiebreaker games (2-way: one game; k-way: mini round robin, recursive)."""
    if len(teams)<=1: return teams
    if len(teams)==2:
        w,l=W.play(teams[0],teams[1],1); return [w,l]
    wins=Counter({t:0 for t in teams})
    for a,b in itertools.combinations(teams,2): wins[W.play(a,b,1)[0]]+=1
    out=[]
    for v in sorted(set(wins.values()),reverse=True):
        grp=[t for t in teams if wins[t]==v]
        if len(grp)==len(teams): W.rng.shuffle(grp); out+=grp
        else: out+=tiebreak(W,grp)
    return out

def group_stage(W,groups,rounds=2,bo=1):
    """Round-robin groups (default: double round robin, Bo1); returns [(1st,2nd)] per group.
    Ties: head-to-head among the tied teams first, then Bo1 tiebreaker games (Riot's rule)."""
    res=[]
    for g in groups:
        wins=Counter({t:0 for t in g}); h2h=Counter()
        for _ in range(rounds):
            for a,b in itertools.combinations(g,2):
                w,l=W.play(a,b,bo); wins[w]+=1; h2h[(w,l)]+=1
        order=[]
        for v in sorted(set(wins.values()),reverse=True):
            grp=[t for t in g if wins[t]==v]
            if len(grp)==1 or len(order)>=2: order+=grp; continue
            hw={t:sum(h2h[(t,u)] for u in grp if u!=t) for t in grp}
            for hv in sorted(set(hw.values()),reverse=True):
                sub=[t for t in grp if hw[t]==hv]
                order+= sub if len(sub)==1 else tiebreak(W,sub)
        res.append((order[0],order[1]))
    return res

def group_knockout(W,top2):
    """Group winners face runners-up from another group; teams from the same group in opposite halves."""
    rng=W.rng; n=len(top2)
    for _ in range(1000):
        perm=list(range(n)); rng.shuffle(perm)
        if any(perm[i]==i for i in range(n)): continue
        qf=[(top2[i][0],top2[perm[i]][1]) for i in range(n)]
        order=list(range(n)); rng.shuffle(order); qf=[qf[i] for i in order]
        grp={t:i for i,(a,b) in enumerate(top2) for t in (a,b)}
        halves=[{grp[t] for m in qf[:2] for t in m},{grp[t] for m in qf[2:] for t in m}]
        # each group's two teams must be split across halves -> each half contains each group once
        if len(halves[0])==4 and len(halves[1])==4: return bracket8(W,qf)
    return bracket8(W,qf)

# ---------- play-in 2026: 4-team double elimination, Bo5 ----------
def double_elim4(W,teams):
    a,b,c,d=teams
    w1,l1=W.play(a,b,5); w2,l2=W.play(c,d,5)
    uw,ul=W.play(w1,w2,5)
    lw,_=W.play(l1,l2,5)
    lf,_=W.play(ul,lw,5)
    return W.play(uw,lf,5)[0]

def run_many(fn,N,seed=0):
    rng=random.Random(seed); champs=Counter(); stage=defaultdict(Counter)
    for _ in range(N):
        c,r=fn(rng)
        champs[c]+=1
        for t,s in r.items(): stage[t][s]+=1
    return champs,stage

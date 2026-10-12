"""Football parallel (Riccardo, 9 Oct 2026): how would the 2026 FIFA World Cup knockout stage have ended with
longer series? World Football Elo computed with eloratings.net's published method (K 60 World Cup, 50 continental
finals, 40 qualifiers and major tournaments, 30 other tournaments, 20 friendlies; goal-difference multiplier;
+100 for the home side) from martj42/international_results, frozen on 10 June 2026 (eve of the tournament).
Then the real round-of-32 bracket (rebuilt from the real results) is replayed 200,000 times with each tie decided by
1, 3, 5 or 7 matches; one match is won with probability = Elo expected score (a draw counts half: extra time and
penalties as a coin flip). Hosts (USA, Mexico, Canada) get +100 in matches in their own country.

    python football/wc2026.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, random
from collections import Counter
R=pd.read_csv('../raw/football/results.csv',parse_dates=['date']); S=pd.read_csv('../raw/football/shootouts.csv',parse_dates=['date'])
def K(t):
    if t=='FIFA World Cup': return 60
    if t in ('UEFA Euro','Copa América','African Cup of Nations','AFC Asian Cup','Gold Cup','CONCACAF Championship','Oceania Nations Cup','Confederations Cup'): return 50
    if 'qualification' in t or t in ('UEFA Nations League','CONCACAF Nations League'): return 40
    if t=='Friendly': return 20
    return 30
elo={}
pre=R[(R.date<'2026-06-11')&R.home_score.notna()]
for r in pre.itertuples():
    a,b=r.home_team,r.away_team; ea,eb=elo.get(a,1500),elo.get(b,1500)
    dr=ea-eb+(0 if r.neutral else 100); we=1/(10**(-dr/400)+1)
    gd=abs(r.home_score-r.away_score); G=1 if gd<=1 else 1.5 if gd==2 else (11+gd)/8
    w=1 if r.home_score>r.away_score else 0.5 if r.home_score==r.away_score else 0
    d=K(r.tournament)*G*(w-we); elo[a]=ea+d; elo[b]=eb-d
wc=R[(R.tournament=='FIFA World Cup')&(R.date>='2026-06-28')&(R.date<='2026-07-19')]
def winner(r):
    if r.home_score>r.away_score: return r.home_team
    if r.home_score<r.away_score: return r.away_team
    s=S[(S.date==r.date)&(S.home_team==r.home_team)]; return s.winner.iloc[0]
rounds=[('2026-06-28','2026-07-03'),('2026-07-04','2026-07-07'),('2026-07-09','2026-07-11'),('2026-07-14','2026-07-15'),('2026-07-19','2026-07-19')]
M=[wc[(wc.date>=a)&(wc.date<=b)] for a,b in rounds]
# rebuild bracket order: order R32 ties so that consecutive pairs feed the same R16 tie, etc.
def order(level):
    if level==0: return None
    return None
win32={winner(r):(r.home_team,r.away_team) for r in M[0].itertuples()}
def tie_of(team,k):  # the round-k tie (as pair) that 'team' played in
    for r in M[k].itertuples():
        if team in (r.home_team,r.away_team): return (r.home_team,r.away_team)
final=M[4].iloc[0]
def expand(team,k):  # list of R32 entrants in bracket order under 'team''s path at round k
    if k<0: return [team]
    a,b=tie_of(team,k); 
    # the teams that reached round k's tie: each came from round k-1
    return expand(a,k-1)+expand(b,k-1) if k>0 else [a,b]
def entrants(k,team):
    a,b=tie_of(team,k)
    if k==0: return [a,b]
    return entrants(k-1,a)+entrants(k-1,b)
field=entrants(4,final.home_team)
assert len(set(field))==32, len(set(field))
HOST={'United States','Mexico','Canada'}
venue={}
for k in range(5):
    for r in M[k].itertuples(): venue[frozenset((r.home_team,r.away_team))]=r.country
def p1(a,b,country=None):
    dr=elo[a]-elo[b]
    # hosts only get home advantage when playing in their own country; unknown venue in simulation -> host's own country assumed
    if a in HOST: dr+=100
    if b in HOST: dr-=100
    return 1/(10**(-dr/400)+1)
def pser(p,bo):
    from math import comb
    n=bo//2+1; return sum(comb(n-1+j,j)*p**n*(1-p)**j for j in range(n))
N=200000; rng=random.Random(5); out={}
for bo in (1,3,5,7):
    ch=Counter()
    for _ in range(N):
        r=field
        while len(r)>1: r=[r[i] if rng.random()<pser(p1(r[i],r[i+1]),bo) else r[i+1] for i in range(0,len(r),2)]
        ch[r[0]]+=1
    out[bo]=ch; print(bo,[(t,round(c/N,3)) for t,c in ch.most_common(6)],'Spain',round(ch['Spain']/N,3))
top=sorted(field,key=lambda t:-elo[t])[:10]; print('pre-WC Elo top:',[(t,round(elo[t])) for t in top])
rows=[dict(team=t,elo=elo[t],**{f'p_bo{bo}':out[bo][t]/N for bo in out}) for t in field]
pd.DataFrame(rows).sort_values('p_bo1',ascending=False).to_csv('../data/wc2026_knockout_series.csv',index=False)
print('field',field)

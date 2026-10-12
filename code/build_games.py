"""Build a clean game-level table of tier-1 pro games from the Leaguepedia mirror (gptilt/lol-esports-matches).

    python build_games.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, zlib
D='../raw/leaguepedia_hf/'
t=pd.read_parquet(D+'tournaments.parquet'); g=pd.read_parquet(D+'games.parquet'); m=pd.read_parquet(D+'matches.parquet')
P=t[(t.tier=='Primary')&~t.league.str.contains('Arabian|Showmatch|Classic|Kickoff|Nexus Arabia',na=False)&~t.name.str.contains('Showmatch|All-Star|All Star',na=False)]
P=P.set_index('tournament_id')
g=g[g.tournament.isin(P.index)&g.winner.notna()&(g.winner!='')]
g=g[(g.winner==g.team_blue)|(g.winner==g.team_red)]
games=pd.DataFrame(dict(dt=pd.to_datetime(g.datetime_utc),tournament=g.tournament,match_id=g.match_id,t1=g.team_blue,t2=g.team_red,win1=(g.winner==g.team_blue).astype(int)))
# series without game-level rows -> expand from score
m=m[m.tournament.isin(P.index)&~m.match_id.isin(set(g.match_id))].copy()
m['s1']=pd.to_numeric(m.team1_score,errors='coerce'); m['s2']=pd.to_numeric(m.team2_score,errors='coerce')
m=m[(m.s1+m.s2>0)&(m.s1+m.s2<8)&m.team1.notna()&(m.team1!='TBD')]
rows=[]
for r in m.itertuples():
    seq=[1]*int(r.s1)+[0]*int(r.s2)
    # game order inside a series known only by its score: a fixed shuffle per match. zlib.crc32 replaces hash(),
    # which Python randomises per process (NOTES.md, entry 11)
    rng=np.random.default_rng(zlib.crc32(r.match_id.encode())); rng.shuffle(seq)
    for i,w in enumerate(seq): rows.append((pd.to_datetime(r.datetime_utc)+pd.Timedelta(minutes=i),r.tournament,r.match_id,r.team1,r.team2,w))
games=pd.concat([games,pd.DataFrame(rows,columns=games.columns)])
games=games[games.dt.notna()&(games.t1!=games.t2)]
games['t_region']=games.tournament.map(P.region); games['league']=games.tournament.map(P.league)
games=games.sort_values('dt').reset_index(drop=True)
games.to_parquet('../data/games_clean.parquet')
print(games.shape, games.dt.min(), games.dt.max()); print(games.t_region.value_counts())

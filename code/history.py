"""Extract each Worlds main event (2014-2025): participants, groups or Swiss round-1 pairs, start date, results.

    python history.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, networkx as nx
from elo import canon
M=pd.read_parquet('../raw/leaguepedia_hf/matches.parquet')
def main_event(y):
    tn=f'{y} Season World Championship'+('' if y<2017 else '/Main Event')
    x=M[M.tournament==tn].copy(); x['dt']=pd.to_datetime(x.datetime_utc)
    x['team1']=x.team1.map(canon); x['team2']=x.team2.map(canon)
    x['w']=x.apply(lambda r: r.team1 if str(r.winner)=='1' else r.team2,axis=1)
    x['l']=x.apply(lambda r: r.team2 if str(r.winner)=='1' else r.team1,axis=1)
    out=dict(year=y,start=x.dt.min())
    ko=x[x.tab.isin(['Quarterfinals','Semifinals','Finals'])]
    out['champion']=ko[ko.tab=='Finals'].w.iat[0]; out['runner_up']=ko[ko.tab=='Finals'].l.iat[0]
    out['semis']=list(ko[ko.tab=='Semifinals'].l); out['quarters']=list(ko[ko.tab=='Quarterfinals'].l)
    if y>=2023:
        r1=x[x.tab=='Round 1']; out['format']='swiss'; out['round1']=list(zip(r1.team1,r1.team2))
        out['teams']=sorted(set(r1.team1)|set(r1.team2))
    else:
        gs=x[x.tab.str.startswith('Day')]; G=nx.Graph(); G.add_edges_from(zip(gs.team1,gs.team2))
        out['format']='groups'; out['groups']=[sorted(c) for c in nx.connected_components(G)]
        out['teams']=sorted(G.nodes)
    return out
if __name__=='__main__':
    for y in range(2014,2026):
        e=main_event(y); print(y,e['start'].date(),e['format'],len(e['teams']),e['champion'],'|',e.get('groups') or e.get('round1'))

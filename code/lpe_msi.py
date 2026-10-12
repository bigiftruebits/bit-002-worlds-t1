"""MSI control with lolproelo ratings: does T1 over-perform at MSI too?

    python lpe_msi.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, time, subprocess
from elo import prep, canon
from scrape_lpe import parse
from compare_published import LPE_FIX
g=prep(); m=g[g.tournament.str.contains('Mid-Season Invitational',na=False)].copy()
m['y']=m.dt.dt.year
rows=[]
for y,gm in m.groupby('y'):
    st=gm.dt.min(); d=(st-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    out=f'../raw/not_redistributed/lolproelo/lpe_msi_{y}.html'
    subprocess.run(['curl','-sS','-A','Mozilla/5.0','-o',out,f'https://lolproelo.com/rankings?year={y}&through={d}'],check=True); time.sleep(2)
    L=parse(open(out).read()); L['team']=L.name.map(lambda n: canon(LPE_FIX.get(n,n))); e=L.drop_duplicates('team').set_index('team').elo
    for r in gm.itertuples():
        if r.t1 in e.index and r.t2 in e.index: rows.append((y,r.t1,r.t2,r.win1,e[r.t1]-e[r.t2]))
    print(y,d,len(gm),'matched',sum(1 for x in rows if x[0]==y))
D=pd.DataFrame(rows,columns=['year','t1','t2','win1','d']); D.to_csv('../data/lpe_msi_games.csv',index=False)
long=pd.concat([D.assign(team=D.t1,win=D.win1,dd=D.d),D.assign(team=D.t2,win=1-D.win1,dd=-D.d)])
long['p']=1/(1+10**(-long.dd/526)); t=long[long.team=='T1']
ex=t.win.sum()-t.p.sum(); print(f'T1 at MSI (lolproelo): {len(t)} games, {t.win.sum()} wins vs {t.p.sum():.1f} expected, excess {ex:+.1f}, z={ex/np.sqrt((t.p*(1-t.p)).sum()):.2f}')

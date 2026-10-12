"""glicko_trueskill_extra.py

    python glicko_trueskill_extra.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import sys; sys.argv=['x']
src=open('glicko_trueskill.py').read().split('res=[]')[0]; exec(src)
import pandas as pd
rows=[]
for ph in (0,50):
    s=score(run('glicko',tau=0.5,phi_reset=ph/173.7178)); rows.append(dict(model='Glicko-2',param=f'tau=0.5, RD reset={ph}',**s)); print(rows[-1],flush=True)
for tau,sr in ((25/300,0),(25/300,1.0),(25/600,0)):
    s=score(run('trueskill',tau=tau,sig_reset=sr)); rows.append(dict(model='TrueSkill',param=f'tau={tau:.3f}, sigma reset={sr:.2f}',**s)); print(rows[-1],flush=True)
old=pd.read_csv('../data/glicko_trueskill.csv'); pd.concat([old,pd.DataFrame(rows)]).to_csv('../data/glicko_trueskill.csv',index=False)

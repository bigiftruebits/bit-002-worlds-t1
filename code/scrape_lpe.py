"""scrape_lpe.py

    python scrape_lpe.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import re, html, time, subprocess, pandas as pd, sys
from history import main_event
def fetch(url,out):
    subprocess.run(['curl','-sS','-A','Mozilla/5.0','-o',out,url],check=True)
    return open(out).read()
def parse(s):
    t=re.sub(r'<script.*?</script>','',s,flags=re.S); t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
    L=[l.strip() for l in t.split('\n') if l.strip()]
    i=L.index('Elo',L.index('Home Elo'))+1; rows=[]
    while i+6<len(L) and L[i].isdigit():
        rank,name,code,region,home,reg,eff=L[i:i+7]
        try: rows.append(dict(rank=int(rank),name=name,code=code,region=region,home=int(home),region_bonus=int(reg.replace('+','').replace('−','-')),elo=int(eff))); i+=7
        except ValueError: break
    return pd.DataFrame(rows)
def main():
  out=[]
  dates={y:(main_event(y)['start']-pd.Timedelta(days=1)).strftime('%Y-%m-%d') for y in range(2014,2026)}
  dates[2026]='2026-10-02'
  for y,d in dates.items():
    s=fetch(f'https://lolproelo.com/rankings?year={y}&through={d}',f'../raw/not_redistributed/lolproelo/lpe_{y}.html')
    df=parse(s); df['year']=y; df['through']=d; out.append(df); print(y,d,len(df),df.head(3)[['name','elo']].values.tolist()); time.sleep(2)
  pd.concat(out).to_csv('../raw/not_redistributed/lolproelo/lolproelo_preworlds.csv',index=False)

if __name__=='__main__': main()

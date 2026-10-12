"""parse_gpr.py

    python parse_gpr.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import json,re,sys,pandas as pd
def parse(path):
    s=open(path).read()
    dec=json.JSONDecoder(); out={}
    for m in re.finditer(r'"teamGPR":\[',s):
        try: arr,_=dec.raw_decode(s[m.end()-1:])
        except Exception as e: continue
        for t in arr:
            if not isinstance(t,dict) or 'team' not in t: continue
            out[t['team']['id']]=t
    rows=[]
    for t in out.values():
        tm=t['team']
        for h in t.get('teamGPRHistory') or []:
            rows.append(dict(team_id=tm['id'],code=tm['code'],name=tm['name'],
              league=(tm.get('homeLeague') or {}).get('name'),date=h['dateCalculated'],elo=h['elo'],gpr=h['gprScore'],rank=h['rank']))
    return pd.DataFrame(rows).drop_duplicates()
for f in sys.argv[1:]:
    df=parse(f); out=f.replace('.html','_history.csv'); df.to_csv(out,index=False)
    print(f,len(df),df.team_id.nunique(),df.date.min(),df.date.max())

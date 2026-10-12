"""Team Elo with regional offsets for pro League of Legends.
Effective rating = team rating (relative to its region) + region offset.
Domestic games move only team ratings; cross-region games also move region offsets (zero-sum).

    python elo.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, math
from collections import defaultdict

REGION_MAP={'Europe':'EMEA','EMEA':'EMEA','North America':'NA','China':'CN','Korea':'KR','LMS':'LMS',
 'Asia Pacific':'APAC','Vietnam':'VN','Japan':'JP','Oceania':'OCE','Brazil':'BR','Latin America':'LAT','LAN':'LAT','LAS':'LAT',
 'Turkey':'TR','CIS':'CIS','SEA':'SEA','MENA':'MENA'}
INTL={'International','Wildcard','Americas'}
# Same organisation under different names (Leaguepedia uses the name at the time)
RENAMES={'SK Telecom T1':'T1','SK Telecom T1 K':'T1','Samsung Galaxy':'Gen.G','KSV eSports':'Gen.G',
 'DAMWON Gaming':'Dplus KIA','DWG KIA':'Dplus KIA','Dplus Kia':'Dplus KIA','kt Rolster':'KT Rolster',
 'MAD Lions':'Movistar KOI','MAD Lions KOI':'Movistar KOI','Rogue (European Team)':'Rogue',
 'Hanwha Life Esports':'Hanwha Life Esports','ROX Tigers':'ROX Tigers','LYON (2024 American Team)':'LYON',
 'PSG Talon':'PSG Talon','Talon Esports':'PSG Talon','Team WE':'Team WE',"Xi'an Team WE":'Team WE',
 'Suning':'Weibo Gaming','Suning Gaming':'Weibo Gaming','JD Gaming':'JD Gaming','Beijing JDG Esports':'JD Gaming',
 'Ninjas in Pyjamas.CN':'Ninjas in Pyjamas.CN','Shenzhen NINJAS IN PYJAMAS':'Ninjas in Pyjamas.CN',
 'Afreeca Freecs':'Kwangdong Freecs','Kwangdong Freecs':'Kwangdong Freecs','KT Rolster ':'KT Rolster'}

def canon(n): return RENAMES.get(n,n)

def team_regions(games):
    """(team, year) -> home region, from domestic games."""
    d=games[~games.t_region.isin(INTL)].copy()
    d['reg']=d.t_region.map(REGION_MAP); d['y']=d.dt.dt.year
    long=pd.concat([d[['t1','y','reg']].rename(columns={'t1':'team'}),d[['t2','y','reg']].rename(columns={'t2':'team'})])
    return long.groupby(['team','y']).reg.agg(lambda s:s.mode().iat[0]).to_dict()

class Elo:
    def __init__(self,K=24,K_intl=32,K_reg=8,carry=0.75,carry_reg=0.85,new_pen=60,init_reg=None):
        self.K,self.K_intl,self.K_reg,self.carry,self.carry_reg,self.new_pen=K,K_intl,K_reg,carry,carry_reg,new_pen
        self.r={}                    # team -> rating relative to region (mean ~0 within region)
        self.R=defaultdict(float)    # region -> offset
        if init_reg: self.R.update(init_reg)
        self.home={}                 # team -> current region
        self.year=None
        self.last={}
    def eff(self,t): return 1500+self.r.get(t,0)+self.R[self.home.get(t,'?')]
    @staticmethod
    def p(e1,e2): return 1/(1+10**(-(e1-e2)/400))
    def _season(self,y,reg_of):
        # move teams whose home region changed (keep effective rating), regress to region mean
        for t in list(self.r):
            nr=reg_of.get((t,y))
            if nr and nr!=self.home.get(t):
                old=self.home.get(t); self.r[t]+=self.R[old]-self.R[nr] if old else 0; self.home[t]=nr
        cutoff=pd.Timestamp(f'{y-1}-01-01')
        active={t for t,d in self.last.items() if d>=cutoff}
        byreg=defaultdict(list)
        for t in active: byreg[self.home.get(t)].append(self.r[t])
        means={k:np.mean(v) for k,v in byreg.items()}
        for t in active: self.r[t]=means[self.home.get(t)]+self.carry*(self.r[t]-means[self.home.get(t)])
        aregs={self.home.get(t) for t in active}
        mR=np.mean([self.R[k] for k in aregs]) if aregs else 0
        for k in aregs: self.R[k]=mR+self.carry_reg*(self.R[k]-mR)
    def _ensure(self,t,y,reg_of):
        if t not in self.r:
            self.home[t]=reg_of.get((t,y)) or reg_of.get((t,y+1)) or reg_of.get((t,y-1)) or 'UNK'
            vals=[v for u,v in self.r.items() if self.home.get(u)==self.home[t] and u in self.last and (self.last[u]-pd.Timestamp(f'{y}-01-01')).days>-400]
            self.r[t]=(np.mean(vals) if vals else 0)-self.new_pen
    def run(self,games,reg_of,until=None,record=False):
        out=[]
        for g in games.itertuples():
            if until is not None and g.dt>=until: break
            y=g.dt.year
            if self.year!=y:
                if self.year is not None: self._season(y,reg_of)
                self.year=y
            a,b=canon(g.t1),canon(g.t2)
            self._ensure(a,y,reg_of); self._ensure(b,y,reg_of)
            ea,eb=self.eff(a),self.eff(b); p=self.p(ea,eb); s=g.win1
            cross=self.home[a]!=self.home[b]
            k=self.K_intl if (cross or g.t_region in INTL) else self.K
            self.r[a]+=k*(s-p); self.r[b]-=k*(s-p)
            if cross:
                self.R[self.home[a]]+=self.K_reg*(s-p); self.R[self.home[b]]-=self.K_reg*(s-p)
            self.last[a]=self.last[b]=g.dt
            if record: out.append((g.Index,p,cross))
        return out
    def table(self,since=None):
        ts=[t for t in self.r if since is None or self.last.get(t,pd.Timestamp(0))>=pd.Timestamp(since)]
        return pd.DataFrame([(t,self.home.get(t),self.eff(t),self.last.get(t)) for t in ts],columns=['team','region','elo','last']).sort_values('elo',ascending=False).reset_index(drop=True)

def prep(path='../data/games_clean.parquet'):
    g=pd.read_parquet(path); g['t1']=g.t1.map(canon); g['t2']=g.t2.map(canon)
    return g

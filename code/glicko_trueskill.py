"""Glicko-2 and TrueSkill vs our Elo (Riccardo, 10 Oct 2026). Both are Elo-like online ratings with an uncertainty
per team. Run over every game since 2011 (same data as our Elo), each game its own rating period; at the start of
each calendar year every team's uncertainty is widened (the analogue of our seasonal reset: new rosters).
Ratings frozen on the first day of each Worlds; predict all 1,248 Worlds games 2014–2025; log loss, accuracy,
and T1's wins above expectation. Implemented from the published algorithms (Glickman 2012; Herbrich et al. 2007),
no region offsets.

    python glicko_trueskill.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import numpy as np, pandas as pd, math, itertools
from scipy.stats import norm
from elo import prep
g=prep().sort_values('dt').reset_index(drop=True)
intl=g[g.tournament.str.contains('Season World Championship')].copy()
intl['event']=intl.tournament.str.replace(r'/(Main Event|Play-In|Group Stage|Knockout Stage|Bracket Stage|Rumble Stage)$','',regex=True)
starts=intl.groupby('event').dt.min(); starts=starts[starts>='2014-01-01']
ev_of={i:e for e,idx in intl.groupby('event').groups.items() for i in idx}
# ---------- Glicko-2 ----------
def glicko(tau=0.5,phi_reset=150/173.7178,phi0=350/173.7178):
    S={}  # team -> [mu, phi, sigma] on Glicko-2 scale
    def get(t): return S.setdefault(t,[0.0,phi0,0.06])
    gfun=lambda p:1/math.sqrt(1+3*p*p/math.pi**2)
    def upd(a,b,s):
        mu,phi,sig=a; muj,phij,_=b
        gj=gfun(phij); E=1/(1+math.exp(-gj*(mu-muj))); v=1/(gj*gj*E*(1-E)); d=v*gj*(s-E)
        A=math.log(sig*sig); f=lambda x: math.exp(x)*(d*d-phi*phi-v-math.exp(x))/(2*(phi*phi+v+math.exp(x))**2)-(x-A)/tau**2
        a_=A
        if d*d>phi*phi+v: B=math.log(d*d-phi*phi-v)
        else:
            k=1
            while f(A-k*tau)<0: k+=1
            B=A-k*tau
        fA,fB=f(a_),f(B)
        for _ in range(60):
            if abs(B-a_)<1e-6: break
            C=a_+(a_-B)*fA/(fB-fA); fC=f(C)
            if fC*fB<=0: a_,fA=B,fB
            else: fA/=2
            B,fB=C,fC
        sig2=math.exp(a_/2); ps=math.sqrt(phi*phi+sig2*sig2); phin=1/math.sqrt(1/ps**2+1/v); mun=mu+phin*phin*gj*(s-E)
        return [mun,phin,sig2]
    def prob(a,b):
        return 1/(1+math.exp(-gfun(math.sqrt(a[1]**2+b[1]**2))*(a[0]-b[0])))
    return S,get,upd,prob,phi_reset
# ---------- TrueSkill (two teams as two players, no draws) ----------
def trueskill(beta=25/6,tau=25/300,sig_reset=25/6,mu0=25.0,sig0=25/3):
    S={}
    def get(t): return S.setdefault(t,[mu0,sig0])
    def upd2(w,l):
        w[1]=math.sqrt(w[1]**2+tau**2); l[1]=math.sqrt(l[1]**2+tau**2)
        c=math.sqrt(2*beta**2+w[1]**2+l[1]**2); t=(w[0]-l[0])/c; v=norm.pdf(t)/max(norm.cdf(t),1e-12); ww=v*(v+t)
        w0,l0=w[1]**2,l[1]**2
        w[0]+=w0/c*v; l[0]-=l0/c*v
        w[1]=math.sqrt(w0*max(1-w0/c**2*ww,1e-4)); l[1]=math.sqrt(l0*max(1-l0/c**2*ww,1e-4))
    def prob(a,b): return norm.cdf((a[0]-b[0])/math.sqrt(2*beta**2+a[1]**2+b[1]**2))
    return S,get,upd2,prob,sig_reset
def run(kind,**kw):
    if kind=='glicko': S,get,upd,prob,reset=glicko(**kw)
    else: S,get,upd,prob,reset=trueskill(**kw)
    frozen={}; out=[]; year=None; st_list=sorted(starts.items(),key=lambda x:x[1]); si=0
    for i,r in enumerate(g.itertuples()):
        if r.dt.year!=year:   # new season: widen every team's uncertainty
            year=r.dt.year
            for t,v in S.items(): v[1]=max(v[1],reset)
        while si<len(st_list) and r.dt>=st_list[si][1]:
            frozen[st_list[si][0]]={t:list(v) for t,v in S.items()}; si+=1
        if i in ev_of and ev_of[i] in frozen:
            F=frozen[ev_of[i]]
            if r.t1 in F and r.t2 in F: out.append((r.dt.year,r.t1,r.t2,prob(F[r.t1],F[r.t2]),r.win1))
        a,b=get(r.t1),get(r.t2)
        if kind=='glicko':
            na=upd(a,b,r.win1); nb=upd(b,a,1-r.win1); S[r.t1]=na; S[r.t2]=nb
        else:
            upd(a,b) if r.win1==1 else upd(b,a)
    return pd.DataFrame(out,columns=['year','t1','t2','p','win1'])
def score(df):
    p=df.p.clip(1e-6,1-1e-6); w=df.win1
    L=pd.concat([df.assign(team=df.t1,q=df.p,win=df.win1),df.assign(team=df.t2,q=1-df.p,win=1-df.win1)]); T=L[L.team=='T1']
    return dict(n=len(df),logloss=round(float(-np.mean(w*np.log(p)+(1-w)*np.log(1-p))),4),acc=round(float(np.mean((p>0.5)==(w==1))),4),
                T1_games=len(T),T1_exp=round(float(T.q.sum()),1),T1_excess=round(float(T.win.sum()-T.q.sum()),1),T1_z=round(float((T.win.sum()-T.q.sum())/np.sqrt((T.q*(1-T.q)).sum())),2))
res=[]
for tau,ph in itertools.product((0.3,0.6,1.0),(100,200,350)):
    s=score(run('glicko',tau=tau,phi_reset=ph/173.7178)); res.append(dict(model='Glicko-2',param=f'tau={tau}, RD reset={ph}',**s)); print(res[-1],flush=True)
for tau,sr in itertools.product((25/300,25/100,25/50),(25/12,25/6,25/3)):
    s=score(run('trueskill',tau=tau,sig_reset=sr)); res.append(dict(model='TrueSkill',param=f'tau={tau:.3f}, sigma reset={sr:.2f}',**s)); print(res[-1],flush=True)
pd.DataFrame(res).to_csv('../data/glicko_trueskill.csv',index=False)

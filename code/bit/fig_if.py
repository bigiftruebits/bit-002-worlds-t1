"""IF figure. (a) each Worlds champion's pre-tournament chance of winning, 2014-2025, with the favourite's;
(b) expected vs actual Worlds win rate, every team-year, T1 highlighted; (c) T1's cumulative wins above expectation, Worlds vs MSI.
Phone spec 4.4 in wide, >=9 pt.

    python bit/fig_if.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.ticker as mt
sys.path.insert(0,'.')
from backtest_params import SCALE
from history import main_event
# ---- table of choices ----
FIG_W,FIG_H,DPI=4.4,7.7,450
OUT='../figures/fig-002-if-worlds-t1.png'
S='#FFFFFF'; INK='#1a1a1a'; INK2='#555555'; FAINT='#e6e5e1'
ACCENT='#C1440E'; BLUE='#5B8FA8'; GRAY='#bdbcb6'
T1_LABEL={2015:(0.014,0.0,'left'),2016:(-0.014,-0.055,'right'),2017:(0.016,-0.045,'left'),2019:(0.016,0.025,'left'),
          2021:(0.0,0.07,'center'),2022:(0.035,0.025,'left'),2023:(0.016,0.0,'left'),2024:(-0.016,0.0,'right'),2025:(0.014,-0.055,'left')}
assert FIG_H<=1.75*FIG_W
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':'#cccccc','axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,
 'figure.facecolor':S,'axes.facecolor':S,'savefig.facecolor':S,'axes.spines.top':False,'axes.spines.right':False})
d=pd.read_csv('../data/worlds_team_games.csv')
a=d.groupby(['year','team']).agg(n=('win','size'),w=('win','mean'),e=('p','mean')).reset_index()
champ={y:main_event(y)['champion'] for y in range(2014,2026)}; a['champ']=[champ[y]==t for y,t in zip(a.year,a.team)]
fig=plt.figure(figsize=(FIG_W,FIG_H))
cx=fig.add_axes([0.20,0.685,0.64,0.24]); ax=fig.add_axes([0.15,0.36,0.80,0.235]); bx=fig.add_axes([0.15,0.06,0.55,0.215])
# (a) champion's pre-tournament chance, by year
B=pd.read_csv('../data/backtest_years.csv')
F26=pd.read_csv('../data/forecast2026_our_elo.csv').set_index('team').p_win
B=pd.concat([B,pd.DataFrame([dict(year=2026,champion='T1',p_champ=F26['T1'],favourite='Gen.G',p_fav=F26['Gen.G'])])],ignore_index=True)
GEN='#2a78d6'
TS=pd.read_csv('../data/t1_structure.csv').set_index('year').p_win_forward   # T1 with bonus fitted on earlier years only
BON={2023:TS[2023],2024:TS[2024],2025:TS[2025],2026:pd.read_csv('../data/forecast2026_our_elo_T1bonus.csv').set_index('team').p_win['T1']}
NM={'Samsung White':'SSW','T1':'T1','Gen.G':'SSG','Invictus Gaming':'IG','FunPlus Phoenix':'FPX','Dplus KIA':'DWG','EDward Gaming':'EDG','DRX':'DRX'}
yy=np.arange(len(B))[::-1]
for yi,r in zip(yy,B.itertuples()):
    col=ACCENT if r.champion=='T1' else GRAY; fut=r.year==2026
    cx.barh(yi,r.p_champ*100,height=0.62,color=S if fut else col,edgecolor=ACCENT if fut else S,linewidth=1.2 if fut else 0.5,hatch='////' if fut else None,zorder=3)
    if r.year in BON: cx.barh(yi,BON[r.year]*100,height=0.62,facecolor='none',edgecolor=ACCENT,linewidth=0.9,linestyle=(0,(2,1.5)),zorder=2)
    cx.plot([r.p_fav*100],[yi],marker='|',ms=8,mew=1.8,color=INK2,zorder=4)
    v=r.p_champ*100; cx.text(57,yi,f'{v:.0f}%' if v>=2 else f'{v:.1f}%',va='center',ha='left',clip_on=False,fontsize=9,color=ACCENT if r.champion=='T1' else INK2,fontweight='bold' if r.champion=='T1' else 'normal')
nm=lambda r: NM.get(r.champion,r.champion)   # T1 also for 2015-16 (then SK Telecom T1; the caption says so)
cx.set_yticks(yy); cx.set_yticklabels([]); cx.tick_params(axis='y',length=0)
for yi,r in zip(yy,B.itertuples()):
    col=ACCENT if r.champion=='T1' else INK2
    cx.text(-0.27,yi,str(r.year),transform=cx.get_yaxis_transform(),ha='left',va='center',fontsize=9,color=col)
    cx.text(-0.02,yi,nm(r),transform=cx.get_yaxis_transform(),ha='right',va='center',fontsize=9,color=col,fontweight='bold' if (r.champion=='T1' and r.year!=2026) else 'normal',fontstyle='italic' if r.year==2026 else 'normal')
cx.set_xlim(0,55); cx.set_xticks([0,10,20,30,40,50]); cx.xaxis.set_major_formatter(mt.PercentFormatter(100,decimals=0))
cx.set_ylim(-0.6,len(B)-0.4); cx.spines['left'].set_visible(False)
cx.grid(axis='x',color=FAINT,lw=0.7); cx.set_axisbelow(True)
cx.set_title("a  Chance to win, before each Worlds",loc='left',fontsize=9.5,fontweight='bold',color=INK,pad=6,x=-0.2)
cx.barh([-2.45],[4],left=[0],height=0.55,color=GRAY,clip_on=False); cx.text(5,-2.45,'champion',fontsize=9,color=INK2,va='center',clip_on=False)
cx.barh([-2.45],[4],left=[34],height=0.55,color=S,edgecolor=ACCENT,linewidth=1.2,hatch='////',clip_on=False); cx.text(39,-2.45,'forecast',fontsize=9,color=INK2,va='center',clip_on=False)
cx.plot([18.6],[-2.45],marker='|',ms=8,mew=1.8,color=INK2,clip_on=False); cx.text(20,-2.45,'favourite',fontsize=9,color=INK2,va='center',clip_on=False)
cx.barh([-3.55],[4],left=[0],height=0.55,facecolor='none',edgecolor=ACCENT,linewidth=0.9,linestyle=(0,(2,1.5)),clip_on=False); cx.text(5,-3.55,"T1 with its Worlds bonus from earlier years",fontsize=9,color=INK2,va='center',clip_on=False)
# (b)
ax.plot([0,1],[0,1],color='#aaaaaa',lw=1,zorder=1)
o=a[a.team!='T1']; sz=lambda n: n*2.2
ax.scatter(o.e,o.w,s=sz(o.n),color=GRAY,alpha=0.6,edgecolor=S,linewidth=0.5,zorder=2)
oc=o[o.champ]; ax.scatter(oc.e,oc.w,s=sz(oc.n)+18,facecolor='none',edgecolor=INK2,linewidth=0.9,zorder=3)
t=a[a.team=='T1']
ax.scatter(t.e,t.w,s=sz(t.n),color=ACCENT,edgecolor=S,linewidth=0.6,zorder=4)
tc=t[t.champ]; ax.scatter(tc.e,tc.w,s=sz(tc.n)+30,facecolor='none',edgecolor=ACCENT,linewidth=1.1,zorder=4)
for _,r in t.iterrows():
    dx,dy,ha=T1_LABEL[r.year]; ax.text(r.e+dx,r.w+dy,str(r.year),fontsize=9,color=ACCENT,fontweight='bold',ha=ha,va='center',zorder=5)
ax.set_xlim(0.15,0.85); ax.set_ylim(0,1.0)
ax.xaxis.set_major_formatter(mt.PercentFormatter(1.0,decimals=0)); ax.yaxis.set_major_formatter(mt.PercentFormatter(1.0,decimals=0))
ax.set_xticks([0.2,0.4,0.6,0.8]); ax.set_yticks([0,0.25,0.5,0.75,1.0])
ax.set_xlabel('Win rate the ratings expected'); ax.set_ylabel('Win rate achieved')
ax.grid(color=FAINT,lw=0.7); ax.set_axisbelow(True)
ax.set_title('b  Every team at every Worlds',loc='left',fontsize=9.5,fontweight='bold',color=INK,pad=6)
# (b)
D=pd.read_csv('../data/intl_games_static.csv'); D=D[D.kind.isin(['Worlds','MSI'])]
L=pd.concat([D.assign(team=D.t1,win=D.win1,dd=D['diff'],o=np.arange(len(D))*2),D.assign(team=D.t2,win=1-D.win1,dd=-D['diff'],o=np.arange(len(D))*2+1)])
L=L[L.team=='T1'].sort_values('o'); L['p']=1/(1+10**(-L.dd/SCALE)); L['res']=L.win-L.p
Lg=pd.concat([D.assign(team=D.t1,win=D.win1,dd=D['diff'],o=np.arange(len(D))*2),D.assign(team=D.t2,win=1-D.win1,dd=-D['diff'],o=np.arange(len(D))*2+1)])
Lg=Lg[(Lg.team=='Gen.G')&(Lg.year>=2018)].sort_values('o'); Lg['p']=1/(1+10**(-Lg.dd/SCALE)); Lg['res']=Lg.win-Lg.p
Lr=pd.concat([D.assign(team=D.t1,win=D.win1,dd=D['diff'],o=np.arange(len(D))*2),D.assign(team=D.t2,win=1-D.win1,dd=-D['diff'],o=np.arange(len(D))*2+1)])
Lr=Lr[Lr.team=='Royal Never Give Up'].sort_values('o'); Lr['p']=1/(1+10**(-Lr.dd/SCALE)); Lr['res']=Lr.win-Lr.p
RNGC='#3d8f5f'
LINES=[('T1','Worlds',L,ACCENT,'-'),('T1','MSI',L,ACCENT,(0,(2.5,1.8))),('Gen.G','Worlds',Lg,GEN,'-'),('Gen.G','MSI',Lg,GEN,(0,(2.5,1.8))),('RNG','Worlds',Lr,RNGC,'-'),('RNG','MSI',Lr,RNGC,(0,(2.5,1.8)))]
KEY_Y={('T1','Worlds'):29,('RNG','MSI'):21.5,('T1','MSI'):14,('RNG','Worlds'):5.5,('Gen.G','MSI'):-2,('Gen.G','Worlds'):-11}
# one grey 95% band: range of cumulative luck for a team playing exactly as rated, per-game variance pooled over the six lines
VAR=np.mean(np.concatenate([(src[src.kind==k].p*(1-src[src.kind==k].p)).values for _,k,src,_,_ in LINES]))
nb=np.arange(0,179); bx.fill_between(nb,-1.96*np.sqrt(VAR*nb),1.96*np.sqrt(VAR*nb),color='#888888',alpha=0.16,lw=0,zorder=1)
for _,k,src,_,_ in LINES:
    v=(src[src.kind==k].p*(1-src[src.kind==k].p)); print(_,k,'own band end %.2f pooled %.2f'%(1.96*np.sqrt(v.sum()),1.96*np.sqrt(VAR*len(v))))
for team,kind,src,col,ls in LINES:
    x=src[src.kind==kind]; c=np.concatenate([[0],x.res.cumsum().values]); n=np.arange(len(c))
    bx.plot(n,c,color=col,lw=1.8 if kind=='Worlds' else 1.4,ls=ls,solid_capstyle='round',zorder=3)
    ky=KEY_Y[(team,kind)]
    bx.plot([182,194],[ky,ky],color=col,lw=1.8 if kind=='Worlds' else 1.4,ls=ls,clip_on=False)
    bx.text(197,ky,f'{team} {kind}\n'+('0' if round(c[-1])==0 else f'{c[-1]:+.0f}'),fontsize=9,color=col,fontweight='bold' if kind=='Worlds' else 'normal',va='center',clip_on=False)
bx.axhline(0,color='#aaaaaa',lw=0.9)
bx.set_xlim(0,178); bx.spines['bottom'].set_bounds(0,178); bx.set_ylim(-14,32); bx.set_xticks([0,50,100,150]); bx.set_yticks([-10,0,10,20,30])
bx.set_xlabel('Games at each event, in order'); bx.set_ylabel('Wins above expectation')
bx.grid(axis='y',color=FAINT,lw=0.7); bx.set_axisbelow(True)
bx.set_title('c  T1, Gen.G and RNG, at Worlds and MSI',loc='left',fontsize=9.5,fontweight='bold',color=INK,pad=6)
fig.text(0.04,0.985,'Who wins Worlds',fontsize=12,fontweight='bold',color=INK,va='top')
sys.path.insert(0,'bit'); from i18n import finish; finish(fig,OUT,DPI)

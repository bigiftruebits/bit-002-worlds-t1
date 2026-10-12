"""BIG figure: the 19 Worlds 2026 contenders ranked by Elo on 10 Oct 2026.
Bar = range of the team's rating through the 2026 season; dot = today. Ratings only: title odds are in the IF figure.
Phone spec (BIG_IF_TRUE_FORMAT.md §4.12): 4.4 in wide, text >= 9 pt, height <= 1.75 x width.

    python bit/fig_big.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'.')
from teams2026 import REGION
# ---- table of choices ----
FIG_W,FIG_H,DPI=4.4,7.2,450
OUT='../figures/fig-002-big-worlds-elo-2026.png'
S='#FFFFFF'; INK='#1a1a1a'; INK2='#555555'; FAINT='#e6e5e1'
RC={'LCK':'#2a78d6','LPL':'#eb6834','LEC':'#1baf7a','LCS':'#eda100','LCP':'#e87ba4','CBLOL':'#4a3aa7'}
SHORT={'Gen.G':'Gen.G','Hanwha Life Esports':'Hanwha Life','Bilibili Gaming':'Bilibili','Dplus KIA':'Dplus KIA','T1':'T1',"Anyone's Legend":"Anyone's Legend",
 'G2 Esports':'G2','Team Liquid':'Team Liquid','Invictus Gaming':'Invictus','LYON':'LYON','Top Esports':'Top Esports','Karmine Corp':'Karmine Corp',
 'Team Secret Whales':'Secret Whales','Cloud9':'Cloud9','Movistar KOI':'Movistar KOI','LØS':'LØS','CTBC Flying Oyster':'CTBC Fl. Oyster','FURIA':'FURIA','LOUD':'LOUD','MVK Esports':'MVK'}
STATUS={'Karmine Corp':'playin','MVK Esports':'playin','Cloud9':'playin','FURIA':'playin'}
XMIN,XMAX=1250,2000
assert FIG_H<=1.75*FIG_W
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':'#cccccc','axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,
 'figure.facecolor':S,'axes.facecolor':S,'savefig.facecolor':S,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False})
T=pd.read_csv('../data/traj2026.csv',parse_dates=['date'])
last=T[T.date==T.date.max()].set_index('team').elo.sort_values(ascending=False)
rng=T.groupby('team').elo.agg(['min','max'])
teams=list(last.index); n=len(teams); y=np.arange(n)[::-1]
fig=plt.figure(figsize=(FIG_W,FIG_H))
ax=fig.add_axes([0.33,0.07,0.62,0.79])
for yi,t in zip(y,teams):
    c=RC[REGION[t]]; st=STATUS.get(t,'swiss')
    ax.plot([rng.loc[t,'min'],rng.loc[t,'max']],[yi,yi],color=c,alpha=0.28,lw=5.5,solid_capstyle='round',zorder=2)
    fs={'swiss':'full','playin':'none','pending':'left'}[st]
    ax.plot([last[t]],[yi],marker='o',ms=6.5,color=c,mec=c,mew=1.2,mfc=c if fs!='none' else S,fillstyle=fs if fs!='none' else 'full',zorder=4)
    fig.text(0.31,0,'')
ax.set_yticks(y); ax.set_yticklabels([SHORT[t] for t in teams]); ax.tick_params(axis='y',length=0,pad=6)
for lab,t in zip(ax.get_yticklabels(),teams):
    if t=='T1': lab.set_fontweight('bold'); lab.set_color(INK)
ax.set_xlim(XMIN,XMAX); ax.set_ylim(-0.7,n-0.3); ax.set_xticks([1400,1600,1800,2000])
ax.grid(axis='x',color=FAINT,lw=0.7); ax.set_axisbelow(True); ax.set_xlabel('Elo rating, 2026 season')
fig.text(0.04,0.975,'Gen.G on top, T1 level with Dplus KIA',fontsize=12,fontweight='bold',color=INK,va='top')
# legends: regions, then entry status
for i,(r,c) in enumerate(RC.items()):
    fig.text(0.04+i*0.16,0.932,'●',color=c,fontsize=10,va='center'); fig.text(0.075+i*0.16,0.932,r,color=INK2,fontsize=9,va='center')
lg=fig.add_axes([0.04,0.885,0.94,0.03]); lg.axis('off'); lg.set_xlim(0,1); lg.set_ylim(0,1)
for k,(fs,txt) in enumerate((('full','Swiss stage'),('none','play-in'))):
    xk=k*0.31; lg.plot([xk+0.02],[0.5],marker='o',ms=6,color=INK2,mec=INK2,mew=1.1,mfc=INK2 if fs!='none' else S,fillstyle=fs if fs!='none' else 'full')
    lg.text(xk+0.055,0.5,txt,va='center',fontsize=9,color=INK2)
sys.path.insert(0,'bit'); from i18n import finish; finish(fig,OUT,DPI)

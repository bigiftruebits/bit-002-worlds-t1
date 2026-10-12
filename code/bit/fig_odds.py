"""IF figure: 2026 forecast as a coloured table. Rows: the 19 qualified teams, by Elo rating on 10 Oct (as in Figure 1);
columns: chance of reaching the quarter-finals, semi-finals, final, and of winning. Extra row: T1 with its Worlds bonus.
Sequential single hue (light -> dark blue) for magnitude; league dot and entry status as in Figure 1.
Landscape 16:9 (8 x 4.5 in) for social media, two panels; text >= 9 pt.

    python bit/fig_odds.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import pandas as pd, numpy as np, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
sys.path.insert(0,'.')
from teams2026 import REGION
# ---- table of choices ----
FIG_W,FIG_H,DPI=8.0,4.5,300
OUT='../figures/fig-002-odds-2026.png'
S='#FFFFFF'; INK='#1a1a1a'; INK2='#555555'; FAINT='#e6e5e1'; ACCENT='#C1440E'
RC={'LCK':'#2a78d6','LPL':'#eb6834','LEC':'#1baf7a','LCS':'#eda100','LCP':'#e87ba4','CBLOL':'#4a3aa7'}
STATUS={'Karmine Corp':'playin','MVK Esports':'playin','Cloud9':'playin','FURIA':'playin'}
CMAP=LinearSegmentedColormap.from_list('bit',['#f3f7fa','#a9c6d6','#5B8FA8','#24506a'])
COLS=[('p_knockouts','Quarters'),('p_semis','Semis'),('p_final','Final'),('p_win','Champion')]
SHORT={'Gen.G':'Gen.G','Hanwha Life Esports':'Hanwha Life','Bilibili Gaming':'Bilibili','Dplus KIA':'Dplus KIA','T1':'T1',"Anyone's Legend":"Anyone's Legend",
 'G2 Esports':'G2','Team Liquid':'Team Liquid','Invictus Gaming':'Invictus','LYON':'LYON','Top Esports':'Top Esports','Karmine Corp':'Karmine Corp',
 'Team Secret Whales':'Secret Whales','Cloud9':'Cloud9','Movistar KOI':'Movistar KOI','LØS':'LØS','CTBC Flying Oyster':'CTBC Fl. Oyster','FURIA':'FURIA','LOUD':'LOUD','MVK Esports':'MVK'}
assert abs(FIG_W/FIG_H-16/9)<0.01   # 16:9 for social media
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'figure.facecolor':S,'savefig.facecolor':S})
F=pd.read_csv('../data/forecast2026_our_elo.csv').sort_values(['elo','p_win'],ascending=False)
B=pd.read_csv('../data/forecast2026_our_elo_T1bonus.csv').set_index('team').loc['T1']
rows=[]
for r in F.itertuples():
    rows.append((r.team,r)); 
    if r.team=='T1': rows.append(('T1+',B))
n=len(rows)
# landscape for social media (16:9): two panels side by side, 10 rows each; units = 0.1 inch
fig=plt.figure(figsize=(FIG_W,FIG_H)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,FIG_W*10); ax.set_ylim(0,FIG_H*10); ax.axis('off')
ax.text(1.5,FIG_H*10-3.0,'Gen.G favourite, T1 at 6%',fontsize=14,fontweight='bold',color=INK,va='center')
ax.text(1.5,FIG_H*10-5.8,'Chance of reaching each round, Worlds 2026 (per cent of 100,000 simulated tournaments; blank = never)',fontsize=9,color=INK2,va='center')
CW,TOP,RH=5.8,FIG_H*10-11.3,3.0
PANELS=[(0.8,rows[:10]),(40.0,rows[10:])]
def fmt(v):
    if v<0.0005: return ''
    if v<0.01: return '<1'
    return f'{v*100:.0f}'
for px,prow in PANELS:
    X0=px+15.4
    for j,(c,lab) in enumerate(COLS):
        ax.text(X0+j*CW+CW/2,TOP+2.4,lab,ha='center',va='center',fontsize=9,color=INK2,fontweight='bold' if c=='p_win' else 'normal')
    for i,(t,r) in enumerate(prow):
        y=TOP-i*RH; bonus=(t=='T1+')
        if bonus:
            ax.text(px+2.4,y,'+ Worlds bonus',fontsize=9,color=ACCENT,style='italic',va='center')
        else:
            reg=REGION[t]; st=STATUS.get(t,'swiss'); c=RC[reg]
            fs={'swiss':'full','playin':'none','pending':'left'}[st]
            ax.plot([px+1.0],[y],marker='o',ms=5.5,color=c,mec=c,mew=1.1,mfc=c if fs!='none' else S,fillstyle=fs if fs!='none' else 'full')
            ax.text(px+2.2,y,SHORT.get(t,t),fontsize=9,va='center',color=ACCENT if t=='T1' else INK,fontweight='bold' if t=='T1' else 'normal')
        for j,(c,lab) in enumerate(COLS):
            v=float(getattr(r,c) if not bonus else r[c]); x=X0+j*CW
            if v>=0.0005:
                ax.add_patch(Rectangle((x+0.15,y-RH/2+0.15),CW-0.3,RH-0.3,fc=CMAP(min(v,1)**0.75),ec=ACCENT if bonus else 'none',lw=1.0 if bonus else 0,ls=(0,(2,1.5)) if bonus else '-'))
            ax.text(x+CW/2,y,fmt(v),ha='center',va='center',fontsize=9,color=S if v>0.42 else INK,fontweight='bold' if c=='p_win' else 'normal')
# legend row: leagues, then entry status
ly=2.2
for k,(r,c) in enumerate(RC.items()):
    ax.plot([1.8+k*5.6],[ly],marker='o',ms=5.5,color=c); ax.text(2.6+k*5.6,ly,r,fontsize=9,color=INK2,va='center')
for k,(fs,txt) in enumerate((('full','Swiss stage'),('none','play-in'))):
    xk=37.5+k*13.5; ax.plot([xk],[ly],marker='o',ms=5.5,color=INK2,mec=INK2,mew=1.1,mfc=INK2 if fs!='none' else S,fillstyle=fs if fs!='none' else 'full')
    ax.text(xk+0.8,ly,txt,fontsize=9,color=INK2,va='center')
sys.path.insert(0,'bit'); from i18n import finish; finish(fig,OUT,DPI)

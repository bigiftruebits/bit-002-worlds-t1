"""TRUE figure: title odds of four 2026 contenders under seven formats, ratings alone
(filled, main number) and with T1's Worlds bonus from the IF beat (dashed ring, number in brackets). Schematic per format.
Phone spec: 4.4 in wide, text >= 9 pt, height <= 1.75 x width.

    python bit/fig_true.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import sys, pandas as pd, numpy as np, matplotlib, math
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
# ---- table of choices ----
FIG_W,FIG_H,DPI=4.4,7.47,450
YLO=-0.6
OUT='../figures/fig-002-true-formats.png'
S='#FFFFFF'; INK='#1a1a1a'; INK2='#555555'; LINE='#8c8b86'; FAINT='#e6e5e1'
ACCENT='#C1440E'; BLUE='#5B8FA8'; STAR='#d99a00'
BONUS=177
TEAMS=[('Gen.G','Gen.G'),('Bilibili Gaming','Bilibili'),('Hanwha Life Esports','Hanwha'),('T1','T1')]
ROWS=[('Swiss + Bo5 knockouts (2023-26)','Worlds 2026: Swiss + knockouts','swiss',True),
      ('Groups + Bo5 knockouts (2014-22)','Groups + knockouts (to 2022)','groups',False),
      ('Single elimination Bo5, random','Knockout, random draw','se',False),
      ('Single elimination Bo5, seeded','Knockout, seeded','se_seed',False),
      ('Double elimination Bo5, seeded','Double elimination','de',False),
      ('League + playoffs, Bo1 then Bo5','League, then playoffs','lp',False),
      ('Double round-robin league, Bo1','Full league, 30 games each','league',False)]
LIKE={'Swiss + Bo5 knockouts (2023-26)':'like the Champions League',
      'Groups + Bo5 knockouts (2014-22)':'like the football World Cup',
      'Single elimination Bo5, random':"like England's FA Cup",
      'Single elimination Bo5, seeded':'like tennis Grand Slams',
      'Double elimination Bo5, seeded':"like MSI's bracket stage",
      'League + playoffs, Bo1 then Bo5':'like the NBA',
      'Double round-robin league, Bo1':'like Serie A'}
AREA=1300   # points^2 per unit probability
assert FIG_H<=1.75*FIG_W
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'figure.facecolor':S,'savefig.facecolor':S})
D=pd.read_csv('../data/formats2026_bonus.csv')
G=pd.read_csv('../data/formats2026_games.csv').set_index('format')
Q=pd.read_csv('../data/formats2026_quality.csv').set_index('format')
RC=pd.read_csv('../data/formats2026_rankcorr.csv').set_index('format').spearman   # how closely the final order follows the ratings
fig=plt.figure(figsize=(FIG_W,FIG_H)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,44); ax.set_ylim(YLO,76); ax.axis('off')
ax.text(1.2,74.2,'On ratings, every format favours Gen.G',fontsize=12,fontweight='bold',color=INK,va='center')
X0,DX=25.6,5.4; TOP=68.4; RH=9.4
for j,(t,lab) in enumerate(TEAMS):
    ax.text(X0+j*DX,TOP+1.2,lab,ha='center',va='center',fontsize=9,fontweight='bold',color=ACCENT if t=='T1' else INK)
CX0,CW=15.6,5.6   # rank-correlation column: bar from 0 to 1
ax.text(CX0+CW/2,TOP+1.2,'Order',ha='center',va='center',fontsize=9,fontweight='bold',color=INK2)
def bracket(x,y,w,h,n,star=True):
    lv=int(math.log2(n)); ys=list(np.linspace(y-h/2,y+h/2,n)); xs=x; st=w/lv
    for _ in range(lv):
        ny=[(ys[i]+ys[i+1])/2 for i in range(0,len(ys),2)]
        for i in range(0,len(ys),2):
            ax.plot([xs,xs+st*0.55,xs+st*0.55,xs],[ys[i],ys[i],ys[i+1],ys[i+1]],color=LINE,lw=0.6)
            ax.plot([xs+st*0.55,xs+st],[ny[i//2]]*2,color=LINE,lw=0.6)
        ys=ny; xs+=st
    if star: ax.scatter([xs+0.35],[ys[0]],marker='*',s=26,color=STAR,zorder=5,edgecolor='none')
    return xs,ys[0]
def swiss_s(x,y):
    swiss_s_nobracket(x,y); bracket(x+6.6,y,3.6,3.2,8)
def swiss_s_nobracket(x,y):
    pos={}
    for rnd in range(6):
        for w in range(rnd,-1,-1):
            l=rnd-w
            if w<=3 and l<=3 and not (w==3 and l==3): pos[(w,l)]=(x+rnd*1.05,y+(w-l)*0.55)
    for (w,l),(px,py) in pos.items():
        if w<3 and l<3:
            for nx in ((w+1,l),(w,l+1)):
                if nx in pos: ax.plot([px,pos[nx][0]],[py,pos[nx][1]],color=FAINT,lw=0.7,zorder=2)
    for (w,l),(px,py) in pos.items():
        if (w==3 and l>0 and (w-1,l) not in pos): continue
        c='#3a9b6e' if w==3 else ('#c4473f' if l==3 else '#6b6a66')
        ax.scatter([px],[py],s=5,color=c,zorder=3,edgecolor='none')
def de_s(x,y):
    # upper bracket (16 teams, seeded) on top; lower bracket below, fed by upper-bracket losers (dashed arrow);
    # the two bracket winners meet in the grand final (star)
    ux,uy=bracket(x+0.9,y+1.0,8.0,2.0,16,star=False)
    ys=np.linspace(y+1.0-1.0,y+1.0+1.0,16)
    for i in (0,15,7,8): ax.scatter([x+0.45],[ys[i]],s=5,color=BLUE,zorder=5,edgecolor='none')
    lx,ly=bracket(x+3.0,y-1.55,5.9,1.0,8,star=False)
    ax.annotate('',xy=(x+2.7,y-1.05),xytext=(x+2.7,y-0.1),arrowprops=dict(arrowstyle='-|>',color=ACCENT,lw=0.8,mutation_scale=6,shrinkA=0,shrinkB=0))
    gx=max(ux,lx)+0.5
    ax.plot([ux,gx],[uy,uy],color=LINE,lw=0.6); ax.plot([lx,gx],[ly,ly],color=LINE,lw=0.6)
    ax.plot([gx,gx],[uy,ly],color=LINE,lw=0.6); ax.plot([gx,gx+0.35],[(uy+ly)/2]*2,color=LINE,lw=0.6)
    ax.scatter([gx+0.7],[(uy+ly)/2],marker='*',s=26,color=STAR,zorder=5,edgecolor='none')
def lp_s(x,y):
    # a small league (round robin) whose top half goes into a seeded bracket
    n=16; cx,cy=x+2.3,y; R=1.45; a=np.linspace(0,2*np.pi,n,endpoint=False); px=cx+R*np.cos(a)*1.25; py=cy+R*np.sin(a)
    for i in range(n):
        for k in range(i+1,n): ax.plot([px[i],px[k]],[py[i],py[k]],color=FAINT,lw=0.3,zorder=1)
    ax.scatter(px,py,s=4,color='#6b6a66',zorder=3,edgecolor='none')
    ax.annotate('',xy=(x+5.6,y),xytext=(x+4.5,y),arrowprops=dict(arrowstyle='-|>',color=LINE,lw=0.7,mutation_scale=6,shrinkA=0,shrinkB=0))
    bracket(x+6.0,y,3.4,2.6,8)
def groups_s(x,y):
    for gi in range(4):
        gx=x+(gi%2)*3.0; gy=y+0.85-(gi//2)*1.8
        ax.add_patch(FancyBboxPatch((gx,gy-0.55),2.5,1.1,boxstyle='round,pad=0.05,rounding_size=0.3',fc='none',ec='#bbbbbb',lw=0.6))
        ax.scatter([gx+0.4+k*0.57 for k in range(4)],[gy]*4,s=4,color='#6b6a66',zorder=3,edgecolor='none')
    bracket(x+6.6,y,3.6,3.2,8)
def se_s(x,y,seeded):
    bracket(x+0.9,y,9.3,3.9,16)
    if seeded:
        ys=np.linspace(y-1.95,y+1.95,16)
        for i in (0,15,7,8): ax.scatter([x+0.45],[ys[i]],s=5,color=BLUE,zorder=5,edgecolor='none')
def league_s(x,y):
    n=16; cx,cy=x+5.0,y; R=1.75; a=np.linspace(0,2*np.pi,n,endpoint=False); px=cx+R*np.cos(a)*1.3; py=cy+R*np.sin(a)
    for i in range(n):
        for k in range(i+1,n): ax.plot([px[i],px[k]],[py[i],py[k]],color=FAINT,lw=0.3,zorder=1)
    ax.scatter(px,py,s=5,color='#6b6a66',zorder=3,edgecolor='none')
for i,(key,title,kind,actual) in enumerate(ROWS):
    yc=TOP-4.6-i*RH
    if actual: ax.add_patch(FancyBboxPatch((0.5,yc-RH/2+0.3),43,RH-0.6,boxstyle='round,pad=0,rounding_size=0.6',fc=ACCENT,alpha=0.07,ec='none'))
    elif i>0: ax.plot([0.8,43.2],[yc+RH/2]*2,color=FAINT,lw=0.6)
    ax.text(1.2,yc+3.55,title,fontsize=9,fontweight='bold',color=ACCENT if actual else INK,va='center')
    gg=G.loc[key]; qq=Q.loc[key]
    ax.text(1.2,yc-3.75,f"{gg.games_per_tournament:.0f} games, winner plays {gg.games_by_champion:.0f}",fontsize=9,color=INK2,va='center')
    ax.text(1.2,yc+2.15,LIKE[key],fontsize=9,color=INK2,style='italic',va='center')
    sy=yc-0.65; sx=1.4
    {'swiss':lambda:swiss_s(sx,sy),'de':lambda:de_s(sx,sy),'groups':lambda:groups_s(sx,sy),'se':lambda:se_s(sx,sy,False),'se_seed':lambda:se_s(sx,sy,True),'league':lambda:league_s(sx,sy),'lp':lambda:lp_s(sx,sy)}[kind]()
    rc=RC[key]; cy=yc-0.65
    ax.plot([CX0,CX0+CW],[cy-0.55]*2,color=FAINT,lw=3.2,solid_capstyle='butt',zorder=2)
    ax.plot([CX0,CX0+CW*rc],[cy-0.55]*2,color=INK2,lw=3.2,solid_capstyle='butt',zorder=3)
    ax.text(CX0+CW/2,cy+0.75,f'{rc:.2f}',ha='center',va='center',fontsize=9,color=INK)
    p0=D[(D.format==key)&(D.bonus==0)].set_index('team').p; pb=D[(D.format==key)&(D.bonus==BONUS)].set_index('team').p
    for j,(t,lab) in enumerate(TEAMS):
        x=X0+j*DX; v0=p0.get(t,0); v=pb.get(t,0); by=yc+1.3
        col=ACCENT if t=='T1' else BLUE
        ax.scatter([x],[by],s=v0*AREA,color=col,alpha=0.85,edgecolor=S,linewidth=0.8,zorder=4)
        ax.scatter([x],[by],s=v*AREA,facecolor='none',edgecolor='#666666',linewidth=0.8,linestyle=(0,(2,1.5)),zorder=5)
        rr=math.sqrt(max(v0,v)*AREA/math.pi)/(FIG_H*72/(76-YLO))
        ly0=by-max(rr,0.35)-0.95
        ax.text(x,ly0,f'{v0*100:.0f}%',ha='center',va='center',fontsize=9,color=ACCENT if t=='T1' else INK,fontweight='bold' if t=='T1' else 'normal')
        ax.text(x,ly0-1.3,f'({v*100:.0f}%)',ha='center',va='center',fontsize=9,color='#666666')
# legend
ly=YLO+1.4
ax.scatter([2.0],[ly],s=90,color=BLUE,edgecolor=S,zorder=4); ax.text(3.2,ly,'ratings alone',fontsize=9,color=INK2,va='center')
ax.scatter([17.0],[ly],s=90,facecolor='none',edgecolor='#666666',linewidth=0.8,linestyle=(0,(2,1.5))); ax.text(18.2,ly,"(with T1's Worlds bonus)",fontsize=9,color=INK2,va='center')
sys.path.insert(0,'bit'); from i18n import finish; finish(fig,OUT,DPI)

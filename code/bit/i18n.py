"""Italian edition of the figures: same drawing, every text artist translated after drawing (BIT_LANG=it).
Exact strings first, then patterns; decimal points become commas. Writes <name>-it.png beside the English file.

    imported by the figure scripts

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import os, re, matplotlib
IT={
 'Gen.G on top, T1 level with Dplus KIA':'Gen.G in testa, T1 appaiata a Dplus KIA','Elo rating, 2026 season':'Punteggio Elo, stagione 2026',
 'Swiss stage':'fase svizzera','play-in':'play-in','not decided yet':'non ancora deciso',
 'a  Chance to win, before each Worlds':'a  Probabilità di vittoria, prima di ogni Mondiale','forecast':'previsione','champion':'campione',
 'favourite':'favorita','T1 with its Worlds bonus from earlier years':'T1 con il bonus stimato sui Mondiali precedenti',
 'Win rate the ratings expected':'Vittorie attese dai punteggi','Win rate achieved':'Vittorie ottenute',
 'b  Every team at every Worlds':'b  Ogni squadra a ogni Mondiale','Games at each event, in order':'Partite di ogni torneo, in ordine',
 'Wins above expectation':'Vittorie sopra le attese','c  T1, Gen.G and RNG, at Worlds and MSI':'c  T1, Gen.G e RNG, ai Mondiali e al MSI',
 'Who wins Worlds':'Chi vince i Mondiali','On ratings, every format favours Gen.G':'Con i soli punteggi vince Gen.G',
 'ratings alone':'solo punteggi',"(with T1's Worlds bonus)":'(con il bonus di T1 ai Mondiali)',
 'Worlds 2026: Swiss + knockouts':'Mondiali 2026: svizzero + eliminazione','Swiss + Bo3 knockouts':'Svizzero + eliminazione Bo3',
 'Swiss + Bo7 knockouts':'Svizzero + eliminazione Bo7','Double elimination':'Doppia eliminazione',
 'Groups + knockouts (to 2022)':'Gironi + eliminazione (fino al 2022)','Knockout, random draw':'Eliminazione, sorteggio libero',
 'Knockout, seeded':'Eliminazione, teste di serie','Full league, 30 games each':'Campionato, 30 partite a testa',
 'like the Champions League':'come la Champions League','like the football World Cup':'come i Mondiali di calcio',"like England's FA Cup":'come la FA Cup inglese',
 'like tennis Grand Slams':'come gli Slam del tennis',"like MSI's bracket stage":'come il tabellone del MSI','like Serie A':'come la Serie A','Order':'Ordine','League, then playoffs':'Campionato, poi playoff','like the NBA':"come l'NBA",
 'Gen.G favourite, T1 at 6%':'Gen.G favorita, T1 al 6%','Chance of reaching each round, Worlds 2026 (per cent of 100,000 simulated tournaments; blank = never)':'Probabilità di arrivare a ogni turno, Mondiali 2026 (percentuale su 100.000 tornei simulati; vuoto = mai)',
 'Quarters':'Quarti','Semis':'Semi','Final':'Finale','Champion':'Campione','+ Worlds bonus':'+ bonus Mondiali',
 'Per cent of 100,000 simulated tournaments; blank = never':'Percentuale su 100.000 tornei simulati; vuoto = mai'}
PAT=[(r'^(\d+) games, winner plays (\d+)$',r'\1 partite, chi vince ne gioca \2'),(r'^(T1|Gen\.G|RNG) Worlds\n',r'\1 Mondiali\n'),
     (r'^(T1|Gen\.G|RNG) MSI\n',r'\1 MSI\n')]
def tr(t):
    if t in IT: return IT[t]
    for a,b in PAT: t=re.sub(a,b,t)
    return re.sub(r'(\d)\.(\d)',r'\1,\2',t)
def finish(fig,out,dpi):
    size=fig.get_size_inches().copy(); ylims=[a.get_ylim() for a in fig.axes]; xlims=[a.get_xlim() for a in fig.axes]
    fig.savefig(out,dpi=dpi); print(out)
    fig.canvas.draw()
    for t in fig.findobj(matplotlib.text.Text):
        s=t.get_text()
        if s: t.set_text(tr(s))
    for ax in fig.axes:   # tick labels are regenerated on draw: freeze them translated
        for get,setl in ((ax.get_xticklabels,ax.set_xticklabels),(ax.get_yticklabels,ax.set_yticklabels)):
            labs=[l.get_text() for l in get()]
            if any(labs): 
                pos=ax.get_xticks() if get==ax.get_xticklabels else ax.get_yticks()
                (ax.set_xticks if get==ax.get_xticklabels else ax.set_yticks)(pos); setl([tr(l) for l in labs])
    fig.set_size_inches(size)
    for a,yl,xl in zip(fig.axes,ylims,xlims):
        if not a.get_autoscaley_on(): a.set_ylim(yl)
        if not a.get_autoscalex_on(): a.set_xlim(xl)
    o=out.replace('.png','-it.png'); fig.savefig(o,dpi=dpi); print(o)

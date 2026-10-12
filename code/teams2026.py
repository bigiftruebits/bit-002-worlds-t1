"""teams2026.py

    python teams2026.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
CODE2NAME={'GEN':'Gen.G','HLE':'Hanwha Life Esports','T1':'T1','DK':'Dplus KIA','KT':'KT Rolster','AL':"Anyone's Legend",'BLG':'Bilibili Gaming',
 'TES':'Top Esports','IG':'Invictus Gaming','JDG':'JD Gaming','LNG':'LNG Esports','WBG':'Weibo Gaming','G2':'G2 Esports','MKOI':'Movistar KOI',
 'KC':'Karmine Corp','FNC':'Fnatic','TLAW':'Team Liquid','C9':'Cloud9','LYON':'LYON','FLY':'FlyQuest','100T':'100 Thieves','TSW':'Team Secret Whales',
 'CFO':'CTBC Flying Oyster','MVK':'MVK Esports','PSG':'PSG Talon','GAM':'GAM Esports','LOS':'LØS','LOUD':'LOUD','FUR':'FURIA','PAIN':'paiN Gaming',
 'VKS':'Vivo Keyd Stars','NIP':'Ninjas in Pyjamas.CN'}
REGION={'Gen.G':'LCK','Hanwha Life Esports':'LCK','T1':'LCK','Dplus KIA':'LCK',"Anyone's Legend":'LPL','Bilibili Gaming':'LPL','Top Esports':'LPL',
 'Invictus Gaming':'LPL','G2 Esports':'LEC','Movistar KOI':'LEC','Karmine Corp':'LEC','Team Liquid':'LCS','Cloud9':'LCS','LYON':'LCS',
 'Team Secret Whales':'LCP','CTBC Flying Oyster':'LCP','MVK Esports':'LCP','LØS':'CBLOL','FURIA':'CBLOL'}   # LOUD eliminated 3 Oct
# results played after the dataset snapshot (2026-09-26): (team1, team2, games won by 1, games won by 2, date)
LATE_RESULTS=[('LOUD','LØS',2,3,'2026-09-27 16:00'),('Team Liquid','Cloud9',3,1,'2026-09-27 20:00'),
              ('LOUD','FURIA',0,3,'2026-10-03 16:00'),('LYON','Cloud9',3,1,'2026-10-03 20:00'),
              ('Team Liquid','LYON',3,1,'2026-10-04 20:00'),
              ('LØS','FURIA',3,2,'2026-10-10 16:00',[1,0,1,0,1])]
# FURIA 3-0 LOUD (CBLOL lower final, 3 Oct; Terra). LYON 3-1 Cloud9 (LCS lower final; Sheep Esports, Dot Esports).
# LØS 3-2 FURIA (CBLOL final, 10 Oct; games LØS, FURIA, LØS, FURIA, LØS; Strafe, Pichau Arena). Play-in draw (10 Oct, Strafe):
# FURIA v MVK Esports and Cloud9 v Karmine Corp, double elimination, Bo5.
# Team Liquid 3-1 LYON (LCS final, 4 Oct; Dot Esports, Sheep Esports). Replaces 'Cloud9 3-2 LYON' taken on 4 Oct from Wikipedia, which was wrong.

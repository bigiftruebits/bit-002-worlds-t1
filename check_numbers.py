"""
Re-derive the article's numbers from the shipped data and check that each one appears in both editions.

Reads data/*.csv (and data/residuals_intl.log for the bootstrap-free interval of the Worlds bonus), computes each
number the way the article prints it (English with a decimal point, Italian with a decimal comma) and looks for
the exact phrase in article/en.md and article/it.md. Prints one line per check and a final N/N PASS.

    python check_numbers.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import re, math, pathlib, numpy as np, pandas as pd
from scipy.optimize import minimize_scalar

HERE = pathlib.Path(__file__).parent
D = HERE / 'data'
if not (HERE / 'article' / 'en.md').exists() or not (HERE / 'article' / 'it.md').exists():
    # the Zenodo record holds code and data, not the article: the texts are in the GitHub repository
    raise SystemExit('check_numbers.py compares with the published texts, which are not in this archive: copy article/en.md '
                     'and article/it.md from https://github.com/bigiftruebits/bit-002-worlds-t1 into article/ and rerun.')
EN = (HERE / 'article' / 'en.md').read_text()
IT = (HERE / 'article' / 'it.md').read_text()
SCALE = 480                     # Elo scale used throughout (code/backtest_params.py)
results = []

def pct(x):    return f'{round(100 * x):.0f}%'
def dec(x, n=2, lang='en'):
    s = f'{x:.{n}f}'
    return s if lang == 'en' else s.replace('.', ',')

def check(label, value, en_phrase, it_phrase):
    ok_en = en_phrase in EN if en_phrase else True
    ok_it = it_phrase in IT if it_phrase else True
    ok = ok_en and ok_it
    results.append(ok)
    miss = [] if ok else [f'EN missing "{en_phrase}"' * (not ok_en), f'IT missing "{it_phrase}"' * (not ok_it)]
    print(f"{'PASS' if ok else 'FAIL'}  {label:58s} {value!s:>10}  {'; '.join(m for m in miss if m)}")

# ---------- BIG: ratings and the 2026 forecast ----------
F = pd.read_csv(D / 'forecast2026_our_elo.csv').set_index('team')
FB = pd.read_csv(D / 'forecast2026_our_elo_T1bonus.csv').set_index('team')
check('Gen.G rating going into Worlds', F.elo['Gen.G'], 'at 1822', 'a 1822')
check('T1 rating (fifth, level with Dplus KIA)', F.elo['T1'], 'at 1696', 'a 1696')
check('Gen.G title chance, ratings alone', pct(F.p_win['Gen.G']), 'Gen.G 40%', 'Gen.G il 40%')
check('Bilibili title chance', pct(F.p_win['Bilibili Gaming']), 'Bilibili 18%', 'Bilibili il 18%')
check('Hanwha Life title chance', pct(F.p_win['Hanwha Life Esports']), 'Hanwha Life 16%', 'Hanwha Life il 16%')
check('T1 title chance, ratings alone', pct(F.p_win['T1']), 'T1 6%', 'a T1 il 6%')
check('T1 title chance with the Worlds bonus', pct(FB.p_win['T1']), 'rise to 46%', 'salirebbe al 46%')
check('Gen.G title chance if T1 has the bonus', pct(FB.p_win['Gen.G']), 'drop to 25%', 'al 25%')
p = 1 / (1 + 10 ** (-(F.elo['T1'] - F.elo['Gen.G']) / SCALE))
check('T1 v Gen.G, one game', pct(p), '35% of games', 'nel 35% delle partite')
p5 = sum(math.comb(2 + j, j) * p ** 3 * (1 - p) ** j for j in range(3))
check('T1 v Gen.G, best of five', pct(p5), '24% of best-of-fives', '24% delle serie')

# ---------- IF: T1 at Worlds and MSI, ratings frozen on day one ----------
G = pd.read_csv(D / 'intl_games_static.csv')
L = pd.concat([G.assign(team=G.t1, win=G.win1, d=G['diff']), G.assign(team=G.t2, win=1 - G.win1, d=-G['diff'])])
L['p'] = 1 / (1 + 10 ** (-L.d / SCALE))
W = L[(L.team == 'T1') & (L.kind == 'Worlds')]; M = L[(L.team == 'T1') & (L.kind == 'MSI')]
check('T1 Worlds games won', f'{int(W.win.sum())}/{len(W)}', f'{int(W.win.sum())} of {len(W)} Worlds games', f'{int(W.win.sum())} partite ai Mondiali su {len(W)}')
check('T1 Worlds games expected', round(W.p.sum()), f'about {round(W.p.sum())} expected', f'circa {round(W.p.sum())} attese')
check('T1 extra Worlds wins', round(W.win.sum() - W.p.sum()), f'{round(W.win.sum() - W.p.sum())} more wins', f'{round(W.win.sum() - W.p.sum())} vittorie in più')
X = pd.read_csv(D / 't1_worlds_2013.csv'); x13 = X.win.sum() - X.p.sum(); tot = W.win.sum() - W.p.sum() + x13
check('T1 2013 Worlds (outside the window): extra wins, total with it', f'{x13:.1f} {tot:.1f}', f'about {round(x13)} more wins than expected that year too, {round(tot)} in all', f'circa {round(x13)} vittorie in più del previsto anche quell\'anno, {round(tot)} in tutto')
check('T1 MSI games won', f'{int(M.win.sum())}/{len(M)}', f'{int(M.win.sum())} of {len(M)} games', f'{int(M.win.sum())} partite su {len(M)}')
check('T1 MSI games expected', round(M.p.sum()), f'about {round(M.p.sum())} expected', f'circa {round(M.p.sum())} attese')
# the Worlds bonus: maximum-likelihood Elo points added to T1 in its Worlds games
nll = lambda b: -np.sum(W.win * np.log(1 / (1 + 10 ** (-(W.d + b) / SCALE))) + (1 - W.win) * np.log(1 - 1 / (1 + 10 ** (-(W.d + b) / SCALE))))
b = minimize_scalar(nll, bounds=(-300, 600), method='bounded').x
grid = np.arange(-100, 500, 1); Ls = np.array([nll(x) for x in grid]); ci = grid[Ls <= nll(b) + 1.92]
asp = lambda pts: 1 / (1 + 10 ** (-pts / SCALE))
check('Worlds bonus as win rate against itself (seven in ten)', pct(asp(b)), '**seven times in ten**' if pct(asp(b)) == '70%' else 'XX', '**sette volte su dieci**' if pct(asp(b)) == '70%' else 'XX')
check('95% interval of that win rate', f'{pct(asp(ci.min()))}-{pct(asp(ci.max()))}', f'between {pct(asp(ci.min()))} and {pct(asp(ci.max()))}', f'fra il {pct(asp(ci.min()))} e il {pct(asp(ci.max()))}')
loo = [int(x) for x in re.findall(r'without \d{4} (\d+)', (D / 'residuals_intl.log').read_text())]
check('leave-one-year-out range', f'{pct(asp(min(loo)))}-{pct(asp(max(loo)))}', f'between {pct(asp(min(loo)))} and {pct(asp(max(loo)))}', f'fra il {pct(asp(min(loo)))} e il {pct(asp(max(loo)))}')
# (the domestic-playoff comparison was cut from the article on 11 Oct; its numbers are in KEY_NUMBERS.md and data/clutch_playoffs.csv)

# ---------- TRUE: formats (16 Swiss teams fixed, 40,000 tournaments) ----------
B = pd.read_csv(D / 'formats2026_bonus.csv'); GM = pd.read_csv(D / 'formats2026_games.csv').set_index('format')
R = pd.read_csv(D / 'formats2026_rankcorr.csv').set_index('format').spearman
T = pd.read_csv(D / 'formats2026_tradeoffs.csv').set_index('format')
FIG = ['Swiss + Bo5 knockouts (2023-26)', 'Groups + Bo5 knockouts (2014-22)', 'Single elimination Bo5, random',
       'Single elimination Bo5, seeded', 'Double elimination Bo5, seeded', 'League + playoffs, Bo1 then Bo5', 'Double round-robin league, Bo1']
g0 = lambda f, t='Gen.G', b=0: B[(B.format == f) & (B.bonus == b) & (B.team == t)].p.iloc[0]
lo, hi = min(g0(f) for f in FIG), max(g0(f) for f in FIG)
check('Gen.G range across the figure\'s formats', f'{pct(lo)}-{pct(hi)}', f'at {pct(lo)} to {pct(hi)}', f'dal {pct(lo)} al {pct(hi)}')
check('T1 never above, ratings alone', pct(max(g0(f, 'T1') for f in FIG)), f'never above {pct(max(g0(f, "T1") for f in FIG))}', f'mai sopra il {pct(max(g0(f, "T1") for f in FIG))}')
blo, bhi = min(g0(f, 'T1', 177) for f in FIG), max(g0(f, 'T1', 177) for f in FIG)
check('T1 with the bonus, range', f'{pct(blo)}-{pct(bhi)}', f'from {pct(blo)} to {pct(bhi)}', f'dal {pct(blo)} al {pct(bhi)}')
check('full league: Gen.G', pct(g0(FIG[6])), f'with Gen.G at {pct(g0(FIG[6]))}', f'con Gen.G al {pct(g0(FIG[6]))}')
SL = pd.read_csv(D / 'formats2026_single_league.csv')
sl = lambda col, v: SL[(SL.rounds == 1) & (SL[col] == v)]
check('single round-robin league: rank correlation', f"{sl('team','spearman').p.iloc[0]:.2f}", f"drops to {sl('team','spearman').p.iloc[0]:.2f}", f"scende a {sl('team','spearman').p.iloc[0]:.2f}".replace('.', ','))
check('single round-robin league: Gen.G', pct(SL[(SL.rounds == 1) & (SL.bonus == 0) & (SL.team == 'Gen.G')].p.iloc[0]), f"Gen.G wins {pct(SL[(SL.rounds == 1) & (SL.bonus == 0) & (SL.team == 'Gen.G')].p.iloc[0])}", f"Gen.G vince il {pct(SL[(SL.rounds == 1) & (SL.bonus == 0) & (SL.team == 'Gen.G')].p.iloc[0])}")
check('full league: games, per team', f'{GM.games_per_tournament[FIG[6]]:.0f}', f'{GM.games_per_tournament[FIG[6]]:.0f} games, 30 per team', f'{GM.games_per_tournament[FIG[6]]:.0f} partite, 30 per squadra')
check('this year: games / winner', f'{GM.games_per_tournament[FIG[0]]:.0f}/{GM.games_by_champion[FIG[0]]:.0f}', f'the {GM.games_per_tournament[FIG[0]]:.0f} of this year', f'le {GM.games_per_tournament[FIG[0]]:.0f} di quest')
check('Bo7: Gen.G and games', f"{pct(g0('Swiss + Bo7 knockouts'))} {GM.games_per_tournament['Swiss + Bo7 knockouts']:.0f}", f"Gen.G rises to {pct(g0('Swiss + Bo7 knockouts'))}", f"Gen.G sale al {pct(g0('Swiss + Bo7 knockouts'))}")
check('Bo7: games and winner', f"{GM.games_per_tournament['Swiss + Bo7 knockouts']:.0f}/{GM.games_by_champion['Swiss + Bo7 knockouts']:.0f}", f"{GM.games_per_tournament['Swiss + Bo7 knockouts']:.0f} games, {GM.games_by_champion['Swiss + Bo7 knockouts']:.0f} for the winner", f"{GM.games_per_tournament['Swiss + Bo7 knockouts']:.0f} partite e chi vince ne gioca {GM.games_by_champion['Swiss + Bo7 knockouts']:.0f}")
check('double elimination: games, Gen.G', f"{GM.games_per_tournament[FIG[4]]:.0f} {pct(g0(FIG[4]))}", f"costs {GM.games_per_tournament[FIG[4]]:.0f} games", f"costa {GM.games_per_tournament[FIG[4]]:.0f} partite")
MR = pd.read_csv(D / 'msi_final_rematch_real.csv'); MS = pd.read_csv(D / 'msi_final_rematch_sim.csv')
check('MSI finals 2023-26 replaying the upper-bracket final', f"{(MR.replay_of == 'upper final').sum()}/{len(MR)}", 'three of the four MSI finals since 2023' if (MR.replay_of == 'upper final').sum() == 3 else 'XX', 'tre delle quattro finali del MSI dal 2023' if (MR.replay_of == 'upper final').sum() == 3 else 'XX')
RM = pd.read_csv(D / 'formats2026_rematch.csv').set_index('format').final_replays_upper_final
check('16-team double elimination: final replays the upper-bracket final (one in two)', f'{RM[FIG[4]]:.2f}', 'one time in two, replay the upper-bracket final' if 0.45 <= RM[FIG[4]] <= 0.55 else 'XX', 'una volta su due sono la rivincita della finale del tabellone dei vincenti' if 0.45 <= RM[FIG[4]] <= 0.55 else 'XX')
mu = MS[(MS.case.str.startswith('MSI 2026')) & (MS.replay_of == 'upper final')].share.iloc[0]
check('MSI format, simulated: final replays the upper-bracket final (about one in two)', f'{mu:.2f}', 'about one time in two' if 0.45 <= mu <= 0.55 else 'XX', 'circa una volta su due' if 0.45 <= mu <= 0.55 else 'XX')
check('this year: Gen.G', pct(g0(FIG[0])), f"holds it to {pct(g0(FIG[0]))}", f"la ferma al {pct(g0(FIG[0]))}")
check('close series: Swiss stage (more than eight)', f'{T.close_series[FIG[0]]:.1f}', 'more than eight', 'più di otto')
check('close series: double elimination (nearly eleven)', f'{T.close_series[FIG[4]]:.1f}', 'nearly eleven', 'quasi undici')
lc = T.loc['league clinch']
check('league: settled three rounds early (1 in 8)', f'{lc.p_clinched_3plus_early:.2f}', 'one time in eight', 'una volta su otto')
check('rank correlation: full league', dec(R[FIG[6]]), f'of {dec(R[FIG[6]])}', f'di {dec(R[FIG[6]], lang="it")}')
check('rank correlation: this year', dec(R[FIG[0]]), f'at {dec(R[FIG[0]])}', f'con {dec(R[FIG[0]], lang="it")}')
B1 = pd.read_csv(D / 'formats2026_bo1.csv')
b1 = lambda t, b: B1[(B1.team == t) & (B1.bonus == b)].p.iloc[0]
check('single-game knockouts: Gen.G', pct(b1('Gen.G', 0)), f'give Gen.G only {pct(b1("Gen.G", 0))}', f'darebbe a Gen.G solo il {pct(b1("Gen.G", 0))}')
check('single-game knockouts: T1 (with bonus)', f"{pct(b1('T1', 0))} ({pct(b1('T1', 177))})", f"T1 {pct(b1('T1', 0))} ({pct(b1('T1', 177))} with the bonus)", f"T1 l'{pct(b1('T1', 0))} (il {pct(b1('T1', 177))} con il bonus)")

FC = pd.read_csv(D / 'forecast2026_our_elo.csv').set_index('team').elo
gaps = [FC[t] - FC['Team Liquid'] for t in ('Hanwha Life Esports', 'Bilibili Gaming')]
check('pools: HLE and BLG above Team Liquid (about 100 points)', f'{gaps[0]:.0f}, {gaps[1]:.0f}', 'about 100 points stronger' if all(90 <= g <= 110 for g in gaps) else 'XX', 'circa 100 punti in più' if all(90 <= g <= 110 for g in gaps) else 'XX')

TR = pd.read_csv(D / 'traj2026.csv'); TL = TR[TR.date == TR.date.max()].set_index('team').elo
gap = TL['Gen.G'] - TL['T1']; pT1 = 1 / (1 + 10 ** (gap / SCALE))
check('Elo gap Gen.G-T1 and T1 game chance (about 1 in 3)', f'{gap:.0f} {pT1:.2f}', f'**{gap:.0f} points**' if 0.30 <= pT1 <= 0.37 else 'XX', f'**{gap:.0f} punti**' if 0.30 <= pT1 <= 0.37 else 'XX')

UW = pd.read_csv(D / 'usage_windows.csv'); um = int(UW.effective_tokens_M.sum())
check('usage, lower bound (million effective tokens)', f'{UW.effective_tokens_M.sum():.2f} -> {um}', f'At least {um} million effective tokens', f'Almeno {um} milioni di token effettivi')

# ---------- football parallel: World Cup 2026 knockout bracket replayed ----------
WC = pd.read_csv(D / 'wc2026_knockout_series.csv').set_index('team')
check('Spain, one match per tie', pct(WC.p_bo1['Spain']), f'won {pct(WC.p_bo1["Spain"])} of the time', f'vinceva il {pct(WC.p_bo1["Spain"])} delle volte')
check('Spain, best of seven matches', pct(WC.p_bo7['Spain']), f'{pct(WC.p_bo7["Spain"])} with best of seven', f'al meglio di sette, il {pct(WC.p_bo7["Spain"])}')

# ---------- the thirteen Worlds fields 2014-2026 (code/formats.py) ----------
Y = pd.read_csv(D / 'formats_by_year.csv'); S = pd.read_csv(D / 'formats_summary.csv').set_index('format')
real = Y[((Y.year <= 2022) & (Y.format == 'Groups + Bo5 knockouts (2014-22)')) | ((Y.year >= 2023) & (Y.format == 'Swiss + Bo5 knockouts (2023-26)'))]

n = len(results); print(f'\n{sum(results)}/{n} PASS')
raise SystemExit(0 if all(results) else 1)

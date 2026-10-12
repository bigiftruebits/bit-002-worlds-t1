# KEY_NUMBERS — worlds-t1

Every number printed in the article, with where it comes from. `check_numbers.py` re-derives 58 of them from `data/` and checks that each appears, as printed, in both `article/en.md` and `article/it.md` (decimal comma in Italian). The notes below are the working log kept while the article was written, oldest first; where a number changed, the latest entry wins (the final update of 11 Oct is at the end). File names refer to `data/` (`out/` in the working folder) and scripts to `code/`.


*Analysis session 2026-10-02 (Cowork, configured as Claude Opus 5.5). Rewritten for the seasonal-reset model, which replaced the partial carry-over model the same day. Every number quoted in `claude/bit-tbd-worlds-t1-article.md`, with its source. Scripts and data are in the figure artifact (https://claude.ai/artifact/WeMpKgB9dcbh4epCyc4yCx): `scripts/` and `data/`. Monte Carlo numbers carry about ±0.3 pp sampling error at 40–100k runs.*

## Rerun of 5 October 2026 (final; supersedes the 4 October rerun and the 2026 numbers below)

- Results by hand: LYON 3–1 Cloud9 (LCS lower final; Sheep Esports, Dot Esports), Team Liquid 3–1 LYON (LCS final, 4 Oct; Dot Esports, Sheep Esports), FURIA 3–0 LOUD (CBLOL lower final, 3 Oct; Terra). The 4 Oct rerun used "Cloud9 3–2 LYON" from Wikipedia, which was wrong. Seeds: TL LCS1, LYON LCS2 (Swiss), Cloud9 LCS3 (play-in). Still simulated: CBLOL final LØS v FURIA (10 Oct). HF dataset: no snapshot newer than 27 Sep (checked 5 Oct).
- Elo 4 Oct: Gen.G 1822, BLG 1760, HLE 1751, DK 1697, T1 1697; TL 1652, LYON 1597, Cloud9 1532.
- Forecast (100k): Gen.G 40.4%, BLG 17.7%, HLE 15.4%, T1 6.2%, DK 6.1%. With bonus 177: T1 45.9%, Gen.G 25.4%. T1 real format with bonus CI 102/255: 24.7–67.4%.
- Formats (fixed field TL, LYON, LØS, KC; field mean 1621): Gen.G alone 40.1 / Bo3 34.5 / Bo7 44.6 / groups 38.9 / KO random 38.1 / KO seeded 44.5 / league 50.3%; T1 alone 4.4–6.9%; T1 +177 40.1–55.2%; Gen.G in bonus run 24.2–27.7%. Matchup Elo vs field: real +16 (1.0%), groups +11 (0.7%), KO random +32 (2.0%), seeded +44 (2.7%), league 0. Games: real 80 (winner 18), Bo3 69 (13), Bo7 91 (23), league 240 (30).
- 13-field averages: Swiss 38.2%, groups 37.9%, Bo3 33.6%, league 45.9%.

## Rerun of 4 October 2026 (superseded: used a wrong LCS result)

- New results by hand: FURIA 3–0 LOUD (3 Oct, CBLOL lower final; Terra), Cloud9 3–2 LYON (3 Oct, LCS lower final; Wikipedia "2026 LCS season", to be confirmed by Riccardo). Cloud9 to the Swiss stage, LYON to the play-in, LOUD out. Still simulated: LCS final TL v C9 (4 Oct, order of seeds 1–2 only), CBLOL final LØS v FURIA (10 Oct).
- Elo 3 Oct: Gen.G 1822, BLG 1760, HLE 1751, DK 1697, T1 1697 (unchanged); Cloud9 1558, LYON 1587, FURIA 1388.
- Forecast (100k): Gen.G 40.6%, BLG 18.0%, HLE 15.6%, T1 6.2%, DK 6.1%. With bonus 177: T1 46.5%, Gen.G 25.2%. T1 real format with bonus CI 102/255: 25.2–67.3%.
- Formats (fixed field TL, C9, LØS, KC; field mean 1617):

| Format | Gen.G alone | T1 alone | T1 + 177 | Gen.G (bonus run) | Games | Winner plays | Matchup Elo vs field |
|---|---|---|---|---|---|---|---|
| Swiss + Bo5 knockouts (2023-26) | 40.5% | 6.1% | 46.2% | 25.2% | 80 | 18 | +16 (1.0%) |
| Swiss + Bo3 knockouts | 34.7% | 7.0% | 40.3% | 24.2% | 69 | 13 | +16 (1.0%) |
| Swiss + Bo7 knockouts | 45.0% | 5.3% | 50.6% | 25.9% | 91 | 23 | +17 (1.0%) |
| Groups + Bo5 knockouts (2014-22) | 39.0% | 6.7% | 45.5% | 24.7% | 78 | 18 | +11 (0.7%) |
| Single elimination Bo5, random | 38.3% | 6.6% | 44.2% | 24.3% | 59 | 16 | +33 (2.0%) |
| Single elimination Bo5, seeded | 44.9% | 5.5% | 49.1% | 27.6% | 59 | 16 | +45 (2.8%) |
| Double round-robin league, Bo1 | 50.6% | 4.7% | 55.3% | 26.0% | 240 | 30 | +0 (0.0%) |

- 13-field averages unchanged: Swiss 38.3%, groups 37.8%, Bo3 33.7%, league 45.7% (`data/formats_summary.csv`, rerun 4 Oct).
- Subtitle: T1's pre-Worlds Elo rank 2023 / 2024 / 2025 = 7 / 5 / 3 (title-odds rank 7 / 6 / 3), `data/backtest_teams.csv`; 2026 joint 4th (with DK).
- Parity bonus (≈128) and T1–Gen.G single-game numbers unchanged (ratings of the top teams did not move).

## Model settings

- **Elo** (`elo.py`; parameters in `backtest_params.py`): domestic K = 23, cross-region K = 36, region-offset K = 15, new-team penalty 26, scale 480.
- **Seasonal reset:** every team returns to its league's mean each season (carry = 0); region offsets carried over in full (carry_reg = 1).
- **Why the reset** (`reset_worlds.py` → `data/reset_worlds.csv`, `reset_worlds_extra.csv`), on Worlds games:
  - reset teams, keep regions: log-loss 0.6277; champion's geometric-mean pre-event chance 11.4%
  - old model (63% team carry, 91% region carry): 0.6340; 10.4%
  - full reset (teams and regions): 0.669
- **Games:** 51,034 tier-1 games, 2011-05-28 to 2026-09-26 (`build_games.py`), plus LØS 3–2 LOUD and TL 3–1 C9 (27 Sep) by hand.

## BIG

| Article | Value | Source |
|---|---|---|
| 5 teams No. 1 in 2026 | Gen.G (Jan–Mar, Sep–), BLG (spring), G2 (one week, May), T1 (Jun–early Jul), HLE (after MSI) | `data/traj2026.csv` |
| Elo on 2 Oct | Gen.G 1822, BLG 1760, HLE 1751, DK 1697, T1 1697 (joint 4th) | `data/traj2026.csv` |
| "about 125 points", T1 beats Gen.G 1 game in 3 | 1/(1+10^(125/480)) ≈ 0.35 | arithmetic |
| Other systems | GPR and lolproelo same top three; T1 4th or 5th everywhere | `data/compare_published_ratings.csv` |

## IF

| Article | Value | Source |
|---|---|---|
| 2026 forecast (real format, regional finals and play-in simulated) | Gen.G 40.3%, BLG 17.7%, HLE 15.9%, T1 6.2%, DK 6.0% | `data/forecast2026_our_elo.csv` |
| Champions' pre-event odds | SSW 26, SKT 43, SKT 14, SSG 16, IG 19, FPX 34, DWG 26, EDG 26, DRX 1.7, T1 1.6, T1 1.9, T1 9.2 (%) | `data/backtest_years.csv` |
| Favourite won | 3 of 12 vs 4.6 expected | same |
| T1 three-peat | 1 in 35,000 (lolproelo 1 in 37,000) | product of 2023–25 odds |
| T1 at Worlds | 115/157 won vs 87.7 expected: +27.3, z 4.62; 69 losses expected, 42 actual | `data/worlds_team_games.csv`, `data/intl_games_static.csv` |
| T1 at MSI | 116/174 vs 115 expected (+1.0, z 0.17) | `data/intl_games_static.csv` |
| T1 per year | 2023 43%→87%; 2024 41%→76%; 7 of 9 main events above expectation | `data/worlds_team_games.csv` |
| Worlds bonus | ML 177 Elo, profile 95% CI 102–255; leave-one-year-out 147–219; forward fit beats no bonus in each of 2021–25 (log-loss total 92.2 vs 96.7) | `residuals_intl.py`, `bonus_oos.py` |
| lolproelo residuals | T1 +23 at Worlds, −7 at MSI | `lpe_msi.py` |
| GPR on T1 | 2024 ≈ 1 in 40; 2025 ≈ 1 in 7 | `backtest_gpr.py` |
| Gen.G since 2018 | Worlds −4.8 (83 games), MSI −0.6 (50); favourite 2022, 2024, 2025; MSI champion 2024, 2025 | `data/intl_games_static.csv` |
| T1 vs LPL (Worlds Bo3/Bo5, main event) | 12/12 vs 5.04 expected, P = 9.5e-6 (1 in 105,000); underdog in 9 of 12, lowest 13% (2023 SF vs JDG). With 2025 play-in vs IG: 13/13, 1 in 222,000. 2023–25 only: 9/9 vs 3.2, 1 in 22,000 | `t1_vs_lpl.py` → `data/lck_vs_lpl_series.csv` (from `data/intl_series.csv`) |
| Other LCK vs LPL | 7/19 vs 10.25 expected, P(≤7) = 8% | same |
| T1 knockout path 2023–25 | 9 Bo5 series: LNG .295, JDG .134, WBG .478; TES .381, Gen.G .122, BLG .249; AL .413, TES .376, KT .696 → product 2.4e-5 (1 in 42,000) | `data/intl_series.csv` |
| Correction (2026-10-02) | earlier table (1 in 48,000, underdog 7 of 12, other LCK 11 of 19) had stale 2025 ratings and merged Bo1 pairs; superseded | — |

### Tournament-structure test (`t1_structure.py` → `data/t1_structure.csv`, 20k runs per year and setting)

- T1 title chance, no bonus / forward bonus (fitted on earlier Worlds only) / full 177: 2023 1.6 / 10.9 / 25.7%; 2024 1.9 / 19.3 / 25.7%; 2025 9.2 / 54.2 / 54.4%. 2026 with 177: 46.0%.
- Three-peat: 1 in 36,000 (2.76e-5) / 1 in 88 (0.0114) / 1 in 28 (0.036).
- Log-likelihood of the stage T1 actually reached, 9 Worlds: −20.73 / −12.98 / −12.19 → forward bonus ≈ 2,300× likelier.
- Forward bonus values: 2016 373, 2017 194, 2019 72, 2021 63, 2022 89, 2023 102, 2024 149, 2025 176 (2016–17 unstable, few games).
- T1 vs Gen.G 2026: game 0.354, Bo5 0.235, title 6%.

### Parity bonus (session check, 20k runs each, real 2026 format)

- T1 / Gen.G title chance by T1 bonus: +60 → 15.4 / 37.1%; +90 → 21.2 / 35.4%; +120 → 29.0 / 32.1%; +150 → 38.0 / 28.2%; +177 → 46.0 / 25.3% (100k).
- Level at ≈ +128 (≈30% each); then T1 1825 vs Gen.G 1822, single game ≈ 50%.

### Where in the mechanism (`t1_by_format.py` → `data/t1_by_format.csv`; T1 only, ratings frozen)

- Worlds by series length: Bo1 36/45 vs 28.4 (+7.6, z 2.46); Bo3 8/8 vs 4.5 (+3.6); Bo5 71/104 vs 54.8 (+16.2, z 3.33).
- MSI: Bo1 39/51 vs 39.1 (−0.1); Bo5 73/119 vs 72.3 (+0.7).
- Bonus by length at Worlds: Bo1 193 (44–363), Bo5 150 (62–241); MSI Bo1 −3, Bo5 +6. LR test Bo5 vs shorter at Worlds: χ² 1.21, p 0.27, no evidence of a Bo5-specific boost.
- Position in series (Worlds, Bo3/Bo5): game 1 23/30 vs 15.9 (+7.1, z 2.70); deciding games 7/9 vs 4.9; other games +10.5.
- Stage (rough flag): Worlds earlier stages +15.6 (81 games), knockouts +11.7 (76).

### Clutch yardstick (`clutch.py` → `data/clutch_playoffs.csv`) — cut from the article on 11 Oct (author's choice); kept here, not printed

- Domestic playoffs/finals 2014–2025, same-region games, pre-game ratings from the running Elo (not frozen). Playoff bonus per team (ML, Elo points), teams with ≥60 playoff games: 72 teams, median +17, SD 50, 90th percentile +60, max +98 (PSG Talon, 26–172). G2 +87 (34–140). T1 +52 (−4 to 108), 12th of 72, 229 games.
- T1's Worlds bonus 177 (102–255) ≈ 1.8× the largest domestic-playoff bonus of any team.

### Worlds risers (`data/worlds_risers.csv`, wins above expectation, z)

- Worlds: T1 +27.3 (4.62); DRX +7.6 (2.76, almost all 2022); KT +6.0 (1.78); DK +6.8 (1.60; MSI +0.2); Cloud9 +5.3 (1.12; MSI −3.2).
- Worst at Worlds: Movistar KOI −7.9 (−2.23), EDG −7.6 (−1.77), TES −5.2 (−1.65).
- MSI riser: RNG +14.6 at MSI (z 3.57), −0.3 at Worlds; won MSI 2018, 2021, 2022. Now drawn in IF panel c (green).
- Multiple testing (~62 tests, two-sided, Bonferroni): T1 Worlds p 3.8e-6 → 0.0002; RNG MSI p 3.6e-4 → 0.02; DRX p 0.006 → 0.36; Movistar KOI p 0.03 → 1.
- Regions, inter-region games: Korea excl. T1 +21.6 at Worlds (z 2.69), −1.4 at MSI; China +21.3 at MSI (z 2.96), −10.4 at Worlds. Possible artefact of region offsets lagging.
- ~30 teams tested: one or two |z| > 2 expected by chance. Only T1 (Worlds) and RNG (MSI) exceed 3.
- Regions: Korea excluding T1 +20 at Worlds / −2 at MSI; China +21 at MSI / −10 at Worlds.

### Betting (`data/betting_vs_model.csv`, margin removed)

- Pinnacle, 26 Sep 2023: T1 6.8% (model 1.6%); JDG 36% (41%).
- Stake via win.gg, 13 Oct 2025: T1 10.2% (9.2%); Gen.G 23.5% (33%).
- No 2026 outright odds found on 2 Oct.

### Benchmark

- Ours vs lolproelo on Worlds games: log-loss 0.627 vs 0.628; favourite won 64.2% vs 65.6%. Rank correlation 0.81–0.98.
- PandaSkill (IEEE ToG 2025; numbers from arXiv 2501.10049): 4,927 players, 37,388 games, Sep 2019–Sep 2024; 65% accuracy overall, 70% inter-region.
- Known miss: 2025 ratings put FlyQuest 2nd.

## TRUE (`data/formats2026_bonus.csv`, `formats2026_games.csv`, `formats2026_quality.csv`; field fixed, 40k each)

| Format | Gen.G alone | T1 alone | T1 + bonus | Gen.G (bonus run) | Games | Winner plays | Mean game Elo (per game) |
|---|---|---|---|---|---|---|---|
| Real: Swiss + Bo5 | 41% | 6% | 47% | 25% | 80 | 18 | 1651 |
| Swiss + Bo3 | 35% | 7% | 40% | 24% | 69 | 13 | 1642 |
| Swiss + Bo7 | 45% | 5% | 51% | 26% | 91 | 23 | 1658 |
| Groups + Bo5 | 39% | 6% | 46% | 25% | 78 | 18 | 1650 |
| Knockout, random | 38% | 6% | 44% | 24% | 59 | 16 | 1654 |
| Knockout, seeded | 45% | 5% | 49% | 28% | 59 | 16 | 1666 |
| Full league | 50% | 4% | 56% | 26% | 240 | 30 | 1620 |

- Field mean 1620. Per game: real format +31, league 0. Share of games top-8 vs top-8: real 37%, league 23%, Bo7 40%.
- **Single-game predictability** (mean P(higher-rated wins a game) per matchup / per game): real 64.5 / 63.3%; Bo3 64.5 / 63.6; Bo7 64.5 / 63.0; groups 66.9 / 65.2; KO random 64.0 / 63.6; KO seeded 65.6 / 65.0; league 65.7 / 65.7.
- **Per matchup (each series once; used in the figure and text):** real 1636 (+16), Swiss+Bo3 1636, Swiss+Bo7 1636, groups 1631 (+11), knockout random 1652 (+32), knockout seeded 1664 (+44), league 1620 (0). Top-8 vs top-8 share of matchups: real 28%, groups 23%, knockout random 37%, seeded 33%, league 23%. Matchups per tournament: Swiss 40, groups 57, knockout 15, league 240.
- Knockout rounds, mean matchup Elo (Bo3 / Bo5 / Bo7): QF 1685 / 1685 / 1685; SF 1710 / 1714 / 1717; final 1731 / 1739 / 1744 (20k runs, session check).
- IF panel c grey band: ±1.96·√(v̄·n), v̄ = mean per-game p(1−p) pooled over the six lines; each line's own band ends within 0.4 wins of it.
- T1 + bonus in real format, CI from bonus range 102–255: 24.6–67.5%.
- Highest-rated team's title chance averaged over the 13 fields 2014–2026: Swiss 38.3%, groups 37.9%, Bo3 33.8%, league 45.9% (`data/formats_summary.csv`).
- BLG and HLE with the bonus: about 10% each.

## Rerun before publication

After the CBLOL final (10 Oct): set real seeds, rerun `forecast_2026.py`, `formats2026_bonus.py`, `formats2026_quality.py`, `traj2026.py`; rebuild figures; update this file and the manifest.

## Update 9 Oct 2026 (Riccardo's review of the Italian draft)
- **Bonus as win rate.** T1's Worlds bonus 177 Elo = T1 would beat a copy of itself 70% of games (95% CI 62–77%; leave-one-out 67–74%); 84% of Bo5s. Playoff clutch: median team 52%, PSG Talon 62% (top), T1 56% (12th of 72).
- **Formats, 16 Swiss teams fixed, 40k runs** (`out/formats2026_bonus.csv`, `out/formats2026_games.csv`). Knockout brackets now avoid same-region first-round matches. Gen.G alone / T1 alone / T1+bonus / games / winner plays:
  - Real Swiss+Bo5 40.1 / 6.0 / 46.3 / 80 / 18
  - Swiss+Bo3 34.5 / 6.9 / 40.1 / 69 / 13
  - Swiss+Bo7 44.6 / 5.4 / 50.8 / 91 / 23
  - Swiss+double elimination (new) 46.7 / 4.8 / 52.5 / 108 / 25
  - Groups+Bo5 38.9 / 6.3 / 45.6 / 78 / 18
  - KO random 38.9 / 6.7 / 44.8 / 59 / 16
  - KO seeded 44.5 / 5.1 / 48.7 / 59 / 16
  - League 50.3 / 4.4 / 55.2 / 240 / 30
- **Trade-offs** (`out/formats2026_tradeoffs.csv`, 8k runs, `formats2026_tradeoffs.py`). Mismatch share = share of matchups where the favourite wins a game ≥75%; close series = Bo3+ series the favourite wins ≤65%, per tournament. Real 18.1% / 8.5; Bo3 18.2 / 9.2; Bo7 18.1 / 7.4; DE 15.9 / 11.6; Groups 23.3 / 3.0; KO random 15.8 / 5.0; KO seeded 21.0 / 4.4; League 21.6 / 0 (all Bo1).
- **League climax.** Title still open going into the last round 51.6%; clinched ≥3 rounds early 13.0%; mean rounds left at clinch 0.96.
- **Polymarket (9 Oct, GPR #1 after Worlds, not champion):** GEN 33, HLE 25, BLG 21, T1 10, G2 5; volume $164k. Not in text yet.
- Italian figures: `*-it.png`, produced by `bit/i18n.py` from the same drawing.
- **MSI format check (9 Oct).** MSI bracket stage is Bo5 double elimination since 2023 (Wikipedia 2023 MSI; LoL Esports MSI 2025 primer). T1 MSI excess wins: 2023–26 +1.8 on 86 games; 2015–22 −0.8 on 88. The residual test conditions on actual opponents, so format changes the schedule, not the yardstick.
- **CBLOL final:** LØS vs FURIA, Sat 10 Oct 2026, Rio de Janeiro, Bo5; Sheep Esports lists 16:00 (timezone not shown).

## Update 9 Oct 2026, late (formats)
- **16-team double elimination, seeded, Bo5** (replaces Swiss + DE): Gen.G 50.1% / T1 3.9% / T1+bonus 53.9% (Gen.G 28.3%); BLG 20.2, HLE 15.1; 119 games, winner 23; 30 series; mismatch share 15.9%; close series 10.7 per tournament.
- **Swiss + Bo1 knockouts (football-style)**, `formats2026_bo1.py` → `out/formats2026_bo1.csv`: Gen.G 26.7%, BLG 16.0, HLE 14.4, DK 8.1, T1 8.0% (T1+bonus 31.0%, Gen.G 21.1%); 59 games, winner 9.
- Figure 4 shows 6 formats (all knockouts Bo5): real, groups, KO random, KO seeded, DE, league. Gen.G alone 39–50%; T1 with bonus 45–55%.
- **Rank correlation of final order with ratings** (`formats2026_rankcorr.py` → `out/formats2026_rankcorr.csv`, 4k runs; result = series won, ties by fewer series lost; Spearman mean / Kendall / share of rating top-4 finishing top-4): real Swiss+Bo5 0.62/0.49/55%; groups 0.67/0.53/58%; KO random 0.50/0.40/52%; KO seeded 0.70/0.58/67%; DE seeded 0.75/0.62/62%; league 0.81/0.67/65%; Swiss+Bo1 0.59; Swiss+Bo3 0.61; Swiss+Bo7 0.63. Caveat: seeds and pots come from the same ratings, which inflates seeded formats.
- **Football parallel, World Cup 2026** (`football/wc2026.py` → `out/wc2026_knockout_series.csv`; data `martj42/international_results` + shootouts, downloaded 9 Oct 2026, kept in `data/football/`). World Football Elo by eloratings.net's method, frozen 10 Jun 2026: Spain 2220, Argentina 2191, France 2126, England 2091, Brazil 2070. Real R32 bracket replayed 200k times; one match won with prob = Elo expected score (draw = half), hosts +100. Spain (actual winner, beat Argentina 1–0 on 19 Jul): Bo1 26.0%, Bo3 38.5%, Bo5 45.6%, Bo7 50.1%; Argentina 24.8/31.0/33.4/34.5%.
- Figure 4: groups row renamed "Groups + knockouts (to 2022)" / "Gironi + eliminazione (fino al 2022)"; italic sport parallel under each format title; DE row draws upper bracket, red drop arrow and lower bracket.
- **League + playoffs** (NBA/LCK structure; `formats.league_playoffs`: single round robin of single games, top 8 by wins → seeded Bo5 bracket 1v8, 4v5, 2v7, 3v6): Gen.G 41.4% / T1 6.0% / T1+bonus 47.3% (Gen.G 25.7%); BLG 18.5, HLE 15.5; 148 games, winner 27; mismatch 20.7%; close series 2.9; rank correlation 0.73 (top-4 62%). LCK 2026 actual: double round-robin Bo3 then 6-team double-elimination Bo5 playoffs (Wikipedia, 2026 LCK season).
- Bug fixed 9 Oct: `bit/i18n.finish` re-set ticks on axis-off figures, which widened the y-limits of the Italian versions of the TRUE and odds figures (shrunken layout, blank margin). It now restores size and limits before saving the -it file; all IT figures re-rendered and checked against EN extents.
- **Bradley–Terry check (10 Oct)** (`bt_compare.py` grid of 40 settings → `out/bt_vs_elo.csv`; `bt_check.py` → `out/bt_check.csv`). BT = ridge logistic fit of one strength per team on all games in a window before each Worlds, exponential time weights, predictions frozen on day one; 1,248 Worlds games 2014–2025. Our Elo: log loss 0.620, accuracy 64.8%, T1 +27.3 wins (z 4.6). Best BT (2-year window, half-life 1 year, C=100): log loss 0.612, accuracy 66.8%, T1 +14.6 (z 2.6) — tuned on the same Worlds games. Same BT without past Worlds games in training: 0.648, 64.1%, T1 +18.8 (z 3.3). BT on the current season only (like our reset): 0.716, 60.6%, T1 +18.6 (z 3.3) — too few cross-region games in one season. Reading: BT can predict slightly better when it sees two years, partly because it learns T1's (and others') past Worlds form; T1's Worlds edge survives every variant but is 15–19 wins instead of 27.
- **Glicko-2 and TrueSkill check (10 Oct)** (`glicko_trueskill.py`, `glicko_trueskill_extra.py` → `out/glicko_trueskill.csv`; own implementations of Glickman 2012 and Herbrich et al. 2007; one rating period per game; uncertainty widened each 1 Jan; no region offsets; frozen at each Worlds start; 1,248 Worlds games). Best Glicko-2 (tau 0.5, no reset): log loss 0.661, accuracy 61.5%, T1 +29.7 (z 5.0); across 11 settings T1 +28.3 to +29.8. Best TrueSkill (tau 0.083, no reset): 0.646, 64.1%, T1 +25.7 (z 4.3); across 14 settings T1 +23.5 to +34.8 (z 4.0–6.0). Both predict worse than our Elo (0.620, 64.8%), mainly because they have no league-strength term.
- **Across rating methods**, T1's Worlds excess: our Elo +27 (z 4.6); lolproelo.com +23; Glicko-2 +30; TrueSkill +26; Bradley–Terry +15 to +19 (z 2.6–3.3, lowest when it sees T1's past Worlds). Significant in all.

## Final update, 11 Oct 2026 (after the CBLOL final and the play-in draw)
- **CBLOL final** (10 Oct): LØS 3–2 FURIA (games LØS, FURIA, LØS, FURIA, LØS; Strafe, Pichau Arena). LØS to the Swiss stage, FURIA to the play-in.
- **Play-in draw** (10 Oct, Strafe): FURIA v MVK Esports, Cloud9 v Karmine Corp; double elimination, Bo5; 15–18 Oct, Los Angeles. Now fixed in `forecast_2026.py` (was drawn at random).
- **Ratings at 10 Oct:** Gen.G 1822, Bilibili 1760, Hanwha Life 1751, Dplus KIA 1697 (1696.75), T1 1696 (1696.43), LØS 1412, FURIA 1380.
- **Forecast (100k):** Gen.G 40.4%, Bilibili 17.7%, Hanwha Life 15.6% (now printed 16%), T1 6.1%, Dplus KIA 6.0%; play-in winner: Karmine Corp 63%, Cloud9 33%, FURIA 4%, MVK 0.2%. With T1 bonus: T1 46.0%, Gen.G 25.4%.
- **Formats rerun** (field unchanged; LØS rating updated): Gen.G alone 39.0–50.1% across the figure's seven formats; T1 with bonus 44.8–55.8% (league now 55.8 → printed "56%"); league rank correlation 0.815 (printed 0.82; was 0.813); all other printed figures unchanged after rounding. Bo1 knockouts: Gen.G 26.7%, T1 8.0% (30.9% with bonus).
- `check_numbers.py` in the package: 58/58 PASS on both editions.

### Usage (12 Oct 2026)
- At least **58 million** effective tokens (Claude Opus 5.5): 18.13 + 19.23 + 21.59 = 58.95 M, three non-overlapping logged windows (`data/usage_windows.csv`, method in USAGE.md). Lower bound; no price.

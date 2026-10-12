# BIG IF TRUE #002 · T1: the Korean esports team that transforms in October

Code and data behind the BIG IF TRUE issue on T1 and the League of Legends World Championship (English and Italian
editions in `article/`).

Article: https://bigiftruebits.substack.com/p/worlds-t1 (also at https://bigiftruebits.github.io/bit-002-worlds-t1/article.html).
The Zenodo record holds the code and data, not the article texts: `check_numbers.py` compares with `article/en.md` and
`article/it.md`, so copy them from this repository into `article/` before running it from the archive.

## Cards on the table

- **Who did what.** Every step, from downloading the data through the Elo ratings, the tournament simulators for each
  year's format and the comparisons with published ratings and betting odds, to the charts, was written and executed by
  **Claude Opus 5.5** (Anthropic), in one extended Cowork session working from Riccardo Gallotti's instructions. He set
  the questions and the framing; the model did the work.
- **Usage** → `USAGE.md`: at least 58 million effective tokens (Claude Opus 5.5), summed over the three logged
  windows that do not overlap; the session's transcript was compressed several times, so the true figure is higher.
- **Errors found and fixed** → `NOTES.md` (14 entries).
- **Every printed number** → `KEY_NUMBERS.md`; `python check_numbers.py` re-derives 46 of them from `data/` and finds
  each one in both editions: **46/46 PASS** (12 Oct 2026).
- **Peer-reviewed work** the article relies on: De Bois et al. (2025), *PandaSkill*, IEEE Transactions on Games;
  González-Díaz, Gossner & Rogers (2012), *J. Econ. Behav. Organ.*; Sziklai, Biró & Csató (2022), *Computers &
  Operations Research*. Full references in the article.
- **Code and data**: this repository; archived, code and data together, on Zenodo (DOI added after publication).
- **How to cite**: Gallotti, R. (2026). *BIG IF TRUE #002: T1: the Korean esports team that transforms in October*
  [Code and data]. Zenodo. (DOI added after publication.)

## What it computes

1. **Ratings** (`code/elo.py`, parameters in `code/backtest_params.py`): Elo for every top-league and international
   pro team since 2011, with a strength term per league that moves only when leagues meet; teams restart at their
   league's average each season, league strength carries over. Parameters chosen by backtest on past Worlds
   (`tune.py`, `backtest.py`, `reset_worlds.py`).
2. **Every Worlds 2014–2026 simulated in its real format** (`code/sim.py`, `code/history.py`, `code/formats.py`),
   50,000 times each, from ratings frozen on the first day.
3. **T1's Worlds over-performance** (`code/residuals_intl.py`, `bonus_oos.py`, `t1_by_format.py`, `clutch.py`,
   `t1_vs_lpl.py`): wins against expectation at Worlds and at MSI, the Worlds bonus with its interval and
   leave-one-out range, a domestic-playoff yardstick (computed, not printed in the article), and robustness against other rating methods
   (`compare_published.py`, `bt_compare.py`, `bt_check.py`, `glicko_trueskill*.py`).
4. **The 2026 forecast** (`code/forecast_2026.py`, `teams2026.py`, `traj2026.py`): every result to the CBLOL final of
   10 October, the real play-in draw, 100,000 tournaments, with and without T1's bonus.
5. **Formats** (`code/formats2026_*.py`): this year's 16 teams under seven formats (plus Bo1, Bo3 and Bo7 knockouts):
   title odds, games, foregone matchups, close series, league climax, rank correlation of the final order.
6. **Football parallel** (`code/football/wc2026.py`): the 2026 World Cup round-of-32 bracket replayed with longer ties.
7. **Figures** (`code/bit/fig_*.py`): each in English and Italian (`figures/*-it.png`).

## Quick start

```
pip install -r requirements.txt
make intermediate      # raw/ -> data/games_clean.parquet   (raw/ comes from the Zenodo record or `make data`)
make forecast figures  # minutes
make check             # 46/46 PASS
```

Scripts run from `code/` and read and write `../data/`, `../raw/`, `../figures/`. `make all` reruns everything
(a few hours; the historical format comparison takes about an hour, each 2026 format sweep about 15 minutes).
`docx/build.js` builds the Word drafts used for review (Node, `docx` package); not needed for the analysis.

## Caveats

- Ratings summarise results; they know nothing of rosters, injuries, patches or draft. Games in a series are treated
  as independent.
- "Expected" wins use ratings frozen on the first day of each event, so a team that improves during an event looks
  lucky. This applies to all teams.
- The 2026 forecast draws the Swiss round-1 pairings itself: the real draw comes after the play-in.
- The format comparison holds the 16 teams fixed (Karmine Corp as play-in winner) and seeds by rating, which favours
  seeded formats in the rank-correlation measure; the text says so.

## What cannot be checked from this package

- **Riot's Global Power Rankings and lolproelo.com ratings** are not redistributed (no licence found). Their values are
  blanked in `data/`; the comparisons that use them (agreement with published ratings, "23 wins above expectation"
  with lolproelo) need the pages recollected with `code/parse_gpr.py` and `code/scrape_lpe.py`. The exact URLs of the
  saved GPR pages were not logged.
- **A few files were produced by one-off commands** during the session rather than by a script here:
  `data/betting_vs_model.csv` (bookmaker odds typed in from the press reports cited in the article),
  `data/worlds_risers.csv`, `data/reset_worlds_extra.csv`, `data/t1_worlds_series.csv`, `data/lck_vs_lpl_worlds.csv`.
  Their numbers are in KEY_NUMBERS.md.
- **`data/games_clean.parquet` cannot be rebuilt byte-identically**: the original build ordered 978 games (1.9%) with
  Python's randomised `hash()`. The shipped file is the one used; see NOTES.md, entry 11.
- The Leaguepedia mirror changes over time; the snapshot used (27 Sep 2026) is the one in `raw/` in the Zenodo record.

## Licences

Code: MIT (`LICENSE`). Derived data, figures and texts: CC BY-SA 4.0, because the game data are Leaguepedia's
(CC BY-SA 3.0) — see `DATA_LICENSE.md` and `DATA_MANIFEST.md`.

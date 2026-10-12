# BIG IF TRUE · worlds-t1. Run from the repository root. Times on a laptop in brackets.
PY ?= python
.PHONY: data intermediate ratings history forecast formats football figures check all

data:            ## raw inputs that may be redistributed (minutes)
	$(PY) download.py

intermediate:    ## raw -> data/games_clean.parquet (seconds)
	cd code && $(PY) build_games.py

ratings:         ## parameter search, backtests, T1 tests (tens of minutes)
	cd code && $(PY) tune.py && $(PY) backtest.py && $(PY) reset_worlds.py && $(PY) residuals.py && $(PY) residuals_intl.py \
	 && $(PY) bonus_oos.py && $(PY) t1_by_format.py && $(PY) t1_structure.py && $(PY) series_table.py && $(PY) t1_vs_lpl.py && $(PY) clutch.py

history:         ## every Worlds 2014-2026 in its real format and in the alternatives (about an hour)
	cd code && $(PY) history.py && $(PY) formats.py

forecast:        ## 2026 forecast and season trajectories (minutes)
	cd code && $(PY) traj2026.py && $(PY) forecast_2026.py

formats:         ## the format comparison with this year's teams (about 15 minutes each, can run in parallel)
	cd code && $(PY) formats2026_bonus.py && $(PY) formats2026_quality.py && $(PY) formats2026_tradeoffs.py \
	 && $(PY) formats2026_rankcorr.py && $(PY) formats2026_bo1.py && $(PY) formats2026_single_league.py && $(PY) formats2026_rematch.py && $(PY) msi_final_rematch.py

robustness:      ## other rating models (tens of minutes)
	cd code && $(PY) bt_compare.py && $(PY) bt_check.py && $(PY) glicko_trueskill.py && $(PY) glicko_trueskill_extra.py

football:        ## World Cup 2026 knockouts replayed with longer ties (minutes)
	cd code && $(PY) football/wc2026.py

figures:         ## every figure, English and Italian, into figures/
	cd code && $(PY) bit/fig_big.py && $(PY) bit/fig_if.py && $(PY) bit/fig_odds.py && $(PY) bit/fig_true.py

check:           ## every printed number re-derived from data/ and found in both editions
	$(PY) check_numbers.py

all: intermediate ratings history forecast formats robustness football figures check

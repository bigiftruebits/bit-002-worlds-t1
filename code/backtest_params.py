"""backtest_params.py

    python backtest_params.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
# Seasonal reset (adopted 2026-10-02 at Riccardo's request): every team's rating returns to its league's
# average each new season (carry=0); region strength is carried over in full (carry_reg=1.0).
# On Worlds games 2014-2025 this predicts better than carrying team ratings over (reset_worlds.py).
PARAMS=dict(K=23,K_intl=36,K_reg=15,carry=0.0,carry_reg=1.0,new_pen=26)
SCALE=480

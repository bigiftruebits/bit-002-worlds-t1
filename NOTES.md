# NOTES — bug log (worlds-t1)

Every real error found during the work, in the order found: what went wrong, how it was found, what it would have
done to the result, and where the fix lives. All code by Claude Opus 5.5 (Anthropic) under Riccardo Gallotti's
direction; errors found by the model's own checks unless stated.

1. **The 2025 notebook (the author's starting point) played every knockout series as one game** instead of a best of
   five, which flattens the odds towards upsets; it **drew the play-in result once** and reused it for all 100,000
   tournaments; and it **re-shuffled the wrong group** before the last Swiss round. Found by reading the notebook before
   reusing it. Fixed in `code/sim.py` (`World.play` with series length; play-in drawn per tournament; Swiss pairing).
2. **A text match counted the IEM World Championship as Worlds**, inflating T1's over-performance by two wins. Found
   when the list of "Worlds" events was printed. Fixed in `code/residuals_intl.py` (match on "Season World Championship").
3. **Group-stage tiebreakers skipped Riot's head-to-head rule.** Effect at most 0.3 percentage points. Fixed in
   `code/sim.py`, `tiebreak`.
4. **The first table of Korea–China series used stale 2025 ratings and merged pairs of single games into series.**
   Rebuilt from Leaguepedia match ids; T1's unbeaten run against the LPL went from one in 48,000 to one in 100,000.
   Fixed in `code/t1_vs_lpl.py` and `code/series_table.py`.
5. **Renamed teams** (SK Telecom T1 → T1, Samsung Galaxy → Gen.G, DAMWON → Dplus KIA) restarted their ratings until
   joined by hand. Fixed in `code/elo.py`, `RENAMES`.
6. **League strength was partly pulled back together each winter** in the first version; testing showed this made Worlds
   predictions worse. The final version carries league strength over in full (`code/backtest_params.py`, `carry_reg=1`;
   tests in `code/reset_test.py`, `code/reset_worlds.py`).
7. **North America's last qualifying result was taken from Wikipedia, which had it the wrong way round** (Cloud9 beating
   LYON; LYON won 3–1). Found the next day by checking two news reports; forecast rerun. Fixed in `code/teams2026.py`.
8. **An early figure listed Team Liquid's path to Worlds as undecided** when it was already sure of the Swiss stage.
   Fixed in `code/bit/fig_big.py`, `STATUS`.
9. **Italian figures were drawn with a stretched vertical scale** (9 Oct). The step that translates labels re-set the
   tick positions on figures whose axes are hidden, which widened their limits: the Italian TRUE figure and predictions
   table looked squeezed with a blank strip. Found by comparing the ink extent of the English and Italian files. Fixed in
   `code/bit/i18n.py`, `finish` (restores size and limits before saving the Italian file); all Italian figures redrawn.
10. **The Bradley–Terry comparison first returned 50% accuracy** (10 Oct): the time weights were not normalised, so the
    ridge penalty shrank every strength to zero. Found because 50% is chance level. Fixed in `code/bt_compare.py`
    (weights rescaled to sum to the number of games).
11. **`build_games.py` used Python's `hash()` to order the games of series known only by their score.** `hash()` is
    randomised per process, so a rebuild orders those games differently: 978 of 51,034 games (1.9%), in 334 series
    where both teams won games. Found while packaging (11 Oct). The shipped `data/games_clean.parquet` is the file used
    for every number in the article; the code now uses `zlib.crc32` so future rebuilds are deterministic, but they will
    not be byte-identical to the shipped file. Not rerun: the effect is the order of games inside a series, which moves
    ratings by a few points at most.
12. **The article said "six results added by hand" when there were five** (before the CBLOL final); with the final there
    are six. Found while packaging. Fixed in both editions.
13. **A personal aside dated Royal Never Give Up's success before the author followed the game**; two of its three MSI
    titles (2021, 2022) came after. Found by checking the claim against the MSI champions list; reworded by the author.
14. **The Figure 1 script still drew an old title** ("Gen.G on top, T1 joint fourth" / "T1 quarta a pari merito"), while the
    figure in the article says "T1 level with Dplus KIA" / "T1 appaiata a Dplus KIA", as the text does (T1 fifth, 1696 to
    Dplus KIA's 1697). Found while packaging (12 Oct, Claude Code) by redrawing every figure and comparing it with the
    shipped file. The figures were right; only a reader rerunning the script would have got the old title. Fixed in
    `code/bit/fig_big.py` and `code/bit/i18n.py`.

## Corrections after publication

(none yet)

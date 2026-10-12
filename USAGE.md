# USAGE — worlds-t1

Usage ledger of the issue (`claude/USAGE-TRACKING-INSTRUCTIONS.md`). Effective tokens = input + 0.1 × cache read
+ 2 × cache write + 5 × output, measured from the chat transcript (`Claude_codes/tools/usage_by_activity.py`).
No prices, no energy or CO₂ figures.

**Coverage verdict: partial, reported as a lower bound.** The analysis and writing were done in one Cowork chat
(Claude Opus 5.5, no sub-agents) whose transcript was compressed several times, so turns before each compression can no
longer be read; the packaging was done in Claude Code. The article reports **at least 63 million effective tokens**
(Claude Opus 5.5, in a Cowork chat and in Claude Code): the three logged Cowork windows that do not overlap plus the
measured Claude Code packaging (`data/usage_windows.csv`), rounded down. The true figure is higher.

| Block | What was done | Effective tokens counted | Coverage |
|---|---|---|---|
| to 4 Oct 2026 | data, Elo model and backtests, tournament simulators, T1 tests, formats, figures, drafts 1–5 | 11.33 M | partial |
| 5 Oct 2026 (cumulative) | reruns after the 3–4 Oct qualifiers, rewrites, format compliance | 18.13 M | partial |
| 9 Oct 2026 | Italian edition review; double elimination, region rule, format trade-offs; Italian figures | 0.44 M (after a compression) | partial |
| 9–11 Oct 2026 | rank correlation, league + playoffs, football parallel, Bradley–Terry, Glicko-2, TrueSkill; CBLOL final and play-in draw; this package | 19.23 M (transcript since the last compression) | partial |

| 11–13 Oct 2026 | final rerun, edits with Riccardo, both texts final, consistency check, packaging requests, DOI | 24.29 M (transcript since the 11 Oct compression, to 12 Oct 22:08 UTC) | partial |

**How the 63 M is summed** (13 Oct 2026, publication morning). The rows above overlap: the 5 Oct count (18.13 M) already contains the
4 Oct one (11.33 M), and the 9–11 Oct count (19.23 M) starts at the same 9 Oct compression as the 0.44 M logged that
day, so it contains it. The three windows that do not overlap are 18.13 M (to 5 Oct), 19.23 M (9 Oct, after the
compression, to 10 Oct 22:45 UTC) and 24.29 M (11 Oct 15:34 UTC to 12 Oct 22:08 UTC): 61.65 M in Cowork. Plus the Claude Code packaging, 1.84 M
(below): **63.49 M, printed as "at least 63 million"**.
Not counted: 5–9 Oct before the 9 Oct compression, and 10 Oct 22:45 to 11 Oct 15:34 UTC.

Breakdown of the last block (19.23 M): analytics and modelling 9.08 M, reading files 3.35 M, orchestrating 1.71 M,
writing documents 1.63 M, writing and reasoning 1.36 M, quality checks 0.89 M, web page reads 0.69 M (24 pages),
search 0.44 M (18 searches), structuring data 0.08 M.

**Packaging in Claude Code** (12 Oct 2026, appended by that session). Measured from the Claude Code transcript with
`tools/bit_usage.py --bit bit-002-worlds-t1`: Claude Opus 5.5, 62 responses attributed to this issue, input 124, output
54,039, cache write 116,068, cache read 13,406,840: **1.84 M effective tokens**, coverage complete for the responses
counted up to the zip build; the rest of the same session (receipts, registry) is in the registry, not here.
**Included in the article's lower bound since 13 Oct** (Riccardo, 12 Oct: the bound covers all of #002's work).

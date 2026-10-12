# DATA_MANIFEST — worlds-t1

Every raw input, where it came from, under which licence, and whether it is in this package.
Licences checked on the providers' pages on 10–11 October 2026.

## Sources

| Source | Provider and dataset | Licence (as stated by the provider) | In this package / Zenodo record | Credit line |
|---|---|---|---|---|
| Pro League of Legends results 2011–2026 | Leaguepedia (lol.fandom.com), via the Hugging Face dataset `gptilt/lol-esports-matches` | CC BY-SA 3.0 (dataset card, https://huggingface.co/datasets/gptilt/lol-esports-matches, checked 2026-10-10) | Yes: `raw/leaguepedia_hf/` (snapshot) | "Data: Leaguepedia contributors, CC BY-SA 3.0, via gptilt/lol-esports-matches" |
| Six series results 27 Sep – 10 Oct 2026, added by hand | Sheep Esports, Dot Esports, Terra, Strafe, Pichau Arena (news reports) | Facts (scores) | Yes, as code: `code/teams2026.py`, `LATE_RESULTS`, with the sources in comments | — |
| Play-in draw of 10 Oct 2026 | Strafe, "Worlds 2026 Play-In Draw Sets Opening Matchups" | Fact | Yes, as code: `code/forecast_2026.py` | — |
| National-team football results 1872–2026 and shootouts | GitHub `martj42/international_results` | CC0-1.0 (repository page, https://github.com/martj42/international_results, checked 2026-10-10) | Yes: `raw/football/` | Courtesy: "martj42/international_results" |
| LoL Esports Global Power Rankings (Riot Games), 2022–2026 pages | lolesports.com, "Global Power Rankings" pages, saved 2 Oct 2026 | No licence for redistribution found | **No.** Values blanked in the derived files; `code/parse_gpr.py` reads the saved pages. The exact page URLs were not logged (see README, "What cannot be checked") | "Global Power Rankings, Riot Games" |
| lolproelo.com ratings, day before each Worlds and MSI | https://lolproelo.com/rankings?year=Y&through=D | No licence for redistribution found | **No.** Values blanked; `code/scrape_lpe.py` and `code/lpe_msi.py` recollect them | "lolproelo.com" |
| Betting odds: Pinnacle outright preview (26 Sep 2023); Stake outright odds as reported by win.gg (13 Oct 2025) | Press reports | Facts quoted | A few values in `data/betting_vs_model.csv` | — |

Leaguepedia's CC BY-SA licence is share-alike: everything in `data/` derived from it, and the figures, are under CC BY-SA 4.0 (see DATA_LICENSE.md).

## Raw files in this package

| File | Source | Retrieved | Bytes | sha256 |
|---|---|---|---|---|
| raw/leaguepedia_hf/entity_aliases.parquet | gptilt/lol-esports-matches (snapshot of 27 Sep 2026) | 2026-10-02 | 823124 | f2b9d32b1eb17684723ebfd5381d310944e332ad700c3dda5faf96b724f93c6b |
| raw/leaguepedia_hf/games.parquet | same | 2026-10-02 | 9204669 | 46c30cca7def7ed5745164f1ebb8d08112712075d7b8ef0175a9822a9626feb2 |
| raw/leaguepedia_hf/matches.parquet | same | 2026-10-02 | 2130346 | 4770c4e3d15dc72f102e9d23325610ed34efd0f85cac40883cc7916f3787d43f |
| raw/leaguepedia_hf/teams.parquet | same | 2026-10-02 | 96272 | dd45cecffc122893eb288e1d1eba040e872f54abfc7239195e2878e3721cd4a4 |
| raw/leaguepedia_hf/tournaments.parquet | same | 2026-10-02 | 289719 | 88729065946347ab7300c4e86fed6c08c81ce72afefb915078d709e743685889 |
| raw/football/results.csv | https://raw.githubusercontent.com/martj42/international_results/master/results.csv (data to 6 Oct 2026) | 2026-10-09 | 3764601 | b38434f8f74cd9faacb269eb1c97760fc2dfac43fcb211779e0bd2cbb48f89e3 |
| raw/football/shootouts.csv | https://raw.githubusercontent.com/martj42/international_results/master/shootouts.csv | 2026-10-09 | 29789 | 072b445adf5183fbe981087857e5b64c8f17abfdbf257b1822ceacb4a37919fa |

The Hugging Face dataset is updated over time; the snapshot used is the one in `raw/`. `download.py` fetches the current version, which will differ.

## Not redistributed (recollect with the scripts)

| Files used in the analysis | Script |
|---|---|
| `gpr_2022_worlds.html`, `gpr_2023_worlds.html`, `gpr_2024_worlds.html`, `gpr_2025_worlds.html`, `gpr_2026_current.html` and the parsed `gpr_*_history.csv` | save the pages, then `code/parse_gpr.py` |
| `lpe_2014.html` … `lpe_2026.html`, `lpe_msi_*.html`, `lolproelo_preworlds.csv` | `code/scrape_lpe.py`, `code/lpe_msi.py` |

Put them in `raw/not_redistributed/` (GPR) and `raw/not_redistributed/lolproelo/`.

## Licences re-checked at packaging (Claude Code, 2026-10-12)

| Source | Page read | What the page states |
|---|---|---|
| Leaguepedia | MediaWiki API of lol.fandom.com, `action=query&meta=siteinfo&siprop=rightsinfo` | `rightsinfo`: "CC BY-SA 3.0", URL https://www.fandom.com/licensing (that page and Leaguepedia:Copyrights answered HTTP 402 to an automated reader, so their wording was not read) |
| `gptilt/lol-esports-matches` | https://huggingface.co/datasets/gptilt/lol-esports-matches | licence tag `cc-by-sa-3.0`; no other licence text, no attribution clause printed |
| `martj42/international_results` | https://github.com/martj42/international_results | "CC0-1.0 license" (repository licence file) |
| lolproelo.com | https://lolproelo.com/ | no licence or terms printed; credits "Match data via Leaguepedia". Not redistributed. |
| Riot Games, Global Power Rankings | https://www.riotgames.com/en/legal ("Legal Jibber Jabber") | a revocable licence for non-commercial fan projects; nothing on republishing esports rankings or data. Not redistributed. |
| Betting odds (Pinnacle, win.gg) | not read | facts quoted from press reports, a few values in `data/betting_vs_model.csv` |

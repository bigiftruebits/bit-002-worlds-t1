# bit-002-worlds-t1 — state for the next session

Issue **#002**, slug `worlds-t1`, launch **Tuesday 13 Oct 2026, 15:00** (Substack `/p/worlds-t1`). Working file: not in the Zenodo zip.

## Phase (2026-10-12): packaged, waiting for Riccardo

- Analysis, figures, texts: Claude Opus 5.5 in one Cowork chat (to 12 Oct). Packaging: Claude Opus 5.5 in Claude Code,
  session "BIG IF TRUE data archive and consistency" (task 16, `registry/FROM_EDITORIAL_MANAGER_2026-10-11_task-16_archive-session.md`).
  The checks run by the packaging session are not an independent gate.
- `check_numbers.py` 46/46; figures redrawn by the scripts and compared with the shipped files (all within the #001 tolerance).
- Zenodo zip: `tools/build_zenodo_zip.sh --repo bit-002-worlds-t1 --no-article` → `sources/bit-002-worlds-t1/zenodo/`.
- Article pages: `tools/article_to_site.py repos/bit-002-worlds-t1 https://bigiftruebits.substack.com/p/worlds-t1 --date 2026-10-13 --fig 1=fig-002-big-worlds-elo-2026.png --fig 2=fig-002-if-worlds-t1.png --fig 3=fig-002-true-formats.png --fig odds=fig-002-odds-2026.png`
- Preview: `cd code && python bit/make_preview.py en|it A|B`; candidates and comparison sheet in `sources/bit-002-worlds-t1/preview-candidates/`; `docs/` holds variant A until Riccardo picks.

## Open

1. Zenodo draft: `zenodo_sandbox_token` missing, so no upload yet (sandbox first, then production: `tools/zenodo_upload.py`).
2. Reserved DOI into both editions ("Code and data", "How to cite"; article files only), then rerun article_to_site.
3. GitHub repository `bigiftruebits/bit-002-worlds-t1` (Riccardo creates it, private), push.
4. REQUESTS.md items 1–4 (writer).
5. Preview variant A or B (Riccardo).

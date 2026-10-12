# Licences of what this package contains

- **Code** (`code/`, `check_numbers.py`, `download.py`, `docx/`): MIT, see LICENSE.
- **Derived data** (`data/`), **figures** (`figures/`) and **texts** (`article/`, the documentation): **CC BY-SA 4.0**.
  Reason: the game results come from Leaguepedia under CC BY-SA 3.0, which is share-alike; adaptations may be
  licensed under the same or a later version of the licence with the same elements, so CC BY-SA 4.0. Attribution:
  "Riccardo Gallotti, BIG IF TRUE; game data from Leaguepedia contributors (CC BY-SA 3.0)".
- **Third-party data** keep their providers' licences (DATA_MANIFEST.md): Leaguepedia CC BY-SA 3.0; football results CC0-1.0.
  Riot Games' Global Power Rankings and lolproelo.com ratings are **not** included: their values are blanked in
  `data/` and the scripts that recollect them are in `code/`.

Decision pending with the author: the share-alike choice also applies to the article text and figures (D15 rule: never
more open than a source allows). If the texts should be CC BY 4.0, they must be separated from the Leaguepedia-derived
figures.

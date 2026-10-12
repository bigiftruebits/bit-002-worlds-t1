"""
Fetch the raw inputs that may be redistributed: the Leaguepedia mirror on Hugging Face and the football results.

Writes raw/leaguepedia_hf/*.parquet and raw/football/*.csv. The Hugging Face dataset changes over time: the
snapshot used in the article (27 Sep 2026) is in the Zenodo record, and a fresh download will differ.

    python download.py

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import os, pathlib, shutil, sys, urllib.request
HERE = pathlib.Path(__file__).parent
UA = {'User-Agent': 'BIG-IF-TRUE-research (' + os.environ.get('BIT_CONTACT', 'contact unset') + ')'}

def fetch(url, out):
    out = pathlib.Path(out); out.parent.mkdir(parents=True, exist_ok=True); part = out.with_suffix(out.suffix + '.part')
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(part, 'wb') as f: shutil.copyfileobj(r, f)
    except Exception as e:
        sys.exit(f'Could not download {url}: {e}. Check the network, or whether the file has moved.')
    part.rename(out); print('saved', out, out.stat().st_size, 'bytes')

if __name__ == '__main__':
    for f in ('results.csv', 'shootouts.csv'):
        fetch(f'https://raw.githubusercontent.com/martj42/international_results/master/{f}', HERE / 'raw' / 'football' / f)
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        sys.exit('pip install huggingface_hub, then rerun: it fetches gptilt/lol-esports-matches from Hugging Face.')
    p = snapshot_download('gptilt/lol-esports-matches', repo_type='dataset', allow_patterns=['*.parquet'])
    dst = HERE / 'raw' / 'leaguepedia_hf'; dst.mkdir(parents=True, exist_ok=True)
    for f in pathlib.Path(p).rglob('*.parquet'):
        shutil.copy(f, dst / f.name); print('saved', dst / f.name)
    print('Note: the dataset may have changed since the 27 Sep 2026 snapshot used in the article; that snapshot is in the Zenodo record.')

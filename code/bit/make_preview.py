"""
Build the issue's preview image (the link card on Substack and social sites), 1200 x 630, English or Italian.

Format §9.8: background #FBF2EC full bleed, everything inside the central safe zone x 305-895, y 80-480. Left
panel: the predictions table (figures/fig-002-odds-2026[-it].png, the figure that shows the Verdict's numbers),
uncropped. Right panel: "BIT VERDICT", the hero number and a gloss of at most eight words. The numbers are read from
the article text, never typed: variant A is T1's chance in the Verdict's Reality line ("T1 6%"); variant B adds T1's
chance with its Worlds bonus from the predictions box ("rise to 46%"). After saving, the PNG is read back and its
content box checked inside the safe zone; a 160 px copy is saved next to it for the post-list check.

    python bit/make_preview.py en|it A|B [OUT.png]      (run from code/; default ../docs/fig-002-preview[-it].png)

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import os, re, sys
from pathlib import Path
import numpy as np
import matplotlib
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
VAR = sys.argv[2] if len(sys.argv) > 2 else "A"
if LANG not in ("en", "it") or VAR not in ("A", "B"):
    sys.exit("usage: python bit/make_preview.py en|it A|B [OUT.png]")
SUF = "-it" if LANG == "it" else ""
OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "docs" / f"fig-002-preview{SUF}.png"
TXT = {"en": dict(kicker="BIT VERDICT", reality=r"\*\*The Reality:\*\*.*?T1 (\d+%)", bonus=r"T1 would rise to (\d+%)",
                  gloss={"A": "T1's chance of a fourth straight title", "B": "T1's title chance, without and with its bonus"}),
       "it": dict(kicker="BIT VERDETTO", reality=r"\*\*La realtà:\*\*.*?T1 il (\d+%)", bonus=r"T1 salirebbe al (\d+%)",
                  gloss={"A": "quarto titolo di fila per T1", "B": "titolo per T1, senza e con il bonus"})}[LANG]
W, H = 1200, 630
SAFE = (305, 80, 895, 480)
BG, PANEL, BORDER, ACCENT, INK = (251, 242, 236), "white", (201, 206, 214), "#C1440E", "#26323F"
fdir = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
font = lambda px, bold=False: ImageFont.truetype(os.path.join(fdir, "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), px)

# the numbers, exactly as the article prints them
art = (ROOT / "article" / f"{LANG}.md").read_text(encoding="utf8")
m = re.search(TXT["reality"], art)
if not m:
    sys.exit("FAIL: T1's chance not found in the Verdict's Reality line")
hero = m.group(1)
if VAR == "B":
    b = re.search(TXT["bonus"], art)
    if not b:
        sys.exit("FAIL: T1's chance with the bonus not found in the predictions box")
    hero = f"{hero} → {b.group(1)}"
HL = hero.replace(" → ", "\n→ ").split("\n")          # variant B on two lines: "6%" / "→ 46%"
gloss = TXT["gloss"][VAR]
if len(gloss.split()) > 8:
    sys.exit("FAIL: gloss over eight words")

x0, y0, x1, y1 = SAFE
img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
# left panel: the predictions table, uncropped, scaled to the panel width
LW, PAD, GAP = 330, 8, 12
f = Image.open(ROOT / "figures" / f"fig-002-odds-2026{SUF}.png").convert("RGB")
fw = LW - 2 * PAD; fh = round(f.height * fw / f.width)
# right panel: kicker, hero, gloss; both panels share one height, centred in the zone
rx0 = x0 + LW + GAP; rw = x1 - 2 - rx0; ip = 14; cw = rw - 2 * ip
size = 110
while size > 1 and max(d.textlength(h, font=font(size, True)) for h in HL) > cw: size -= 1
if size < 60:
    sys.exit(f"FAIL: the hero number would be {size} px, below 60")
gs, lines = 28, None
while gs >= 20:
    ls = [""]
    for w_ in gloss.split():
        t = (ls[-1] + " " + w_).strip()
        if d.textlength(t, font=font(gs)) <= cw: ls[-1] = t
        else: ls.append(w_)
    if len(ls) <= 4: lines = ls; break
    gs -= 1
if lines is None:
    sys.exit("FAIL: the gloss needs more than 4 lines")
ks = 24
hb = d.textbbox((0, 0), "0%→", font=font(size, True)); lh = hb[3] - hb[1]
block = ks + 14 + lh * len(HL) + 12 * (len(HL) - 1) + 16 + round(gs * 1.25) * len(lines)
PH = max(fh + 2 * PAD, block + 40)
py0 = y0 + ((y1 - y0) - PH) // 2; py1 = py0 + PH
d.rounded_rectangle([x0 + 1, py0, x0 + LW, py1], radius=14, fill=PANEL, outline=BORDER, width=2)
img.paste(f.resize((fw, fh), Image.LANCZOS), (x0 + PAD + 1, py0 + (PH - fh) // 2))
d.rounded_rectangle([rx0, py0, x1 - 2, py1], radius=14, fill=PANEL, outline=BORDER, width=2)
y = py0 + (PH - block) // 2
d.text((rx0 + ip, y), TXT["kicker"], font=font(ks, True), fill=ACCENT); y += ks + 14
for h in HL:
    d.text((rx0 + ip, y - hb[1]), h, font=font(size, True), fill=ACCENT); y += lh + 12
y += 4
for ln in lines:
    d.text((rx0 + ip, y), ln, font=font(gs), fill=INK); y += round(gs * 1.25)
if y > py1 - 10:
    sys.exit("FAIL: the verdict panel overflows")
OUT.parent.mkdir(parents=True, exist_ok=True); img.save(OUT)

# read the PNG back: content inside the safe zone; 160 px copy for the post-list check
a = np.asarray(Image.open(OUT).convert("RGB")).astype(int)
ys, xs = np.where(np.abs(a - np.array(BG)).sum(axis=2) > 0)
box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
inside = box[0] >= x0 and box[1] >= y0 and box[2] <= x1 and box[3] <= y1
print(f"{OUT.name}: variant {VAR}, hero '{hero}' {size} px ({size * 160 / W:.0f} px at 160 wide); gloss {len(lines)} lines at {gs} px;"
      f" box x {box[0]}-{box[2]}, y {box[1]}-{box[3]}; inside the safe zone: {inside}")
if not inside:
    sys.exit("FAIL: content outside the safe zone")
Image.open(OUT).resize((160, 84), Image.LANCZOS).save(OUT.with_name(OUT.stem + "-160.png"))

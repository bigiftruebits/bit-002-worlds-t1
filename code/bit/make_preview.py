"""
Build the issue's preview image (the link card on Substack and social sites), 1200 x 630, English or Italian.

Format §9.8: background #FBF2EC full bleed, everything inside the central safe zone x 305-895, y 80-480.
Left panel: a bar chart drawn for the preview, large enough to read in a link card: each top contender's chance of
winning Worlds 2026 on ratings alone, plus T1 with its Worlds bonus (dashed). The bars are read from
data/forecast2026_our_elo.csv and data/forecast2026_our_elo_T1bonus.csv, the files behind the predictions table, and
checked against the article text. Right panel: the kicker, the hero number exactly as the Verdict prints it, a gloss
of at most three lines at 28 px.
  variant C: hero = T1's chance on ratings alone ("6%")
  variant D: hero = T1's chance if its bonus holds, any format ("45% to 56%" / "dal 45% al 56%")
  variant E: hero = T1 alone to T1 with its bonus, this year's format ("from 6% to 46%" / "dal 6% al 46%"; Riccardo, 13 Oct)
After saving, the PNG is read back and its content box checked inside the safe zone; a 160 px copy is saved next
to it for the post-list check.

    python bit/make_preview.py en|it C|D|E [OUT.png]    (run from code/; default ../docs/fig-002-preview[-it].png)

BIG IF TRUE · worlds-t1 · https://github.com/bigiftruebits/bit-002-worlds-t1
Author: Riccardo Gallotti (FBK). Code by Claude Opus 5.5 under his direction.
Licence: MIT (code); data licences in DATA_MANIFEST.md.
"""
import csv, os, re, sys
from pathlib import Path
import numpy as np
import matplotlib
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
VAR = sys.argv[2] if len(sys.argv) > 2 else "E"
if LANG not in ("en", "it") or VAR not in ("C", "D", "E"):
    sys.exit("usage: python bit/make_preview.py en|it C|D|E [OUT.png]")
SUF = "-it" if LANG == "it" else ""
OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "docs" / f"fig-002-preview{SUF}.png"
TXT = {"en": dict(kicker="BIT VERDICT", title=["Chance of winning", "LoL Worlds 2026"], bonus_lab="with its October bonus",
                  alone=r"\*\*The Reality:\*\*.*?T1 (\d+%)", range_=r"\*\*The Reality:\*\*.*?\*\*(\d+% to \d+%)\*\*",
                  gen=r"\*\*The Reality:\*\*.*?Gen\.G wins Worlds (\d+%)", bonus=r"T1 would rise to (\d+%)",
                  gloss={"C": "T1's chance of a fourth straight title", "D": "T1's title chance if its October bonus holds", "E": "Increase in T1's title chance with its bonus"}),
       "it": dict(kicker="BIT VERDETTO", title=["Probabilità di vincere", "i Mondiali LoL 2026"], bonus_lab="con il bonus di ottobre",
                  alone=r"\*\*La realtà:\*\*.*?T1 il (\d+%)", range_=r"\*\*La realtà:\*\*.*?\*\*(dal \d+% al \d+%)\*\*",
                  gen=r"\*\*La realtà:\*\*.*?Gen\.G vince i Mondiali il (\d+%)", bonus=r"T1 salirebbe al (\d+%)",
                  gloss={"C": "quarto titolo di fila per T1", "D": "titolo per T1 se il bonus regge", "E": "aumento della probabilità di titolo di T1 col bonus"})}[LANG]
SHORT = {"Gen.G": "Gen.G", "Bilibili Gaming": "BLG", "Hanwha Life Esports": "HLE", "T1": "T1"}
W, H = 1200, 630
SAFE = (305, 80, 895, 480)
BG, PANEL, BORDER, ACCENT, INK = (251, 242, 236), "white", (201, 206, 214), "#C1440E", "#26323F"
GREY, PALE = "#8E9AAB", "#F6D9CB"
fdir = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
font = lambda px, bold=False: ImageFont.truetype(os.path.join(fdir, "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), px)
pct = lambda p: f"{round(100 * p)}%"

# numbers: bars from the data files, hero from the article; the two must agree
art = (ROOT / "article" / f"{LANG}.md").read_text(encoding="utf8")
def grab(rx, what):
    m = re.search(rx, art, re.S)
    if not m:
        sys.exit(f"FAIL: {what} not found in the article")
    return m.group(1)
alone, rng, gen, bonus = grab(TXT["alone"], "T1 alone"), grab(TXT["range_"], "bonus range"), grab(TXT["gen"], "Gen.G"), grab(TXT["bonus"], "T1 with bonus")
read = lambda f: {r["team"]: float(r["p_win"]) for r in csv.DictReader(open(ROOT / "data" / f, encoding="utf8"))}
base, withb = read("forecast2026_our_elo.csv"), read("forecast2026_our_elo_T1bonus.csv")
rows = [(SHORT[t], base[t], t == "T1", False) for t in SHORT]
rows.append(("T1", withb["T1"], True, True))
for got, want, what in [(pct(base["T1"]), alone, "T1 alone"), (pct(base["Gen.G"]), gen, "Gen.G"), (pct(withb["T1"]), bonus, "T1 with bonus")]:
    if got != want:
        sys.exit(f"FAIL: {what}: data {got}, article {want}")
if VAR == "C":
    HL = [alone]
elif VAR == "D":
    HL = (rng.replace(" to ", " to\n") if LANG == "en" else rng.replace(" al ", "\nal ")).split("\n")
else:                                                   # Riccardo, 13 Oct: "from 6 to 46%"
    HL = [f"from {alone}", f"to {bonus}"] if LANG == "en" else [f"dal {alone}", f"al {bonus}"]
hero = " ".join(HL)
gloss = TXT["gloss"][VAR]


x0, y0, x1, y1 = SAFE
img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
LW, GAP, ip = {"C": 340, "D": 280, "E": 266}[VAR], 12, 16
PH = y1 - y0 - 20; py0 = y0 + 10; py1 = py0 + PH

# left panel: bar chart
d.rounded_rectangle([x0 + 1, py0, x0 + LW, py1], radius=14, fill=PANEL, outline=BORDER, width=2)
lx, rx = x0 + 1 + ip, x0 + LW - ip
ts = 26
while max(d.textlength(t, font=font(ts, True)) for t in TXT["title"]) > rx - lx: ts -= 1
y = py0 + 18
for t in TXT["title"]:
    d.text((lx, y), t, font=font(ts, True), fill=INK); y += round(ts * 1.2)
y += 14
fl, fv, bh, rowgap = font(26, True), font(26, True), 32, 17
labw = max(d.textlength(r[0], font=fl) for r in rows) + 10
valw = d.textlength("46%", font=fv) + 8
bx0, bxmax = lx + labw, rx - valw
scale = (bxmax - bx0) / max(r[1] for r in rows)
for i, (lab, p, t1, dashed) in enumerate(rows):
    if dashed:
        y += 6
        d.line([lx, y - 12, rx, y - 12], fill=BORDER, width=1)
    col = ACCENT if t1 else GREY
    d.text((lx, y + bh / 2), lab, font=fl, fill=col if t1 else INK, anchor="lm")
    bx1 = bx0 + max(4, p * scale)
    if dashed:
        d.rectangle([bx0, y, bx1, y + bh], fill=PALE)
        for xx in np.arange(bx0, bx1, 14):                       # dashed outline
            d.line([xx, y, min(xx + 8, bx1), y], fill=ACCENT, width=3)
            d.line([xx, y + bh, min(xx + 8, bx1), y + bh], fill=ACCENT, width=3)
        for yy in np.arange(y, y + bh, 12):
            d.line([bx1, yy, bx1, min(yy + 7, y + bh)], fill=ACCENT, width=3)
    else:
        d.rectangle([bx0, y, bx1, y + bh], fill=col)
    d.text((bx1 + 8, y + bh / 2), pct(p), font=fv, fill=col if t1 else INK, anchor="lm")
    y += bh
    if dashed:
        cs = 19
        while d.textlength(TXT["bonus_lab"], font=font(cs)) > rx - lx: cs -= 1
        if cs < 15:
            sys.exit("FAIL: the bonus caption does not fit")
        d.text((rx, y + 6), TXT["bonus_lab"], font=font(cs), fill=ACCENT, anchor="ra"); y += 30
    y += rowgap
if y > py1 - 4:
    sys.exit(f"FAIL: the chart overflows its panel ({y} > {py1})")

# right panel: kicker, hero, gloss
rx0 = x0 + LW + GAP; cw = x1 - 2 - rx0 - ip - 8
size = 110
while size > 1 and max(d.textlength(h, font=font(size, True)) for h in HL) > cw: size -= 1
if size < 60:
    sys.exit(f"FAIL: the hero number would be {size} px, below 60")
gs, ls = 28, [""]                                        # gloss: at most three lines at 28 px (Riccardo, 13 Oct;
for w_ in gloss.split():                                 # replaces the eight-word cap)
    t = (ls[-1] + " " + w_).strip()
    if d.textlength(t, font=font(gs)) <= cw: ls[-1] = t
    else: ls.append(w_)
if len(ls) > 3:
    sys.exit(f"FAIL: the gloss needs {len(ls)} lines at {gs} px; at most 3")
lines = ls
ks = 24
hb = d.textbbox((0, 0), "0%", font=font(size, True)); lh = hb[3] - hb[1]
block = ks + 16 + lh * len(HL) + 14 * (len(HL) - 1) + 20 + round(gs * 1.25) * len(lines)
d.rounded_rectangle([rx0, py0, x1 - 2, py1], radius=14, fill=PANEL, outline=BORDER, width=2)
y = py0 + (PH - block) // 2
d.text((rx0 + ip, y), TXT["kicker"], font=font(ks, True), fill=ACCENT); y += ks + 16
for h in HL:
    d.text((rx0 + ip, y - hb[1]), h, font=font(size, True), fill=ACCENT); y += lh + 14
y += 6
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
print(f"{OUT.name}: variant {VAR}, hero '{hero}' {size} px ({size * 160 / W:.0f} px at 160 wide); bars "
      + ", ".join(f"{r[0]}{' bonus' if r[3] else ''} {pct(r[1])}" for r in rows)
      + f"; gloss {len(lines)} lines at {gs} px; box x {box[0]}-{box[2]}, y {box[1]}-{box[3]}; inside the safe zone: {inside}")
if not inside:
    sys.exit("FAIL: content outside the safe zone")
Image.open(OUT).resize((160, 84), Image.LANCZOS).save(OUT.with_name(OUT.stem + "-160.png"))

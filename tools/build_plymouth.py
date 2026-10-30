#!/usr/bin/env python3
"""Nightfeed Plymouth assets. Every word is pre-rendered (no fonts in initramfs)."""
import shutil, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
import palette as P

A = R / "assets"
OUT = R / "plymouth/nightfeed"
OUT.mkdir(parents=True, exist_ok=True)
for f in OUT.glob("*.png"):
    f.unlink()
FB = str(R / "sddm/nightfeed/fonts/TerminessNerdFontMono-Bold.ttf")
FR = str(R / "sddm/nightfeed/fonts/TerminessNerdFontMono-Regular.ttf")

def osd(text, size, ink=P.TEXT_HI, glow=P.VIOLET, bold=True, spacing=2, glow_a=150):
    f = ImageFont.truetype(FB if bold else FR, size)
    # letter-spaced layout
    widths = [f.getlength(ch) for ch in text]
    w = int(sum(widths) + spacing * len(text)) + 24
    asc, desc = f.getmetrics()
    h = asc + desc + 24
    def draw(fill):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im); x = 12
        for ch, cw in zip(text, widths):
            d.text((x, 12), ch, font=f, fill=fill); x += cw + spacing
        return im
    g = draw(P.rgb(glow) + (glow_a,)).filter(ImageFilter.GaussianBlur(size / 9))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(draw(P.rgb(glow) + (110,)), (-2, 0))     # chroma split
    out.alpha_composite(draw(P.rgb(ink) + (255,)), (1, 0))
    return out

def save(im, name):
    im.save(OUT / name, optimize=True)

# background with scanlines + vignette baked in
bg = Image.open(A / "background.png").convert("RGBA")
bg = Image.eval(bg, lambda v: v)  # copy
dimmer = Image.new("RGBA", bg.size, (0, 0, 0, 70))
bg.alpha_composite(dimmer)
bg.alpha_composite(Image.open(A / "scanlines-1080.png"))
bg.alpha_composite(Image.open(A / "vignette.png"))
bg.convert("RGB").save(OUT / "bg.png", optimize=True)

for i in range(4):
    shutil.copy(A / f"noise_{i}.png", OUT / f"noise_{i}.png")
shutil.copy(A / "tracking.png", OUT / "tracking.png")
shutil.copy(A / "glow.png", OUT / "glow.png")

save(osd("PLAY ▶", 46), "osd_play.png")
save(osd("STOP ■", 46, ink="#ffd0dc", glow=P.NEGATIVE), "osd_stop.png")
save(osd("REW ◀◀", 46), "osd_rew.png")
save(osd("CH 03   SP", 22, ink=P.TEXT, bold=False), "osd_ch.png")
save(osd("CNT", 22), "osd_cnt.png")
for ch, name in list(zip("0123456789", [f"d{i}" for i in range(10)])) + [(":", "dcolon")]:
    save(osd(ch, 22, spacing=0), f"{name}.png")

save(osd("NIGHTFEED", 64, glow_a=190, spacing=6), "logo.png")
save(osd("LOADING TAPE", 18, ink=P.TEXT_DIM, glow=P.VIOLET_DEEP, bold=False, spacing=5, glow_a=90), "cap_boot.png")
save(osd("EJECTING TAPE", 18, ink=P.TEXT_DIM, glow=P.VIOLET_DEEP, bold=False, spacing=5, glow_a=90), "cap_halt.png")
save(osd("PASSWORD", 18, ink=P.VIOLET_HI, glow=P.VIOLET_DEEP, bold=False, spacing=5, glow_a=90), "cap_pw.png")

# tape-block progress bar: 32 blocks
N, BW, BH, GAP = 32, 11, 20, 5
W = N * BW + (N - 1) * GAP + 16
def blocks(lit):
    im = Image.new("RGBA", (W, BH + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(N):
        x = 8 + i * (BW + GAP)
        c = P.rgb(P.VIOLET if lit else P.EDGE) + (255 if lit else 200,)
        d.rectangle([x, 8, x + BW - 1, 8 + BH - 1], fill=c)
    if lit:
        g = im.filter(ImageFilter.GaussianBlur(4))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(im)
        d2 = ImageDraw.Draw(out)
        for i in range(N):   # hot top edge on every block
            x = 8 + i * (BW + GAP)
            d2.line([x, 8, x + BW - 1, 8], fill=P.rgb(P.VIOLET_GLOW) + (255,))
        return out
    return im
save(blocks(False), "bar_dim.png")
save(blocks(True), "bar_lit.png")

# password plate + block bullet
pw = Image.new("RGBA", (520, 58), (0, 0, 0, 0))
d = ImageDraw.Draw(pw)
d.rounded_rectangle([4, 4, 515, 53], 4, fill=P.rgb(P.ABYSS) + (235,), outline=P.rgb(P.VIOLET) + (255,))
g = pw.filter(ImageFilter.GaussianBlur(3)); plate = Image.new("RGBA", pw.size, (0, 0, 0, 0)); plate.alpha_composite(g); plate.alpha_composite(pw)
save(plate, "pw_plate.png")
b = Image.new("RGBA", (13, 22), (0, 0, 0, 0)); ImageDraw.Draw(b).rectangle([2, 2, 10, 19], fill=P.rgb(P.VIOLET_HI) + (255,))
save(b, "bullet.png")
print("plymouth assets ->", OUT)

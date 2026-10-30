#!/usr/bin/env python3
"""Shared raster textures: padded 16:9 backgrounds, scanline tile, VHS noise frames."""
import random, sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import palette as P

A = Path(__file__).resolve().parent.parent / "assets"
A.mkdir(exist_ok=True)
random.seed(2133)

# 1. wallpaper padded to 1920x1080 (face stays left, black extends east)
src = Image.open(P.WALLPAPER).convert("RGB")
s = src.resize((round(src.width * 1080 / src.height), 1080), Image.LANCZOS)
bg = Image.new("RGB", (1920, 1080), (1, 1, 1))
bg.paste(s, (0, 0))
bg.save(A / "background.png", optimize=True)
bg.save(A / "background.jpg", quality=92)

# dimmed + slightly blurred version for splash/plymouth/lock behind UI
dim = bg.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: int(v * 0.55))
dim.save(A / "background-dim.jpg", quality=90)

# 2. scanline tile: 1px dark line every 3px (overlay; alpha only)
scan = Image.new("RGBA", (4, 3), (0, 0, 0, 0))
for x in range(4):
    scan.putpixel((x, 2), (0, 0, 0, 70))
scan.save(A / "scanline.png")
# full-screen scanlines (for QML/plymouth where tiling an image is easiest as one sprite)
full = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
d = ImageDraw.Draw(full)
for y in range(0, 1080, 3):
    d.line([(0, y + 2), (1919, y + 2)], fill=(0, 0, 0, 60))
full.save(A / "scanlines-1080.png", optimize=True)

# 3. noise frames: sparse cool-tinted grain + a few horizontal dropout streaks
def noise(w, h, density, alpha, streaks):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for _ in range(int(w * h * density)):
        x, y = random.randrange(w), random.randrange(h)
        v = random.randint(120, 230)
        px[x, y] = (int(v * .78), int(v * .82), v, random.randint(alpha // 3, alpha))
    d = ImageDraw.Draw(im)
    for _ in range(streaks):
        y = random.randrange(h); x = random.randrange(w); L = random.randint(w // 12, w // 3)
        d.line([(x, y), (min(w - 1, x + L), y)], fill=(170, 180, 255, random.randint(alpha // 3, alpha)))
    return im

for i in range(6):
    noise(512, 288, 0.035, 46, 5).resize((1920, 1080), Image.NEAREST).save(A / f"noise_{i}.png", optimize=True)
    noise(128, 128, 0.05, 40, 1).save(A / f"noise_tile_{i}.png")

# 4. tracking band: soft bright horizontal band that rolls down the screen
band = Image.new("RGBA", (1920, 90), (0, 0, 0, 0))
d = ImageDraw.Draw(band)
for y in range(90):
    t = 1 - abs(y - 45) / 45
    d.line([(0, y), (1919, y)], fill=(150, 160, 255, int(28 * t ** 2)))
for _ in range(220):  # torn grain inside the band
    y = random.randint(30, 60); x = random.randrange(1920)
    d.line([(x, y), (x + random.randint(6, 80), y)], fill=(200, 205, 255, random.randint(20, 70)))
band.save(A / "tracking.png", optimize=True)

# 5. vignette
vig = Image.new("L", (480, 270), 0)
vp = vig.load()
for y in range(270):
    for x in range(480):
        dx, dy = (x - 240) / 240, (y - 135) / 135
        vp[x, y] = int(max(0, min(1, (dx * dx + dy * dy - 0.35) / 1.2)) * 210)
v = Image.new("RGBA", (480, 270), P.rgb(P.VOID) + (0,))
v.putalpha(vig)
v.resize((1920, 1080), Image.BICUBIC).save(A / "vignette.png", optimize=True)

# 6. soft violet glow sprite
g = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
gp = g.load(); r, gg, b = P.rgb(P.VIOLET)
for y in range(256):
    for x in range(256):
        dd = ((x - 128) ** 2 + (y - 128) ** 2) ** .5 / 128
        if dd < 1:
            gp[x, y] = (r, gg, b, int(255 * (1 - dd) ** 2.2))
g.save(A / "glow.png")
print("textures ->", A)

#!/usr/bin/env python3
"""Composite the Plymouth assets at the script's 1080p positions (static preview)."""
import sys
from pathlib import Path
from PIL import Image
D = Path(__file__).resolve().parent.parent / "plymouth/nightfeed"
OUT = Path(sys.argv[1])
def L(n): return Image.open(D / n).convert("RGBA")
for mode, name in (("boot", "plymouth.png"), ("pw", "plymouth-password.png"), ("halt", "plymouth-shutdown.png")):
    W, H = 1920, 1080; PX = int(W * 0.705); M = 44
    im = L("bg.png")
    n = L("noise_1.png"); n.putalpha(n.getchannel("A").point(lambda v: int(v * .55))); im.alpha_composite(n)
    im.alpha_composite(L("tracking.png"), (0, 300))
    m = L("osd_stop.png" if mode == "halt" else "osd_play.png"); im.alpha_composite(m, (M, M))
    im.alpha_composite(L("osd_ch.png"), (M, M + m.height - 10))
    cnt = L("osd_cnt.png"); cy = H - M - cnt.height; im.alpha_composite(cnt, (M, cy))
    x = M + cnt.width - 6
    for c in "0:00:07":
        g = L("dcolon.png" if c == ":" else f"d{c}.png"); im.alpha_composite(g, (x, cy)); x += g.width - 22
    ly = int(H * 0.44)
    gl = L("glow.png").resize((760, 380)); gl.putalpha(gl.getchannel("A").point(lambda v: int(v * 0.2))); im.alpha_composite(gl, (PX - 380, ly + 40 - 190))
    lo = L("logo.png"); im.alpha_composite(lo, (PX - lo.width // 2, ly - lo.height // 2))
    by = ly + 112
    if mode != "pw":
        cap = L("cap_halt.png" if mode == "halt" else "cap_boot.png"); im.alpha_composite(cap, (PX - cap.width // 2, ly + 62 - cap.height // 2))
        d = L("bar_dim.png"); im.alpha_composite(d, (PX - d.width // 2, by - d.height // 2))
        lit = L("bar_lit.png"); lit = lit.crop((0, 0, int(lit.width * (0.55 if mode == "boot" else 0.8)), lit.height)); im.alpha_composite(lit, (PX - d.width // 2, by - d.height // 2))
    else:
        pl = L("pw_plate.png"); im.alpha_composite(pl, (PX - pl.width // 2, by - pl.height // 2))
        pc = L("cap_pw.png"); im.alpha_composite(pc, (PX - pc.width // 2, by - pl.height // 2 - 20 - pc.height // 2))
        b = L("bullet.png")
        for i in range(9): im.alpha_composite(b, (PX - pl.width // 2 + 22 + i * 16, by - b.height // 2))
    im.convert("RGB").save(OUT / name)

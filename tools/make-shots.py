#!/usr/bin/env python3
"""Store/README screenshots, rendered with QtSvg (the renderer KDE uses).

    QT_QPA_PLATFORM=offscreen python3 tools/make-shots.py <out-dir>

Expects <out-dir> to already hold the QML renders:
  sddm.png sddm-error.png splash.png splash-rew.png gallery.png
and writes desktop.png panel.png decoration.png buttons.png icons.png
terminal.png plymouth.png plymouth-password.png plymouth-shutdown.png colors.png
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QImage, QPainter, QColor, QFont, QFontDatabase, QPen
from PyQt6.QtCore import QRectF, Qt

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
import palette as P

OUT = Path(sys.argv[1])
app = QApplication(sys.argv)
fid = QFontDatabase.addApplicationFont(str(R / "sddm/nightfeed/fonts/TerminessNerdFontMono-Regular.ttf"))
QFontDatabase.addApplicationFont(str(R / "sddm/nightfeed/fonts/TerminessNerdFontMono-Bold.ttf"))
MONO = QFontDatabase.applicationFontFamilies(fid)[0]
NAMES = ["topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright"]
PT = R / "plasma/desktoptheme/Nightfeed"
AU = R / "aurorae/Nightfeed"
ICONS = R / "icons/Nightfeed"
TELA = Path.home() / ".local/share/icons/Tela-circle-dark"


def frame(p, svg, x, y, w, h, cs, shadow=0, tile=96, prefix=""):
    r = QSvgRenderer(str(svg))
    if shadow:
        S = shadow
        for n, (a, b, c, d) in {"topleft": (x - S, y - S, S, S), "top": (x, y - S, w, S), "topright": (x + w, y - S, S, S),
                                "left": (x - S, y, S, h), "right": (x + w, y, S, h), "bottomleft": (x - S, y + h, S, S),
                                "bottom": (x, y + h, w, S), "bottomright": (x + w, y + h, S, S)}.items():
            r.render(p, "shadow-" + n, QRectF(a, b, c, d))
    boxes = {"topleft": (x, y, cs, cs), "top": (x + cs, y, w - 2 * cs, cs), "topright": (x + w - cs, y, cs, cs),
             "left": (x, y + cs, cs, h - 2 * cs), "right": (x + w - cs, y + cs, cs, h - 2 * cs),
             "bottomleft": (x, y + h - cs, cs, cs), "bottom": (x + cs, y + h - cs, w - 2 * cs, cs),
             "bottomright": (x + w - cs, y + h - cs, cs, cs)}
    for n, b in boxes.items():
        r.render(p, prefix + n, QRectF(*b))
    for tx in range(int(x + cs), int(x + w - cs), tile):
        for ty in range(int(y + cs), int(y + h - cs), tile):
            r.render(p, prefix + "center", QRectF(tx, ty, min(tile, x + w - cs - tx), min(tile, y + h - cs - ty)))


def icon(p, name, x, y, size, theme_dirs=None):
    for d in (ICONS / "scalable/places", ICONS / "scalable/apps", TELA / "scalable/apps", TELA / "scalable/places"):
        f = d / f"{name}.svg"
        if f.exists():
            QSvgRenderer(str(f.resolve())).render(p, QRectF(x, y, size, size))
            return True
    return False


def text(p, s, x, y, size, color, bold=False, align=None, w=0, h=0, spacing=1.5):
    f = QFont(MONO, -1); f.setPixelSize(size); f.setBold(bold); f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, spacing)
    p.setFont(f); p.setPen(QColor(color))
    if align is not None:
        p.drawText(QRectF(x, y, w, h), align, s)
    else:
        p.drawText(int(x), int(y), s)


# Aurorae window -----------------------------------------------------------------
AP, AB, AT = 20, 3, 36


def window(p, x, y, w, h, title, active=True, content=None):
    """x,y,w,h = window outer frame (without shadow)."""
    d = QSvgRenderer(str(AU / "decoration.svg"))
    pre = "decoration-" if active else "decoration-inactive-"
    X, Y = x - AP, y - AP
    parts = {"topleft": (X, Y, AP + AB, AP + AT), "top": (x + AB, Y, w - 2 * AB, AP + AT), "topright": (x + w - AB, Y, AB + AP, AP + AT),
             "left": (X, y + AT, AP + AB, h - AT - AB), "right": (x + w - AB, y + AT, AB + AP, h - AT - AB),
             "bottomleft": (X, y + h - AB, AP + AB, AB + AP), "bottom": (x + AB, y + h - AB, w - 2 * AB, AB + AP),
             "bottomright": (x + w - AB, y + h - AB, AB + AP, AB + AP)}
    for n, b in parts.items():
        d.render(p, pre + n, QRectF(*b))
    p.fillRect(QRectF(x + AB, y + AT, w - 2 * AB, h - AT - AB), QColor(P.BASE))
    if content is not None:
        p.drawImage(QRectF(x + AB, y + AT, w - 2 * AB, h - AT - AB), content)
    st = "active-center" if active else "inactive-center"
    bx = x + w - AB - 9 - 24
    for b in ("close", "maximize", "minimize"):
        QSvgRenderer(str(AU / f"{b}.svg")).render(p, st, QRectF(bx, y + 6, 24, 24)); bx -= 26
    QSvgRenderer(str(AU / "menu.svg")).render(p, st, QRectF(x + AB + 9, y + 6, 24, 24))
    text(p, title, x, y, 15, P.TEXT if active else P.TEXT_MUTE, align=Qt.AlignmentFlag.AlignCenter, w=w, h=AT - 2)


def terminal_image(w, h):
    img = QImage(w, h, QImage.Format.Format_ARGB32); img.fill(QColor(P.BASE))
    p = QPainter(img); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    cols = ["#14172c", "#d9406a", "#4fc9a6", "#d0a85c", "#5b6ff0", "#9a6cff", "#56b6e8", "#aeb4dc",
            "#3a4170", "#ff6b93", "#7ee8c8", "#f0c97c", "#8796ff", "#c3a6ff", "#8fd8ff", "#e6e8ff"]
    lines = [
        [(P.VIOLET_HI, "scorn"), (P.TEXT_DIM, "@"), (cols[12], "nightfeed"), (P.TEXT, " ~/tapes "), (P.VIOLET, "▶ "), (P.TEXT, "ls -la")],
        [(cols[4], "drwxr-xr-x "), (P.TEXT, "scorn  "), (cols[13], "basement.vhs/")],
        [(cols[2], "-rw-r--r-- "), (P.TEXT, "scorn  "), (P.TEXT, "night_feed_01.mp4")],
        [(cols[2], "-rw-r--r-- "), (P.TEXT, "scorn  "), (cols[3], "channel_03.log")],
        [(cols[1], "-rw------- "), (P.TEXT, "scorn  "), (cols[9], "eyes_only.key")],
        [],
        [(P.VIOLET_HI, "scorn"), (P.TEXT_DIM, "@"), (cols[12], "nightfeed"), (P.TEXT, " ~/tapes "), (P.VIOLET, "▶ "), (P.TEXT, "git status")],
        [(P.TEXT, "On branch "), (cols[6], "main")],
        [(cols[1], "\tmodified:   "), (P.TEXT, "tracking.conf")],
        [(cols[2], "\tnew file:   "), (P.TEXT, "static.png")],
        [],
    ]
    f = QFont(MONO, -1); f.setPixelSize(17); p.setFont(f)
    y = 30
    for ln in lines:
        x = 16
        for c, s in ln:
            p.setPen(QColor(c)); s = s.replace("\t", "    "); p.drawText(x, y, s); x += p.fontMetrics().horizontalAdvance(s)
        y += 24
    for i, c in enumerate(cols):
        p.fillRect(QRectF(16 + (i % 8) * 46, y + (i // 8) * 30 - 14, 40, 24), QColor(c))
    p.end()
    return img


def panel(p, W, H):
    ph, m = 34, 8
    px, py, pw = m, H - ph - m, W - 2 * m
    frame(p, PT / "widgets/panel-background.svg", px, py, pw, ph, 6, shadow=12)
    icon(p, "start-here-kde", px + 8, py + 4, 26)
    x = px + 52
    for n in ("system-file-manager", "org.kde.konsole", "firefox", "obsidian", "spotify", "org.kde.dolphin"):
        if icon(p, n, x, py + 5, 24):
            if n == "org.kde.konsole":   # active task underline
                p.fillRect(QRectF(x - 6, py + ph - 4, 36, 2), QColor(P.VIOLET))
                p.fillRect(QRectF(x - 6, py + ph - 9, 36, 5), QColor(123, 92, 255, 40))
            x += 40
    text(p, "11:24 AM", px + pw - 170, py, 15, P.TEXT, align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, w=150, h=ph)
    for i, n in enumerate(("network-wireless", "audio-volume-high", "battery-080")):
        pass


def new(w, h, fill=P.VOID):
    img = QImage(w, h, QImage.Format.Format_ARGB32); img.fill(QColor(fill))
    p = QPainter(img); p.setRenderHint(QPainter.RenderHint.Antialiasing); p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    return img, p


bgimg = QImage(str(R / "assets/background.png"))
gallery = QImage(str(OUT / "gallery.png"))

# 1. full desktop ---------------------------------------------------------------
img, p = new(1920, 1080)
p.drawImage(0, 0, bgimg)
term = terminal_image(700, 330)
window(p, 1130, 560, 700, 366, "konsole — ~/tapes", active=False, content=term)
window(p, 880, 110, 900 + 2 * AB, 520 + AT + AB, "Nightfeed — widget gallery", active=True, content=gallery)
# a plasma popup (dialog) above the panel
frame(p, PT / "dialogs/background.svg", 14, 1080 - 34 - 8 - 12 - 300, 360, 300, 8, shadow=18)
text(p, "NIGHTFEED", 40, 1080 - 54 - 300 + 22, 22, P.TEXT_HI, bold=True, align=Qt.AlignmentFlag.AlignLeft, w=300, h=30, spacing=4)
for i, (ic, label) in enumerate((("folder", "Home"), ("folder-download", "Downloads"), ("folder-music", "Music"),
                                 ("folder-pictures", "Pictures"), ("folder-videos", "Videos"))):
    yy = 1080 - 54 - 300 + 70 + i * 44
    if i == 1:
        p.fillRect(QRectF(26, yy - 4, 336, 40), QColor(51, 37, 154, 150))
    icon(p, ic, 40, yy, 32)
    text(p, label, 86, yy, 16, P.TEXT, align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, w=250, h=32)
panel(p, 1920, 1080)
p.end(); img.save(str(OUT / "desktop.png"))

# 2. panel + popup crop ----------------------------------------------------------
img.copy(0, 640, 900, 440).save(str(OUT / "panel.png"))

# 3. decoration ------------------------------------------------------------------
img, p = new(1200, 560)
p.drawImage(QRectF(0, 0, 1200, 560), bgimg, QRectF(500, 150, 1200, 560))
window(p, 90, 70, 620, 330, "nightfeed — active", True, terminal_image(614, 291))
window(p, 640, 230, 480, 260, "inactive window", False)
p.end(); img.save(str(OUT / "decoration.png"))

# 4. buttons strip (scaled 3x) ----------------------------------------------------
img, p = new(3 * 26 * 9 + 40, 3 * 24 * 2 + 50, P.SURFACE)
for row, states in enumerate((("active-center", "hover-center"),)):
    pass
x = 20
for b in ("menu", "minimize", "maximize", "restore", "close", "keepabove", "keepbelow", "shade", "alldesktops"):
    r = QSvgRenderer(str(AU / f"{b}.svg"))
    r.render(p, "active-center", QRectF(x, 15, 72, 72))
    r.render(p, "hover-center", QRectF(x, 15 + 80, 72, 72))
    x += 78
p.end(); img.save(str(OUT / "buttons.png"))

# 5. icons -----------------------------------------------------------------------
names = ["folder", "user-home", "folder-documents", "folder-download", "folder-music", "folder-pictures",
         "folder-videos", "folder-desktop", "folder-templates", "folder-publicshare", "folder-development", "folder-git",
         "folder-games", "folder-cloud", "network-server", "user-trash", "start-here-kde", "folder-image-people"]
img, p = new(6 * 140 + 40, 3 * 150 + 40, P.BASE)
i = 0
for n in names:
    if not (ICONS / f"scalable/places/{n}.svg").exists():
        continue
    cx, cy = 20 + (i % 6) * 140, 20 + (i // 6) * 150
    icon(p, n, cx + 22, cy + 10, 96)
    text(p, n, cx, cy + 112, 13, P.TEXT_DIM, align=Qt.AlignmentFlag.AlignHCenter, w=140, h=24, spacing=0.5)
    i += 1
    if i == 18:
        break
p.end(); img.save(str(OUT / "icons.png"))

# 6. terminal --------------------------------------------------------------------
img, p = new(820, 440)
p.drawImage(QRectF(0, 0, 820, 440), bgimg, QRectF(900, 300, 820, 440))
window(p, 30, 30, 760, 380, "konsole — Nightfeed", True, terminal_image(754, 341))
p.end(); img.save(str(OUT / "terminal.png"))

# 7. colour swatches ---------------------------------------------------------------
sw = [("VOID", P.VOID), ("ABYSS", P.ABYSS), ("BASE", P.BASE), ("SURFACE", P.SURFACE), ("RAISED", P.RAISED), ("EDGE", P.EDGE),
      ("COBALT", P.COBALT), ("PERI", P.PERI), ("VIOLET DEEP", P.VIOLET_DEEP), ("SELECT", P.SELECT), ("VIOLET", P.VIOLET),
      ("VIOLET HI", P.VIOLET_HI), ("TEXT", P.TEXT), ("REC", P.NEGATIVE), ("NEUTRAL", P.NEUTRAL), ("POSITIVE", P.POSITIVE)]
img, p = new(8 * 130 + 40, 2 * 150 + 40, P.VOID)
for i, (n, c) in enumerate(sw):
    x, y = 20 + (i % 8) * 130, 20 + (i // 8) * 150
    p.fillRect(QRectF(x, y, 118, 96), QColor(c)); p.setPen(QPen(QColor(P.EDGE), 1)); p.drawRect(QRectF(x, y, 118, 96))
    text(p, n, x, y + 100, 13, P.TEXT, align=Qt.AlignmentFlag.AlignLeft, w=118, h=20, spacing=1)
    text(p, c, x, y + 118, 13, P.TEXT_DIM, align=Qt.AlignmentFlag.AlignLeft, w=118, h=20, spacing=1)
p.end(); img.save(str(OUT / "colors.png"))
print("shots ->", OUT)

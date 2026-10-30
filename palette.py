"""Nightfeed palette: one source of truth for every generator.

Sampled from the wallpaper (near-black + night-vision cobalt face) and pushed
toward blue-violet for glow/accents. Surfaces are cobalt-black, never #000.
"""
WALLPAPER = "/home/scorn/Pictures/1b6c35a7-578c-4fb3-a811-1bed374eeaf5.png"

# surfaces, darkest -> lightest (all carry a blue cast so they read as "tinted")
VOID    = "#03040a"   # deepest: shadows, plymouth/sddm base
ABYSS   = "#06070f"   # view / text-field background
BASE    = "#0a0c18"   # window background
SURFACE = "#0f1223"   # header / alt rows / panel
RAISED  = "#151a33"   # buttons
EDGE    = "#1e2552"   # borders (wallpaper #181F62 family)
EDGE_HI = "#2b347a"

# wallpaper cobalt
COBALT_LO = "#181f62"
COBALT    = "#25309b"
COBALT_HI = "#3343bb"
PERI      = "#6981e3"   # brightest wallpaper tone (eye whites)

# violet glow: the accent
VIOLET_DEEP = "#2a1d6e"
VIOLET_LO   = "#4a35b8"
VIOLET      = "#7b5cff"
VIOLET_HI   = "#a38cff"
VIOLET_GLOW = "#c4b5ff"

# text
TEXT      = "#c3c8ee"
TEXT_HI   = "#e6e8ff"
TEXT_DIM  = "#7a80b0"
TEXT_MUTE = "#4a5080"

# states (kept cool so nothing breaks the mood)
NEGATIVE = "#e0466e"   # VHS "REC" magenta-red
NEUTRAL  = "#d0a85c"
POSITIVE = "#4fd1b5"
LINK     = "#8fa2ff"
VISITED  = "#b48cff"

# selection: dim, not neon
SELECT    = "#33259a"
SELECT_HI = "#4330c0"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def csv(h):
    return ",".join(map(str, rgb(h)))

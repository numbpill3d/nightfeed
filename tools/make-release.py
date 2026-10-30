#!/usr/bin/env python3
"""Assemble the publishable Nightfeed pieces.

For each piece this writes
  repos/<repo>/            a self-contained git working tree: theme files at the root,
                           README.md (screenshot, description, tags), LICENSE, install.sh,
                           screenshots/
  <docs>/<repo>/           the KDE Store upload: <tar_top>.tar.gz, screenshots/,
                           STORE-LISTING.txt (name, category, description, tags)

    python3 tools/make-release.py [docs-dir]

Run tools/make-shots.py first (screenshots/ must be filled).
"""
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
DOCS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents" / "Nightfeed Release"
REPOS = ROOT / "repos"
GPL = Path("/usr/share/licenses/spdx/GPL-3.0-or-later.txt")
GH = "https://github.com/numbpill3d"
VERSION = "1.0"

BLURB = ("Nightfeed is a night-vision VHS look for KDE Plasma 6, built around a cobalt-lit face on near-black: "
         "cobalt-black surfaces, faint scanlines and tape grain, and a slight violet glow on whatever has focus.")
BASE_TAGS = ["nightfeed", "kde", "plasma6", "dark", "vhs", "scanlines", "cobalt", "violet", "purple", "retro", "analog-horror", "glow"]

PIECES = {}


def piece(repo, **kw):
    PIECES[repo] = kw


def suite_table(skip):
    rows = [f"| {p['short']} | [{r}]({GH}/{r}) |" for r, p in PIECES.items() if r != skip]
    return "## The rest of the suite\n\n| piece | repo |\n|---|---|\n" + "\n".join(rows) + \
           f"\n\nEverything at once, with the generators: [nightfeed]({GH}/nightfeed).\n"


CREDITS = """## Credits and licence

By splicer scorn (voidrane). GPL-3.0-or-later.{extra}
"""
TERMINESS = "\nOSD font: Terminess Nerd Font (Terminus, SIL OFL 1.1), bundled with its licence."

# ---- pieces -------------------------------------------------------------------
piece("nightfeed-sddm",
      short="SDDM login", title="Nightfeed — SDDM Login", category="SDDM Login Themes",
      src=ROOT / "sddm/nightfeed", tar_top="nightfeed",
      shots={"login.jpg": "sddm.png", "login-error.jpg": "sddm-error.png"},
      tags=["sddm", "sddm-theme", "login-screen", "qt6", "qml", "vcr", "osd"],
      summary="A night-vision VHS login for SDDM (Qt6): VCR on-screen display, rolling tracking band, tape grain and tears, violet-glow glass panel.",
      features="""- The wallpaper face as a tape on playback: scanlines, flickering grain, a soft tracking band rolling down the screen and a slow drift, like a tape that never quite settles.
- Every 7–16 s a tape tear: a slice of the picture jumps sideways and the frame jitters (set `glitches=false` in `theme.conf` to stop it).
- VCR on-screen display: blinking `PLAY ▶` top left, `AM 11:24` and the date top right, a running tape counter and the host name bottom left.
- Cobalt glass login panel with a violet glow seam. The password shows as a strip of tape blocks.
- A wrong password flips the OSD to `STOP ■` with a red `TRACKING ERROR // ACCESS DENIED` and a shake. Logging in fast-forwards (`FF ▶▶`) and the screen collapses to a line like a CRT switching off.
- Power controls are transport buttons: `❚❚ PAUSE` (suspend), `◀◀ REWIND` (reboot), `■ STOP` (shut down).
- Pure QtQuick, no shaders: every effect is an image swap or a transform, so it is light on integrated GPUs.""",
      requires="SDDM with the Qt6 greeter (`sddm-greeter-qt6`). The OSD font is bundled.",
      install_store="Extract to `/usr/share/sddm/themes/` and pick **Nightfeed** in System Settings → Colors & Themes → Login Screen (SDDM).",
      install_sh="""DST=/usr/share/sddm/themes/nightfeed
[[ $EUID -eq 0 ]] || { echo "run with sudo: sudo ./install.sh" >&2; exit 1; }
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{Main.qml,metadata.desktop,theme.conf,assets,fonts,preview.jpg} "$DST"/
chmod -R a+rX "$DST"
found=0
for f in /etc/sddm.conf /etc/sddm.conf.d/*.conf; do
    if [[ -f $f ]] && grep -q '^Current=' "$f"; then sed -i 's/^Current=.*/Current=nightfeed/' "$f"; found=1; fi
done
(( found )) || { mkdir -p /etc/sddm.conf.d; printf '[Theme]\\nCurrent=nightfeed\\n' > /etc/sddm.conf.d/nightfeed.conf; }
echo "Installed. Test without logging out: sddm-greeter-qt6 --test-mode --theme $DST" """,
      config="""`theme.conf`:

| key | default | |
|---|---|---|
| `background` | `assets/background.png` | any image; the face is kept to the left |
| `tagline` | `SIGNAL ACQUIRED // IDENTIFY` | line under the panel title |
| `channel` | `CH 03` | OSD channel label |
| `glitches` | `true` | `false` stops the tape tears |""",
      credit_extra=TERMINESS)

piece("nightfeed-plymouth",
      short="Plymouth boot splash", title="Nightfeed — Plymouth Boot Splash", category="Plymouth Themes",
      src=ROOT / "plymouth/nightfeed", tar_top="nightfeed",
      shots={"boot.jpg": "plymouth.png", "password.jpg": "plymouth-password.png", "shutdown.jpg": "plymouth-shutdown.png"},
      tags=["plymouth", "plymouth-theme", "boot-splash", "bootscreen", "luks"],
      summary="Night-vision VHS boot splash: the cobalt face under scanlines and grain, a rolling tracking band, VCR OSD, tape-block progress.",
      features="""- Live grain, a tracking band rolling top to bottom, and an occasional tape wobble of the picture.
- VCR OSD: `PLAY ▶` blinks while the deck engages, plus `CH 03 SP` and a tape counter that ticks every second.
- Boot progress as a strip of 32 violet tape blocks under a glowing **NIGHTFEED**.
- Shutdown shows `STOP ■` / **EJECTING TAPE**, reboot shows `REW ◀◀`.
- Disk-unlock prompt (LUKS): a glowing field with block bullets.
- Every word is pre-rendered, so no fonts are needed in the initramfs. Laid out for 16:9 and scaled by screen height.""",
      requires="Plymouth with the `script` plugin (standard).",
      install_store="Extract to `/usr/share/plymouth/themes/`, then `sudo plymouth-set-default-theme -R nightfeed` (on dracut systems: `sudo plymouth-set-default-theme nightfeed && sudo dracut -f`).",
      install_sh="""DST=/usr/share/plymouth/themes/nightfeed
[[ $EUID -eq 0 ]] || { echo "run with sudo: sudo ./install.sh" >&2; exit 1; }
rm -rf "$DST"; mkdir -p "$DST"
cp "$HERE"/*.png "$HERE"/nightfeed.plymouth "$HERE"/nightfeed.script "$DST"/
chmod -R a+rX "$DST"
if command -v dracut >/dev/null && ! command -v mkinitcpio >/dev/null; then
    plymouth-set-default-theme nightfeed
    if command -v dracut-rebuild >/dev/null; then dracut-rebuild; else dracut -f; fi
else
    plymouth-set-default-theme -R nightfeed
fi
echo "Installed; you will see it at next boot." """,
      config="Make sure `splash` is on the kernel command line.",
      credit_extra="")

piece("nightfeed-global",
      short="Global theme + splash screen", title="Nightfeed — Global Theme (Plasma 6)", category="Global Themes (Plasma 6)",
      src=ROOT / "plasma/look-and-feel/scorn.nightfeed", tar_top="scorn.nightfeed",
      shots={"desktop.jpg": "desktop.png", "splash.jpg": "splash.png", "splash-rewind.jpg": "splash-rew.png"},
      tags=["global-theme", "look-and-feel", "splash-screen", "ksplash", "plasma-6"],
      summary="The Nightfeed global theme: switches Plasma to the whole suite at once, and ships the VHS rewind/play splash screen.",
      features="""- **Splash screen:** the tape rewinds (`REW ◀◀`, fast tracking band) and then plays (`PLAY ▶`). Tape blocks fill as Plasma's six startup stages arrive.
- **Defaults:** colour scheme, Plasma style, icons, Kvantum widget style, Aurorae window decoration and splash, all set to Nightfeed.
- **Ships no panel layout,** so applying it never rearranges your panels or widgets.""",
      requires="Plasma 6. Install the other Nightfeed pieces first (colour scheme, Plasma style, Aurorae, icons, Kvantum), or the global theme falls back to Breeze for whatever is missing. Kvantum needs `kvantum` installed.",
      install_store="System Settings → Colors & Themes → Global Theme → Install from File, or extract to `~/.local/share/plasma/look-and-feel/`. The splash alone can be picked under Colors & Themes → Splash Screen.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/plasma/look-and-feel/scorn.nightfeed
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{metadata.json,contents} "$DST"/
echo "Installed. Apply: plasma-apply-lookandfeel -a scorn.nightfeed  (splash only: kwriteconfig6 --file ksplashrc --group KSplash --key Theme scorn.nightfeed)" """,
      config="",
      credit_extra=TERMINESS)

piece("nightfeed-plasma",
      short="Plasma style (panel, popups)", title="Nightfeed — Plasma Style", category="Plasma Themes",
      src=ROOT / "plasma/desktoptheme/Nightfeed", tar_top="Nightfeed",
      shots={"panel.jpg": "panel.png", "desktop.jpg": "desktop.png"},
      tags=["plasma-style", "desktoptheme", "panel", "plasma-theme", "translucent", "blur"],
      summary="Cobalt-black glass for the Plasma panel, popups and tooltips: tiled VHS scanlines and grain, a violet glow seam and violet-tinted shadows.",
      features="""- Panel, popups/dialogs, tooltips and widget backgrounds in cobalt-black glass.
- VHS scanlines and tape grain tiled at 1:1, so they never smear or stretch at any panel size.
- A thin violet seam along the top edge with a soft glow below it, and shadows with a faint violet bleed nearest the frame.
- Translucent variants with blur and contrast behind them, plus solid variants for when compositing is off.
- Everything else (buttons, sliders, task highlights) falls back to Breeze and follows your colour scheme, so the Nightfeed colour scheme is recommended.""",
      requires="Plasma 6.",
      install_store="System Settings → Colors & Themes → Plasma Style → Install from File, or extract to `~/.local/share/plasma/desktoptheme/`.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/plasma/desktoptheme/Nightfeed
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{metadata.json,plasmarc,widgets,dialogs,solid,translucent} "$DST"/
plasma-apply-desktoptheme Nightfeed""",
      config="",
      credit_extra="")

piece("nightfeed-aurorae",
      short="Aurorae window decoration", title="Nightfeed — Aurorae Window Decoration", category="Aurorae Themes",
      src=ROOT / "aurorae/Nightfeed", tar_top="Nightfeed",
      shots={"decoration.jpg": "decoration.png", "buttons.jpg": "buttons.png"},
      tags=["aurorae", "window-decoration", "kwin", "titlebar", "vcr-buttons"],
      summary="A cobalt-black VHS window frame: a scanline title bar with tape-grain streaks, a violet glow seam, a violet-glow shadow and VCR transport buttons.",
      features="""- Title bar with faint scanlines and tape grain that stretches into horizontal VHS streaks.
- A violet glow seam under the title, with a hot 1 px core.
- The active window casts a soft violet glow; inactive windows dim to cobalt-black with a plain shadow.
- Square transport-style buttons that light up violet on hover (close glows REC red). The window-menu button is a VCR `▶ PLAY` triangle.
- Centred title, 3 px borders, no rounded corners.""",
      requires="KWin (Plasma 6) with Aurorae.",
      install_store="System Settings → Colors & Themes → Window Decorations → Install from File, or extract to `~/.local/share/aurorae/themes/`.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/aurorae/themes/Nightfeed
rm -rf "$DST"; mkdir -p "$DST"
cp "$HERE"/*.svg "$HERE"/Nightfeedrc "$HERE"/metadata.desktop "$DST"/
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__Nightfeed
qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true""",
      config="",
      credit_extra="")

piece("nightfeed-colors",
      short="Colour scheme", title="Nightfeed — Colour Scheme", category="Plasma Color Schemes",
      src=ROOT / "colors", tar_top="nightfeed-colors", files=["Nightfeed.colors"],
      shots={"palette.jpg": "colors.png", "desktop.jpg": "desktop.png"},
      tags=["color-scheme", "colour-scheme", "dark-theme", "kdeglobals"],
      summary="Cobalt-black KDE colour scheme with a violet accent and muted selections, sampled from a night-vision wallpaper.",
      features="""- The surfaces are blue-black, never pure #000: window `#0a0c18`, views `#06070f`, headers `#0f1223`, borders `#1e2552`.
- Violet `#7b5cff` for the accent, focus and hover, with a dimmer `#33259a` for selections, so a selected row glows without shouting.
- Pale periwinkle text `#c3c8ee`. The state colours stay cool: REC magenta for negative, teal for positive, muted amber for neutral.
- The titlebar colours are set too, for Breeze decorations.""",
      requires="Plasma 5 or 6.",
      install_store="System Settings → Colors & Themes → Colors → Install from File, or copy to `~/.local/share/color-schemes/`.",
      install_sh="""install -Dm644 "$HERE/Nightfeed.colors" "${XDG_DATA_HOME:-$HOME/.local/share}/color-schemes/Nightfeed.colors"
plasma-apply-colorscheme Nightfeed""",
      config="",
      credit_extra="")

piece("nightfeed-kvantum",
      short="Kvantum widget style", title="Nightfeed — Kvantum Theme", category="Kvantum",
      src=ROOT / "kvantum/Nightfeed", tar_top="Nightfeed",
      shots={"widgets.jpg": "gallery.png", "desktop.jpg": "desktop.png"},
      tags=["kvantum", "qt-style", "widget-style", "qt6", "qt5"],
      summary="Kvantum widget style in cobalt-black with violet accents: recessed text fields, violet sliders, checks and progress bars, dim selections.",
      features="""- Built on KvArcDark's engine map. The greys are remapped by luminance onto a cobalt-black ramp, and Arc's blue becomes violet.
- Text fields sit recessed, darker than the buttons.
- Sliders, checks, progress bars and focus rings are violet. Selections are a dimmer violet.
- Blurred popups. Matches the Nightfeed colour scheme.""",
      requires="Kvantum (`kvantum` package), with the widget style set to kvantum.",
      install_store="Extract to `~/.config/Kvantum/` and select **Nightfeed** in Kvantum Manager, then set the Application Style to kvantum.",
      install_sh="""DST=${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum/Nightfeed
rm -rf "$DST"; mkdir -p "$DST"
cp "$HERE"/Nightfeed.kvconfig "$HERE"/Nightfeed.svg "$DST"/
kwriteconfig6 --file Kvantum/kvantum.kvconfig --group General --key theme Nightfeed
kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle kvantum
echo "Restart apps to see it." """,
      config="",
      credit_extra="\nEngine map adapted from KvArcDark by Tsu Jan (Kvantum, GPL-3.0).")

piece("nightfeed-icons",
      short="Icon theme", title="Nightfeed — Icons", category="Full Icon Themes",
      src=ROOT / "icons/Nightfeed", tar_top="Nightfeed",
      shots={"icons.jpg": "icons.png", "desktop.jpg": "desktop.png"},
      tags=["icon-theme", "icons", "folders", "tela", "purple-folders"],
      summary="Violet folder and places icons plus a VHS-play launcher icon, layered over Tela circle dark.",
      features="""- Every folder and places icon (home, downloads, music, git, trash and the rest) recoloured to a deep violet with lavender glyphs.
- A VHS `▶ PLAY` app-launcher icon: a scanlined cobalt disc with a violet ring and glow, used for all `start-here` and `distributor-logo` names, symbolic ones included.
- All other icons are inherited from **Tela circle dark**, then breeze-dark.""",
      requires="[Tela circle icon theme](https://github.com/vinceliuice/Tela-circle-icon-theme), dark variant (`Tela-circle-dark`), installed alongside.",
      install_store="Extract to `~/.local/share/icons/` and pick **Nightfeed** in System Settings → Colors & Themes → Icons. Install Tela-circle-dark first.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/icons/Nightfeed
rm -rf "$DST"; mkdir -p "$DST"
cp -a "$HERE"/index.theme "$HERE"/scalable "$HERE"/scalable@2x "$HERE"/16 "$HERE"/16@2x "$HERE"/22 "$HERE"/22@2x "$HERE"/24 "$HERE"/24@2x "$HERE"/32 "$HERE"/32@2x "$HERE"/symbolic "$DST"/ 2>/dev/null || true
/usr/lib/plasma-changeicons Nightfeed 2>/dev/null || echo "Pick Nightfeed in System Settings > Icons." """,
      config="",
      credit_extra="\nFolder artwork recoloured from Tela circle icon theme by Vince Liuice (GPL-3.0).")

piece("nightfeed-konsole",
      short="Konsole + kitty colours", title="Nightfeed — Konsole & kitty Colours", category="Konsole color schemes",
      src=ROOT / "terminal", tar_top="nightfeed-konsole",
      files=["Nightfeed.colorscheme", "Nightfeed.profile", "nightfeed-kitty.conf"],
      shots={"terminal.jpg": "terminal.png", "desktop.jpg": "desktop.png"},
      tags=["konsole", "kitty", "terminal", "colorscheme", "terminal-theme"],
      summary="Cobalt-black terminal colours for Konsole and kitty, with a violet cursor and a cool 16-colour palette.",
      features="""- A blue-black background with pale periwinkle text and a violet block cursor.
- 16 colours tuned for the cobalt background: REC magenta, teal, amber, cobalt, violet and sky blue, plus bright variants.
- A Konsole profile with Terminess, a slight translucency and blur, and roomy margins.
- A kitty theme with matching tab and border colours.""",
      requires="Konsole and/or kitty. The profile uses Terminess Nerd Font if it is installed.",
      install_store="Copy `Nightfeed.colorscheme` and `Nightfeed.profile` to `~/.local/share/konsole/`, then pick the profile in Konsole. For kitty, add `include nightfeed-kitty.conf` to kitty.conf.",
      install_sh="""K=${XDG_DATA_HOME:-$HOME/.local/share}/konsole; mkdir -p "$K"
cp "$HERE"/Nightfeed.colorscheme "$HERE"/Nightfeed.profile "$K"/
C=${XDG_CONFIG_HOME:-$HOME/.config}/kitty; mkdir -p "$C"; cp "$HERE"/nightfeed-kitty.conf "$C"/
echo "Konsole: Settings > Switch Profile > Nightfeed.   kitty: add 'include nightfeed-kitty.conf' to kitty.conf" """,
      config="",
      credit_extra="")


# ---- build --------------------------------------------------------------------
def jpg(src, dst):
    subprocess.run(["magick", str(src), "-quality", "90", str(dst)], check=True)


def readme(repo, p):
    first = next(iter(p["shots"]))
    more = "\n".join(f"![{n.rsplit('.', 1)[0]}](screenshots/{n})" for n in list(p["shots"])[1:])
    tags = " ".join(f"`{t}`" for t in BASE_TAGS + p["tags"])
    cfg = f"\n## Configuration\n\n{p['config']}\n" if p["config"] else ""
    return f"""# {p['title']}

{p['summary']}

![{first.rsplit('.', 1)[0]}](screenshots/{first})

{BLURB}

## Features

{p['features']}

{more}

## Requirements

{p['requires']}

## Install

```bash
git clone {GH}/{repo}
cd {repo} && {"sudo " if "EUID" in p["install_sh"] else ""}./install.sh
```

Or from the KDE Store: {p['install_store']}
{cfg}
{suite_table(repo)}
## Tags

{tags}

{CREDITS.format(extra=p['credit_extra'])}"""


def store_listing(repo, p):
    return f"""NAME: {p['title']}
CATEGORY: {p['category']}
VERSION: {VERSION}
LICENSE: GPL-3.0-or-later
SOURCE: {GH}/{repo}
UPLOAD: {repo}.tar.gz
SCREENSHOTS (in order): {", ".join("screenshots/" + n for n in p["shots"])}
TAGS: {", ".join(BASE_TAGS + p["tags"])}

SUMMARY:
{p['summary']}

DESCRIPTION:
{p['summary']}

{BLURB}

{p['features']}

Requirements: {p['requires']}

Install: {p['install_store']}

Part of the Nightfeed suite: SDDM login, Plymouth boot splash, global theme + splash screen, Plasma style, Aurorae window decoration, colour scheme, Kvantum, icons, and Konsole/kitty colours. Source for every piece: {GH}/nightfeed
"""


def main():
    REPOS.mkdir(exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    for repo, p in PIECES.items():
        d = REPOS / repo
        keep_git = d / ".git"
        if d.exists():
            for c in d.iterdir():
                if c.name != ".git":
                    shutil.rmtree(c) if c.is_dir() and not c.is_symlink() else c.unlink()
        d.mkdir(exist_ok=True)
        # theme payload at the repo root
        if "files" in p:
            for f in p["files"]:
                shutil.copy2(p["src"] / f, d / f)
        else:
            for c in p["src"].iterdir():
                if c.is_dir() and not c.is_symlink():
                    shutil.copytree(c, d / c.name, symlinks=True)
                else:
                    shutil.copy2(c, d / c.name, follow_symlinks=False)
        (d / "screenshots").mkdir(exist_ok=True)
        for n, s in p["shots"].items():
            jpg(SHOTS / s, d / "screenshots" / n)
        (d / "README.md").write_text(readme(repo, p))
        shutil.copy(GPL, d / "LICENSE")
        sh = d / "install.sh"
        sh.write_text(f"#!/usr/bin/env bash\n# {p['title']} — install.  ./install.sh\nset -euo pipefail\nHERE=$(cd \"$(dirname \"${{BASH_SOURCE[0]}}\")\" && pwd)\n{p['install_sh'].strip()}\n")
        sh.chmod(0o755)

        # store kit
        k = DOCS / repo
        if k.exists():
            shutil.rmtree(k)
        (k / "screenshots").mkdir(parents=True)
        for n in p["shots"]:
            shutil.copy(d / "screenshots" / n, k / "screenshots" / n)
        with tarfile.open(k / f"{repo}.tar.gz", "w:gz") as t:
            if "files" in p:
                for f in p["files"]:
                    t.add(p["src"] / f, arcname=f"{p['tar_top']}/{f}")
            else:
                t.add(p["src"], arcname=p["tar_top"])
        (k / "STORE-LISTING.txt").write_text(store_listing(repo, p))
        print(f"{repo:22s} -> repos/{repo}, {k}")

    # suite-wide overview in the docs folder
    (DOCS / "README.txt").write_text(
        "Nightfeed — KDE Store upload kit\n\nOne folder per component. Each holds the upload tarball, screenshots/ (upload in the listed order) and STORE-LISTING.txt (name, category, tags, description to paste).\n\n"
        + "\n".join(f"  {r:22s} {p['category']:28s} {r}.tar.gz" for r, p in PIECES.items())
        + f"\n\nSource repos: {GH}/<folder name>   (hub with everything: {GH}/nightfeed)\n")
    shutil.copy(SHOTS / "desktop.png", DOCS / "nightfeed-desktop.png")


if __name__ == "__main__":
    main()

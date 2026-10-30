#!/usr/bin/env bash
# nightfeed — install the SDDM login theme and the Plymouth boot splash (needs root).
#
#   sudo bash ~/nightfeed/install.sh                  both
#   sudo bash ~/nightfeed/install.sh --sddm-only
#   sudo bash ~/nightfeed/install.sh --plymouth-only
#   sudo bash ~/nightfeed/install.sh --revert         put the previous themes back
set -euo pipefail

NAME=nightfeed
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
STATE=/var/lib/$NAME
SDDM_DST=/usr/share/sddm/themes/$NAME
PLY_DST=/usr/share/plymouth/themes/$NAME

[[ $EUID -eq 0 ]] || { echo "run with sudo: sudo bash $0 $*" >&2; exit 1; }

do_sddm=1 do_ply=1 revert=0
case "${1:-}" in
    --sddm-only)     do_ply=0 ;;
    --plymouth-only) do_sddm=0 ;;
    --revert)        revert=1 ;;
    "")              ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
esac

# SDDM reads /etc/sddm.conf.d/*.conf in name order and the last Current= wins,
# so every file that sets it is updated.
set_sddm_theme() {
    local theme=$1 f
    for f in /etc/sddm.conf /etc/sddm.conf.d/*.conf; do
        [[ -f $f ]] && grep -q '^Current=' "$f" && sed -i "s/^Current=.*/Current=$theme/" "$f"
    done
    echo "    SDDM theme -> $(cat /etc/sddm.conf /etc/sddm.conf.d/*.conf 2>/dev/null | grep '^Current=' | tail -1)"
}

rebuild_initramfs() {
    echo "==> Rebuilding initramfs (dracut)..."
    # plymouth-set-default-theme -R calls mkinitcpio, which this system does not have
    dracut-rebuild
}

mkdir -p "$STATE"

if (( revert )); then
    old_sddm=$(cat "$STATE/previous-sddm" 2>/dev/null || echo daedric-morrowind)
    old_ply=$(cat "$STATE/previous-plymouth" 2>/dev/null || echo daedric-morrowind)
    echo "==> Reverting to SDDM '$old_sddm' and Plymouth '$old_ply'"
    set_sddm_theme "$old_sddm"
    plymouth-set-default-theme "$old_ply"
    rebuild_initramfs
    echo "Done. Theme files are left in place; remove $SDDM_DST and $PLY_DST to delete them."
    exit 0
fi

if (( do_sddm )); then
    echo "==> Installing SDDM theme to $SDDM_DST"
    current=$(cat /etc/sddm.conf /etc/sddm.conf.d/*.conf 2>/dev/null | grep '^Current=' | tail -1 | cut -d= -f2 || true)
    [[ -n $current && $current != "$NAME" ]] && echo "$current" > "$STATE/previous-sddm"
    rm -rf "$SDDM_DST"
    cp -r "$HERE/sddm/$NAME" "$SDDM_DST"
    chmod -R a+rX "$SDDM_DST"
    set_sddm_theme "$NAME"
fi

if (( do_ply )); then
    echo "==> Installing Plymouth theme to $PLY_DST"
    current=$(plymouth-set-default-theme)
    [[ -n $current && $current != "$NAME" ]] && echo "$current" > "$STATE/previous-plymouth"
    rm -rf "$PLY_DST"
    cp -r "$HERE/plymouth/$NAME" "$PLY_DST"
    chmod -R a+rX "$PLY_DST"
    plymouth-set-default-theme "$NAME"
    rebuild_initramfs
    # NB: no `grep -q` here. With `set -o pipefail`, grep -q quits on the
    # first match, lsinitrd then dies with SIGPIPE (141), and the `if`
    # always fails even when the theme is present. Plain grep reads the
    # whole listing, so the pipeline status is grep's real answer.
    if lsinitrd /boot/initramfs-linux.img | grep "plymouth/themes/$NAME/$NAME.script" > /dev/null; then
        echo "    initramfs contains $NAME"
    else
        echo "!!  $NAME not found in /boot/initramfs-linux.img — splash will not change" >&2
        exit 1
    fi
fi

echo "Done. The login screen changes at next logout; the splash at next boot."
echo "Undo with: sudo bash $HERE/install.sh --revert"

#!/usr/bin/env bash
# Rootless Plymouth preview: virtual KWin + Xwayland, plymouthd with the x11
# renderer in a user+mount namespace with the theme bind-mounted in.
#   bash tools/test-plymouth.sh <out.png> [boot|shutdown|reboot] [password]
set -u
OUT=${1:?out.png}; MODE=${2:-boot}; PW=${3:-}
HERE=$(cd "$(dirname "$0")/.." && pwd)
TMP=$(mktemp -d)
mkdir -p "$TMP/themes" "$TMP/etc" "$TMP/run" "$TMP/xdg"
cp -r "$HERE/plymouth/nightfeed" "$TMP/themes/nightfeed"
cp -r /usr/share/plymouth/themes/{details,text} "$TMP/themes/" 2>/dev/null
printf '[Daemon]\nTheme=nightfeed\n' > "$TMP/etc/plymouthd.conf"
cat > "$TMP/inner.sh" <<IN
set -u
env > "$TMP/env.txt"
mount --bind "$TMP/themes" /usr/share/plymouth/themes
mount --bind "$TMP/etc" /etc/plymouth
mount --bind "$TMP/run" /run/plymouth

GDK_BACKEND=x11 WAYLAND_DISPLAY= script -qfec 'plymouthd --no-daemon --mode=${MODE/reboot/shutdown} --tty=\$(tty) --kernel-command-line="splash quiet plymouth.ignore-udev" --no-boot-log --graphical-boot --debug-file=$TMP/ply.log' /dev/null < /dev/zero > /dev/null 2>&1 &
sleep 1.5
plymouth show-splash
plymouth system-update --progress=0 2>/dev/null
for p in 10 25 40 55; do plymouth --update=x\$p; sleep 0.4; done
if [ -n "$PW" ]; then plymouth ask-for-password --prompt=x & sleep 0.6; fi
sleep 3
touch "$TMP/ready"
sleep 4
plymouth quit
IN
cat > "$TMP/session.sh" <<SE
#!/usr/bin/env bash
(unshare -rm bash "$TMP/inner.sh") &
for i in \$(seq 1 60); do [ -f "$TMP/ready" ] && break; sleep 0.25; done
rm -f "$OUT"
import -window root "$TMP/root.png" > "$TMP/spectacle.log" 2>&1
spectacle -b -n -f -o "$TMP/spec.png" >> "$TMP/spectacle.log" 2>&1
sleep 3
ls -la "$TMP" >> "$TMP/spectacle.log"
sleep 1
SE
chmod +x "$TMP/session.sh"
XDG_CONFIG_HOME=$TMP/xdg dbus-run-session -- kwin_wayland --virtual --xwayland --width 1920 --height 1080 --no-lockscreen --exit-with-session "$TMP/session.sh" >"$TMP/kwin.log" 2>&1
grep -iE "error|fail|script" "$TMP/ply.log" 2>/dev/null | grep -v "^$" | tail -8
cp "$TMP/spec.png" "$OUT" 2>/dev/null || cp "$TMP/root.png" "$OUT" 2>/dev/null
echo "log: $TMP"

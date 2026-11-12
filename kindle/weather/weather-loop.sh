#!/bin/sh
# Turn the Kindle into a weather display (after mpetroff's init-weather.sh):
# stop the reader UI so it can't draw over the image, keep the device
# awake (Wi-Fi and timers stop in sleep), then refresh forever.
# Keep the Kindle on USB power. Output goes to loop.log (see start.sh).
cd "$(dirname "$0")"
. ./config.sh
trap '' HUP
echo $$ > weather.pid
say() { echo "$(date '+%F %T') loop: $*"; }

say "started, pid $$"
lipc-set-prop com.lab126.powerd preventScreenSaver 1
sleep 2
if [ -x /etc/init.d/framework ]; then
	say "stopping UI (init.d framework)"
	/etc/init.d/framework stop      # Kindle Touch (FW 5.0-5.3)
else
	say "stopping UI (upstart lab126_gui)"
	stop lab126_gui 2>/dev/null || stop framework   # PW2 and later
fi
say "UI stopped"
sleep 5

while true; do
	sh ./display-weather.sh
	say "next update in $INTERVAL min"
	sleep $((INTERVAL * 60))
done

#!/bin/sh
# Turn the Kindle into a weather display (after mpetroff's init-weather.sh):
# stop the reader UI so it can't draw over the image, keep the device
# awake (Wi-Fi and timers stop in sleep), then refresh forever.
# Keep the Kindle on USB power.
cd "$(dirname "$0")"
. ./config.sh
echo $$ > weather.pid

lipc-set-prop com.lab126.powerd preventScreenSaver 1
sleep 2
if [ -x /etc/init.d/framework ]; then
	/etc/init.d/framework stop      # Kindle Touch (FW 5.0-5.3)
else
	stop lab126_gui 2>/dev/null || stop framework   # PW2 and later (upstart)
fi
sleep 5

while true; do
	./display-weather.sh
	sleep $((INTERVAL * 60))
done

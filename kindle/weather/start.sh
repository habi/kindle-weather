#!/bin/sh
# Called from KUAL. KUAL runs inside the Kindle UI's process group, and the
# loop stops that UI, so start the loop in its own session (setsid) or it
# gets killed along with the UI.
cd "$(dirname "$0")"
[ -f weather.pid ] && kill "$(cat weather.pid)" 2>/dev/null
echo "$(date '+%F %T') start.sh" >> loop.log
if command -v setsid > /dev/null 2>&1; then
	setsid sh ./weather-loop.sh >> loop.log 2>&1 < /dev/null &
else
	nohup sh ./weather-loop.sh >> loop.log 2>&1 < /dev/null &
fi

#!/bin/sh
# Called from KUAL. KUAL runs inside the Kindle UI's process group, and the
# loop stops that UI, so start the loop detached from it or it gets killed
# along with the UI. The Kindle Touch's busybox has neither setsid nor nohup,
# so try several ways and log which one was used.
cd "$(dirname "$0")"
[ -f weather.pid ] && kill -9 "$(cat weather.pid)" 2>/dev/null
LOOP="sh ./weather-loop.sh"
if command -v setsid > /dev/null 2>&1; then
	how=setsid; set -- setsid $LOOP
elif busybox setsid true > /dev/null 2>&1; then
	how="busybox setsid"; set -- busybox setsid $LOOP
elif command -v start-stop-daemon > /dev/null 2>&1; then
	how=start-stop-daemon
elif command -v nohup > /dev/null 2>&1; then
	how=nohup; set -- nohup $LOOP
else
	how="double fork"; set -- $LOOP
fi
echo "$(date '+%F %T') start.sh ($how)" >> loop.log
if [ "$how" = start-stop-daemon ]; then
	start-stop-daemon -S -b -x /bin/sh -- -c "cd '$PWD' && exec sh ./weather-loop.sh >> loop.log 2>&1 < /dev/null"
else
	# the subshell exits at once, so the loop is re-parented to init
	( trap '' HUP TERM INT; "$@" >> loop.log 2>&1 < /dev/null & ) &
fi

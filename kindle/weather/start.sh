#!/bin/sh
# Called from KUAL. Detach, because stopping the UI also ends KUAL.
cd "$(dirname "$0")"
[ -f weather.pid ] && kill "$(cat weather.pid)" 2>/dev/null
nohup sh ./weather-loop.sh > /dev/null 2>&1 &

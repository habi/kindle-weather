#!/bin/sh
# Stop the weather display and give the Kindle back its normal UI.
# Reach it via KUAL after a reboot (hold power ~20 s), or run it in kterm/SSH.
cd "$(dirname "$0")"
[ -f weather.pid ] && kill "$(cat weather.pid)" 2>/dev/null
rm -f weather.pid
lipc-set-prop com.lab126.powerd preventScreenSaver 0
eips -c
if [ -x /etc/init.d/framework ]; then
	/etc/init.d/framework start
else
	start lab126_gui 2>/dev/null || start framework
fi

#!/bin/sh
# Switch off the front light (Paperwhite); a no-op on Kindles without one.
lipc-set-prop com.lab126.powerd flIntensity 0 2>/dev/null
for b in /sys/class/backlight/*/brightness; do
	[ -w "$b" ] && echo 0 > "$b"
done
exit 0

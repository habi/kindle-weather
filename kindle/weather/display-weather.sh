#!/bin/sh
# Fetch the forecast PNG and show it full-screen (after mpetroff's
# display-weather.sh). Shows the error image only after 3 failed fetches
# in a row, so a single Wi-Fi hiccup keeps the last good forecast up.
cd "$(dirname "$0")"
. ./config.sh

log() { echo "$(date '+%F %T') $*" >> weather.log; }

# Screen size: override with a file "screen" containing touch or pw2
if [ -s screen ]; then
	SCREEN=$(cat screen)
else
	XRES=$(eips -i 2>/dev/null | grep -o 'xres:[[:space:]]*[0-9]*' | head -n1 | grep -o '[0-9]*$')
	if [ "${XRES:-600}" -ge 700 ]; then SCREEN=pw2; else SCREEN=touch; fi
fi
log "screen $SCREEN, waiting for Wi-Fi"

# Make sure Wi-Fi is on and wait up to 60 s for a connection
lipc-set-prop com.lab126.cmd wirelessEnable 1 2>/dev/null
i=0
while [ $i -lt 30 ] && [ "$(lipc-get-prop com.lab126.wifid cmState 2>/dev/null)" != CONNECTED ]; do
	sleep 2; i=$((i + 1))
done

log "Wi-Fi: $(lipc-get-prop com.lab126.wifid cmState 2>/dev/null), downloading"
rm -f new.png
if curl -k -s -f -m 60 -o new.png "$BASE_URL/weather-$SCREEN.png" ||
   wget -q -T 60 -O new.png "$BASE_URL/weather-$SCREEN.png"; then
	mv new.png weather.png
	echo 0 > failures
	eips -c
	eips -c
	eips -g weather.png
	log "ok ($SCREEN)"
else
	n=$(( $(cat failures 2>/dev/null || echo 0) + 1 ))
	echo $n > failures
	log "fetch failed ($n) $SCREEN"
	if [ $n -ge 3 ] || [ ! -f weather.png ]; then
		eips -c
		eips -c
		eips -g weather-image-error-$SCREEN.png
	fi
fi
# keep the logs small
for f in weather.log loop.log; do
	[ -f $f ] && tail -n 200 $f > $f.tmp && mv $f.tmp $f
done

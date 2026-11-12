#!/bin/sh
# Build the Kindle weather PNGs, as in mpetroff's weather-script.sh:
# fill the SVG template, render with rsvg-convert, make 8-bit greyscale
# without alpha (the Kindle's eips shows RGB PNGs distorted).
# Needs: python3, rsvg-convert (librsvg2-bin), pngcrush, DejaVu Sans.
set -eu
cd "$(dirname "$0")"
OUT=${1:-../output}
python3 weather.py "$OUT"
for svg in "$OUT"/weather-*.svg; do
	png=${svg%.svg}.png
	${RSVG_CONVERT:-rsvg-convert} --background-color=white -o "$png" "$svg"
	pngcrush -q -c 0 "$png" "$png.tmp" && mv "$png.tmp" "$png"
done
ls -l "$OUT"

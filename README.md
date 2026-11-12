# Kindle weather display

A rebuild of Matthew Petroff's [Kindle Weather Display](https://mpetroff.net/2012/09/kindle-weather-display/) ([source](https://github.com/mpetroff/kindle-weather-display)), using the open local forecast from [MeteoSwiss](https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data) instead of NOAA, in German and °C.

![Kindle Touch preview](https://habi.github.io/kindle-weather/weather-touch.png)

## How it works

```
GitHub Actions (hourly)                         Kindle (every 30 min)
server/weather.py   MeteoSwiss CSV -> SVG       weather/display-weather.sh
server/render.sh    rsvg-convert, pngcrush  ->  curl PNG, eips -c, eips -g
gh-pages            weather-touch.png 600x800
                    weather-pw2.png   758x1024
```

- **Data:** MeteoSwiss `ogd-local-forecasting` (STAC on data.geo.admin.ch), for the postal-code point `POSTAL_CODE` (default 3097 Liebefeld): daily pictogram `jp2000d0` and local-day max/min `tre200px`/`tre200pn`. This is the same forecast as the MeteoSwiss app.
- **Layout and icons:** mpetroff's SVG template and CC0 weather icons (`server/template.svg`). Labels are translated, units changed to °C, long weekday names shrunk, and a footer added with the forecast time and source (required by MeteoSwiss's CC BY terms). MeteoSwiss pictogram numbers are mapped to the icons in `ICONS` in `server/weather.py`. MeteoSwiss's own pictogram graphics are not licensed for reuse.
- **Screens:** The same 600×800 design is rendered for the Kindle Touch (and Kindle 4), and scaled to 758×1024 for the Paperwhite 2.

## Kindle setup (jailbroken, KUAL installed)

1. Copy `kindle/weather/` to the Kindle's root as `weather/`, and `kindle/extensions/weather/` to `extensions/weather/`.
2. Plug the Kindle into USB power. It must stay awake, because Wi-Fi and timers stop in sleep.
3. Open KUAL → *Wetter* → *Wetteranzeige starten*. The reader UI stops and the forecast appears. If not, `weather/loop.log` and `weather/weather.log` say how far it got.
4. To get the normal Kindle back, use *Wetteranzeige beenden*. Since the UI is gone, that means rebooting (hold the power button ~20 s) and then using KUAL.

The screen size is detected automatically. To force it, put `touch` or `pw2` into `weather/screen`. The server URL and interval are in `weather/config.sh`, and each fetch is logged to `weather/weather.log`.

## Local run

```sh
sudo apt install librsvg2-bin pngcrush fonts-dejavu-core
POSTAL_CODE=3097 server/render.sh /tmp/weather
```

## Licences

Scripts and template derived from mpetroff's work: MIT (`server/COPYING-mpetroff`). Icons: CC0. Weather data: © MeteoSwiss, CC BY.

#!/usr/bin/env python3
"""
Kindle weather display, MeteoSwiss edition.

Fetches the MeteoSwiss local forecast (open data, same forecast as the
MeteoSwiss app) for one Swiss postal code and fills in the SVG template
from Matthew Petroff's Kindle Weather Display
(https://mpetroff.net/2012/09/kindle-weather-display/).

Output: one SVG per Kindle screen size; render.sh turns them into PNGs.
Standard library only.
"""

import csv
import io
import json
import math
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

POSTAL_CODE = os.environ.get("POSTAL_CODE", "3097")  # Liebefeld
POINT_ID = POSTAL_CODE + "00"  # MeteoSwiss point_id of a postal-code centre

# Kindle screens: name -> (width, height)
SCREENS = {
    "touch": (600, 800),  # Kindle Touch (D01200), also Kindle 4
    "pw2": (758, 1024),   # Kindle Paperwhite 2
}

STAC_ITEMS = ("https://data.geo.admin.ch/api/stac/v1/collections/"
              "ch.meteoschweiz.ogd-local-forecasting/items/")
PARAMS = ("jp2000d0", "tre200px", "tre200pn")  # daily symbol, local-day max, min
TZ = ZoneInfo("Europe/Zurich")

DAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
           "Freitag", "Samstag", "Sonntag"]

# MeteoSwiss pictogram number (1-42 day, 101-142 night) -> icon id in the
# template (mpetroff's CC0 "Weather Icons", originally NOAA icon names).
# Descriptions: MeteoSwiss pictogram reference, 2022-02-14.
ICONS = {
    1: "skc",        # sonnig
    2: "few",        # ziemlich sonnig
    3: "sct",        # teilweise sonnig
    4: "bkn",        # wechselnd bewölkt
    5: "ovc",        # bedeckt
    6: "hi_shwrs",   # Aufhellungen, einzelne Regenschauer
    7: "rasn",       # Aufhellungen, einzelne Regen- oder Schneeschauer
    8: "sn",         # Aufhellungen, einzelne Schneeschauer
    9: "shra",       # bewölkt, einige Regenschauer
    10: "rasn",      # bewölkt, einige Regen- oder Schneeschauer
    11: "sn",        # bewölkt, einige Schneeschauer
    12: "scttsra",   # Aufhellungen, leicht gewitterhaft
    13: "scttsra",   # Aufhellungen und gewitterhaft
    14: "shra",      # stark bewölkt, schwacher Regen
    15: "rasn",      # stark bewölkt, schwacher Schnee oder Regen
    16: "sn",        # stark bewölkt, schwacher Schnee
    17: "ra",        # stark bewölkt, zeitweise Regen
    18: "rasn",      # stark bewölkt, zeitweise Schnee oder Regen
    19: "sn",        # stark bewölkt, zeitweise Schnee
    20: "ra",        # stark bewölkt, anhaltender Regen
    21: "rasn",      # stark bewölkt, anhaltender Regen oder Schnee
    22: "sn",        # stark bewölkt, anhaltender Schnee
    23: "tsra",      # stark bewölkt, leicht gewitterhaft
    24: "tsra",      # stark bewölkt, gewitterhaft
    25: "tsra",      # stark bewölkt, stark gewitterhaft
    26: "few",       # hohe Bewölkung
    27: "fg",        # Hochnebel
    28: "fg",        # Nebel
    29: "hi_shwrs",  # leicht bewölkt, einzelne Regenschauer
    30: "sn",        # leicht bewölkt, leichter Schneefall
    31: "rasn",      # teilweise sonnig, einige Schnee- oder Regenschauer
    32: "hi_shwrs",  # teilweise sonnig, einige Regenschauer
    33: "ra",        # bewölkt, häufige Regenschauer
    34: "sn",        # bewölkt, häufige Schneeschauer
    35: "ovc",       # bedeckt und trocken
    36: "scttsra",   # teilweise sonnig, gewitterhaft
    37: "scttsra",   # teilweise sonnig, Gewitter und Schneeschauer
    38: "tsra",      # bewölkt, Gewitter und häufige Regenschauer
    39: "tsra",      # bewölkt, Gewitter und häufige Schneeschauer
    40: "tsra",      # stark bewölkt, leicht gewitterhaft
    41: "tsra",      # bewölkt, leicht gewitterhaft
    42: "tsra",      # stark bewölkt, Gewitter und häufige Schneeschauer
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "kindle-weather"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def latest_run():
    """Return {param: csv_url} for the newest forecast run that has all PARAMS.

    Items are one per day (YYYYMMDD-ch) and hold every hourly run of that day.
    """
    today = datetime.now(timezone.utc).date()
    for day in (today, today - timedelta(days=1)):
        try:
            item = json.loads(get(STAC_ITEMS + day.strftime("%Y%m%d") + "-ch"))
        except Exception as e:  # item for today not there yet just after 00 UTC
            print(f"no item for {day}: {e}", file=sys.stderr)
            continue
        runs = {}
        for name, asset in item["assets"].items():
            # vnut12.lssw.YYYYMMDDHHMM.<param>.csv
            parts = name.split(".")
            if len(parts) == 5 and parts[3] in PARAMS:
                runs.setdefault(parts[2], {})[parts[3]] = asset["href"]
        complete = [r for r in runs if len(runs[r]) == len(PARAMS)]
        if complete:
            run = max(complete)
            return run, runs[run]
    raise RuntimeError("no complete MeteoSwiss forecast run found")


def read_param(url, param):
    """Return {date: value} for POINT_ID from one parameter CSV."""
    text = get(url).decode("latin-1")
    out = {}
    for row in csv.DictReader(io.StringIO(text), delimiter=";"):
        if row["point_id"] == POINT_ID and row[param] not in ("", None):
            out[row["Date"][:8]] = float(row[param])
    if not out:
        raise RuntimeError(f"no {param} data for point {POINT_ID}")
    return out


def rnd(x):
    """Round half up to an int string, with a real minus sign."""
    return str(int(math.floor(x + 0.5))).replace("-", "−")


def main(outdir):
    run, urls = latest_run()
    data = {p: read_param(u, p) for p, u in urls.items()}

    now = datetime.now(TZ)
    today = now.strftime("%Y%m%d")
    dates = sorted(d for d in data["jp2000d0"] if d >= today)[:4]
    if len(dates) < 4:
        raise RuntimeError(f"only {len(dates)} forecast days: {dates}")

    icons, highs, lows = [], [], []
    for d in dates:
        code = int(data["jp2000d0"][d])
        icons.append(ICONS.get(code if code < 100 else code - 100, "ovc"))
        highs.append(rnd(data["tre200px"][d]))
        lows.append(rnd(data["tre200pn"][d]))
    days = [DAYS_DE[datetime.strptime(d, "%Y%m%d").weekday()] for d in dates]

    run_local = (datetime.strptime(run, "%Y%m%d%H%M")
                 .replace(tzinfo=timezone.utc).astimezone(TZ))
    footer = (f"{POSTAL_CODE} · Prognose {run_local:%d.%m. %H:%M} · "
              f"abgerufen {now:%H:%M} · Quelle: MeteoSchweiz")

    here = os.path.dirname(os.path.abspath(__file__))
    svg = open(os.path.join(here, "template.svg"), encoding="utf-8").read()
    names = ["ONE", "TWO", "THREE", "FOUR"]
    for i, n in enumerate(names):
        svg = (svg.replace("ICON_" + n, icons[i])
                  .replace("HIGH_" + n, highs[i])
                  .replace("LOW_" + n, lows[i]))
    for i, n in ((2, "THREE"), (3, "FOUR")):
        # columns are ~200px wide; "Donnerstag:" at 32px would overlap
        svg = (svg.replace("DAY_" + n, days[i])
                  .replace("FS_" + n, "32px" if len(days[i]) <= 8 else "27px"))
    svg = svg.replace("FOOTER", footer)

    os.makedirs(outdir, exist_ok=True)
    for name, (w, h) in SCREENS.items():
        out = svg.replace("SVG_WIDTH", str(w)).replace("SVG_HEIGHT", str(h))
        with open(os.path.join(outdir, f"weather-{name}.svg"), "w",
                  encoding="utf-8") as f:
            f.write(out)

    print(f"run {run} UTC, point {POINT_ID}")
    for d, day, ic, hi, lo in zip(dates, days, icons, highs, lows):
        print(f"  {d} {day:<10} {ic:<9} {hi:>4} / {lo:>4}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "output")

from datetime import datetime, timedelta
import meteostat as ms
from meteostat import Point
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Kindle PW2 resolution
W, H = 758, 1024

# Coordinates for Liebefeld, Switzerland
location = Point(46.9326, 7.4176)

# Time range: last 12 hours
end = datetime.utcnow()
start = end - timedelta(hours=12)

# Fetch hourly data (nearest stations automatically)
ts = ms.hourly(location, start, end)
data = ts.fetch()

# Ensure we have at least one row
if data.empty:
    raise RuntimeError("No weather data available")

# Take latest point
latest = data.iloc[-1]

temp_now = round(latest["temp"])
precip = latest.get("prcp", 0)

# Is it night?
now = datetime.utcnow()
night = now.hour < 6 or now.hour > 20

# Create the image
img = Image.new("L", (W, H), 255)
draw = ImageDraw.Draw(img)

# Fonts
font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
font_mid = ImageFont.truetype("DejaVuSans.ttf", 48)
font_small = ImageFont.truetype("DejaVuSans.ttf", 36)

# Current temperature
draw.text((60, 80), f"{temp_now}°C", font=font_big, fill=0)
draw.text((60, 220), "Liebefeld", font=font_mid, fill=0)
draw.text((60, 280), now.strftime("%H:%M UTC"), font=font_small, fill=120)

# Precipitation bar
draw.rectangle((60, 340, 660, 380), outline=0, width=2)
bar_width = min(int(precip * 50), 600)
draw.rectangle((60, 340, 60 + bar_width, 380), fill=0)
draw.text((60, 390), f"Precip {precip:.1f} mm", font=font_small, fill=0)

# 12‑hour temperature graph
temps = data["temp"].tolist()
if temps:
    tmin, tmax = min(temps), max(temps)
    graph_x, graph_y = 60, 460
    graph_w, graph_h = 640, 220
    scale = graph_h / max(1, tmax - tmin)
    points = [
        (graph_x + int(i * graph_w / max(1, len(temps) - 1)),
         graph_y + graph_h - int((t - tmin) * scale))
        for i, t in enumerate(temps)
    ]
    draw.rectangle((graph_x, graph_y, graph_x + graph_w, graph_y + graph_h), outline=0)
    draw.line(points, fill=0, width=3)
    draw.text((graph_x, graph_y + graph_h + 10),
              "Last 12h temp trend", font=font_small, fill=0)

# Invert for night
if night:
    img = ImageOps.invert(img)

# Save
img.save("output/weather.png")

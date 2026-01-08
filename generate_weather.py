import os
import json
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps

# -------------------------------
# Settings
# -------------------------------
LAT, LON = 46.9326, 7.4176
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENWEATHER_API_KEY not set!")

# Kindle Paperwhite 2 resolution
W, H = 758, 1024

# Fonts
FA_PATH = "fa-solid-900.ttf"  # Must exist in repo
font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
font_small = ImageFont.truetype("DejaVuSans.ttf", 36)

# Map OpenWeatherMap codes to FontAwesome glyphs
OWM_TO_FA = {
    "01d": "\uf185", "01n": "\uf186",
    "02d": "\uf6c4", "02n": "\uf6c3",
    "03d": "\uf0c2", "03n": "\uf0c2",
    "09d": "\uf73d", "09n": "\uf73d",
    "10d": "\uf740", "10n": "\uf740",
    "13d": "\uf2dc", "13n": "\uf2dc",
    "50d": "\uf75f", "50n": "\uf75f"
}

def draw_weather_icon(draw, code, x, y, size=48):
    try:
        glyph = OWM_TO_FA.get(code, "\uf0c2")
        icon_font = ImageFont.truetype(FA_PATH, size)
        draw.text((x, y), glyph, font=icon_font, fill=0)
    except OSError:
        print(f"⚠️ Font {FA_PATH} not found. Skipping icons.")

# -------------------------------
# Fetch weather
# -------------------------------
url = (
    f"https://api.openweathermap.org/data/2.5/onecall"
    f"?lat={LAT}&lon={LON}&exclude=minutely,daily,alerts&units=metric&appid={API_KEY}"
)
try:
    resp = requests.get(url, timeout=10)
    data = resp.json()
except Exception as e:
    print(f"⚠️ Failed to fetch weather: {e}")
    data = {}

# Debug API response
print("🌤 API response:")
print(json.dumps(data, indent=2))

# -------------------------------
# Check API response validity
# -------------------------------
if "current" not in data or "hourly" not in data:
    # If API failed, use fallback
    print("⚠️ API did not return expected data. Using fallback values.")
    data = {
        "current": {"temp": 20, "weather": [{"icon": "01d"}], "dt": 0},
        "hourly": [{"temp": 20, "weather": [{"icon": "01d"}], "pop": 0}] * 48
    }

current = data["current"]
hourly = data["hourly"][:48]

# -------------------------------
# Create image
# -------------------------------
img = Image.new("L", (W, H), 255)
draw = ImageDraw.Draw(img)

# Current temp + city
draw.text((60, 80), f"{round(current['temp'])}°C", font=font_big, fill=0)
draw.text((60, 220), "Liebefeld", font=font_small, fill=0)

# Current weather icon
draw_weather_icon(draw, current["weather"][0]["icon"], x=60, y=280, size=64)

# 48h forecast graph
temps = [round(h["temp"]) for h in hourly]
precip = [round(h.get("pop", 0)*100) for h in hourly]
graph_x, graph_y, graph_w, graph_h = 60, 400, 640, 300
tmin, tmax = min(temps), max(temps)
scale = graph_h / max(1, tmax - tmin)

# Temperature line
points = [(graph_x + int(i * graph_w / 47),
           graph_y + graph_h - int((t - tmin) * scale)) for i, t in enumerate(temps)]
draw.rectangle((graph_x, graph_y, graph_x+graph_w, graph_y+graph_h), outline=0)
draw.line(points, fill=0, width=2)

# Precipitation bars
for i, p in enumerate(precip):
    bar_height = int(p / 100 * 50)
    x = graph_x + int(i * graph_w / 47)
    draw.line((x, graph_y - bar_height, x, graph_y), fill=0)

draw.text((graph_x, graph_y + graph_h + 10),
          "Next 48h temperature & precipitation", font=font_small, fill=0)

# Draw hourly icons above graph
icon_size = 24
for i, h in enumerate(hourly):
    x = graph_x + int(i * graph_w / 47) - icon_size // 2
    y = graph_y - 60
    draw_weather_icon(draw, h["weather"][0]["icon"], x, y, size=icon_size)

# Night inversion
now_hour = datetime.utcfromtimestamp(current["dt"]).hour
if now_hour < 6 or now_hour > 20:
    img = ImageOps.invert(img)

# Save output
os.makedirs("output", exist_ok=True)
img.save("output/weather.png")
print("✅ Weather image generated successfully")

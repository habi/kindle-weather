import os
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

# FontAwesome
FA_PATH = "fonts/fa-solid-900.ttf"
fa_font = ImageFont.truetype(FA_PATH, 48)
font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
font_small = ImageFont.truetype("DejaVuSans.ttf", 36)

# Map OpenWeatherMap icon codes to FontAwesome glyphs
OWM_TO_FA = {
    "01d": "\uf185",  # Sun
    "01n": "\uf186",  # Moon
    "02d": "\uf6c4",  # Cloud Sun
    "02n": "\uf6c3",  # Cloud Moon
    "03d": "\uf0c2",  # Cloud
    "03n": "\uf0c2",
    "09d": "\uf73d",  # Cloud Rain
    "09n": "\uf73d",
    "10d": "\uf740",  # Cloud Showers
    "10n": "\uf740",
    "13d": "\uf2dc",  # Snowflake
    "13n": "\uf2dc",
    "50d": "\uf75f",  # Fog
    "50n": "\uf75f",
}

# -------------------------------
# Helper function to draw icons
# -------------------------------
def draw_weather_icon(draw, code, x, y, size=48):
    glyph = OWM_TO_FA.get(code, "\uf0c2")  # default cloud
    icon_font = ImageFont.truetype(FA_PATH, size)
    draw.text((x, y), glyph, font=icon_font, fill=0)

# -------------------------------
# Fetch weather data
# -------------------------------
url = (
    f"https://api.openweathermap.org/data/3.0/onecall"
    f"?lat={LAT}&lon={LON}&exclude=minutely,daily,alerts&units=metric&appid={API_KEY}"
)
resp = requests.get(url, timeout=10)
data = resp.json()

current = data["current"]
hourly = data["hourly"][:48]  # next 48 hours

# -------------------------------
# Create image
# -------------------------------
img = Image.new("L", (W, H), 255)
draw = ImageDraw.Draw(img)

# Current temperature
temp_now = round(current["temp"])
draw.text((60, 80), f"{temp_now}°C", font=font_big, fill=0)
draw.text((60, 220), "Liebefeld", font=font_small, fill=0)

# Current weather icon
current_icon = current["weather"][0]["icon"]
draw_weather_icon(draw, current_icon, x=60, y=280, size=64)

# 48h forecast graph
temps = [round(h["temp"]) for h in hourly]
precip = [round(h.get("pop", 0)*100) for h in hourly]  # % chance

graph_x, graph_y = 60, 400
graph_w, graph_h = 640, 300
tmin, tmax = min(temps), max(temps)
scale = graph_h / max(1, tmax - tmin)

# Temperature line
points = [
    (graph_x + int(i * graph_w / 47),
     graph_y + graph_h - int((t - tmin) * scale))
    for i, t in enumerate(temps)
]
draw.rectangle((graph_x, graph_y, graph_x+graph_w, graph_y+graph_h), outline=0)
draw.line(points, fill=0, width=2)

# Precipitation bars
for i, p in enumerate(precip):
    bar_height = int(p / 100 * 50)
    x = graph_x + int(i * graph_w / 47)
    draw.line((x, graph_y - bar_height, x, graph_y), fill=0)

draw.text((graph_x, graph_y + graph_h + 10),
          "Next 48h temperature & precipitation", font=font_small, fill=0)

# Draw small icons above graph for each hour
icon_size = 24
for i, h in enumerate(hourly):
    icon_code = h["weather"][0]["icon"]
    x = graph_x + int(i * graph_w / 47) - icon_size // 2
    y = graph_y - 60
    draw_weather_icon(draw, icon_code, x, y, size=icon_size)

# -------------------------------
# Night inversion
# -------------------------------
now_hour = datetime.utcfromtimestamp(current["dt"]).hour
if now_hour < 6 or now_hour > 20:
    img = ImageOps.invert(img)

# -------------------------------
# Save output
# -------------------------------
os.makedirs("output", exist_ok=True)
img.save("output/weather.png")
print("✅ Weather image generated successfully")

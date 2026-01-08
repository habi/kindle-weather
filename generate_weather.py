import os
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Kindle PW2 resolution
W, H = 758, 1024

# Liebefeld coordinates
LAT, LON = 46.9326, 7.4176
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENWEATHER_API_KEY not set in environment variables!")

# Fetch current weather
current_url = (
    f"https://api.openweathermap.org/data/2.5/weather"
    f"?lat={LAT}&lon={LON}&units=metric&appid={API_KEY}"
)
current_data = requests.get(current_url, timeout=10).json()

temp_now = round(current_data["main"]["temp"])
precip_now = 0
if "rain" in current_data:
    precip_now = current_data["rain"].get("1h", 0)
elif "snow" in current_data:
    precip_now = current_data["snow"].get("1h", 0)

# Fetch hourly forecast (next 12 hours)
forecast_url = (
    f"https://api.openweathermap.org/data/2.5/forecast"
    f"?lat={LAT}&lon={LON}&units=metric&cnt=12&appid={API_KEY}"
)
forecast_data = requests.get(forecast_url, timeout=10).json()
temps = [round(hour["main"]["temp"]) for hour in forecast_data["list"]]

# Night detection
now = datetime.utcnow()
night = now.hour < 6 or now.hour > 20

# Create image
img = Image.new("L", (W, H), 255)
draw = ImageDraw.Draw(img)

# Fonts
font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
font_mid = ImageFont.truetype("DejaVuSans.ttf", 48)
font_small = ImageFont.truetype("DejaVuSans.ttf", 36)

# Current temperature & city
draw.text((60, 80), f"{temp_now}°C", font=font_big, fill=0)
draw.text((60, 220), "Liebefeld", font=font_mid, fill=0)
draw.text((60, 280), now.strftime("%H:%M UTC"), font=font_small, fill=120)

# Precipitation bar
draw.rectangle((60, 340, 660, 380), outline=0, width=2)
bar_width = min(int(precip_now * 50), 600)
draw.rectangle((60, 340, 60 + bar_width, 380), fill=0)
draw.text((60, 390), f"Precip {precip_now:.1f} mm", font=font_small, fill=0)

# 12-hour temperature graph
if temps:
    tmin, tmax = min(temps), max(temps)
    graph_x, graph_y = 60, 460
    graph_w, graph_h = 640, 220
    scale = graph_h / max(1, tmax - tmin)
    points = [
        (graph_x + int(i * graph_w / max(1, len(temps)-1)),
         graph_y + graph_h - int((t - tmin) * scale))
        for i, t in enumerate(temps)
    ]
    draw.rectangle((graph_x, graph_y, graph_x+graph_w, graph_y+graph_h), outline=0)
    draw.line(points, fill=0, width=3)
    draw.text((graph_x, graph_y+graph_h+10), "Next 12h temp trend", font=font_small, fill=0)

# Invert for night
if night:
    img = ImageOps.invert(img)

# Save
img.save("output/weather.png")
print("✅ Weather image generated successfully")

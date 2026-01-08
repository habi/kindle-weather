from meteostat import Point, Hourly
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Liebefeld, Switzerland
location = Point(46.9326, 7.4176)

data = Hourly(location).fetch().iloc[-1]

temp = round(data['temp'])
desc = "Weather"
time = datetime.utcnow().strftime("%H:%M UTC")

img = Image.new("L", (758, 1024), 255)  # PW2 resolution
draw = ImageDraw.Draw(img)

font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
font_small = ImageFont.truetype("DejaVuSans.ttf", 42)

draw.text((60, 100), f"{temp}°C", font=font_big, fill=0)
draw.text((60, 260), "Liebefeld", font=font_small, fill=0)
draw.text((60, 320), f"Updated {time}", font=font_small, fill=120)

img.save("output/weather.png")

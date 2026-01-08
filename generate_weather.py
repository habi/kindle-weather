from PIL import Image, ImageDraw, ImageFont
import requests
import datetime

API_KEY = os.environ["OPENWEATHER_API_KEY"]
CITY = "Liebefeld"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&units=metric&appid={API_KEY}"

data = requests.get(URL).json()

temp = round(data["main"]["temp"])
desc = data["weather"][0]["description"].title()
now = datetime.datetime.now().strftime("%H:%M")

img = Image.new("L", (758, 1024), 255)  # PW2 resolution
draw = ImageDraw.Draw(img)

font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
font_small = ImageFont.truetype("DejaVuSans.ttf", 40)

draw.text((50, 80), f"{temp}°C", font=font_big, fill=0)
draw.text((50, 230), desc, font=font_small, fill=0)
draw.text((50, 300), f"Updated {now}", font=font_small, fill=120)

img.save("output/weather.png")

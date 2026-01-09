import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

class WeatherKindleImage:
    def __init__(self, api_key, city="London", country_code="UK"):
        self.api_key = api_key
        self.city = city
        self.country_code = country_code
        # Kindle Paperwhite dimensions (or adjust for your model)
        self.width = 758
        self.height = 1024
        
    def get_weather_data(self):
        """Fetch current weather and forecast from OpenWeatherMap"""
        # Current weather
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city},{self.country_code}&appid={self.api_key}&units=metric"
        current_response = requests.get(current_url)
        current_data = current_response.json()
        
        # 5-day forecast
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city},{self.country_code}&appid={self.api_key}&units=metric"
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()
        
        return current_data, forecast_data
    
    def create_weather_image(self, output_path="output/weather.png"):
        """Generate PNG image optimized for Kindle display"""
        # Get weather data
        current, forecast = self.get_weather_data()
        
        # Create grayscale image (Kindle displays work best with grayscale)
        img = Image.new('L', (self.width, self.height), color=255)
        draw = ImageDraw.Draw(img)
        
        # Try to use default font, or create a basic one
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        y_offset = 30
        
        # Title with location and date
        title = f"Weather - {current['name']}"
        draw.text((30, y_offset), title, fill=0, font=title_font)
        y_offset += 60
        
        date_str = datetime.now().strftime("%A, %B %d, %Y")
        draw.text((30, y_offset), date_str, fill=0, font=small_font)
        y_offset += 50
        
        # Draw separator line
        draw.line([(30, y_offset), (self.width - 30, y_offset)], fill=0, width=2)
        y_offset += 30
        
        # Current Weather Section
        draw.text((30, y_offset), "CURRENT", fill=0, font=header_font)
        y_offset += 50
        
        temp = current['main']['temp']
        feels_like = current['main']['feels_like']
        description = current['weather'][0]['description'].capitalize()
        humidity = current['main']['humidity']
        wind_speed = current['wind']['speed']
        
        # Temperature (large)
        temp_text = f"{temp:.1f}°C"
        draw.text((30, y_offset), temp_text, fill=0, font=title_font)
        y_offset += 55
        
        # Weather description
        draw.text((30, y_offset), description, fill=0, font=text_font)
        y_offset += 40
        
        # Details
        details = [
            f"Feels like: {feels_like:.1f}°C",
            f"Humidity: {humidity}%",
            f"Wind: {wind_speed} m/s"
        ]
        
        for detail in details:
            draw.text((30, y_offset), detail, fill=0, font=small_font)
            y_offset += 35
        
        y_offset += 20
        draw.line([(30, y_offset), (self.width - 30, y_offset)], fill=0, width=2)
        y_offset += 30
        
        # Forecast Section
        draw.text((30, y_offset), "5-DAY OUTLOOK", fill=0, font=header_font)
        y_offset += 50
        
        # Process forecast data (get one per day at noon)
        daily_forecasts = {}
        for item in forecast['list']:
            date = datetime.fromtimestamp(item['dt']).date()
            hour = datetime.fromtimestamp(item['dt']).hour
            
            # Get forecast around noon for each day
            if date not in daily_forecasts and 11 <= hour <= 14:
                daily_forecasts[date] = item
                
            if len(daily_forecasts) >= 5:
                break
        
        # Display forecast
        for date, data in list(daily_forecasts.items())[:5]:
            day_name = date.strftime("%a, %b %d")
            temp_min = data['main']['temp_min']
            temp_max = data['main']['temp_max']
            desc = data['weather'][0]['description'].capitalize()
            
            draw.text((30, y_offset), day_name, fill=0, font=text_font)
            y_offset += 30
            
            forecast_line = f"  {temp_min:.0f}°C - {temp_max:.0f}°C | {desc}"
            draw.text((30, y_offset), forecast_line, fill=0, font=small_font)
            y_offset += 40
        
        # Footer with update time
        y_offset = self.height - 50
        draw.line([(30, y_offset), (self.width - 30, y_offset)], fill=0, width=1)
        y_offset += 15
        update_time = datetime.now().strftime("%I:%M %p")
        draw.text((30, y_offset), f"Updated: {update_time}", fill=0, font=small_font)
        
        # Save image
        img.save(output_path, 'PNG')
        print(f"Weather image saved to {output_path}")
        return output_path

# Usage
if __name__ == "__main__":
    # Get API key from environment variable
    API_KEY = os.environ.get("OPENWEATHER_API_KEY")
    
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable not set")
    
    # Create weather image (customize city as needed)
    weather = WeatherKindleImage(
        api_key=API_KEY,
        city="Bern",
        country_code="CH"
    )
    os.makedirs("output", exist_ok=True)    
    weather.create_weather_image(output_path="output/weather.png")
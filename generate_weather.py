import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo
import os

class WeatherKindleImage:
    def __init__(self, api_key, city="London", country_code="UK"):
        self.api_key = api_key
        self.city = city
        self.country_code = country_code
        # Kindle Paperwhite dimensions (or adjust for your model)
        self.width = 758
        self.height = 1024
        
        # German day names
        self.day_names = {
            'Monday': 'Montag',
            'Tuesday': 'Dienstag',
            'Wednesday': 'Mittwoch',
            'Thursday': 'Donnerstag',
            'Friday': 'Freitag',
            'Saturday': 'Samstag',
            'Sunday': 'Sonntag'
        }
        
        # German month names
        self.month_names = {
            'January': 'Januar',
            'February': 'Februar',
            'March': 'März',
            'April': 'April',
            'May': 'Mai',
            'June': 'Juni',
            'July': 'Juli',
            'August': 'August',
            'September': 'September',
            'October': 'Oktober',
            'November': 'November',
            'December': 'Dezember'
        }
        
    def get_weather_data(self):
        """Fetch current weather and forecast from OpenWeatherMap"""
        # Current weather
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city},{self.country_code}&appid={self.api_key}&units=metric&lang=de"
        current_response = requests.get(current_url)
        current_data = current_response.json()
        
        # 5-day forecast
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city},{self.country_code}&appid={self.api_key}&units=metric&lang=de"
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()
        
        return current_data, forecast_data
    
    def get_weather_icon(self, icon_code):
        """Download weather icon from OpenWeatherMap"""
        # Use 2x size for better quality
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        response = requests.get(icon_url)
        
        if response.status_code == 200:
            from io import BytesIO
            icon_image = Image.open(BytesIO(response.content))
            return icon_image
        return None
    
    def paste_weather_icon(self, img, icon_code, x, y, size=80):
        """Download and paste weather icon, convert to grayscale for Kindle"""
        icon = self.get_weather_icon(icon_code)
        
        if icon:
            # Resize icon to desired size
            icon = icon.resize((size, size), Image.Resampling.LANCZOS)
            
            # Convert to grayscale
            icon_gray = icon.convert('L')
            
            # If icon has transparency, handle it by making transparent areas white
            if icon.mode == 'RGBA' or 'transparency' in icon.info:
                # Create a white background
                background = Image.new('L', (size, size), 255)
                # Paste icon on white background
                icon_rgba = icon.convert('RGBA')
                background.paste(icon_gray, (0, 0), icon_rgba.split()[3])  # Use alpha channel as mask
                icon_gray = background
            
            # Paste the grayscale icon onto the main image
            img.paste(icon_gray, (x, y))
        
        return img
    
    def translate_date(self, date_str):
        """Translate English date to German"""
        for eng, ger in self.day_names.items():
            date_str = date_str.replace(eng, ger)
        for eng, ger in self.month_names.items():
            date_str = date_str.replace(eng, ger)
        return date_str
    
    def get_timezone(self):
        """Return the timezone string based on the country code."""
        country_timezones = {
            'CH': 'Europe/Zurich',
            'DE': 'Europe/Berlin',
            'AT': 'Europe/Vienna',
            'FR': 'Europe/Paris',
            'IT': 'Europe/Rome',
            'UK': 'Europe/London',
            'GB': 'Europe/London',
            'US': 'America/New_York',
            'CA': 'America/Toronto',
            # Add more as needed
        }
        return country_timezones.get(self.country_code.upper(), 'UTC')
    
    def create_weather_image(self, output_path="output/weather.png"):
        """Generate PNG image optimized for Kindle display"""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
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
        title = f"Wetter - {current['name']}"
        draw.text((30, y_offset), title, fill=0, font=title_font)
        y_offset += 60
        
        # Use timezone based on country code
        tz = ZoneInfo(self.get_timezone())
        now_local = datetime.now(tz)
        date_str = now_local.strftime("%A, %d. %B %Y")
        date_str = self.translate_date(date_str)
        draw.text((30, y_offset), date_str, fill=0, font=small_font)
        y_offset += 50
        
        # Draw separator line
        draw.line([(30, y_offset), (self.width - 30, y_offset)], fill=0, width=2)
        y_offset += 30
        
        # Current Weather Section
        draw.text((30, y_offset), "AKTUELL", fill=0, font=header_font)
        y_offset += 50
        
        temp = current['main']['temp']
        feels_like = current['main']['feels_like']
        description = current['weather'][0]['description'].capitalize()
        humidity = current['main']['humidity']
        wind_speed = current['wind']['speed']
        icon_code = current['weather'][0]['icon']
        
        # Draw weather icon for current weather
        icon_x = self.width - 130
        icon_y = y_offset - 10
        img = self.paste_weather_icon(img, icon_code, icon_x, icon_y, size=100)
        
        # Temperature (large)
        temp_text = f"{temp:.1f}°C"
        draw.text((30, y_offset), temp_text, fill=0, font=title_font)
        y_offset += 55
        
        # Weather description
        draw.text((30, y_offset), description, fill=0, font=text_font)
        y_offset += 40
        
        # Details
        details = [
            f"Gefühlt: {feels_like:.1f}°C",
            f"Luftfeuchtigkeit: {humidity}%",
            f"Wind: {wind_speed} m/s"
        ]
        
        for detail in details:
            draw.text((30, y_offset), detail, fill=0, font=small_font)
            y_offset += 35
        
        y_offset += 20
        draw.line([(30, y_offset), (self.width - 30, y_offset)], fill=0, width=2)
        y_offset += 30
        
        # Forecast Section
        draw.text((30, y_offset), "5-TAGE-VORHERSAGE", fill=0, font=header_font)
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
            day_name = date.strftime("%a, %d. %b")
            # Translate abbreviated day names
            day_abbr = {
                'Mon': 'Mo', 'Tue': 'Di', 'Wed': 'Mi', 
                'Thu': 'Do', 'Fri': 'Fr', 'Sat': 'Sa', 'Sun': 'So'
            }
            month_abbr = {
                'Jan': 'Jan', 'Feb': 'Feb', 'Mar': 'Mär', 'Apr': 'Apr',
                'May': 'Mai', 'Jun': 'Jun', 'Jul': 'Jul', 'Aug': 'Aug',
                'Sep': 'Sep', 'Oct': 'Okt', 'Nov': 'Nov', 'Dec': 'Dez'
            }
            for eng, ger in day_abbr.items():
                day_name = day_name.replace(eng, ger)
            for eng, ger in month_abbr.items():
                day_name = day_name.replace(eng, ger)
            
            temp_min = data['main']['temp_min']
            temp_max = data['main']['temp_max']
            desc = data['weather'][0]['description'].capitalize()
            icon_code = data['weather'][0]['icon']
            
            # Draw small weather icon
            img = self.paste_weather_icon(img, icon_code, 30, y_offset, size=50)
            
            draw.text((85, y_offset), day_name, fill=0, font=text_font)
            y_offset += 30
            
            forecast_line = f"  {temp_min:.0f}°C - {temp_max:.0f}°C | {desc}"
            draw.text((85, y_offset), forecast_line, fill=0, font=small_font)
            y_offset += 45
        
        # Footer with update time
        y_offset = self.height - 50
        draw.line([(30, y_offset), (self.width - 30, y_offset)], fill=0, width=1)
        y_offset += 15
        update_time = now_local.strftime("%H:%M")
        draw.text((30, y_offset), f"Aktualisiert: {update_time} Uhr", fill=0, font=small_font)
        
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
        city="Bern",  # Change to your city
        country_code="CH"  # Change to your country code
    )
    
    weather.create_weather_image()
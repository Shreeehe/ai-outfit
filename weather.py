# weather.py
import requests
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use os.environ directly

class WeatherService:
    def __init__(self):
        # Get API key from environment or use default
        self.API_KEY = os.getenv('OPENWEATHER_API_KEY', 'ef785c660c0f2875d4b30d8eb775fb0c')
        self.default_city = os.getenv('DEFAULT_CITY', 'Theni')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city=None):
        """
        Get current weather for a city
        Returns: dict with temp, condition, description, humidity
        """
        if city is None:
            city = self.default_city
            
        try:
            params = {
                'q': city,
                'appid': self.API_KEY,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'temp': data['main']['temp'],
                    'condition': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'feels_like': data['main']['feels_like'],
                    'icon': data['weather'][0]['icon'],
                    'city': city
                }
            else:
                return self._get_default_weather()
                
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._get_default_weather()
    
    def _get_default_weather(self):
        """Fallback weather data"""
        return {
            'temp': 28,
            'condition': 'Clear',
            'description': 'sunny',
            'humidity': 60,
            'feels_like': 30,
            'icon': '01d',
            'city': self.default_city
        }
    
    def get_weather_icon_emoji(self, condition):
        """Convert weather condition to emoji"""
        emoji_map = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Fog': '🌫️'
        }
        return emoji_map.get(condition, '🌤️')

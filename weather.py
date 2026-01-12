# weather.py
import requests

class WeatherService:
    def __init__(self):
        # Free API key from OpenWeatherMap
        # Sign up at: https://openweathermap.org/api
        self.API_KEY = ""  # Replace this!
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city="Tiruppur"):
        """
        Get current weather for a city
        Returns: dict with temp, condition, description, humidity
        """
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
                    'condition': data['weather'][0]['main'],  # Rain, Clear, Clouds, etc.
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'feels_like': data['main']['feels_like'],
                    'icon': data['weather'][0]['icon']
                }
            else:
                # Fallback if API fails
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
            'icon': '01d'
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


# Quick setup instructions:
"""
To get FREE API key:
1. Go to: https://openweathermap.org/api
2. Click "Sign Up"
3. Verify email
4. Go to API Keys section
5. Copy your API key
6. Replace "YOUR_API_KEY_HERE" above

For now, it will use default weather (28°C, Sunny) as fallback
"""

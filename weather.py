# weather.py
import requests
import os

def get_secret(key, default=None):
    """Get secret from Streamlit secrets or environment"""
    try:
        import streamlit as st
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets'):
            if 'api_keys' in st.secrets and key in st.secrets['api_keys']:
                return st.secrets['api_keys'][key]
            if 'settings' in st.secrets and key in st.secrets['settings']:
                return st.secrets['settings'][key]
    except:
        pass
    
    # Fall back to environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    return os.getenv(key, default)

class WeatherService:
    def __init__(self):
        # Get API key from Streamlit secrets or environment
        self.API_KEY = get_secret('OPENWEATHER_API_KEY', 'ef785c660c0f2875d4b30d8eb775fb0c')
        self.default_city = get_secret('DEFAULT_CITY', 'Theni')
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
            
            response = requests.get(self.base_url, params=params, timeout=5)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'temp': round(data['main']['temp']),
                    'condition': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'feels_like': round(data['main']['feels_like']),
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
            'Fog': '🌫️',
            'Haze': '🌫️'
        }
        return emoji_map.get(condition, '🌤️')

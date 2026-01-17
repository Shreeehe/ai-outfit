# routers/weather.py - Weather API
from fastapi import APIRouter
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.schemas import WeatherResponse

router = APIRouter(prefix="/api", tags=["weather"])

# Lazy load weather service
_weather_service = None

def get_weather_service():
    global _weather_service
    if _weather_service is None:
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, parent_dir)
        from weather import WeatherService
        _weather_service = WeatherService()
    return _weather_service

@router.get("/weather", response_model=WeatherResponse)
def get_weather(city: str = None):
    """Get current weather"""
    ws = get_weather_service()
    weather = ws.get_weather(city)
    weather['emoji'] = ws.get_weather_icon_emoji(weather.get('condition', 'Clear'))
    return WeatherResponse(**weather)

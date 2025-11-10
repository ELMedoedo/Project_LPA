import requests
from typing import Dict, Any
from app.config import API_KEY , BASE_URL


def get_weather_data(city: str) -> Dict[str, Any]:

    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',  # Цельсия
        'lang': 'ru'        
    }
    
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()

        
        return _format_weather_data(data)
    elif response.status_code == 404:
        raise ValueError(f"Город '{city}' не найден")
    elif response.status_code == 401:
        raise ValueError("Неверный API токен")
    else:
        response.raise_for_status()


def _format_weather_data(data: Dict) -> Dict[str, Any]:
    """Форматирование данных о погоде для API response"""
    return {
        "city": data['name'],
        "country": data['sys']['country'],
        "temperature": data['main']['temp'],
        "feels_like": data['main']['feels_like'],
        "description": data['weather'][0]['description'],
        "humidity": data['main']['humidity'],
        "pressure": data['main']['pressure'],
        "wind_speed": data['wind']['speed'],
        "visibility": data.get('visibility', 'N/A')
    }
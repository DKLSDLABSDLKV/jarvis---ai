"""
Weather Service Module for Secure Intelligent Desktop Assistant
Fetches real-time weather using OpenWeather API
"""

import requests
import logging
from pathlib import Path
import sys

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class WeatherService:
    """
    Weather Service
    Fetches weather data from OpenWeather API
    """
    
    def __init__(self, api_key=None):
        """
        Initialize weather service
        
        Args:
            api_key: OpenWeather API key
        """
        self.logger = logging.getLogger('DesktopAssistant.Weather')
        self.api_key = api_key or config.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if self.api_key == "YOUR_API_KEY_HERE":
            self.logger.warning("OpenWeather API key not configured")
        
        self.logger.info("Weather Service initialized")
    
    def get_weather(self, city):
        """
        Get current weather for a city
        
        Args:
            city: City name
            
        Returns:
            Dictionary with weather data
        """
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            self.logger.error("API key not configured")
            return None
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_weather_data(data)
            elif response.status_code == 404:
                self.logger.warning(f"City not found: {city}")
                return None
            else:
                self.logger.error(f"Weather API error: {response.status_code}")
                return None
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return None
    
    def get_weather_by_coords(self, lat, lon):
        """
        Get weather by coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with weather data
        """
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            return None
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_weather_data(data)
            else:
                return None
        
        except Exception as e:
            self.logger.error(f"Error getting weather: {e}")
            return None
    
    def _parse_weather_data(self, data):
        """
        Parse weather API response
        
        Args:
            data: API response data
            
        Returns:
            Parsed weather dictionary
        """
        try:
            weather = data['weather'][0]
            main = data['main']
            wind = data.get('wind', {})
            sys_data = data.get('sys', {})
            
            return {
                'city': data['name'],
                'country': sys_data.get('country', ''),
                'temperature': round(main['temp'], 1),
                'feels_like': round(main['feels_like'], 1),
                'temp_min': round(main['temp_min'], 1),
                'temp_max': round(main['temp_max'], 1),
                'humidity': main['humidity'],
                'pressure': main['pressure'],
                'description': weather['description'],
                'main': weather['main'],
                'icon': weather['icon'],
                'wind_speed': wind.get('speed', 0),
                'wind_deg': wind.get('deg', 0),
                'visibility': data.get('visibility', 0),
                'clouds': data.get('clouds', {}).get('all', 0),
                'sunrise': sys_data.get('sunrise', 0),
                'sunset': sys_data.get('sunset', 0),
                'timezone': data.get('timezone', 0)
            }
        
        except Exception as e:
            self.logger.error(f"Error parsing weather data: {e}")
            return None
    
    def get_forecast(self, city, days=5):
        """
        Get weather forecast
        
        Args:
            city: City name
            days: Number of days (1-5)
            
        Returns:
            List of forecast data
        """
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            return None
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 3-hour intervals
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_forecast_data(data)
            else:
                return None
        
        except Exception as e:
            self.logger.error(f"Error getting forecast: {e}")
            return None
    
    def _parse_forecast_data(self, data):
        """Parse forecast API response"""
        try:
            forecasts = []
            
            for item in data.get('list', []):
                forecasts.append({
                    'datetime': item['dt_txt'],
                    'temperature': round(item['main']['temp'], 1),
                    'feels_like': round(item['main']['feels_like'], 1),
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description'],
                    'main': item['weather'][0]['main'],
                    'icon': item['weather'][0]['icon'],
                    'wind_speed': item['wind'].get('speed', 0)
                })
            
            return forecasts
        
        except Exception as e:
            self.logger.error(f"Error parsing forecast: {e}")
            return None
    
    def get_weather_report(self, city):
        """
        Get weather report for a city
        
        Args:
            city: City name
            
        Returns:
            Weather report string
        """
        weather = self.get_weather(city)
        
        if not weather:
            return f"Sorry, I couldn't get weather information for {city}."
        
        report = (
            f"Weather in {weather['city']}, {weather['country']}: "
            f"Temperature is {weather['temperature']} degrees Celsius. "
            f"It feels like {weather['feels_like']} degrees. "
            f"Current conditions: {weather['description']}. "
            f"Humidity is {weather['humidity']} percent. "
        )
        
        return report
    
    def speak_weather(self, city, voice_engine=None):
        """
        Speak weather report
        
        Args:
            city: City name
            voice_engine: Voice engine for TTS
            
        Returns:
            Weather report string
        """
        report = self.get_weather_report(city)
        
        if voice_engine:
            voice_engine.speak(report)
        
        return report
    
    def get_clothing_recommendation(self, temperature):
        """
        Get clothing recommendation based on temperature
        
        Args:
            temperature: Temperature in Celsius
            
        Returns:
            Recommendation string
        """
        if temperature < 0:
            return "It's very cold! Wear a heavy winter coat, boots, and warm accessories."
        elif temperature < 10:
            return "It's cold. Wear a warm jacket, sweater, and long pants."
        elif temperature < 18:
            return "It's cool. A light jacket or sweater is recommended."
        elif temperature < 24:
            return "The weather is pleasant. Wear light clothing."
        elif temperature < 30:
            return "It's warm. Wear comfortable, light clothes."
        else:
            return "It's hot! Wear very light, breathable clothing."


# ============================================
# Main function for testing
# ============================================

def test_weather_service():
    """Test weather service"""
    print("Testing Weather Service...")
    
    service = WeatherService()
    
    # Test with a city
    city = "London"
    
    print(f"\nGetting weather for {city}...")
    weather = service.get_weather(city)
    
    if weather:
        print("\n" + "="*60)
        print(f"Weather in {weather['city']}:")
        print("="*60)
        print(f"  Temperature: {weather['temperature']}°C")
        print(f"  Feels like: {weather['feels_like']}°C")
        print(f"  Description: {weather['description']}")
        print(f"  Humidity: {weather['humidity']}%")
        print(f"  Wind speed: {weather['wind_speed']} m/s")
        
        # Get report
        print("\n" + "="*60)
        print("Weather Report:")
        print("="*60)
        report = service.get_weather_report(city)
        print(report)
        
        # Clothing recommendation
        print("\nClothing recommendation:")
        print(service.get_clothing_recommendation(weather['temperature']))
    else:
        print("Weather data not available (check API key)")
    
    return service


if __name__ == "__main__":
    test_weather_service()

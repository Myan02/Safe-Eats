"""Address geocoding with caching."""
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from functools import lru_cache
import logging

class GeoService:
    """Geocoding service with rate limiting and caching."""
    
    def __init__(self):
        """Initialize geocoder with rate limiter."""
        self.geolocator = Nominatim(user_agent="nyc_restaurant_locator")
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)

    @lru_cache(maxsize=1024)
    def geocode_address(self, address):
        """Convert address to (lat, lon) with caching."""
        try:
            location = self.geocode(f"{address}, New York, NY", timeout=10)
            return (location.latitude, location.longitude) if location else (None, None)
        except Exception as e:
            logging.error(f"Geocoding error: {str(e)}")
            return None, None
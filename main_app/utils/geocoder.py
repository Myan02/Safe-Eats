from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import logging
from flask import current_app
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Geocoder:
    def __init__(self, clean_data_path):
        self.df = pd.read_csv(clean_data_path)
        self._validate_data()
        self.geolocator = Nominatim(
            user_agent=current_app.config.get('GEOCODE_USER_AGENT', 'address_app'),
            timeout=current_app.config.get('GEOCODE_TIMEOUT', 10)
        )

    def _validate_data(self):
        required = ['dba', 'building', 'street', 'boro', 'zipcode', 'latitude', 'longitude']
        if not all(col in self.df.columns for col in required):
            raise ValueError("Missing required columns")
        
        if self.df[['latitude', 'longitude']].isna().any().any():
            raise ValueError("Clean data contains NaN coordinates")

    def find_nearby(self, target_address, radius_km=1, limit=None):
        try:
            # Validate input
            if not target_address or not isinstance(target_address, str):
                raise ValueError("Invalid target address")
            
            # Geocode target
            location = self.geolocator.geocode(target_address)
            if not location:
                return []
                
            target_coords = (location.latitude, location.longitude)
            results = []
            
            # Calculate distances safely
            for _, row in self.df.iterrows():
                try:
                    lat, lon = float(row['latitude']), float(row['longitude'])
                    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                        continue
                        
                    distance = geodesic(target_coords, (lat, lon)).kilometers
                    if distance <= radius_km:
                        results.append({
                            'dba': row['dba'],
                            'building': row['building'],
                            'street': row['street'],
                            'boro': row['boro'],
                            'zipcode': row['zipcode'],
                            'distance': round(distance, 2)
                        })
                except (ValueError, TypeError) as e:
                    logger.debug(f"Skipping row {_}: {str(e)}")
                    continue
            
            # Sort and limit
            results.sort(key=lambda x: x['distance'])
            return results[:limit] if limit else results
            
        except Exception as e:
            logger.error(f"Geocoding failed: {str(e)}")
            return []
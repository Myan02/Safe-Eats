"""Restaurant data loading and spatial operations."""
import pandas as pd
from scipy.spatial import cKDTree
from geopy.distance import geodesic
import logging
from pathlib import Path
from main_app.config import FlaskConfig

class DataService:
    """Service for restaurant data loading and queries."""
    
    def __init__(self, data_path=None):
        """Initialize with optional data path override."""
        self.data_path = data_path or (FlaskConfig.DATA_DIR / "restaurant_data.csv")
        self.data = None
        self.spatial_index = None
        self.load_data()

    def load_data(self):
        """Load and preprocess restaurant data."""
        try:
            parquet_path = self.data_path.with_suffix('.parquet')
            if parquet_path.exists():
                df = pd.read_parquet(parquet_path)
            else:
                df = pd.read_csv(self.data_path, dtype=self._get_dtypes())
                df.to_parquet(parquet_path)
            
            df = self._clean_data(df)
            valid_coords = df[['Latitude', 'Longitude']].dropna().values
            self.spatial_index = cKDTree(valid_coords)
            self.data = df
            
        except Exception as e:
            logging.error(f"Data loading failed: {str(e)}")
            raise

    def _get_dtypes(self):
        """Return column dtype specifications."""
        return {
            'CAMIS': 'string', 'DBA': 'string', 'BORO': 'string',
            'BUILDING': 'string', 'STREET': 'string', 'ZIPCODE': 'string',
            'PHONE': 'string', 'CUISINE DESCRIPTION': 'string',
            'VIOLATION DESCRIPTION': 'string', 'GRADE': 'string',
            'SCORE': 'float32', 'Latitude': 'float32', 'Longitude': 'float32',
            'INSPECTION DATE': 'string'
        }

    def _clean_data(self, df):
        """Clean and filter raw data."""
        df = df.replace(r'^\s*$', None, regex=True)
        df = df.dropna(subset=['Latitude', 'Longitude', 'DBA'])
        nyc_bbox = (40.4, -74.5, 41.0, -73.5)
        df = df[
            (df['Latitude'].between(nyc_bbox[0], nyc_bbox[2])) & 
            (df['Longitude'].between(nyc_bbox[1], nyc_bbox[3]))
        ]
        df['INSPECTION DATE'] = pd.to_datetime(df['INSPECTION DATE'], errors='coerce')
        return df[df['INSPECTION DATE'] > pd.to_datetime('2000-01-01')]

    def get_nearby_restaurants(self, lat, lon, max_distance=1):
        """Find restaurants within max_distance miles."""
        # Get initial nearby restaurants
        if self.spatial_index:
            radius_deg = max_distance / 69  # Approximate degrees per mile
            idx = self.spatial_index.query_ball_point([lat, lon], radius_deg)
            nearby = self.data.iloc[idx].copy()
        else:
            nearby = self.data.copy()
        
        nearby['distance'] = [
            geodesic((lat, lon), (row['Latitude'], row['Longitude'])).miles
             for _, row in nearby.iterrows()
         ]
        
        # Filter and return
        return nearby[nearby['distance'] <= max_distance].copy()
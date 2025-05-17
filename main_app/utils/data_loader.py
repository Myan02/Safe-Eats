"""Restaurant data loading and spatial operations."""
import pandas as pd
import geopandas as gpd
from matplotlib import colors
from scipy.spatial import cKDTree
from geopy.distance import geodesic
import logging
from pathlib import Path
from main_app.config import FlaskConfig


class SpatialService:
    """Service for NYC zipcode border geometries"""
    
    def __init__(self, data_path=None):
        """Initialize with optional data path override"""
        self.data_path = data_path or (FlaskConfig.DATA_DIR / "zipcode_border_data.geojson")
        self.data = None
        self.load_data()
        
    def load_data(self):
        """Load and preprocess zipcode geojson data"""
        try:
            parquet_path = self.data_path.with_suffix('.parquet')
            if parquet_path.exists():
                gdf = gpd.read_parquet(parquet_path)
            else:
                gdf = gpd.read_file(self.data_path)
                gdf.to_parquet(parquet_path)
            
            gdf = self._clean_data(gdf)
            self.data = gdf
                
        except Exception as e:
            logging.error(f"GeoJSON data loading Failed: {str(e)}")
            raise
        
    def _clean_data(self, gdf):
        """Drop zipcodes that do not exist"""
        gdf = gdf[gdf['postalCode'] < str(99999)]
        return gdf


class DataService:
    """Service for restaurant data loading and queries."""
    
    def __init__(self, data_path=None):
        """Initialize with optional data path override."""
        self.data_path = data_path or (FlaskConfig.DATA_DIR / "restaurant_data.csv")
        self.data = None
        self.unique_restaurants = None
        self.mean_grades = None
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
            
            """Set Data"""
            df = self._clean_data(df)
            valid_coords = df[['Latitude', 'Longitude']].dropna().values
            self.spatial_index = cKDTree(valid_coords)
            self.data = df
            
            """Get the most recent record of each restaurant"""
            df = self._get_unique(df)
            self.unique_restaurants = df.to_dict(orient='records')
            
            """Get the mean restaurant grade of each zipcode"""
            df = self._get_means(df)
            self.mean_grades = df.to_dict(orient='records')
            
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
    
    def _get_unique(self, df):
        """Get the most recent record of each restaurant"""
        df = df[['DBA', 'BORO', 'ZIPCODE', 'CUISINE DESCRIPTION', 'INSPECTION DATE', 'GRADE', 'Latitude', 'Longitude']]
        df = df.sort_values(by='INSPECTION DATE', ascending=False)
        df = df.drop_duplicates(subset=['DBA'], keep='first')
        return df.sort_values(by='DBA', ascending=True)
    
    def _get_means(self, df: pd.DataFrame):
        """Get mean restaurant grade per zipcode and update spatial data"""
        grade_to_value = {
            'A': 1,
            'B': 2,
            'C': 3,
        }
        
        # Get means per zip
        df['GRADE'] = df['GRADE'].str.upper()
        df = df[df['GRADE'].isin(['A', 'B', 'C'])]
        means_df = df[['ZIPCODE', 'GRADE']].copy()
        means_df['MEAN'] = means_df['GRADE'].map(grade_to_value)
        means_df = means_df.groupby('ZIPCODE')['MEAN'].mean().reset_index()
        
        # Map zip to color
        cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['blue', 'green', 'orange'])
        norm = colors.Normalize(vmin=1, vmax=3)
        means_df['COLOR'] = means_df['MEAN'].apply(
            lambda x: colors.rgb2hex(tuple(cmap(norm(x))[:3]))
        )
        
        # Convert all to str to make types more consistent
        means_df = means_df.astype(str)
        
        # Merge with zipcode geoms and export
        spatial_service = SpatialService()
        spatial_df = spatial_service.data.merge(
            means_df, left_on='postalCode', right_on='ZIPCODE', how='left'
        )
        spatial_df.drop(columns=['ZIPCODE'], inplace=True)
        spatial_df.to_file(FlaskConfig.DATA_DIR / "zipcode_border_grades.geojson", driver='GeoJSON')
        
        return means_df
        
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
from flask import Blueprint, render_template, request, jsonify, current_app
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import os
import logging
import numpy as np

bp = Blueprint('main', __name__)

def get_data_path():
    """Get the absolute path to the data file."""
    return os.path.join(current_app.root_path, '../data/restaurant_data.csv')

def load_data():
    """Load and clean restaurant data with proper type handling."""
    data_path = get_data_path()
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}")
    
    try:
        # Load with explicit dtype to prevent type issues
        df = pd.read_csv(
            data_path,
            dtype={
                'CAMIS': str,
                'ZIPCODE': str,
                'PHONE': str,
                'SCORE': float,
                'Latitude': float,
                'Longitude': float
            },
            keep_default_na=False,
            na_values=['', 'NA', 'N/A', 'NaN', 'null']
        )
        
        # Convert empty strings to None
        df = df.replace(r'^\s*$', None, regex=True)
        
        # Clean data
        df = df.dropna(subset=['Latitude', 'Longitude', 'DBA'])
        df = df[
            (df['Latitude'].between(40.4, 41.0)) & 
            (df['Longitude'].between(-74.5, -73.5))
        ]
        
        return df
    
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        raise

def geocode_address(address):
    """Convert address to coordinates with error handling."""
    geolocator = Nominatim(user_agent="nyc_restaurant_locator")
    try:
        location = geolocator.geocode(f"{address}, New York, NY", timeout=10)
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception as e:
        logging.error(f"Geocoding error: {str(e)}")
        return None, None

def clean_for_json(value):
    """Convert pandas/numpy types to JSON-compatible types."""
    if pd.isna(value) or value is None:
        return None
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return value.isoformat()
    return value

@bp.route('/')
def index():
    """Render main search page."""
    return render_template('index.html', mapbox_token=current_app.config['MAPBOX_TOKEN'])

@bp.route('/about')
def about():
    """Render about page."""
    return render_template('about.html')

@bp.route('/search', methods=['POST'])
def search():
    """Handle search requests with comprehensive error handling."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        address = data.get('address', '').strip()
        
        if not address:
            return jsonify({'error': 'Address cannot be empty'}), 400
        
        # Geocode address
        lat, lon = geocode_address(address)
        if not lat or not lon:
            return jsonify({'error': 'Could not locate address'}), 400
        
        # Find nearby restaurants
        df = load_data()
        df['distance'] = df.apply(
            lambda row: geodesic((lat, lon), (row['Latitude'], row['Longitude'])).miles,
            axis=1
        )
        nearby = df[df['distance'] <= 1].sort_values('distance').head(10)
        
        # Prepare JSON-compatible results
        results = []
        for _, row in nearby.iterrows():
            clean_row = {
                col: clean_for_json(val) 
                for col, val in row.items()
                if col in [
                    'DBA', 'BORO', 'BUILDING', 'STREET', 'ZIPCODE',
                    'PHONE', 'CUISINE DESCRIPTION', 'GRADE', 'SCORE',
                    'Latitude', 'Longitude', 'distance'
                ]
            }
            results.append(clean_row)
        
        return jsonify({
            'search_location': {'lat': lat, 'lon': lon, 'label': address},
            'restaurants': results
        })
        
    except Exception as e:
        logging.exception("Search error")
        return jsonify({'error': 'Search failed'}), 500
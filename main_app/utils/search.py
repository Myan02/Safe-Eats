"""Core restaurant search functionality."""
from .data_loader import DataService
from .geocoder import GeoService
import pandas as pd
import logging

geo_service = GeoService()

def search_restaurants(address):
    """Find nearby restaurants with complete details."""
    try:
        data_service = DataService()
        lat, lon = geo_service.geocode_address(address)
        if not lat or not lon:
            raise ValueError("Could not locate address")
        
        nearby = data_service.get_nearby_restaurants(lat, lon)
        grouped = nearby.sort_values('INSPECTION DATE', ascending=False).groupby('CAMIS')
        
        results = []
        inspection_history = {}
        
        for camis, group in grouped:
            latest = group.iloc[0]
            restaurant = {
                'CAMIS': str(camis),
                'DBA': str(latest['DBA']) if pd.notna(latest['DBA']) else 'Unknown',
                'BORO': str(latest['BORO']) if pd.notna(latest['BORO']) else '',
                'BUILDING': str(latest['BUILDING']) if pd.notna(latest['BUILDING']) else '',
                'STREET': str(latest['STREET']) if pd.notna(latest['STREET']) else '',
                'ZIPCODE': str(latest['ZIPCODE']) if pd.notna(latest['ZIPCODE']) else '',
                'PHONE': str(latest['PHONE']) if pd.notna(latest['PHONE']) else '',
                'CUISINE_DESCRIPTION': str(latest['CUISINE DESCRIPTION']) if pd.notna(latest['CUISINE DESCRIPTION']) else '',
                'GRADE': str(latest['GRADE']) if pd.notna(latest['GRADE']) else 'N/A',
                'SCORE': float(latest['SCORE']) if pd.notna(latest['SCORE']) else None,
                'Latitude': float(latest['Latitude']),
                'Longitude': float(latest['Longitude']),
                'distance': round(float(latest['distance']), 2)
            }
            results.append(restaurant)
            
            inspections = [{
                'DATE': row['INSPECTION DATE'].strftime('%Y-%m-%d') if pd.notna(row['INSPECTION DATE']) else None,
                'GRADE': str(row['GRADE']) if pd.notna(row['GRADE']) else None,
                'SCORE': float(row['SCORE']) if pd.notna(row['SCORE']) else None,
                'VIOLATIONS': str(row['VIOLATION DESCRIPTION']) if pd.notna(row['VIOLATION DESCRIPTION']) else None
            } for _, row in group.iterrows()]
            
            inspection_history[camis] = inspections
        
        return {
            'search_location': {'lat': lat, 'lon': lon, 'label': address},
            'restaurants': sorted(results, key=lambda x: x['distance']),
            'inspection_history': inspection_history
        }
        
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        raise
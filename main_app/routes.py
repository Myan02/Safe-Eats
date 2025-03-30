from flask import Blueprint, render_template, request, flash
import os
import pandas as pd
from main_app.utils.data_cleaner import DataCleaner
from main_app.utils.geocoder import Geocoder

# Initialize Blueprint
bp = Blueprint('main', __name__)

def format_zipcode(zipcode):
    """Format zip code to handle decimals and NaN values"""
    try:
        if pd.isna(zipcode):
            return ""
        zip_str = str(zipcode).strip()
        if '.' in zip_str:
            return zip_str.split('.')[0]  # Remove decimal portion
        return zip_str.zfill(5)  # Ensure 5 digits
    except:
        return ""

def format_address(building, street, boro, zipcode):
    """Format address components"""
    parts = []
    if building and str(building).lower() != 'nan':
        parts.append(str(building).strip())
    if street and str(street).lower() != 'nan':
        parts.append(str(street).strip())
    if boro and str(boro).lower() != 'nan':
        parts.append(str(boro).strip())
    
    formatted_zip = format_zipcode(zipcode)
    if formatted_zip:
        parts.append(formatted_zip)
    
    return ', '.join(parts) if parts else 'Address not available'

@bp.route('/', methods=['GET', 'POST'])
def index():
    results = []
    search_params = {
        'address': '',
        'radius': 1.0,
        'limit': 10
    }
    
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(current_dir, 'data/raw_locations.csv')
    clean_path = os.path.join(current_dir, 'data/locations_cleaned.csv')
    
    if request.method == 'POST':
        try:
            search_params = {
                'address': request.form.get('address', '').strip(),
                'radius': float(request.form.get('radius', 1)),
                'limit': int(request.form.get('limit', 10)) or None
            }
            
            cleaner = DataCleaner(raw_path, clean_path)
            clean_df = cleaner.clean_data()
            
            geocoder = Geocoder(clean_path)
            
            if not search_params['address']:
                flash("Please enter an address", 'error')
            else:
                raw_results = geocoder.find_nearby(
                    search_params['address'],
                    search_params['radius'],
                    search_params['limit']
                )
                results = [{
                    'dba': r['dba'],
                    'formatted_address': format_address(
                        r['building'], 
                        r['street'], 
                        r['boro'], 
                        r['zipcode']
                    ),
                    'distance': r['distance']
                } for r in raw_results]
                
                if not results:
                    flash("No restaurants found nearby", 'info')
                    
        except ValueError as e:
            flash(f"Invalid input: {str(e)}", 'error')
        except Exception as e:
            flash(f"Search error: {str(e)}", 'error')
    
    return render_template(
        'index.html', 
        results=results,
        search_params=search_params,
        active_page='home'
    )

@bp.route('/about')
def about():
    return render_template('about.html', active_page='about')
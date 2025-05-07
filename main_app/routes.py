"""Flask route handlers for the application."""
from flask import Blueprint, render_template, request, current_app, jsonify, send_from_directory
from main_app.utils.search import search_restaurants
import logging

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Render the main search page."""
    return render_template('index.html', mapbox_token=current_app.config['MAPBOX_TOKEN'])

@bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@bp.route('/search', methods=['POST'])
def search():
    """Handle restaurant search requests."""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    data = request.get_json()
    address = data.get('address', '').strip()
    
    try:
        response_data = search_restaurants(address)
        return current_app.response_class(
            response=current_app.json.dumps(response_data),
            mimetype='application/json'
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500
    
@bp.route('/fetch_geoms', methods=['POST', 'GET'])
def fetch_geoms():
    try:
        return send_from_directory('../data', 'zipcode_border_grades.geojson')
    
    except Exception as e:
        logging.error(f'Fetch error: {str(e)}')
        return jsonify({'error': 'Fetching geoms failed'}), 500

@bp.route('/fetch_unique_restaurants', methods=['POST', 'GET'])
def fetch_unique_restaurants():
    try:
        return current_app.response_class(
            response=current_app.json.dumps(current_app.data_service.unique_restaurants),
            mimetype='application/json'
        )
    
    except Exception as e:
        logging.error(f'Fetch error: {str(e)}')
        return jsonify({'error': 'Fetching unique restaurants failed'}), 500

@bp.route('/fetch_means', methods=['POST', 'GET'])
def fetch_means():
    try:
        return current_app.response_class(
            response=current_app.json.dumps(current_app.data_service.mean_grades),
            mimetype='application/json'
        )
    
    except Exception as e:
        logging.error(f'Fetch error: {str(e)}')
        return jsonify({'error': 'Fetching zipcode means failed'}), 500
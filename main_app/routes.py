"""Flask route handlers for the application."""
from flask import Blueprint, render_template, request, current_app, jsonify
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
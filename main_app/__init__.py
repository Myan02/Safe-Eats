"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from main_app.config import FlaskConfig
from main_app.utils.data_loader import DataService
from main_app.utils.json_encoder import SafeEncoder
from main_app.utils.data_loader import DataService
from main_app.utils.geocoder import GeoService
import logging

def create_app():
    """Create and configure the Flask app."""
    data_service = DataService()
    app = Flask(__name__)
    app.config.from_object(FlaskConfig)
    app.json = SafeEncoder(app)
    app.data_service = data_service
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )
    
    CORS(app)
    # Initialize services at startup
    app.extensions['data_service'] = DataService()
    app.extensions['geo_service'] = GeoService()

    from .routes import bp
    app.register_blueprint(bp)
    return app
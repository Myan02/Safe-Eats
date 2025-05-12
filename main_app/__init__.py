"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from main_app.config import FlaskConfig
from main_app.utils.data_loader import DataService
from main_app.utils.json_encoder import SafeEncoder
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
    from .routes import bp
    app.register_blueprint(bp)
    return app
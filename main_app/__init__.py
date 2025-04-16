"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from main_app.config import FlaskConfig
from main_app.utils.json_encoder import SafeEncoder
import logging

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(FlaskConfig)
    app.json = SafeEncoder(app)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )
    
    CORS(app)
    from .routes import bp
    app.register_blueprint(bp)
    return app
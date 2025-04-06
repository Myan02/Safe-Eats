from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging

load_dotenv()

def create_app():
    """Initialize the Flask application."""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app
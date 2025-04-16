"""Application configuration settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class FlaskConfig:
    """Configuration values with environment fallbacks."""
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
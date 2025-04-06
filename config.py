import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')
    
    if not MAPBOX_TOKEN or not MAPBOX_TOKEN.startswith('pk.ey'):
        raise ValueError("Invalid Mapbox token configuration")
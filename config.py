import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ProjectConfig:
    # Project metadata
    PROJECT_NAME = "Safe-Eats"
    VERSION = "1.0"
    
    # Directory paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    
    # Third-party API configurations
    MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')
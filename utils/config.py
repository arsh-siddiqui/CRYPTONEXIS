import os
from dotenv import load_dotenv

def load_config():
    """Loads environment variables from .env file."""
    load_dotenv()
    return {
        "APP_ENV": os.getenv("APP_ENV", "development"),
        "DATA_MODE": os.getenv("DATA_MODE", "demo"),
    }

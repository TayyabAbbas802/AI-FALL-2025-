# config.py
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

USDA_API_KEY = os.getenv('USDA_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = "models/gemini-2.5-flash"


def validate_environment():
    missing_vars = []
    if not USDA_API_KEY:
        missing_vars.append("USDA_API_KEY")
    if not GEMINI_API_KEY:
        missing_vars.append("GEMINI_API_KEY")

    if missing_vars:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")
    else:
        print("✅ All environment variables loaded successfully")
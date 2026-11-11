"""
Configuration module for PrepMate - AI Interview Trainer Agent.
Supports environment variable loading via python-dotenv.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env if present
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prepmate-dev-key-change-me-2026')
    DEBUG = os.environ.get('FLASK_DEBUG', '1').lower() in ('1', 'true', 'yes')
    PORT = int(os.environ.get('PORT', 5000))

    # Database configuration
    DB_PATH = os.environ.get('DATABASE_PATH', str(BASE_DIR / 'database' / 'prepmate.db'))

    # IBM watsonx.ai settings
    WATSONX_APIKEY = os.environ.get('WATSONX_APIKEY', '').strip()
    WATSONX_PROJECT_ID = os.environ.get('WATSONX_PROJECT_ID', '').strip()
    WATSONX_URL = os.environ.get('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com').rstrip('/')
    WATSONX_MODEL_ID = os.environ.get('WATSONX_MODEL_ID', 'ibm/granite-3-8b-instruct').strip()
    WATSONX_API_VERSION = os.environ.get('WATSONX_API_VERSION', '2023-05-29').strip()

    # Mock mode flag: if explicitly enabled OR if credentials are placeholders/empty
    _explicit_mock = os.environ.get('MOCK_MODE', '').strip().lower() in ('1', 'true', 'yes')
    _has_real_credentials = bool(
        WATSONX_APIKEY and 
        WATSONX_PROJECT_ID and 
        'your_' not in WATSONX_APIKEY.lower() and 
        'your_' not in WATSONX_PROJECT_ID.lower()
    )
    
    # Auto-mock is true only if explicitly requested or credentials are blank
    MOCK_MODE = _explicit_mock or (not _has_real_credentials)

    # Knowledge base directory
    KNOWLEDGE_BASE_DIR = BASE_DIR / 'knowledge_base'

    @classmethod
    def is_watsonx_configured(cls) -> bool:
        """Check whether valid IBM watsonx credentials are configured."""
        return cls._has_real_credentials


config = Config()

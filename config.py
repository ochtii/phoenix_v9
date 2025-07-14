# config.py
# Configuration for the Phoenix Flask application
# Loads environment variables for security and external services
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    Main configuration class for Flask application.
    Loads sensitive data and settings from environment variables.
    """
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key'

    # Firebase credentials (path to service account JSON)
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')

    # Debug mode
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

    # Add other configuration variables as needed

"""
Configuration module for the Phoenix web application.
Handles environment variables and application settings.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with default settings."""
    
    # Flask core settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'phoenix-dev-secret-key-change-in-production'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    
    # Firebase configuration
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID') or 'phoenix-dev-project'
    FIREBASE_PRIVATE_KEY_ID = os.environ.get('FIREBASE_PRIVATE_KEY_ID') or ''
    FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY') or ''
    FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL') or ''
    FIREBASE_CLIENT_ID = os.environ.get('FIREBASE_CLIENT_ID') or ''
    FIREBASE_AUTH_URI = os.environ.get('FIREBASE_AUTH_URI') or 'https://accounts.google.com/o/oauth2/auth'
    FIREBASE_TOKEN_URI = os.environ.get('FIREBASE_TOKEN_URI') or 'https://oauth2.googleapis.com/token'
    
    # Firebase availability flag - only if real credentials are provided
    FIREBASE_AVAILABLE = bool(
        os.environ.get('FIREBASE_PROJECT_ID') and 
        os.environ.get('FIREBASE_PROJECT_ID') != 'phoenix-dev-project' and
        os.environ.get('FIREBASE_PRIVATE_KEY') and 
        os.environ.get('FIREBASE_CLIENT_EMAIL') and
        os.environ.get('FIREBASE_CLIENT_EMAIL') != ''
    )
    
    # Force development mode if no real Firebase credentials
    USE_MOCK_DATABASE = not FIREBASE_AVAILABLE
    
    # Application settings
    DEBUG = False
    TESTING = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # Pagination settings
    PROJECTS_PER_PAGE = 12
    MESSAGES_PER_PAGE = 20
    TICKETS_PER_PAGE = 15
    
    # User roles
    USER_ROLES = ['User', 'Moderator', 'Admin', 'Webmaster']
    
    # Ticket statuses
    TICKET_STATUSES = ['Open', 'In Progress', 'Closed']
    
    # Project statuses
    PROJECT_STATUSES = ['Planning', 'Active', 'On Hold', 'Completed', 'Archived']


class DevelopmentConfig(Config):
    """Development configuration with debugging enabled."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration with security hardening."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def init_app(cls, app):
        """Initialize production-specific settings."""
        Config.init_app(app)


class TestingConfig(Config):
    """Testing configuration for unit tests."""
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'testing-secret-key'
    FIREBASE_PROJECT_ID = 'phoenix-test-project'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
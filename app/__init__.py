"""
Phoenix Web Application Factory
Initializes the Flask application with all necessary components.
"""

import os
from flask import Flask, session, request, g, render_template
from config import config
import firebase_admin
from firebase_admin import credentials, firestore
from functools import wraps


def get_category_icon(category):
    """Return FontAwesome icon class for project category."""
    category_icons = {
        'Web Development': 'fas fa-globe',
        'Mobile App': 'fas fa-mobile-alt',
        'Desktop Software': 'fas fa-desktop',
        'Game Development': 'fas fa-gamepad',
        'Data Science': 'fas fa-chart-bar',
        'AI/ML': 'fas fa-brain',
        'DevOps': 'fas fa-server',
        'Design': 'fas fa-paint-brush',
        'Marketing': 'fas fa-bullhorn',
        'Research': 'fas fa-microscope',
        'E-Commerce': 'fas fa-shopping-cart',
        'IoT': 'fas fa-microchip',
        'Blockchain': 'fas fa-link',
        'Cybersecurity': 'fas fa-shield-alt',
        'Education': 'fas fa-graduation-cap',
        'Healthcare': 'fas fa-heartbeat',
        'Finance': 'fas fa-chart-line',
        'Entertainment': 'fas fa-film',
        'Social Media': 'fas fa-share-alt',
        'Productivity': 'fas fa-tasks'
    }
    return category_icons.get(category, 'fas fa-folder')


class MockFirestore:
    """Mock Firestore client for development when Firebase is not available."""
    
    def __init__(self):
        self._collections = {}
    
    def collection(self, name):
        if name not in self._collections:
            self._collections[name] = MockCollection(name)
        return self._collections[name]


class MockCollection:
    """Mock Firestore collection."""
    
    def __init__(self, name):
        self.name = name
        self._documents = {}
    
    def document(self, doc_id):
        if doc_id not in self._documents:
            self._documents[doc_id] = MockDocument(doc_id)
        return self._documents[doc_id]
    
    def add(self, data):
        import uuid
        doc_id = str(uuid.uuid4())
        doc = self.document(doc_id)
        doc._data = data
        return doc, doc_id
    
    def stream(self):
        return list(self._documents.values())


class MockDocument:
    """Mock Firestore document."""
    
    def __init__(self, doc_id):
        self.id = doc_id
        self._data = None
    
    def get(self):
        return self
    
    def set(self, data):
        self._data = data
        return self
    
    def update(self, data):
        if self._data:
            self._data.update(data)
        else:
            self._data = data
        return self
    
    def delete(self):
        self._data = None
        return self
    
    def to_dict(self):
        return self._data or {}
    
    @property
    def exists(self):
        return self._data is not None


def initialize_firebase(app):
    """Initialize Firebase Admin SDK with proper error handling."""
    if not firebase_admin._apps:
        try:
            # Try to use service account from environment
            if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                cred = credentials.ApplicationDefault()
                app.logger.info("Using Google Application Default Credentials")
            else:
                # Check if we should use mock database
                if app.config.get('USE_MOCK_DATABASE', False):
                    app.logger.info("Using mock Firestore for development (no real Firebase credentials)")
                    return False
                
                # Check if all required Firebase config is present
                required_config = [
                    'FIREBASE_PROJECT_ID',
                    'FIREBASE_PRIVATE_KEY',
                    'FIREBASE_CLIENT_EMAIL'
                ]
                
                missing_config = [key for key in required_config 
                                if not app.config.get(key) or app.config.get(key) == '']
                
                if missing_config:
                    app.logger.warning(f"Missing Firebase configuration: {missing_config}")
                    app.logger.warning("Firebase will not be initialized. Using mock Firestore for development.")
                    return False
                
                # Don't initialize if using placeholder values
                if app.config['FIREBASE_PROJECT_ID'] in ['phoenix-dev-project', 'your-firebase-project-id']:
                    app.logger.info("Using placeholder Firebase project ID. Starting with mock database.")
                    return False
                
                # Use manual configuration
                cred_dict = {
                    "type": "service_account",
                    "project_id": app.config['FIREBASE_PROJECT_ID'],
                    "private_key_id": app.config.get('FIREBASE_PRIVATE_KEY_ID', ''),
                    "private_key": app.config['FIREBASE_PRIVATE_KEY'].replace('\\n', '\n'),
                    "client_email": app.config['FIREBASE_CLIENT_EMAIL'],
                    "client_id": app.config.get('FIREBASE_CLIENT_ID', ''),
                    "auth_uri": app.config.get('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                    "token_uri": app.config.get('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token')
                }
                cred = credentials.Certificate(cred_dict)
                app.logger.info("Using manual Firebase credentials")
            
            firebase_admin.initialize_app(cred, {
                'projectId': app.config['FIREBASE_PROJECT_ID']
            })
            app.logger.info("Firebase Admin SDK initialized successfully")
            return True
            
        except Exception as e:
            app.logger.error(f"Firebase initialization failed: {e}")
            return False
    else:
        app.logger.info("Firebase already initialized")
        return True


def create_app(config_name=None):
    """
    Create and configure the Flask application.
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_CONFIG') or 'default'
    app.config.from_object(config[config_name])
    
    # Initialize Firebase Admin SDK
    firebase_available = initialize_firebase(app)
    
    # Initialize Firestore client
    try:
        if firebase_available:
            app.db = firestore.client()
            app.logger.info("Firestore client initialized successfully")
        else:
            raise Exception("Firebase not available")
    except Exception as e:
        app.logger.warning(f"Failed to initialize Firestore client: {e}")
        # Use a mock database for development if Firebase is not available
        app.db = MockFirestore()
        app.logger.warning("Using mock Firestore client for development")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Set up before request handlers
    @app.before_request
    def load_logged_in_user():
        """Load current user information into Flask's g object."""
        user_id = session.get('user_id')
        
        if user_id is None:
            g.user = None
        else:
            try:
                user_doc = app.db.collection('users').document(user_id).get()
                if user_doc.exists:
                    g.user = user_doc.to_dict()
                    g.user['uid'] = user_id
                else:
                    # User document doesn't exist, clear session
                    session.clear()
                    g.user = None
            except Exception as e:
                app.logger.error(f"Error loading user: {e}")
                g.user = None
    
    return app


def register_blueprints(app):
    """Register all application blueprints."""
    from app.routes.main import main_bp
    from app.routes.user import user_bp
    from app.routes.projects import projects_bp
    from app.routes.tasks import tasks_bp
    from app.routes.discover import discover_bp
    from app.routes.messages import messages_bp
    from app.routes.support import support_bp
    from app.routes.admin import admin_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(discover_bp, url_prefix='/discover')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(support_bp, url_prefix='/support')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_error_handlers(app):
    """Register custom error handlers."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403


def register_context_processors(app):
    """Register template context processors."""
    
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to <br> tags."""
        if text is None:
            return ''
        return text.replace('\n', '<br>')
    
    @app.context_processor
    def inject_user():
        """Make current user available in all templates."""
        return dict(current_user=g.get('user'))
    
    @app.context_processor
    def inject_config():
        """Make configuration values available in templates."""
        return dict(
            USER_ROLES=app.config['USER_ROLES'],
            TICKET_STATUSES=app.config['TICKET_STATUSES'],
            PROJECT_STATUSES=app.config['PROJECT_STATUSES'],
            get_category_icon=get_category_icon
        )


# Authentication decorators
def login_required(f):
    """Decorator to require user authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            from flask import redirect, url_for, flash
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(required_roles):
    """
    Decorator to require specific user roles.
    
    Args:
        required_roles (list): List of roles that can access the route
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user is None:
                from flask import redirect, url_for, flash
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('user.login'))
            
            user_role = g.user.get('role', 'User')
            if user_role not in required_roles:
                from flask import abort
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin privileges."""
    return role_required(['Admin', 'Webmaster'])(f)
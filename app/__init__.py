# app/__init__.py
"""
Initializes the Flask application using the application factory pattern.
Loads configuration, registers blueprints, and initializes extensions.
"""
from flask import Flask
from config import Config

def create_app():
    """
    Application factory for the Phoenix Flask app.
    Returns a configured Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints (routes must exist and be imported here)
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    from .routes.projects import projects as projects_blueprint
    app.register_blueprint(projects_blueprint)

    from .routes.messages import messages as messages_blueprint
    app.register_blueprint(messages_blueprint)

    from .routes.support import support as support_blueprint
    app.register_blueprint(support_blueprint)

    from .routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .routes.discover import discover as discover_blueprint
    app.register_blueprint(discover_blueprint)

    # Initialize extensions here (e.g., database, login manager)
    # Example: db.init_app(app)

    return app

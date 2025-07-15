"""
Routes package initialization.
Imports all blueprints for the Phoenix web application.
"""

from .main import main_bp
from .user import user_bp
from .projects import projects_bp
from .messages import messages_bp
from .support import support_bp
from .admin import admin_bp
from .discover import discover_bp

__all__ = ['main_bp', 'user_bp', 'projects_bp', 'messages_bp', 'support_bp', 'admin_bp', 'discover_bp']
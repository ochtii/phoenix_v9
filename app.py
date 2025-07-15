#!/usr/bin/env python3
"""
Phoenix Web Application
A collaborative project management platform built with Flask and Firebase.

This is the main application entry point.
"""

import os
from app import create_app

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment variables
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print(f"""
    🚀 Starting Phoenix Web Application
    
    Environment: {os.environ.get('FLASK_CONFIG', 'default')}
    Debug Mode: {debug_mode}
    Server: http://{host}:{port}
    
    Features Available:
    ✅ User Authentication & Profiles
    ✅ Project Management
    ✅ Team Collaboration
    ✅ Messaging System
    ✅ Project Discovery
    ✅ Admin Dashboard
    ✅ Support System
    ✅ Dark/Light Theme
    
    """)
    
    # Run the application
    app.run(
        debug=debug_mode,
        host=host,
        port=port,
        threaded=True
    )

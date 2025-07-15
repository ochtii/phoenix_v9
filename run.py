#!/usr/bin/env python3
"""
Phoenix Web Application Entry Point
Run this file to start the Flask development server.
"""

import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Set development environment if not specified
    if not os.environ.get('FLASK_CONFIG'):
        os.environ['FLASK_CONFIG'] = 'development'
    
    # Run the application
    print("🔥 Starting Phoenix Web Application...")
    print("📱 Navigate to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    if not app.config.get('FIREBASE_AVAILABLE'):
        print("⚠️  Warning: Firebase is not configured. Using mock database.")
        print("   To use Firebase, set these environment variables:")
        print("   - FIREBASE_PROJECT_ID")
        print("   - FIREBASE_PRIVATE_KEY")
        print("   - FIREBASE_CLIENT_EMAIL")
        print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

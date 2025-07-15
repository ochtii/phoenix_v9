#!/usr/bin/env python3
"""
Einfacher Firebase Test für Phoenix
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("🔥 Phoenix Firebase Status Check")
print("="*40)

# Check basic config
project_id = os.getenv('FIREBASE_PROJECT_ID')
has_private_key = bool(os.getenv('FIREBASE_PRIVATE_KEY'))
client_email = os.getenv('FIREBASE_CLIENT_EMAIL')

print(f"Project ID: {project_id}")
print(f"Private Key: {'✓' if has_private_key else '✗'}")
print(f"Client Email: {client_email}")

# Check file
import pathlib
service_file = pathlib.Path('firebase-service-account.json')
print(f"Service Account File: {'✓' if service_file.exists() else '✗'}")

# Test app import
try:
    from app import create_app
    app = create_app()
    print("✓ App created successfully")
    
    # Check if Firebase was initialized
    with app.app_context():
        from app import db
        if hasattr(db, '_mock'):
            print("⚠ Using MOCK database")
        else:
            print("✓ Using REAL Firebase database")
            
except Exception as e:
    print(f"✗ Error: {e}")

print("\nFür echte Firebase-Verbindung muss die App neu gestartet werden!")

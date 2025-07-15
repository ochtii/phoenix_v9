#!/usr/bin/env python3
"""
Phoenix Projektplaner - Einfacher Start
Direkter Start mit Firebase-Konfiguration
"""

# Add necessary imports with error handling
try:
    import os
    import sys
    from pathlib import Path
    
    # Add project directory to path
    project_dir = Path(__file__).parent
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️ python-dotenv not available, using system environment")
    
    # Check Firebase config
    firebase_config = {
        'project_id': os.getenv('FIREBASE_PROJECT_ID'),
        'has_private_key': bool(os.getenv('FIREBASE_PRIVATE_KEY')),
        'client_email': os.getenv('FIREBASE_CLIENT_EMAIL')
    }
    
    print(f"\n🔥 Firebase Configuration:")
    print(f"   Project ID: {firebase_config['project_id']}")
    print(f"   Private Key: {'✓' if firebase_config['has_private_key'] else '✗'}")
    print(f"   Client Email: {firebase_config['client_email']}")
    
    # Check service account file
    service_file = project_dir / 'firebase-service-account.json'
    print(f"   Service File: {'✓' if service_file.exists() else '✗'}")
    
    # Import Flask app
    from app import create_app
    
    # Create app with current environment
    app = create_app()
    
    print(f"\n🚀 Starting Phoenix Projektplaner...")
    print(f"   URL: http://localhost:5000")
    print(f"   Debug Mode: {app.debug}")
    print(f"   Press Ctrl+C to stop\n")
    
    # Start the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print(f"   Missing module: {e.name if hasattr(e, 'name') else 'unknown'}")
    print(f"\n💡 Try installing missing packages:")
    print(f"   pip install flask firebase-admin python-dotenv bcrypt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error starting application: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)

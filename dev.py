"""
Phoenix Development Setup and Startup Script
This script helps set up and run the Phoenix web application in development mode.
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'flask',
        'firebase_admin',
        'dotenv'  # This is the import name for python-dotenv
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("   OR")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def setup_environment():
    """Set up environment variables."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating .env file from .env.example...")
            env_file.write_text(env_example.read_text())
            print("✅ .env file created. Please edit it with your configuration.")
        else:
            print("⚠️  No .env file found. Creating basic one...")
            basic_env = """# Phoenix Development Environment
SECRET_KEY=phoenix-dev-secret-key-change-this
FLASK_CONFIG=development

# Firebase Configuration (Optional - leave empty to use mock database)
# FIREBASE_PROJECT_ID=
# FIREBASE_PRIVATE_KEY=
# FIREBASE_CLIENT_EMAIL=
"""
            env_file.write_text(basic_env)
            print("✅ Basic .env file created.")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not available. Using system environment only.")

def start_application():
    """Start the Flask application."""
    try:
        from app import create_app
        
        # Create the application
        app = create_app()
        
        print("\n🔥 Starting Phoenix Web Application...")
        print("📱 Navigate to: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Check Firebase configuration
        firebase_configured = all([
            os.environ.get('FIREBASE_PROJECT_ID'),
            os.environ.get('FIREBASE_PRIVATE_KEY'),
            os.environ.get('FIREBASE_CLIENT_EMAIL')
        ])
        
        if not firebase_configured and not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            print("\n⚠️  Warning: Firebase is not configured.")
            print("   Using mock database for development.")
            print("   To use Firebase, set these environment variables in .env:")
            print("   - FIREBASE_PROJECT_ID")
            print("   - FIREBASE_PRIVATE_KEY")
            print("   - FIREBASE_CLIENT_EMAIL")
        else:
            print("✅ Firebase configuration detected")
        
        print("\n" + "="*50)
        
        # Start the development server
        app.run(
            debug=True,
            host='127.0.0.1',
            port=5000,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("   Make sure all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main function to set up and start the application."""
    print("🔥 Phoenix Web Application - Development Setup")
    print("=" * 50)
    
    # Check requirements
    check_python_version()
    
    if not check_dependencies():
        sys.exit(1)
    
    # Set up environment
    setup_environment()
    
    # Start application
    start_application()

if __name__ == '__main__':
    main()

# Create app instance for external import (e.g., for start.py)
from app import create_app
app = create_app()

#!/usr/bin/env python3
"""
Phoenix Projektplaner - Startup Script
Startet die Anwendung mit korrekter Konfiguration
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """Load environment variables from .env files"""
    env_files = ['.env', '.env.development']
    
    for env_file in env_files:
        if Path(env_file).exists():
            print(f"📄 Lade Umgebungsvariablen aus {env_file}")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if value and not os.environ.get(key):
                            os.environ[key] = value
            return True
    return False

def check_firebase_config():
    """Check Firebase configuration status"""
    firebase_vars = {
        'FIREBASE_PROJECT_ID': os.environ.get('FIREBASE_PROJECT_ID'),
        'FIREBASE_PRIVATE_KEY': os.environ.get('FIREBASE_PRIVATE_KEY'),
        'FIREBASE_CLIENT_EMAIL': os.environ.get('FIREBASE_CLIENT_EMAIL')
    }
    
    has_firebase = all(
        value and value.strip() and value not in ['', 'your-firebase-project-id', 'phoenix-dev-project']
        for value in firebase_vars.values()
    )
    
    print("\n🔥 Firebase-Status:")
    if has_firebase:
        print("✅ Firebase konfiguriert - Verbindung zu echter Datenbank")
        print(f"   Projekt: {firebase_vars['FIREBASE_PROJECT_ID']}")
    else:
        print("⚠️  Firebase nicht konfiguriert - Mock-Datenbank wird verwendet")
        print("   Perfekt für Entwicklung und Tests!")
        print("   Für Produktionsumgebung: siehe FIREBASE_SETUP.md")
    
    return has_firebase

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import firebase_admin
        print("✅ Abhängigkeiten installiert")
        return True
    except ImportError as e:
        print(f"❌ Fehlende Abhängigkeit: {e}")
        print("   Führen Sie aus: pip install -r requirements.txt")
        return False

def main():
    """Main startup function"""
    print("🚀 Phoenix Projektplaner wird gestartet...\n")
    
    # Load environment variables
    if not load_env_file():
        print("ℹ️  Keine .env Datei gefunden - Standard-Entwicklungseinstellungen werden verwendet")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Firebase config
    check_firebase_config()
    
    # Set Flask app
    os.environ.setdefault('FLASK_APP', 'dev.py')
    os.environ.setdefault('FLASK_ENV', 'development')
    
    print("\n🌐 Starte Flask-Entwicklungsserver...")
    print("   URL: http://localhost:5000")
    print("   Zum Stoppen: Ctrl+C\n")
    
    # Start Flask development server
    try:
        from dev import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Server gestoppt")
    except Exception as e:
        print(f"\n❌ Fehler beim Starten: {e}")
        print("   Prüfen Sie die Logs für weitere Details")
        sys.exit(1)

if __name__ == '__main__':
    main()

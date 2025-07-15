#!/usr/bin/env python3
"""
Firebase Connection Test
Testet die Firebase-Verbindung mit den konfigurierten Credentials
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_firebase_connection():
    """Test Firebase connection"""
    print("🔥 Firebase Verbindungstest")
    print("=" * 50)
    
    # Check environment variables
    project_id = os.getenv('FIREBASE_PROJECT_ID')
    private_key = os.getenv('FIREBASE_PRIVATE_KEY')
    client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
    
    print(f"📋 Projekt ID: {project_id}")
    print(f"🔑 Private Key: {'✅ Vorhanden' if private_key else '❌ Fehlt'}")
    print(f"📧 Client Email: {client_email}")
    
    # Check service account file
    service_account_file = project_root / 'firebase-service-account.json'
    print(f"📁 Service Account Datei: {'✅ Vorhanden' if service_account_file.exists() else '❌ Fehlt'}")
    
    # Try to initialize Firebase
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Clear any existing apps
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
        
        # Try service account file first
        if service_account_file.exists():
            print("\n🔄 Versuche Service Account Datei...")
            cred = credentials.Certificate(str(service_account_file))
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            print("✅ Firebase mit Service Account Datei initialisiert!")
        
        elif project_id and private_key and client_email:
            print("\n🔄 Versuche Umgebungsvariablen...")
            cred_dict = {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                "private_key": private_key.replace('\\n', '\n'),
                "client_email": client_email,
                "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            print("✅ Firebase mit Umgebungsvariablen initialisiert!")
        
        else:
            print("❌ Keine gültigen Firebase-Credentials gefunden")
            return False
        
        # Test Firestore connection
        print("\n🔄 Teste Firestore-Verbindung...")
        db = firestore.client()
        
        # Try to create a test document
        test_ref = db.collection('test').document('connection_test')
        test_ref.set({
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Connection test successful',
            'source': 'Firebase Connection Test Script'
        })
        
        print("✅ Firestore-Verbindung erfolgreich!")
        print("✅ Test-Dokument in 'test/connection_test' erstellt")
        
        # Clean up test document
        test_ref.delete()
        print("🗑️ Test-Dokument wieder gelöscht")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase-Initialisierung fehlgeschlagen: {e}")
        print(f"   Typ: {type(e).__name__}")
        return False

def main():
    """Main test function"""
    success = test_firebase_connection()
    
    if success:
        print("\n🎉 Firebase ist korrekt konfiguriert!")
        print("   Die Phoenix-Anwendung kann jetzt echte Firebase-Datenbank verwenden.")
    else:
        print("\n⚠️ Firebase-Konfiguration unvollständig")
        print("   Die Anwendung wird weiterhin Mock-Datenbank verwenden.")
        print("   Siehe SERVICE_ACCOUNT_SETUP.md für Details.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

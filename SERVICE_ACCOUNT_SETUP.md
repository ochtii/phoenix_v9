# 🔑 Service Account Schlüssel für Phoenix-v9 erstellen

## ⚠️ WICHTIG: Backend benötigt Service Account-Daten

Ihre Web-Konfiguration ist bereits eingetragen! Aber für das Flask-Backend benötigen wir zusätzlich **Service Account-Schlüssel**.

## 📋 Schritt-für-Schritt Anleitung:

### 1. Firebase Console öffnen
- Gehen Sie zu: https://console.firebase.google.com
- Wählen Sie Ihr Projekt "phoenix-v9"

### 2. Service Account erstellen
1. Klicken Sie auf das **Zahnrad-Symbol** (Projekteinstellungen)
2. Wählen Sie **"Dienstkonten"** im linken Menü
3. Klicken Sie auf **"Neuen privaten Schlüssel generieren"**
4. Bestätigen Sie mit **"Schlüssel generieren"**
5. Eine JSON-Datei wird heruntergeladen

### 3. JSON-Datei verwenden
Die heruntergeladene Datei enthält etwa folgende Struktur:
```json
{
  "type": "service_account",
  "project_id": "phoenix-v9",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xyz@phoenix-v9.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xyz%40phoenix-v9.iam.gserviceaccount.com"
}
```

### 4. Werte in .env eintragen
Öffnen Sie Ihre `.env` Datei und tragen Sie die Werte ein:

```env
FIREBASE_PROJECT_ID=phoenix-v9
FIREBASE_PRIVATE_KEY_ID=abc123...
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xyz@phoenix-v9.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456789...
```

### 5. Alternative: JSON-Datei direkt verwenden
Sie können die JSON-Datei auch als `firebase-service-account.json` im Projektverzeichnis speichern.

## 🚀 Nach der Konfiguration

Starten Sie die Anwendung mit:
```bash
python start.py
```

Sie sollten dann sehen:
```
✅ Firebase konfiguriert - Verbindung zu echter Datenbank
   Projekt: phoenix-v9
```

## 🔧 Firestore aktivieren

Falls noch nicht geschehen:
1. Firebase Console → **Firestore Database**
2. Klicken Sie auf **"Datenbank erstellen"**
3. Wählen Sie **"Im Produktionsmodus starten"**
4. Wählen Sie eine Region (z.B. europe-west3)

## 🔐 Authentication aktivieren

1. Firebase Console → **Authentication**
2. Klicken Sie auf **"Loslegen"**
3. Tab **"Sign-in method"**
4. Aktivieren Sie **"E-Mail/Passwort"**

## ✅ Nächste Schritte

Nach der Service Account-Konfiguration:
1. `python start.py` - Anwendung starten
2. `firebase deploy --only firestore:rules` - Sicherheitsregeln deployen
3. `firebase deploy --only firestore:indexes` - Indizes deployen

Bei Fragen: siehe FIREBASE_SETUP.md für weitere Details!

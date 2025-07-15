# Phoenix Projektplaner - Firebase Setup Guide

## Firebase-Projekt einrichten

### 1. Firebase-Projekt erstellen

1. Besuchen Sie [Firebase Console](https://console.firebase.google.com)
2. Klicken Sie auf "Neues Projekt erstellen"
3. Geben Sie den Projektnamen ein (z.B. "phoenix-projektplaner")
4. Aktivieren Sie Google Analytics (optional)
5. Wählen Sie ein Analytics-Konto aus oder erstellen Sie ein neues

### 2. Firestore-Datenbank einrichten

1. Navigieren Sie zu "Firestore Database" im linken Menü
2. Klicken Sie auf "Datenbank erstellen"
3. Wählen Sie "Im Produktionsmodus starten"
4. Wählen Sie eine Region (empfohlen: europe-west3 für Deutschland)

### 3. Authentication einrichten

1. Navigieren Sie zu "Authentication" im linken Menü
2. Klicken Sie auf "Loslegen"
3. Gehen Sie zu "Sign-in method"
4. Aktivieren Sie "E-Mail/Passwort"

### 4. Service Account erstellen

1. Gehen Sie zu "Projekteinstellungen" (Zahnrad-Symbol)
2. Klicken Sie auf "Dienstkonten"
3. Klicken Sie auf "Neuen privaten Schlüssel generieren"
4. Laden Sie die JSON-Datei herunter
5. Benennen Sie sie in `firebase-service-account.json` um
6. Platzieren Sie sie im Projektverzeichnis

### 5. Firebase CLI installieren

```powershell
npm install -g firebase-tools
```

### 6. Firebase CLI anmelden

```powershell
firebase login
```

### 7. Firebase-Projekt initialisieren

```powershell
firebase init
```

Wählen Sie:
- ✅ Firestore: Configure security rules and indexes files
- ✅ Hosting: Configure files for Firebase Hosting

### 8. Firestore-Regeln und Indizes deployen

```powershell
firebase deploy --only firestore:rules
firebase deploy --only firestore:indexes
```

### 9. Umgebungsvariablen konfigurieren

Erstellen Sie eine `.env` Datei basierend auf `.env.example`:

```env
FLASK_APP=dev.py
FLASK_ENV=development
SECRET_KEY=ihr-geheimer-schluessel
FIREBASE_PROJECT_ID=ihr-firebase-projekt-id
FIREBASE_PRIVATE_KEY_ID=ihre-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-...@ihr-projekt.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=ihre-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-...
```

### 10. Anwendung starten

```powershell
# Virtuelle Umgebung aktivieren
python -m venv venv
.\venv\Scripts\Activate.ps1

# Abhängigkeiten installieren
pip install -r requirements.txt

# Entwicklungsserver starten
python dev.py
```

## Firebase-Emulator für Entwicklung

### Emulator starten

```powershell
firebase emulators:start
```

### Emulator-UI öffnen

- Firestore: http://localhost:4000
- Auth: http://localhost:9099

### Mit Emulator entwickeln

Setzen Sie in der `.env` Datei:

```env
FIREBASE_EMULATOR=true
```

## Deployment

### Flask-App auf Firebase Hosting deployen

1. Build-Ordner erstellen:

```powershell
python build.py
```

2. Firebase deployen:

```powershell
firebase deploy
```

### Produktionsumgebung

Für die Produktion:

1. Setzen Sie `FLASK_ENV=production` in der `.env`
2. Generieren Sie einen starken `SECRET_KEY`
3. Konfigurieren Sie HTTPS
4. Aktivieren Sie Firebase Security Rules

## Firestore-Datenstruktur

### Collections

- `users`: Benutzerprofile und Einstellungen
- `projects`: Projekte und Metadaten
- `messages`: Private Nachrichten zwischen Benutzern
- `tickets`: Support-Tickets
- `activities`: Benutzeraktivitäten für das Dashboard
- `notifications`: Benachrichtigungen für Benutzer

### Security Rules

Die Firestore-Regeln in `firestore.rules` stellen sicher:

- Benutzer können nur ihre eigenen Daten lesen/schreiben
- Projektmitglieder können Projektdaten einsehen
- Admins haben erweiterte Berechtigungen
- Support-Tickets sind nur für Ersteller und Support-Team sichtbar

### Indizes

Die `firestore.indexes.json` optimiert Abfragen für:

- Projektsuche nach Sichtbarkeit und Datum
- Nachrichtenverlauf nach Teilnehmern
- Ticket-Verwaltung nach Status
- Aktivitätenverfolgung nach Benutzer

## Troubleshooting

### Häufige Probleme

1. **Firebase-Initialisierung fehlgeschlagen**: Überprüfen Sie die Service Account-Datei
2. **Berechtigung verweigert**: Prüfen Sie die Firestore-Regeln
3. **Indizes fehlen**: Deployen Sie die Indizes mit `firebase deploy --only firestore:indexes`

### Logs anzeigen

```powershell
firebase functions:log
```

### Emulator-Daten zurücksetzen

```powershell
firebase emulators:exec --only firestore "python reset_db.py"
```

## Support

Bei Problemen:

1. Überprüfen Sie die Firebase Console für Fehler
2. Prüfen Sie die Browser-Entwicklertools
3. Schauen Sie in die Flask-Logs
4. Konsultieren Sie die [Firebase-Dokumentation](https://firebase.google.com/docs)

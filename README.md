# 🔥 Phoenix - Collaborative Project Platform

Phoenix is a modern, collaborative web application for managing and discovering projects. Built with Flask and designed for teams who want to organize their work efficiently.

## ✨ Features

- **🔐 User Authentication**: Secure registration, login, and profile management
- **📊 Project Management**: Create, organize, and collaborate on projects
- **💬 Messaging System**: Built-in communication for team collaboration
- **🎫 Support Tickets**: Integrated help desk for user support
- **🛡️ Admin Panel**: Comprehensive administration interface
- **🔍 Discovery**: Explore and discover public projects
- **📱 Responsive Design**: Works perfectly on all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd projektplaner_v8/8.1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the development server**
   ```bash
   python dev.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_CONFIG=development

# Firebase Configuration (Optional)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
```

### Firebase Setup (Optional)

Phoenix can work with or without Firebase:

- **With Firebase**: Full cloud database functionality
- **Without Firebase**: Uses a mock database for development

To use Firebase:
1. Create a Firebase project
2. Generate a service account key
3. Add the credentials to your `.env` file

## 📁 Project Structure

Hier ist eine detaillierte Aufschlüsselung der gesamten Projektstruktur, um die Navigation und das Verständnis des Codes zu erleichtern.

```plaintext
.
├── app/                    # Hauptverzeichnis der Flask-Anwendung
│   ├── __init__.py         # Initialisiert die App, erstellt die "Application Factory" und registriert Blueprints
│   ├── models.py           # Definiert die Datenmodelle (z.B. User, Project, Task) für die Datenbank
│   ├── routes/             # Enthält die Blueprints (Routen-Gruppen) für die Anwendungsbereiche
│   │   ├── admin.py        # Routen für den Administrationsbereich
│   │   ├── discover.py     # Routen für die Entdeckungsseite (öffentliche Projekte)
│   │   ├── main.py         # Hauptrouten (Homepage, Dashboard, Startseite)
│   │   ├── messages.py     # Routen für das interne Nachrichtensystem
│   │   ├── projects.py     # Routen für das Projektmanagement (Erstellen, Anzeigen, Bearbeiten)
│   │   ├── support.py      # Routen für das Support-Ticket-System
│   │   └── user.py         # Routen für Benutzer (Login, Registrierung, Profil, Einstellungen)
│   ├── static/             # Statische Dateien (werden direkt an den Browser ausgeliefert)
│   │   ├── css/            # CSS-Stylesheets für die verschiedenen Bereiche der Anwendung
│   │   ├── js/             # JavaScript-Dateien für clientseitige Logik
│   │   └── img/            # Bilder, Icons und andere grafische Assets
│   └── templates/          # Jinja2-Templates für die HTML-Seiten
│       ├── admin/          # Templates für den Admin-Bereich (Dashboard, User-Management)
│       ├── components/     # Wiederverwendbare Template-Teile (z.B. Header, Footer)
│       ├── discover/       # Templates für die "Entdecken"-Funktion
│       ├── messages/       # Templates für das Nachrichtensystem
│       ├── projects/       # Templates für Projektansichten, Erstellung, etc.
│       ├── support/        # Templates für das Support-System
│       ├── user/           # Templates für Benutzerprofil, Login, Registrierung, etc.
│       ├── base.html       # Basis-Template, von dem alle anderen Templates erben
│       ├── index.html      # Landing-Page für nicht angemeldete Benutzer
│       ├── main_dashboard.html # Haupt-Dashboard für eingeloggte Benutzer
│       └── start.html      # Personalisierte Startseite für eingeloggte Benutzer
│
├── docs/                   # Projektdokumentation
│   ├── index.html          # HTML-Version der Dokumentation
│   └── style.css           # Styles für die HTML-Doku
│
├── venv/                   # Virtuelle Python-Umgebung (wird von .gitignore ignoriert)
│
├── .env                    # Lokale Umgebungsvariablen (geheim, wird NICHT versioniert)
├── .env.example            # Vorlage für die .env-Datei mit allen benötigten Variablen
├── .gitignore              # Definiert Dateien und Ordner, die von Git ignoriert werden sollen
├── config.py               # Konfigurationsklassen für verschiedene Umgebungen (Development, Production)
├── dev.py                  # Start-Skript für die Entwicklungsumgebung (mit Debug-Funktionen)
├── run.py                  # Einfaches Start-Skript für die Produktion (z.B. für Gunicorn)
├── requirements.txt        # Liste der Python-Abhängigkeiten für das Projekt
├── README.md               # Diese Datei - Die zentrale Projektdokumentation
├── firebase.json           # Konfiguration für Firebase Hosting und Emulatoren
├── firestore.rules         # Sicherheitsregeln für die Firestore-Datenbank
└── firestore.indexes.json  # Definition der Datenbank-Indizes für schnelle Abfragen
```

## 🎨 Frontend Technologies

- **Bootstrap 5.3.0**: Responsive UI framework
- **Font Awesome 6.4.0**: Icon library
- **Custom CSS**: Modern design system with CSS custom properties
- **Vanilla JavaScript**: ES6+ with modular architecture

## 💻 JavaScript-Funktionalität

Die clientseitige Logik wird durch modulare Vanilla-JavaScript-Dateien in `app/static/js/` gesteuert. Hier ist eine umfassende Übersicht der wichtigsten Funktionen, gruppiert nach ihren jeweiligen Dateien.

### `main.js` (Globale Skripte)

| Funktion              | Beschreibung                                                              |
| --------------------- | ------------------------------------------------------------------------- |
| `toggleMobileNav()`   | Schaltet die Sichtbarkeit der mobilen Navigation um.                      |
| `initTooltips()`      | Initialisiert alle Bootstrap-Tooltips auf der Seite für eine bessere UX.  |
| `handleNotifications()`| Holt und zeigt Benutzerbenachrichtigungen in der UI an.                   |
| `themeSwitcher()`     | Ermöglicht dem Benutzer den Wechsel zwischen Light- und Dark-Theme.       |
| `initModals()`        | Richtet Event-Listener für das Öffnen und Schließen von Modals ein.       |
| `dismissFlashMessage()`| Ermöglicht das Schließen von Flash-Nachrichten (z.B. "Erfolgreich gespeichert"). |
| `ajaxRequest(url, options)`| Eine Hilfsfunktion für standardisierte AJAX (Fetch API) Anfragen.    |

### `auth.js` (Authentifizierung)

| Funktion                   | Beschreibung                                                              |
| -------------------------- | ------------------------------------------------------------------------- |
| `validateRegistrationForm()`| Bietet Echtzeit-Validierung für die Felder des Registrierungsformulars. |
| `checkPasswordStrength()`  | Gibt visuelles Feedback zur Stärke des gewählten Passworts.             |
| `handlePasswordReset()`    | Steuert die Logik für das Anfordern eines Passwort-Resets.              |

### `projects.js` (Projektmanagement)

| Funktion                 | Beschreibung                                                              |
| ------------------------ | ------------------------------------------------------------------------- |
| `handleProjectForm()`    | Verarbeitet das Senden von "Projekt erstellen/bearbeiten"-Formularen via AJAX. |
| `addTask(projectId)`     | Fügt dynamisch eine neue Aufgabe zur Aufgabenliste hinzu.                 |
| `deleteTask(taskId)`     | Entfernt eine Aufgabe aus der UI und sendet eine Löschanfrage.            |
| `updateTaskStatus(taskId)`| Aktualisiert den Status einer Aufgabe (z.B. "To Do" zu "Done") via API.   |
| `editTaskInline(taskId)` | Ermöglicht die direkte Bearbeitung eines Aufgabentitels in der Liste.     |
| `filterTasks(filter)`    | Filtert die angezeigten Aufgaben nach Status oder zugewiesener Person.    |
| `handleFileUpload()`     | Steuert den Upload von Dateien zu einem Projekt, inkl. Fortschrittsanzeige. |
| `inviteMember()`         | Steuert die Logik zum Einladen und Hinzufügen neuer Mitglieder.           |

### `messages.js` (Nachrichtensystem)

| Funktion                   | Beschreibung                                                              |
| -------------------------- | ------------------------------------------------------------------------- |
| `loadConversation(userId)` | Lädt den Nachrichtenverlauf mit einem bestimmten Benutzer.                |
| `sendMessage(formData)`    | Sendet eine neue Nachricht via AJAX und fügt sie zur Konversation hinzu.  |
| `pollNewMessages()`        | Überprüft periodisch auf neue Nachrichten und zeigt eine Benachrichtigung an. |

### `user_profile.js` (Benutzerprofil & Einstellungen)

| Funktion                   | Beschreibung                                                              |
| -------------------------- | ------------------------------------------------------------------------- |
| `updateProfile(formData)`  | Sendet Aktualisierungen des Benutzerprofils via AJAX.                     |
| `handleAvatarUpload()`     | Ermöglicht den Upload und die Vorschau eines neuen Profilbildes.          |
| `requestAccountDeletion()` | Steuert den Prozess zur Beantragung der Account-Löschung.                 |

### `admin.js` (Admin-Panel)

| Funktion             | Beschreibung                                                              |
| -------------------- | ------------------------------------------------------------------------- |
| `initDataTable()`    | Initialisiert eine sortier- und durchsuchbare Datentabelle (z.B. für Benutzer). |
| `confirmAction(url, message)`| Zeigt einen Bestätigungsdialog vor einer kritischen Aktion (Löschen, Sperren). |
| `updateUserRole(userId, newRole)`| Ändert die Rolle eines Benutzers (z.B. von 'user' zu 'moderator'). |

## 🔒 Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **Input Validation**: Client and server-side validation
- **Role-based Access**: User, Moderator, and Admin roles
- **Secure Sessions**: Encrypted session management
- **Password Hashing**: bcrypt for secure password storage

## 📱 Responsive Design

Phoenix works beautifully on:
- 💻 Desktop computers
- 📱 Mobile phones
- 📟 Tablets
- 🖥️ Large displays

## 🛠️ Development

### Running in Development Mode

```bash
python dev.py
```

This will:
- Check dependencies
- Set up environment
- Start the Flask development server
- Show helpful warnings and tips

### Available Scripts

- `python dev.py` - Start development server with setup checks
- `python run.py` - Simple Flask server start
- `python -m flask run` - Standard Flask development server

### Debug Mode

When running in development mode, Phoenix includes:
- **Debug toolbar**: Extra development information
- **Auto-reload**: Automatic server restart on file changes
- **Error pages**: Detailed error information
- **Debug indicator**: Visual indicator in the browser

## 🚢 Deployment

### Production Setup

1. **Set environment variables**
   ```bash
   export FLASK_CONFIG=production
   export SECRET_KEY=your-production-secret-key
   # Add Firebase credentials for production
   ```

2. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn "app:create_app()" --bind 0.0.0.0:8000
   ```

3. **Configure reverse proxy** (nginx recommended)
4. **Set up SSL/HTTPS** for secure communication

## 📊 Features Overview

### User Management
- User registration and authentication
- Profile management with avatars
- Role-based permissions
- Account settings and privacy controls

### Project Management
- Create and organize projects
- Invite team members
- Track project progress
- File sharing and collaboration

### Communication
- Built-in messaging system
- Team communication
- Notification system
- Real-time updates

### Administration
- User management
- System monitoring
- Content moderation
- Analytics and reporting

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and inline documentation
- **Issues**: Report bugs via GitHub issues
- **Email**: contact@phoenix.app
- **Community**: Join our Discord server

## 🔮 Roadmap

- [ ] Real-time messaging with WebSockets
- [ ] Advanced project analytics
- [ ] Mobile app (React Native)
- [ ] API for third-party integrations
- [ ] Plugin system for extensions

---

**Made with ❤️ by the Phoenix team**
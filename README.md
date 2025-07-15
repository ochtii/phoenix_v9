# 🔥 Phoenix - Collaborative Project Platform

<div align="center">

![Phoenix Logo](app/static/img/logo7.webp)

**A modern, collaborative web application for project management and team collaboration**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange.svg)](https://firebase.google.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## ✨ Key Features

Phoenix is a comprehensive project management platform with modern design and powerful features:

- **🔐 User Authentication**: Secure registration, login, and profile management
- **📊 Project Management**: Create, organize, and collaborate on projects
- **💬 Messaging System**: Built-in communication for team collaboration
- **🎫 Support Tickets**: Integrated help desk for user support
- **🛡️ Admin Panel**: Comprehensive administration interface
- **🔍 Project Discovery**: Explore and discover public projects
- **📱 Responsive Design**: Works perfectly on all devices
- **💳 Voucher System**: Complete voucher management for administrators
- **📈 Plan Management**: Starter, Pro, and Enterprise plans for users
- **🎨 Modern UI**: Video backgrounds and glassmorphism effects
- **📊 Live Statistics**: Real-time data from Firestore database

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Optional Firebase project for cloud functionality

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ochtii/phoenix_v9.git
   cd phoenix_v9
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

<details>
<summary><strong>🗂️ Complete Project Structure</strong> (Click to expand)</summary>

```plaintext
phoenix_v9/
├── 📁 app/                         # Main Flask application directory
│   ├── 📄 __init__.py              # App initialization and blueprint registration
│   ├── 📄 models.py                # Data models (User, Project, etc.)
│   ├── 📄 custom_debugger.py       # Custom debug functions
│   ├── 📄 debugger.py              # Debug system for development
│   ├── 📄 debugger_injection.py    # Debug code injection
│   │
│   ├── 📁 routes/                  # Blueprint routes for different areas
│   │   ├── 📄 __init__.py          # Route initialization
│   │   ├── 📄 admin.py             # 🛡️ Admin area with voucher management
│   │   ├── 📄 discover.py          # 🔍 Project discovery and public projects
│   │   ├── 📄 main.py              # 🏠 Main routes with live statistics
│   │   ├── 📄 messages.py          # 💬 Messaging system and chat
│   │   ├── 📄 projects.py          # 📊 Project management and collaboration
│   │   ├── 📄 support.py           # 🎫 Support ticket system
│   │   ├── 📄 user.py              # 👤 User management and authentication
│   │   ├── 📄 tasks.py             # ✅ Task management for projects
│   │   ├── 📄 test.py              # 🧪 Test routes for development
│   │   └── 📄 debugger.py          # 🐛 Debug routes and panels
│   │
│   ├── 📁 static/                  # Static frontend files
│   │   ├── 📁 css/                 # 🎨 Stylesheets with modern design
│   │   │   ├── 📄 base.css         # Base styles and CSS variables
│   │   │   ├── 📄 index.css        # Landing page specific styles
│   │   │   ├── 📄 main_dashboard.css # Dashboard layout
│   │   │   ├── 📄 start.css        # Start page styles
│   │   │   ├── 📄 debugger.css     # Debug panel styling
│   │   │   │
│   │   │   ├── 📁 admin/           # Admin panel styles
│   │   │   │   ├── 📄 admin_dashboard.css
│   │   │   │   ├── 📄 backend_control.css
│   │   │   │   ├── 📄 phoenix_core.css
│   │   │   │   ├── 📄 settings.css
│   │   │   │   └── 📄 user_management.css
│   │   │   │
│   │   │   ├── 📁 components/      # 🧩 Component-specific CSS files
│   │   │   │   ├── 📄 cards.css    # Card layout components
│   │   │   │   ├── 📄 footer.css   # ⭐ Standalone footer styling
│   │   │   │   └── 📄 header.css   # Header and navigation
│   │   │   │
│   │   │   ├── 📁 discover/        # Project discovery styles
│   │   │   │   └── 📄 explore.css
│   │   │   │
│   │   │   ├── 📁 messages/        # Messages UI styles
│   │   │   │   ├── 📄 conversation.css
│   │   │   │   └── 📄 inbox.css
│   │   │   │
│   │   │   ├── 📁 projects/        # Project management styles
│   │   │   │   ├── 📄 create.css
│   │   │   │   ├── 📄 index.css
│   │   │   │   ├── 📄 project_settings.css
│   │   │   │   └── 📄 project_view.css
│   │   │   │
│   │   │   ├── 📁 support/         # Support system styles
│   │   │   │   ├── 📄 new_ticket.css
│   │   │   │   └── 📄 view_ticket.css
│   │   │   │
│   │   │   └── 📁 user/            # User interface styles
│   │   │       ├── 📄 edit_profile.css
│   │   │       ├── 📄 login.css
│   │   │       ├── 📄 profile.css
│   │   │       └── 📄 register.css
│   │   │
│   │   ├── 📁 js/                  # 🔧 JavaScript modules
│   │   │   ├── 📄 base.js          # Base JavaScript functions
│   │   │   ├── 📄 debug.js         # Debug functionalities
│   │   │   ├── 📄 debugger.js      # Debug panel interactions
│   │   │   ├── 📄 firebase-config.js # Firebase configuration
│   │   │   ├── 📄 function-checker.js # Function validation
│   │   │   │
│   │   │   ├── 📁 admin/           # Admin panel JavaScript
│   │   │   │   ├── 📄 backend_control.js
│   │   │   │   ├── 📄 dashboard.js
│   │   │   │   ├── 📄 phoenix_core.js
│   │   │   │   └── 📄 user_management.js
│   │   │   │
│   │   │   ├── 📁 components/      # Component JavaScript
│   │   │   │   ├── 📄 footer.js
│   │   │   │   └── 📄 header.js
│   │   │   │
│   │   │   ├── 📁 discover/        # Discovery JavaScript
│   │   │   │   └── 📄 explore.js
│   │   │   │
│   │   │   ├── 📁 messages/        # Messages JavaScript
│   │   │   │   ├── 📄 conversation.js
│   │   │   │   └── 📄 inbox.js
│   │   │   │
│   │   │   ├── 📁 projects/        # Project JavaScript
│   │   │   │   ├── 📄 project_settings.js
│   │   │   │   └── 📄 project_view.js
│   │   │   │
│   │   │   ├── 📁 support/         # Support JavaScript
│   │   │   │   ├── 📄 new_ticket.js
│   │   │   │   └── 📄 view_ticket.js
│   │   │   │
│   │   │   └── 📁 user/            # User JavaScript
│   │   │       ├── 📄 account_settings.js
│   │   │       ├── 📄 edit_profile.js
│   │   │       ├── 📄 login.js
│   │   │       ├── 📄 privacy_settings.js
│   │   │       ├── 📄 profile.js
│   │   │       └── 📄 register.js
│   │   │
│   │   └── 📁 img/                 # 🖼️ Images and assets
│   │       ├── 📄 favicon.ico      # Website favicon
│   │       ├── 🎥 phoenix.mp4      # Video background for landing page
│   │       ├── 🖼️ phoenix.png      # Main logo
│   │       ├── 🖼️ logo1.png...logo9.jpg # Various logo variants
│   │       ├── 🖼️ phoenix-icon1.png...phoenix-icon3.png # Icon variants
│   │       ├── 🖼️ phoenix2.png...phoenix12.png # Additional Phoenix assets
│   │       └── 🎨 background_blue.png, background_red.png # Backgrounds
│   │
│   └── 📁 templates/               # 🖼️ Jinja2 templates
│       ├── 📄 base.html            # Base template for all pages
│       ├── 📄 index.html           # 🌟 Modern landing page with video background
│       ├── 📄 main_dashboard.html  # Main dashboard for logged-in users
│       ├── 📄 start.html           # Personalized start page
│       ├── 📄 dashboard.html       # Alternative dashboard view
│       ├── 📄 faq.html             # FAQ page
│       │
│       ├── 📁 admin/               # Admin templates
│       │   ├── 📄 admin_dashboard.html # Admin dashboard
│       │   ├── 📄 backend_control.html # Backend controls
│       │   ├── 📄 phoenix_core.html    # Core system management
│       │   ├── 📄 settings.html        # Admin settings
│       │   ├── 📄 user_management.html # 👥 User management with plan system
│       │   └── 📄 vouchers.html        # 💳 Voucher management
│       │
│       ├── 📁 components/          # Reusable components
│       │   ├── 📄 header.html      # Navigation and header
│       │   └── 📄 footer.html      # Footer with consistent width
│       │
│       ├── 📁 debugger/            # Debug templates
│       │   ├── 📄 dashboard.html   # Debug dashboard
│       │   └── 📄 debugger.html    # Debug panel
│       │
│       ├── 📁 discover/            # Project discovery templates
│       │   └── 📄 explore.html     # Project exploration
│       │
│       ├── 📁 errors/              # Error pages
│       │   ├── 📄 403.html         # Forbidden
│       │   ├── 📄 404.html         # Not Found
│       │   └── 📄 500.html         # Server Error
│       │
│       ├── 📁 messages/            # Messages templates
│       │   ├── 📄 conversation.html # Chat conversation
│       │   └── 📄 inbox.html       # Messages inbox
│       │
│       ├── 📁 projects/            # Project templates
│       │   ├── 📄 create.html      # Create project
│       │   ├── 📄 edit.html        # Edit project
│       │   ├── 📄 index.html       # Project list
│       │   ├── 📄 join.html        # Join project
│       │   ├── 📄 project_settings.html # Project settings
│       │   ├── 📄 project_view.html     # Project view
│       │   ├── 📄 tasks.html       # Task management
│       │   ├── 📄 timeline.html    # Project timeline
│       │   ├── 📄 financials.html  # Financial management
│       │   └── 📄 view.html        # Project details
│       │
│       ├── 📁 support/             # Support templates
│       │   ├── 📄 all_tickets.html # All tickets (admin)
│       │   ├── 📄 new_ticket.html  # Create new ticket
│       │   ├── 📄 tickets.html     # User tickets
│       │   └── 📄 view_ticket.html # Ticket details
│       │
│       └── 📁 user/                # User templates
│           ├── 📄 account_settings.html # Account settings
│           ├── 📄 edit_profile.html     # Edit profile
│           ├── 📄 friends.html          # Friends system
│           ├── 📄 login.html            # Login page
│           ├── 📄 privacy_settings.html # Privacy settings
│           ├── 📄 profile.html          # User profile
│           ├── 📄 register.html         # Registration
│           └── 📄 upgrade.html          # Plan upgrade page
│
├── 📁 docs/                        # 📚 Project documentation
│   ├── 📄 index.html               # HTML documentation
│   ├── 📄 script.js                # Documentation JavaScript
│   └── 📄 style.css                # Documentation styles
│
├── 📁 functions/                   # ☁️ Firebase Functions (optional)
│   ├── 📄 index.js                 # Cloud Functions code
│   └── 📄 package.json             # Node.js dependencies
│
├── 📁 public/                      # 🌐 Firebase Hosting files
│   ├── 📄 index.html               # Static landing page
│   └── 📁 static/                  # Static assets for hosting
│       ├── 📁 css/                 # CSS copies for hosting
│       ├── 📁 js/                  # JavaScript copies for hosting
│       └── 📁 img/                 # Image assets for hosting
│
├── 📁 venv/                        # 🐍 Python Virtual Environment
│   ├── 📁 Lib/                     # Python libraries
│   ├── 📁 Scripts/                 # Executable scripts
│   └── 📄 pyvenv.cfg               # Virtual environment config
│
├── 📁 .vscode/                     # 🔧 VS Code configuration
│   └── 📄 tasks.json               # Build tasks for VS Code
│
├── 📁 __pycache__/                 # 🔄 Python bytecode cache
│
├── 📄 .env                         # 🔐 Local environment variables (secret)
├── 📄 .env.development            # 🛠️ Development environment variables
├── 📄 .env.example                # 📋 Template for environment variables
├── 📄 .firebaserc                 # Firebase project configuration
├── 📄 .gitignore                  # Git ignore rules
├── 📄 app.py                      # 🚀 Alternative app entry point
├── 📄 build.py                    # 🏗️ Build script for deployment
├── 📄 config.py                   # ⚙️ Flask configuration classes
├── 📄 create_admin.py             # 👑 Create admin user
├── 📄 dev.py                      # 🛠️ Development server with setup checks
├── 📄 firebase.json               # Firebase hosting/functions config
├── 📄 firebase-service-account.json # 🔑 Firebase service account
├── 📄 firestore.indexes.json     # 📊 Firestore database indexes
├── 📄 firestore.rules             # 🛡️ Firestore security rules
├── 📄 netlify.toml                # Netlify deployment config
├── 📄 quick_test.py               # 🧪 Quick tests
├── 📄 README.md                   # 📖 This documentation
├── 📄 requirements.txt            # 📦 Python dependencies
├── 📄 run.py                      # 🏃 Production server
├── 📄 run_simple.py               # 🎯 Simple server start
├── 📄 start.py                    # ▶️ Start script
├── 📄 test_firebase.py            # 🔥 Firebase connection test
├── 📄 test_routes.py              # 🧪 Route tests
├── 📄 vercel.json                 # Vercel deployment config
├── 📄 DEPLOYMENT_ALTERNATIVES.md  # 📋 Alternative deployment options
├── 📄 FIREBASE_SETUP.md           # 🔥 Firebase setup guide
├── 📄 FIREBASE_HOSTING.md         # 🌐 Firebase hosting guide
└── 📄 SERVICE_ACCOUNT_SETUP.md    # 🔑 Service account setup
```

### 🎯 **Important Directories in Detail:**

#### **📁 app/routes/** - Blueprint Routes
- **admin.py**: Complete voucher management system, plan assignments
- **main.py**: Live statistics from Firestore, landing page logic
- **user.py**: Authentication, profile management, plan management
- **projects.py**: CRUD operations for projects, collaboration features
- **messages.py**: Real-time messaging system with WebSocket support
- **support.py**: Ticket system with status tracking

#### **📁 app/static/css/components/** - Modular CSS Architecture
- **footer.css**: Standalone styling without Bootstrap dependencies
- **header.css**: Navigation and responsive header components
- **cards.css**: Reusable card layouts for modern UI

#### **📁 app/templates/** - Template Hierarchy
- **base.html**: Master template with theme system and navigation
- **index.html**: Modern landing page with video background and 80% layout
- **admin/**: Complete admin suite with voucher and user management

#### **📁 Firebase Integration**
- **firebase.json**: Hosting, Functions and emulator configuration
- **firestore.rules**: Granular security rules for data access
- **functions/**: Cloud Functions for backend logic

</details>


## 🎨 Frontend Technologies

- **Bootstrap 5.3.0**: Responsive UI framework
- **Font Awesome 6.4.0**: Icon library
- **Custom CSS**: Modern design system with CSS custom properties
- **Vanilla JavaScript**: ES6+ with modular architecture

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
- **Community**: Join our Discord server (soon)

---

**Made with ❤️ by the Phoenix team**
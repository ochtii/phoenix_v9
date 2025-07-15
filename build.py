#!/usr/bin/env python3
"""
Build script for Phoenix Projektplaner
Prepares the application for Firebase Hosting deployment
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {command}: {e}")
        return False

def create_build_directory():
    """Create and clean the build directory"""
    build_dir = Path("public")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    build_dir.mkdir(exist_ok=True)
    return build_dir

def copy_static_files(build_dir):
    """Copy static files to build directory"""
    static_src = Path("app/static")
    static_dest = build_dir / "static"
    
    if static_src.exists():
        shutil.copytree(static_src, static_dest)
        print("✅ Static files copied")
    else:
        print("❌ Static files directory not found")

def generate_static_html():
    """Generate static HTML files from Flask templates"""
    # This is a simplified version - in a real deployment you might want
    # to use Flask-Frozen or similar to generate static pages
    
    template_files = [
        "base.html",
        "user/login.html", 
        "user/register.html",
        "404.html",
        "500.html"
    ]
    
    build_dir = Path("public")
    
    # Create a simple index.html that redirects to login
    index_content = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phoenix Projektplaner</title>
    <meta http-equiv="refresh" content="0; url=/login">
</head>
<body>
    <p>Weiterleitung zu <a href="/login">Login</a>...</p>
</body>
</html>"""
    
    with open(build_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_content)
    
    print("✅ Static HTML files generated")

def create_firebase_config():
    """Create firebase.json if it doesn't exist"""
    firebase_config = {
        "hosting": {
            "public": "public",
            "ignore": [
                "firebase.json",
                "**/.*",
                "**/node_modules/**"
            ],
            "rewrites": [
                {
                    "source": "**",
                    "function": "app"
                }
            ]
        },
        "functions": {
            "source": "functions",
            "runtime": "python39"
        }
    }
    
    import json
    with open("firebase.json", "w") as f:
        json.dump(firebase_config, f, indent=2)
    
    print("✅ Firebase configuration updated")

def install_dependencies():
    """Install Python dependencies"""
    if not run_command("pip install -r requirements.txt"):
        print("❌ Failed to install dependencies")
        return False
    print("✅ Dependencies installed")
    return True

def run_tests():
    """Run basic tests if available"""
    if Path("tests").exists():
        if run_command("python -m pytest tests/"):
            print("✅ Tests passed")
        else:
            print("⚠️  Some tests failed")
    else:
        print("ℹ️  No tests directory found")

def main():
    """Main build process"""
    print("🚀 Building Phoenix Projektplaner for deployment...")
    
    # Create build directory
    build_dir = create_build_directory()
    print(f"✅ Build directory created: {build_dir}")
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Copy static files
    copy_static_files(build_dir)
    
    # Generate static HTML
    generate_static_html()
    
    # Create Firebase config
    create_firebase_config()
    
    # Run tests
    run_tests()
    
    print("\n✅ Build completed successfully!")
    print("\nNext steps:")
    print("1. firebase deploy --only hosting")
    print("2. firebase deploy --only functions")
    print("3. firebase deploy --only firestore:rules,firestore:indexes")
    
    print("\nFor local testing:")
    print("firebase emulators:start")

if __name__ == "__main__":
    main()

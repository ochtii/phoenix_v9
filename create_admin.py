#!/usr/bin/env python3
"""
Phoenix Admin Setup Script
Creates the first admin user for the Phoenix application.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User
from flask import current_app
import getpass

def create_admin():
    """Create the first admin user."""
    app = create_app()
    
    with app.app_context():
        print("🔥 Phoenix Admin Setup")
        print("=" * 50)
        
        # Check if admin already exists
        try:
            db = current_app.db
            # Simplified check - just try to get all users and check roles
            users_query = db.collection('users')
            existing_users = []
            try:
                existing_users = list(users_query.stream())
            except:
                pass  # Database might be empty
            
            admin_exists = False
            for user_doc in existing_users:
                user_data = user_doc.to_dict()
                if user_data.get('role') in ['Admin', 'Webmaster']:
                    admin_exists = True
                    print("❌ Admin user already exists!")
                    print(f"   Username: {user_data.get('username')}")
                    print(f"   Email: {user_data.get('email')}")
                    print(f"   Role: {user_data.get('role')}")
                    return
            
            if not admin_exists:
                print("✅ No admin found, creating first admin...")
                
        except Exception as e:
            print(f"⚠️  Database connection warning: {e}")
            print("Continuing with admin creation...")
            print()
        
        print("Creating the first admin user...")
        print()
        
        # Get admin details
        while True:
            username = input("👤 Admin Username: ").strip()
            if username and len(username) >= 3:
                # Simplified username check
                username_exists = False
                try:
                    users_query = db.collection('users')
                    for user_doc in users_query.stream():
                        user_data = user_doc.to_dict()
                        if user_data.get('username') == username:
                            username_exists = True
                            break
                except:
                    pass  # If check fails, continue anyway
                
                if username_exists:
                    print("❌ Username already exists!")
                    continue
                break
            else:
                print("❌ Username must be at least 3 characters!")
        
        while True:
            email = input("📧 Admin Email: ").strip().lower()
            if email and '@' in email and '.' in email:
                # Simplified email check
                email_exists = False
                try:
                    users_query = db.collection('users')
                    for user_doc in users_query.stream():
                        user_data = user_doc.to_dict()
                        if user_data.get('email') == email:
                            email_exists = True
                            break
                except:
                    pass  # If check fails, continue anyway
                
                if email_exists:
                    print("❌ Email already exists!")
                    continue
                break
            else:
                print("❌ Please enter a valid email address!")
        
        while True:
            password = getpass.getpass("🔒 Admin Password: ")
            if len(password) >= 8:
                confirm_password = getpass.getpass("🔒 Confirm Password: ")
                if password == confirm_password:
                    break
                else:
                    print("❌ Passwords don't match!")
            else:
                print("❌ Password must be at least 8 characters!")
        
        # Create admin user
        try:
            from firebase_admin import auth
            
            # Create Firebase Auth user
            firebase_user = auth.create_user(
                email=email,
                password=password,
                display_name=username,
                email_verified=True
            )
            
            # Create admin user object
            admin_user = User(
                uid=firebase_user.uid,
                username=username,
                email=email,
                password=password,
                role='Admin'
            )
            
            # Save to Firestore
            db.collection('users').document(admin_user.uid).set(admin_user.to_dict())
            
            print()
            print("✅ Admin user created successfully!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Role: Admin")
            print(f"   Firebase UID: {firebase_user.uid}")
            print()
            print("🚀 You can now log in to the admin panel!")
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            # Clean up Firebase user if Firestore failed
            try:
                if 'firebase_user' in locals():
                    auth.delete_user(firebase_user.uid)
            except:
                pass

if __name__ == '__main__':
    create_admin()

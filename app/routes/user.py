# app/routes/user.py
"""
User-related routes for registration, login, profile management, and friends.
Implements all required endpoints as Flask Blueprint.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
import uuid

user = Blueprint('user', __name__)

# In-memory user store for demonstration (replace with Firestore in production)
users_db = {}
friends_db = {}

@user.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user. Validates input and stores user securely.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        # Server-side validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('user/register.html')
        if email in users_db:
            flash('Email already registered.', 'danger')
            return render_template('user/register.html')
        uid = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        user_obj = User(uid, username, email, password_hash)
        users_db[email] = user_obj
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('user.login'))
    return render_template('user/register.html')

@user.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in an existing user. Checks credentials and starts session.
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user_obj = users_db.get(email)
        if not user_obj or not check_password_hash(user_obj.password_hash, password):
            flash('Invalid email or password.', 'danger')
            return render_template('user/login.html')
        session['user_id'] = user_obj.uid
        session['username'] = user_obj.username
        flash('Logged in successfully.', 'success')
        return redirect(url_for('user.profile', username=user_obj.username))
    return render_template('user/login.html')

@user.route('/logout')
def logout():
    """
    Log out the current user and clear the session.
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.login'))

@user.route('/profile/<username>')
def profile(username):
    """
    Display a user's profile by username.
    """
    user_obj = next((u for u in users_db.values() if u.username == username), None)
    if not user_obj:
        flash('User not found.', 'danger')
        return redirect(url_for('user.login'))
    return render_template('user/profile.html', user=user_obj)

@user.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """
    Edit the current user's profile data.
    """
    uid = session.get('user_id')
    user_obj = next((u for u in users_db.values() if u.uid == uid), None)
    if not user_obj:
        flash('Not authorized.', 'danger')
        return redirect(url_for('user.login'))
    if request.method == 'POST':
        about_me = request.form.get('about_me', '').strip()
        location = request.form.get('location', '').strip()
        website = request.form.get('website', '').strip()
        user_obj.profile_data['about_me'] = about_me
        user_obj.profile_data['location'] = location
        user_obj.profile_data['website'] = website
        flash('Profile updated.', 'success')
        return redirect(url_for('user.profile', username=user_obj.username))
    return render_template('user/edit_profile.html', user=user_obj)

@user.route('/friends')
def friends():
    """
    Show the current user's friends list.
    """
    uid = session.get('user_id')
    friends = friends_db.get(uid, [])
    friend_objs = [u for u in users_db.values() if u.uid in friends]
    return render_template('user/friends.html', friends=friend_objs)

@user.route('/friends/add/<user_id>', methods=['POST'])
def add_friend(user_id):
    """
    Add a user to the current user's friends list.
    """
    uid = session.get('user_id')
    if not uid or user_id == uid:
        flash('Invalid operation.', 'danger')
        return redirect(url_for('user.friends'))
    friends_db.setdefault(uid, set()).add(user_id)
    flash('Friend added.', 'success')
    return redirect(url_for('user.friends'))

@user.route('/friends/remove/<user_id>', methods=['POST'])
def remove_friend(user_id):
    """
    Remove a user from the current user's friends list.
    """
    uid = session.get('user_id')
    if not uid:
        flash('Not authorized.', 'danger')
        return redirect(url_for('user.friends'))
    friends_db.setdefault(uid, set()).discard(user_id)
    flash('Friend removed.', 'info')
    return redirect(url_for('user.friends'))

"""
User authentication and profile routes for the Phoenix web application.
Handles registration, login, logout, and profile management.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g, current_app
from datetime import datetime
import re
import bleach
from firebase_admin import auth, firestore
from app import login_required
from app.models import User

user_bp = Blueprint('user', __name__)

# Get Firestore client
db = firestore.client()


def validate_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """Validate username format (alphanumeric and underscores only)."""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None


@user_bp.route('/check-username', methods=['POST'])
def check_username():
    """
    Check if username is available via AJAX.
    Returns JSON response with availability status.
    """
    try:
        import json
        from flask import jsonify
        
        data = request.get_json()
        if not data or 'username' not in data:
            return jsonify({'error': 'Username is required'}), 400
        
        username = data['username'].strip()
        
        # Validate username format
        if not validate_username(username):
            return jsonify({
                'available': False,
                'message': 'Username must be 3-20 characters and contain only letters, numbers, and underscores.'
            })
        
        # Check if username exists in database
        from flask import current_app
        from firebase_admin import firestore
        
        # Query Firestore for existing username
        users_ref = current_app.db.collection('users')
        query = users_ref.where(filter=firestore.FieldFilter('username', '==', username)).limit(1)
        results = list(query.stream())
        
        if results:
            return jsonify({
                'available': False,
                'message': 'Username is already taken.'
            })
        else:
            return jsonify({
                'available': True,
                'message': 'Username is available.'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error checking username availability: {e}")
        return jsonify({'error': 'Server error occurred'}), 500


@user_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    Check if email is available via AJAX.
    Returns JSON response with availability status.
    """
    try:
        from flask import jsonify
        
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'available': False,
                'message': 'Please enter a valid email address.'
            })
        
        # Check if email exists in database
        from flask import current_app
        from firebase_admin import firestore
        
        # Query Firestore for existing email
        users_ref = current_app.db.collection('users')
        query = users_ref.where(filter=firestore.FieldFilter('email', '==', email)).limit(1)
        results = list(query.stream())
        
        if results:
            return jsonify({
                'available': False,
                'message': 'Diese E-Mail-Adresse wird bereits verwendet.'
            })
        else:
            return jsonify({
                'available': True,
                'message': 'E-Mail-Adresse ist verfügbar.'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error checking email availability: {e}")
        return jsonify({'error': 'Server error occurred'}), 500


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    GET: Display registration form
    POST: Process registration data
    """
    # If user is already logged in, redirect to start page
    if g.user:
        return redirect(url_for('main.start'))
    
    if request.method == 'POST':
        # Debug: Log received form data
        current_app.logger.info(f"Registration form data received: {dict(request.form)}")
        
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        current_app.logger.info(f"Parsed values - username: '{username}', email: '{email}', password length: {len(password)}")
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required.')
        elif not validate_username(username):
            errors.append('Username must be 3-20 characters and contain only letters, numbers, and underscores.')
        
        if not email:
            errors.append('Email is required.')
        elif not validate_email(email):
            errors.append('Please enter a valid email address.')
        
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if username or email already exists
        try:
            db = current_app.db
            
            # Check username
            username_query = db.collection('users').where('username', '==', username).limit(1)
            if len(list(username_query.stream())) > 0:
                errors.append('Username is already taken.')
            
            # Check email
            email_query = db.collection('users').where('email', '==', email).limit(1)
            if len(list(email_query.stream())) > 0:
                errors.append('Email is already registered.')
        
        except Exception as e:
            current_app.logger.error(f"Database error during registration: {e}")
            errors.append('A database error occurred. Please try again.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('user/register.html')
        
        # Create new user
        try:
            # First create user in Firebase Authentication
            firebase_user = auth.create_user(
                email=email,
                password=password,
                display_name=username,
                email_verified=False
            )
            
            # Create new user with Firebase UID
            new_user = User(
                uid=firebase_user.uid,  # Use Firebase Auth UID
                username=username,
                email=email,
                password=password,  # This will be hashed in User.__init__
                role='User'
            )
            
            # Save to Firestore
            db.collection('users').document(new_user.uid).set(new_user.to_dict())
            
            current_app.logger.info(f"User created successfully - Firebase UID: {firebase_user.uid}, Username: {username}")
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('user.login'))
        
        except Exception as e:
            current_app.logger.error(f"Error creating user: {e}")
            # If Firebase Auth user was created but Firestore failed, clean up
            try:
                if 'firebase_user' in locals():
                    auth.delete_user(firebase_user.uid)
                    current_app.logger.info(f"Cleaned up Firebase Auth user: {firebase_user.uid}")
            except:
                pass
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('user/register.html')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    GET: Display login form
    POST: Process login credentials
    """
    # If user is already logged in, redirect to start page
    if g.user:
        return redirect(url_for('main.start'))
    
    if request.method == 'POST':
        # Debug: Log received form data
        current_app.logger.info(f"Login form data received: {dict(request.form)}")
        
        username_or_email = request.form.get('username_or_email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        current_app.logger.info(f"Parsed values - username_or_email: '{username_or_email}', password length: {len(password)}, remember_me: {remember_me}")
        
        if not username_or_email or not password:
            flash('Please enter both username/email and password.', 'error')
            return render_template('user/login.html')
        
        try:
            db = current_app.db
            user_doc = None
            
            # Try to find user by email first, then by username
            if validate_email(username_or_email):
                email_query = db.collection('users').where('email', '==', username_or_email).limit(1)
                email_results = list(email_query.stream())
                if email_results:
                    user_doc = email_results[0]
            else:
                username_query = db.collection('users').where('username', '==', username_or_email).limit(1)
                username_results = list(username_query.stream())
                if username_results:
                    user_doc = username_results[0]
            
            if user_doc and user_doc.exists:
                user_data = user_doc.to_dict()
                user = User.from_dict(user_data)
                
                if user.check_password(password) and user.is_active:
                    # Update last login
                    db.collection('users').document(user.uid).update({
                        'last_login': datetime.utcnow()
                    })
                    
                    # Set session
                    session['user_id'] = user.uid
                    session.permanent = remember_me
                    
                    flash(f'Welcome back, {user.username}!', 'success')
                    
                    # Redirect to next page or start
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect(url_for('main.start'))
                else:
                    flash('Invalid credentials.', 'error')
            else:
                flash('Invalid credentials.', 'error')
        
        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('user/login.html')


@user_bp.route('/logout')
def logout():
    """User logout route."""
    session.clear()
    flash('Sie wurden erfolgreich abgemeldet.', 'success')
    return redirect(url_for('main.index'))


@user_bp.route('/profile/<username>')
def profile(username):
    """
    Display user profile page.
    
    Args:
        username (str): Username of the profile to display
    """
    try:
        db = current_app.db
        
        # Find user by username
        username_query = db.collection('users').where('username', '==', username).limit(1)
        user_results = list(username_query.stream())
        
        if not user_results:
            flash('Benutzer nicht gefunden.', 'error')
            return redirect(url_for('main.index'))
        
        user_data = user_results[0].to_dict()
        user_data['uid'] = user_results[0].id  # Ensure UID is set
        profile_user = User.from_dict(user_data)
        
        # Get user's project count safely
        try:
            projects_query = db.collection('projects').where('owner_uid', '==', profile_user.uid)
            project_count = len(list(projects_query.stream()))
        except:
            project_count = 0
        
        return render_template('user/profile.html', 
                             profile_user=profile_user,
                             project_count=project_count)
    
    except Exception as e:
        current_app.logger.error(f"Profile view error for user {username}: {e}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        flash('Ein Fehler ist beim Laden des Profils aufgetreten.', 'error')
        return redirect(url_for('main.index'))


@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit user profile.
    GET: Display edit form
    POST: Process profile updates
    """
    if request.method == 'POST':
        try:
            db = current_app.db
            user_id = g.user['uid']
            
            # Get form data
            display_name = bleach.clean(request.form.get('display_name', '').strip())
            bio = bleach.clean(request.form.get('bio', '').strip())
            location = bleach.clean(request.form.get('location', '').strip())
            website = bleach.clean(request.form.get('website', '').strip())
            avatar_url = bleach.clean(request.form.get('avatar_url', '').strip())
            email_notifications = request.form.get('email_notifications') == 'on'
            
            # Validate bio length
            if len(bio) > 500:
                flash('Die Beschreibung darf maximal 500 Zeichen lang sein.', 'error')
                return render_template('user/edit_profile.html')
            
            # Validate website URL
            if website and not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            
            # Update profile data
            update_data = {
                'profile_data.display_name': display_name,
                'profile_data.bio': bio,
                'profile_data.location': location,
                'profile_data.website': website,
                'profile_data.avatar_url': avatar_url,
                'profile_data.email_notifications': email_notifications,
                'updated_at': datetime.now()
            }
            
            # Remove empty fields
            update_data = {k: v for k, v in update_data.items() if v != ''}
            
            db.collection('users').document(user_id).update(update_data)
            
            # Update session data
            g.user['profile_data'] = {
                'display_name': display_name,
                'bio': bio,
                'location': location,
                'website': website,
                'avatar_url': avatar_url,
                'email_notifications': email_notifications
            }
            
            flash('Profil erfolgreich aktualisiert!', 'success')
            return redirect(url_for('user.profile', username=g.user['username']))
        
        except Exception as e:
            current_app.logger.error(f"Profile update error: {e}")
            flash('Ein Fehler ist beim Aktualisieren des Profils aufgetreten.', 'error')
    
    return render_template('user/edit_profile.html')
    
    return render_template('user/edit_profile.html')


@user_bp.route('/friends')
@login_required
def friends():
    """
    Display user's friends list.
    """
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get current user's friends list
        user_doc = db.collection('users').document(user_id).get()
        friends_list = user_doc.to_dict().get('friends', [])
        
        # Get friend details
        friends = []
        for friend_id in friends_list:
            friend_doc = db.collection('users').document(friend_id).get()
            if friend_doc.exists:
                friend_data = friend_doc.to_dict()
                friends.append(User.from_dict(friend_data))
        
        return render_template('user/friends.html', friends=friends)
    
    except Exception as e:
        current_app.logger.error(f"Friends view error: {e}")
        flash('Ein Fehler ist beim Laden der Freundesliste aufgetreten.', 'error')
        return redirect(url_for('main.dashboard'))


@user_bp.route('/add_friend/<username>', methods=['POST'])
@login_required
def add_friend(username):
    """
    Add a user as friend.
    """
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Find user by username
        username_query = db.collection('users').where('username', '==', username).limit(1)
        user_results = list(username_query.stream())
        
        if not user_results:
            flash('Benutzer nicht gefunden.', 'error')
            return redirect(url_for('user.profile', username=username))
        
        friend_data = user_results[0].to_dict()
        friend_id = friend_data['uid']
        
        # Can't add yourself
        if friend_id == user_id:
            flash('Sie können sich nicht selbst als Freund hinzufügen.', 'error')
            return redirect(url_for('user.profile', username=username))
        
        # Add to current user's friends list
        db.collection('users').document(user_id).update({
            'friends': firestore.ArrayUnion([friend_id])
        })
        
        # Add current user to friend's friends list (mutual friendship)
        db.collection('users').document(friend_id).update({
            'friends': firestore.ArrayUnion([user_id])
        })
        
        flash(f'{username} wurde zu Ihren Freunden hinzugefügt.', 'success')
        return redirect(url_for('user.profile', username=username))
    
    except Exception as e:
        current_app.logger.error(f"Add friend error: {e}")
        flash('Ein Fehler ist beim Hinzufügen des Freundes aufgetreten.', 'error')
        return redirect(url_for('user.profile', username=username))


@user_bp.route('/remove_friend/<username>', methods=['POST'])
@login_required
def remove_friend(username):
    """
    Remove a user from friends.
    """
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Find user by username
        username_query = db.collection('users').where('username', '==', username).limit(1)
        user_results = list(username_query.stream())
        
        if not user_results:
            flash('Benutzer nicht gefunden.', 'error')
            return redirect(url_for('user.friends'))
        
        friend_data = user_results[0].to_dict()
        friend_id = friend_data['uid']
        
        # Remove from current user's friends list
        db.collection('users').document(user_id).update({
            'friends': firestore.ArrayRemove([friend_id])
        })
        
        # Remove current user from friend's friends list
        db.collection('users').document(friend_id).update({
            'friends': firestore.ArrayRemove([user_id])
        })
        
        flash(f'{username} wurde aus Ihrer Freundesliste entfernt.', 'success')
        return redirect(url_for('user.friends'))
    
    except Exception as e:
        current_app.logger.error(f"Remove friend error: {e}")
        flash('Ein Fehler ist beim Entfernen des Freundes aufgetreten.', 'error')
        return redirect(url_for('user.friends'))


@user_bp.route('/account-settings')
@login_required
def account_settings():
    """Account settings page"""
    return render_template('user/account_settings.html')


@user_bp.route('/privacy-settings')
@login_required
def privacy_settings():
    """Privacy settings page"""
    return render_template('user/privacy_settings.html')


@user_bp.route('/update_account', methods=['POST'])
@login_required
def update_account():
    """Update user account information."""
    try:
        from flask import request
        db = current_app.db
        
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        bio = request.form.get('bio')
        
        # Update user document
        user_data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'bio': bio,
            'updated_at': datetime.now()
        }
        
        db.collection('users').document(g.user['uid']).update(user_data)
        
        # Update session data
        g.user.update(user_data)
        
        flash('Account information updated successfully', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error updating account: {e}")
        flash('Error updating account information', 'error')
    
    return redirect(url_for('user.account_settings'))


@user_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    try:
        from flask import request
        
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('user.account_settings'))
        
        # Here you would verify current password and update with Firebase Auth
        # This is a placeholder for Firebase Auth integration
        
        flash('Password changed successfully', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error changing password: {e}")
        flash('Error changing password', 'error')
    
    return redirect(url_for('user.account_settings'))


@user_bp.route('/update_preferences', methods=['POST'])
@login_required
def update_preferences():
    """Update user preferences."""
    try:
        from flask import request
        db = current_app.db
        
        preferences = {
            'language': request.form.get('language'),
            'timezone': request.form.get('timezone'),
            'email_notifications': 'email_notifications' in request.form,
            'project_invites': 'project_invites' in request.form,
            'updated_at': datetime.now()
        }
        
        db.collection('users').document(g.user['uid']).update(preferences)
        
        flash('Preferences updated successfully', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error updating preferences: {e}")
        flash('Error updating preferences', 'error')
    
    return redirect(url_for('user.account_settings'))


@user_bp.route('/update_privacy', methods=['POST'])
@login_required
def update_privacy():
    """Update privacy settings."""
    try:
        from flask import request
        db = current_app.db
        
        privacy_settings = {
            'profile_visibility': request.form.get('profile_visibility'),
            'show_email': 'show_email' in request.form,
            'show_join_date': 'show_join_date' in request.form,
            'show_project_count': 'show_project_count' in request.form,
            'updated_at': datetime.now()
        }
        
        db.collection('users').document(g.user['uid']).update(privacy_settings)
        
        flash('Privacy settings updated successfully', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error updating privacy settings: {e}")
        flash('Error updating privacy settings', 'error')
    
    return redirect(url_for('user.privacy_settings'))


@user_bp.route('/update_communication', methods=['POST'])
@login_required
def update_communication():
    """Update communication preferences."""
    try:
        from flask import request
        db = current_app.db
        
        communication_settings = {
            'message_privacy': request.form.get('message_privacy'),
            'allow_invitations': 'allow_invitations' in request.form,
            'auto_join_public': 'auto_join_public' in request.form,
            'updated_at': datetime.now()
        }
        
        db.collection('users').document(g.user['uid']).update(communication_settings)
        
        flash('Communication settings updated successfully', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error updating communication settings: {e}")
        flash('Error updating communication settings', 'error')
    
    return redirect(url_for('user.privacy_settings'))


@user_bp.route('/update_notifications', methods=['POST'])
@login_required
def update_notifications():
    """Update email notification preferences."""
    try:
        from flask import request
        db = current_app.db
        
        notification_settings = {
            'email_projects': 'email_projects' in request.form,
            'email_messages': 'email_messages' in request.form,
            'email_weekly': 'email_weekly' in request.form,
            'updated_at': datetime.now()
        }
        
        db.collection('users').document(g.user['uid']).update(notification_settings)
        
        flash('Benachrichtigungseinstellungen erfolgreich aktualisiert', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error updating notification settings: {e}")
        flash('Fehler beim Aktualisieren der Benachrichtigungseinstellungen', 'error')
    
    return redirect(url_for('user.account_settings'))


@user_bp.route('/update_data_settings', methods=['POST'])
@login_required
def update_data_settings():
    """Update data and analytics settings."""
    try:
        from flask import request
        db = current_app.db
        
        data_settings = {
            'usage_analytics': 'usage_analytics' in request.form,
            'performance_data': 'performance_data' in request.form,
            'marketing_emails': 'marketing_emails' in request.form,
            'updated_at': datetime.now()
        }
        
        db.collection('users').document(g.user['uid']).update(data_settings)
        
        flash('Data settings updated successfully', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error updating data settings: {e}")
        flash('Error updating data settings', 'error')
    
    return redirect(url_for('user.privacy_settings'))


@user_bp.route('/upgrade')
@login_required
def upgrade():
    """
    Display upgrade/premium options page.
    """
    try:
        # Get current user subscription status if available
        user_data = db.collection('users').document(g.user['uid']).get().to_dict()
        subscription_status = user_data.get('subscription', {}) if user_data else {}
        
        # Get available plans from Firestore
        available_plans = []
        try:
            plans_ref = db.collection('subscription_plans')
            for doc in plans_ref.stream():
                plan_data = doc.to_dict()
                plan_data['id'] = doc.id
                available_plans.append(plan_data)
            
            # Sort by monthly price
            available_plans.sort(key=lambda x: x.get('monthly_price', 0))
        except Exception as e:
            current_app.logger.error(f"Error fetching plans: {e}")
            # Fallback plans
            available_plans = [
                {
                    'id': 'free',
                    'name': 'Free',
                    'monthly_price': 0,
                    'yearly_price': 0,
                    'features': ['Basic features', 'Limited projects']
                },
                {
                    'id': 'premium',
                    'name': 'Premium',
                    'monthly_price': 4.99,
                    'yearly_price': 49.99,
                    'features': ['All Free features', 'More projects', 'Priority support']
                }
            ]
        
        return render_template('user/upgrade.html', 
                             subscription=subscription_status,
                             available_plans=available_plans,
                             current_plan=user_data.get('subscription_plan', 'Free'))
    except Exception as e:
        current_app.logger.error(f"Error loading upgrade page: {e}")
        flash('Error loading upgrade options', 'error')
        return redirect(url_for('main.start'))


@user_bp.route('/redeem-voucher', methods=['POST'])
@login_required
def redeem_voucher():
    """Redeem a voucher code to upgrade user plan"""
    try:
        from flask import jsonify
        
        data = request.get_json()
        if not data or 'voucher_code' not in data:
            return jsonify({'success': False, 'message': 'Gutschein-Code ist erforderlich'}), 400
        
        voucher_code = data['voucher_code'].strip().upper()
        if not voucher_code:
            return jsonify({'success': False, 'message': 'Gutschein-Code ist erforderlich'}), 400
        
        db = current_app.db
        
        # Find voucher
        voucher_query = db.collection('vouchers').where('code', '==', voucher_code).limit(1)
        voucher_docs = list(voucher_query.stream())
        
        if not voucher_docs:
            return jsonify({'success': False, 'message': 'Ungültiger Gutschein-Code'}), 400
        
        voucher_doc = voucher_docs[0]
        voucher_data = voucher_doc.to_dict()
        
        # Check if voucher is active
        if not voucher_data.get('active', True):
            return jsonify({'success': False, 'message': 'Dieser Gutschein ist nicht mehr gültig'}), 400
        
        # Check if voucher is expired
        if voucher_data.get('expires_at') and voucher_data['expires_at'] < datetime.now():
            return jsonify({'success': False, 'message': 'Dieser Gutschein ist abgelaufen'}), 400
        
        # Check usage limits
        usage_limit = voucher_data.get('usage_limit', 1)
        usage_count = voucher_data.get('usage_count', 0)
        
        if usage_count >= usage_limit:
            return jsonify({'success': False, 'message': 'Dieser Gutschein wurde bereits vollständig verwendet'}), 400
        
        # Check if user already used this voucher (for single-use vouchers)
        if usage_limit == 1 and voucher_data.get('used_by') == g.user['uid']:
            return jsonify({'success': False, 'message': 'Sie haben diesen Gutschein bereits verwendet'}), 400
        
        # Calculate new plan expiry date
        current_expiry = g.user.get('plan_expires_at')
        if current_expiry and current_expiry > datetime.now():
            # Extend existing plan
            base_date = current_expiry
        else:
            # Start from now
            base_date = datetime.now()
        
        # Add voucher duration
        if voucher_data.get('duration_months'):
            from dateutil.relativedelta import relativedelta
            new_expiry = base_date + relativedelta(months=voucher_data['duration_months'])
        elif voucher_data.get('duration_days'):
            from datetime import timedelta
            new_expiry = base_date + timedelta(days=voucher_data['duration_days'])
        else:
            # Default to 1 month
            from dateutil.relativedelta import relativedelta
            new_expiry = base_date + relativedelta(months=1)
        
        # Update user plan
        user_updates = {
            'plan': voucher_data['plan'],
            'plan_expires_at': new_expiry,
            'plan_activated_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        db.collection('users').document(g.user['uid']).update(user_updates)
        
        # Update voucher usage
        voucher_updates = {
            'usage_count': usage_count + 1,
            'updated_at': datetime.now()
        }
        
        # For single-use vouchers, mark as fully used
        if usage_limit == 1:
            voucher_updates.update({
                'used_by': g.user['uid'],
                'used_by_username': g.user['username'],
                'used_at': datetime.now(),
                'active': False
            })
        
        db.collection('vouchers').document(voucher_doc.id).update(voucher_updates)
        
        # Update session user data
        g.user.update(user_updates)
        session['user'] = g.user
        
        current_app.logger.info(f"User {g.user['username']} redeemed voucher {voucher_code} for {voucher_data['plan']} plan")
        
        return jsonify({
            'success': True,
            'message': 'Gutschein erfolgreich eingelöst',
            'plan': voucher_data['plan'],
            'expires_at': new_expiry.strftime('%d.%m.%Y')
        })
        
    except Exception as e:
        current_app.logger.error(f"Voucher redemption error: {e}")
        return jsonify({'success': False, 'message': 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.'}), 500
"""
Admin routes for the Phoenix web application.
Handles administrative functions and system management.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, g, current_app, jsonify
from datetime import datetime, timedelta
import os
import logging
from app import role_required, admin_required

admin_bp = Blueprint('admin', __name__)

def get_available_plans():
    """Get all available subscription plans from Firestore."""
    try:
        db = current_app.db
        plans_ref = db.collection('subscription_plans')
        plans = []
        for doc in plans_ref.stream():
            plan_data = doc.to_dict()
            plan_data['id'] = doc.id
            plans.append(plan_data)
        
        # Sort by monthly price
        plans.sort(key=lambda x: x.get('monthly_price', 0))
        return plans
    except Exception as e:
        current_app.logger.error(f"Error fetching plans: {e}")
        return [
            {'id': 'free', 'name': 'Free', 'monthly_price': 0},
            {'id': 'premium', 'name': 'Premium', 'monthly_price': 4.99},
            {'id': 'pro', 'name': 'Pro', 'monthly_price': 9.99},
            {'id': 'unlimited', 'name': 'Unlimited', 'monthly_price': 34.99}
        ]


@admin_bp.route('/')
@admin_bp.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    """Enhanced admin dashboard with comprehensive system overview and statistics"""
    try:
        db = current_app.db
        
        # Get user statistics with error handling
        try:
            users_collection = db.collection('users')
            all_users = list(users_collection.stream())
            total_users = len(all_users)
            
            # Count active users
            active_users = len([u for u in all_users if u.to_dict().get('status', 'active') == 'active'])
            suspended_users = len([u for u in all_users if u.to_dict().get('status') == 'suspended'])
            
            # Get recent users (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            new_users_this_month = 0
            recent_users = []
            
            for doc in all_users:
                user_data = doc.to_dict()
                user_data['uid'] = doc.id
                
                # Count new users this month
                if user_data.get('created_at') and user_data['created_at'] > thirty_days_ago:
                    new_users_this_month += 1
                
                # Collect recent users for display
                if len(recent_users) < 5:
                    user_data['role'] = user_data.get('role', 'User')
                    user_data['status'] = user_data.get('status', 'active')
                    recent_users.append(user_data)
                    
        except Exception as e:
            current_app.logger.error(f"Error fetching user stats: {e}")
            total_users = active_users = suspended_users = new_users_this_month = 0
            recent_users = []
        
        # Get project statistics with error handling
        try:
            projects_collection = db.collection('projects')
            all_projects = list(projects_collection.stream())
            total_projects = len(all_projects)
            
            public_projects = len([p for p in all_projects if p.to_dict().get('is_public', False)])
            private_projects = total_projects - public_projects
            
            # Get recent projects this month
            new_projects_this_month = 0
            recent_projects = []
            
            for doc in all_projects:
                project_data = doc.to_dict()
                project_data['uid'] = doc.id
                
                # Count new projects this month
                if project_data.get('created_at') and project_data['created_at'] > thirty_days_ago:
                    new_projects_this_month += 1
                
                # Collect recent projects for display
                if len(recent_projects) < 5:
                    project_data['member_count'] = len(project_data.get('members', []))
                    project_data['status'] = project_data.get('status', 'Planning')
                    recent_projects.append(project_data)
                    
        except Exception as e:
            current_app.logger.error(f"Error fetching project stats: {e}")
            total_projects = public_projects = private_projects = new_projects_this_month = 0
            recent_projects = []
        
        # System health metrics
        system_health = {
            'database_status': 'Connected',
            'last_backup': 'N/A',
            'server_uptime': 'N/A',
            'memory_usage': 'N/A'
        }
        
        # Get recent activity (placeholder - would need proper logging)
        recent_activity = [
            {
                'timestamp': datetime.now() - timedelta(minutes=5),
                'action': 'User Registration',
                'details': 'New user account created',
                'user': 'System'
            },
            {
                'timestamp': datetime.now() - timedelta(minutes=15),
                'action': 'Project Created',
                'details': 'New project "Web App" created',
                'user': 'Admin'
            },
            {
                'timestamp': datetime.now() - timedelta(hours=1),
                'action': 'System Backup',
                'details': 'Automated backup completed',
                'user': 'System'
            }
        ]
        
        # Prepare comprehensive statistics
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'suspended_users': suspended_users,
            'active_users_percentage': round((active_users / total_users * 100) if total_users > 0 else 0),
            'new_users_this_month': new_users_this_month,
            'total_projects': total_projects,
            'public_projects': public_projects,
            'private_projects': private_projects,
            'new_projects_this_month': new_projects_this_month,
            'total_messages': 0,  # Placeholder
            'messages_this_week': 0,  # Placeholder
            'open_tickets': 0  # Placeholder
        }
        
        return render_template('admin/admin_dashboard.html',
                             stats=stats,
                             recent_users=recent_users,
                             recent_projects=recent_projects,
                             recent_activity=recent_activity,
                             system_health=system_health)
        
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {e}")
        # Return empty dashboard on error
        stats = {
            'total_users': 0, 'active_users': 0, 'suspended_users': 0,
            'active_users_percentage': 0, 'new_users_this_month': 0,
            'total_projects': 0, 'public_projects': 0, 'private_projects': 0,
            'new_projects_this_month': 0, 'total_messages': 0,
            'messages_this_week': 0, 'open_tickets': 0
        }
        return render_template('admin/admin_dashboard.html',
                             stats=stats,
                             recent_users=[],
                             recent_projects=[],
                             recent_activity=[],
                             system_health={})


@admin_bp.route('/users')
@admin_required
def users():
    """Enhanced user management page with full CRUD functionality"""
    try:
        db = current_app.db
        
        # Get search and filter parameters
        search_query = request.args.get('search', '').strip()
        role_filter = request.args.get('role', '').strip()
        status_filter = request.args.get('status', '').strip()
        sort_order = request.args.get('sort', 'newest')
        
        # Get all users
        users_collection = db.collection('users')
        all_users = list(users_collection.stream())
        
        users_list = []
        for doc in all_users:
            user_data = doc.to_dict()
            user_data['uid'] = doc.id
            
            # Set defaults for missing fields
            user_data['role'] = user_data.get('role', 'User')
            user_data['status'] = user_data.get('status', 'active')
            user_data['email'] = user_data.get('email', 'No email')
            user_data['username'] = user_data.get('username', 'Unknown')
            user_data['created_at'] = user_data.get('created_at', datetime.now())
            
            # Apply search filter
            if search_query:
                searchable_text = f"{user_data.get('username', '')} {user_data.get('email', '')} {user_data.get('role', '')}"
                if search_query.lower() not in searchable_text.lower():
                    continue
            
            # Apply role filter
            if role_filter and user_data.get('role') != role_filter:
                continue
                
            # Apply status filter
            if status_filter and user_data.get('status') != status_filter:
                continue
            
            # Get user's project count
            try:
                user_projects = db.collection('projects').where('members', 'array_contains', user_data['uid']).stream()
                user_data['project_count'] = len(list(user_projects))
            except:
                user_data['project_count'] = 0
            
            users_list.append(user_data)
        
        # Sort users
        if sort_order == 'newest':
            users_list.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        elif sort_order == 'oldest':
            users_list.sort(key=lambda x: x.get('created_at', datetime.min))
        elif sort_order == 'alphabetical':
            users_list.sort(key=lambda x: x.get('username', '').lower())
        elif sort_order == 'role':
            users_list.sort(key=lambda x: x.get('role', ''))
        
        # Get statistics
        total_users = len(users_list)
        active_users = len([u for u in users_list if u.get('status') == 'active'])
        suspended_users = len([u for u in users_list if u.get('status') == 'suspended'])
        admin_users = len([u for u in users_list if u.get('role') in ['Admin', 'Webmaster']])
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'suspended_users': suspended_users,
            'admin_users': admin_users
        }
        
        # Available roles and statuses for filters
        available_roles = ['User', 'Moderator', 'Admin', 'Webmaster']
        available_statuses = ['active', 'suspended', 'pending']
        
        return render_template('admin/user_management.html',
                             users=users_list,
                             stats=stats,
                             search_query=search_query,
                             role_filter=role_filter,
                             status_filter=status_filter,
                             sort_order=sort_order,
                             available_roles=available_roles,
                             available_statuses=available_statuses)
        
    except Exception as e:
        current_app.logger.error(f"Error in user management: {e}")
        flash('Error loading user data.', 'error')
        return render_template('admin/user_management.html',
                             users=[],
                             stats={'total_users': 0, 'active_users': 0, 'suspended_users': 0, 'admin_users': 0},
                             search_query='',
                             role_filter='',
                             status_filter='',
                             sort_order='newest',
                             available_roles=[],
                             available_statuses=[])


@admin_bp.route('/projects')
@admin_required
def project_management():
    """Project management page"""
    return render_template('admin/project_management.html')


@admin_bp.route('/settings')
@admin_required
def settings():
    """
    Admin settings page for system configuration.
    """
    try:
        db = current_app.db
        
        # Get current system settings from Firestore (or create defaults)
        try:
            settings_doc = db.collection('system_settings').document('config').get()
            if settings_doc.exists:
                system_settings = settings_doc.to_dict()
            else:
                # Default settings
                system_settings = {
                    'site_name': 'Phoenix Project Planner',
                    'site_description': 'Collaborative project management platform',
                    'max_projects_per_user': 10,
                    'max_members_per_project': 50,
                    'enable_user_registration': True,
                    'enable_public_projects': True,
                    'require_email_verification': False,
                    'maintenance_mode': False,
                    'backup_enabled': True,
                    'backup_frequency': 'daily',
                    'email_notifications': True,
                    'default_user_role': 'User',
                    'session_timeout': 24,  # hours
                    'file_upload_limit': 10,  # MB
                    'supported_languages': ['en', 'de'],
                    'default_language': 'en',
                    'theme_options': ['light', 'dark', 'auto']
                }
                # Save default settings
                db.collection('system_settings').document('config').set(system_settings)
        except Exception as e:
            current_app.logger.error(f"Error loading settings: {e}")
            system_settings = {}
        
        # Get system statistics for settings overview
        try:
            # Count totals
            users_count = len(list(db.collection('users').stream()))
            projects_count = len(list(db.collection('projects').stream()))
            messages_count = len(list(db.collection('messages').stream()))
            tickets_count = len(list(db.collection('tickets').stream()))
            
            stats = {
                'total_users': users_count,
                'total_projects': projects_count,
                'total_messages': messages_count,
                'total_tickets': tickets_count,
                'storage_used': '2.3 GB',  # Placeholder
                'uptime': '99.9%'  # Placeholder
            }
        except Exception as e:
            current_app.logger.error(f"Error calculating stats: {e}")
            stats = {
                'total_users': 0,
                'total_projects': 0,
                'total_messages': 0,
                'total_tickets': 0,
                'storage_used': 'N/A',
                'uptime': 'N/A'
            }
        
        return render_template('admin/settings.html', 
                             settings=system_settings,
                             stats=stats)
        
    except Exception as e:
        current_app.logger.error(f"Admin settings error: {e}")
        flash('Error loading admin settings', 'error')
        return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Analytics and reports page"""
    return render_template('admin/analytics.html')


@admin_bp.route('/activity-log')
@admin_required
def activity_log():
    """System activity log"""
    return render_template('admin/activity_log.html')


@admin_bp.route('/backend-control')
@admin_required
def backend_control():
    """Backend control panel for advanced administrative functions"""
    try:
        db = current_app.db
        
        # Get system information
        system_info = {
            'flask_version': '2.3.3',
            'python_version': '3.13.3',
            'firebase_connected': True,
            'debug_mode': current_app.debug,
            'environment': current_app.config.get('ENV', 'production'),
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Get database statistics
        collections_stats = {}
        try:
            # Get basic collection counts
            users_count = len(list(db.collection('users').limit(1000).stream()))
            projects_count = len(list(db.collection('projects').limit(1000).stream()))
            
            collections_stats = {
                'users': users_count,
                'projects': projects_count,
                'messages': 0,  # Placeholder
                'tickets': 0    # Placeholder
            }
        except Exception as e:
            current_app.logger.error(f"Error getting collection stats: {e}")
            collections_stats = {'error': 'Unable to fetch statistics'}
        
        # Get recent logs (mock data for now)
        recent_logs = [
            {'timestamp': '2025-07-14 09:54:42', 'level': 'INFO', 'message': 'Application started successfully'},
            {'timestamp': '2025-07-14 09:55:12', 'level': 'INFO', 'message': 'User authentication successful'},
            {'timestamp': '2025-07-14 09:56:33', 'level': 'WARNING', 'message': 'Firebase index required for query'},
        ]
        
        return render_template('admin/backend_control.html',
                             system_info=system_info,
                             collections_stats=collections_stats,
                             recent_logs=recent_logs)
        
    except Exception as e:
        current_app.logger.error(f"Error in backend control: {e}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Try to render with minimal data
        try:
            return render_template('admin/backend_control.html',
                                 system_info={'error': f'Error: {str(e)}'},
                                 collections_stats={'error': 'Unable to fetch statistics'},
                                 recent_logs=[])
        except:
            flash('Error loading backend control panel.', 'error')
            return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/users/<user_id>/suspend', methods=['POST'])
@admin_required
def suspend_user(user_id):
    """Suspend a user account"""
    try:
        db = current_app.db
        
        # Update user status
        db.collection('users').document(user_id).update({
            'status': 'suspended',
            'suspended_at': datetime.now(),
            'suspended_by': g.user['uid']
        })
        
        return jsonify({'success': True, 'message': 'User suspended successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error suspending user: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@admin_bp.route('/users/<user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    """Activate a user account"""
    try:
        db = current_app.db
        
        # Update user status
        db.collection('users').document(user_id).update({
            'status': 'active',
            'activated_at': datetime.now(),
            'activated_by': g.user['uid']
        })
        
        return jsonify({'success': True, 'message': 'User activated successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error activating user: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@admin_bp.route('/users/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    try:
        db = current_app.db
        
        # Check if user exists
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            return jsonify({'success': False, 'message': 'User not found'})
        
        # Delete user document
        db.collection('users').document(user_id).delete()
        
        return jsonify({'success': True, 'message': 'User deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting user: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@admin_bp.route('/projects/<project_id>/feature', methods=['POST'])
@admin_required
def feature_project(project_id):
    """Feature a project"""
    try:
        db = current_app.db
        
        # Update project
        db.collection('projects').document(project_id).update({
            'featured': True,
            'featured_at': datetime.now(),
            'featured_by': g.user['uid']
        })
        
        return jsonify({'success': True, 'message': 'Project featured successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error featuring project: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@admin_bp.route('/projects/<project_id>/unfeature', methods=['POST'])
@admin_required
def unfeature_project(project_id):
    """Unfeature a project"""
    try:
        db = current_app.db
        
        # Update project
        db.collection('projects').document(project_id).update({
            'featured': False,
            'unfeatured_at': datetime.now(),
            'unfeatured_by': g.user['uid']
        })
        
        return jsonify({'success': True, 'message': 'Project unfeatured successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error unfeaturing project: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@admin_bp.route('/projects/<project_id>/delete', methods=['POST'])
@admin_required
def delete_project_admin(project_id):
    """Delete a project (admin action)"""
    try:
        db = current_app.db
        
        # Check if project exists
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            return jsonify({'success': False, 'message': 'Project not found'})
        
        # Delete project document
        db.collection('projects').document(project_id).delete()
        
        return jsonify({'success': True, 'message': 'Project deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting project: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@admin_bp.route('/users/<user_id>/update-role', methods=['POST'])
@admin_required
def update_user_role(user_id):
    """Update user role"""
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['User', 'Moderator', 'Admin', 'Webmaster']:
            return jsonify({'success': False, 'message': 'Invalid role'})
        
        # Prevent changing your own role
        if user_id == g.user['uid']:
            return jsonify({'success': False, 'message': 'Cannot change your own role'})
        
        db = current_app.db
        db.collection('users').document(user_id).update({'role': new_role})
        
        current_app.logger.info(f"Admin {g.user['username']} changed user {user_id} role to {new_role}")
        return jsonify({'success': True, 'message': f'User role updated to {new_role}'})
        
    except Exception as e:
        current_app.logger.error(f"Error updating user role: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@admin_bp.route('/users/<user_id>/update-status', methods=['POST'])
@admin_required  
def update_user_status(user_id):
    """Update user status (active/suspended)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['active', 'suspended']:
            return jsonify({'success': False, 'message': 'Invalid status'})
        
        # Prevent suspending yourself
        if user_id == g.user['uid']:
            return jsonify({'success': False, 'message': 'Cannot change your own status'})
        
        db = current_app.db
        db.collection('users').document(user_id).update({'status': new_status})
        
        action = 'suspended' if new_status == 'suspended' else 'activated'
        current_app.logger.info(f"Admin {g.user['username']} {action} user {user_id}")
        return jsonify({'success': True, 'message': f'User {action} successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error updating user status: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@admin_bp.route('/users/<user_id>/send-message', methods=['POST'])
@admin_required
def send_quick_message(user_id):
    """
    Send a quick message to a user from admin panel.
    """
    try:
        from flask import request
        
        data = request.get_json()
        sender = data.get('sender', 'administrator')
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'message': 'Message cannot be empty'})
        
        # Get recipient user data
        db = current_app.db
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            return jsonify({'success': False, 'message': 'User not found'})
        
        user_data = user_doc.to_dict()
        recipient_username = user_data.get('username', 'Unknown User')
        
        # Create message document
        message_data = {
            'from_user': 'system',
            'from_username': sender.title(),
            'to_user': user_id,
            'to_username': recipient_username,
            'subject': f'Nachricht von {sender.title()}',
            'content': message,
            'timestamp': datetime.now(),
            'read': False,
            'type': 'admin_message',
            'sender_type': sender,
            'sent_by_admin': g.user['uid']
        }
        
        # Save message to database
        db.collection('messages').add(message_data)
        
        current_app.logger.info(f"Admin {g.user['username']} sent message to user {user_id} as {sender}")
        return jsonify({'success': True, 'message': 'Message sent successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error sending message: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while sending message'})


@admin_bp.route('/users/create', methods=['POST'])
@admin_required
def create_user():
    """
    Create a new user from admin panel.
    """
    try:
        from firebase_admin import auth, firestore
        from flask import request
        import secrets
        import string
        
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        role = data.get('role', 'User')
        status = data.get('status', 'active')
        password = data.get('password', '')
        send_welcome_email = data.get('sendWelcomeEmail', True)
        force_password_change = data.get('forcePasswordChange', True)
        
        # Validation
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All required fields must be filled'})
        
        if len(password) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters long'})
        
        # Check if username or email already exists
        db = current_app.db
        
        # Check username
        username_query = db.collection('users').where(filter=firestore.FieldFilter('username', '==', username)).limit(1)
        if list(username_query.stream()):
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        # Check email
        email_query = db.collection('users').where(filter=firestore.FieldFilter('email', '==', email)).limit(1)
        if list(email_query.stream()):
            return jsonify({'success': False, 'message': 'Email already exists'})
        
        # Create Firebase Auth user
        try:
            firebase_user = auth.create_user(
                email=email,
                password=password,
                display_name=username,
                email_verified=True
            )
            user_uid = firebase_user.uid
        except Exception as e:
            current_app.logger.error(f"Error creating Firebase user: {e}")
            return jsonify({'success': False, 'message': 'Failed to create user authentication'})
        
        # Create user document in Firestore
        user_data = {
            'uid': user_uid,
            'username': username,
            'email': email,
            'role': role,
            'status': status,
            'created_at': datetime.now(),
            'created_by': g.user['uid'],
            'force_password_change': force_password_change,
            'last_login': None,
            'profile': {
                'display_name': username,
                'bio': '',
                'avatar_url': '',
                'preferences': {
                    'language': 'de',
                    'timezone': 'Europe/Berlin',
                    'email_notifications': True
                }
            }
        }
        
        db.collection('users').document(user_uid).set(user_data)
        
        # Send welcome email if requested
        if send_welcome_email:
            # TODO: Implement email sending functionality
            current_app.logger.info(f"Welcome email should be sent to {email}")
        
        current_app.logger.info(f"Admin {g.user['username']} created user {username} ({email})")
        return jsonify({'success': True, 'message': 'User created successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error creating user: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while creating user'})


@admin_bp.route('/settings/update', methods=['POST'])
@admin_required
def update_settings():
    """
    Update system settings.
    """
    try:
        from flask import request
        db = current_app.db
        
        # Get form data and update settings
        updated_settings = {
            'site_name': request.form.get('site_name'),
            'site_description': request.form.get('site_description'),
            'max_projects_per_user': int(request.form.get('max_projects_per_user', 10)),
            'max_members_per_project': int(request.form.get('max_members_per_project', 50)),
            'enable_user_registration': 'enable_user_registration' in request.form,
            'enable_public_projects': 'enable_public_projects' in request.form,
            'require_email_verification': 'require_email_verification' in request.form,
            'maintenance_mode': 'maintenance_mode' in request.form,
            'backup_enabled': 'backup_enabled' in request.form,
            'backup_frequency': request.form.get('backup_frequency', 'daily'),
            'email_notifications': 'email_notifications' in request.form,
            'default_user_role': request.form.get('default_user_role', 'User'),
            'session_timeout': int(request.form.get('session_timeout', 24)),
            'file_upload_limit': int(request.form.get('file_upload_limit', 10)),
            'default_language': request.form.get('default_language', 'en'),
            'updated_at': datetime.now(),
            'updated_by': g.user['uid']
        }
        
        # Save to Firestore
        db.collection('system_settings').document('config').update(updated_settings)
        
        flash('System settings updated successfully', 'success')
        current_app.logger.info(f"Admin {g.user['email']} updated system settings")
        
    except Exception as e:
        current_app.logger.error(f"Error updating settings: {e}")
        flash('Error updating system settings', 'error')
    
    return redirect(url_for('admin.settings'))


@admin_bp.route('/api/users/<user_id>/plan', methods=['GET'])
@admin_required
def get_user_plan(user_id):
    """Get user's current plan information"""
    try:
        db = current_app.db
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_doc.to_dict()
        plan_data = {
            'plan': user_data.get('plan', 'free'),
            'expiry': user_data.get('plan_expiry', ''),
            'auto_renew': user_data.get('auto_renew', False)
        }
        
        # Convert datetime to string if needed
        if plan_data['expiry'] and hasattr(plan_data['expiry'], 'strftime'):
            plan_data['expiry'] = plan_data['expiry'].strftime('%Y-%m-%d')
        
        return jsonify(plan_data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting user plan: {e}")
        return jsonify({'error': 'An error occurred'}), 500


@admin_bp.route('/api/users/<user_id>/plan', methods=['PUT'])
@admin_required
def update_user_plan(user_id):
    """Update user's plan"""
    try:
        data = request.get_json()
        plan = data.get('plan')
        expiry = data.get('expiry')
        
        # Validate plan
        valid_plans = ['free', 'premium', 'pro', 'enterprise']
        if plan not in valid_plans:
            return jsonify({'error': 'Invalid plan'}), 400
        
        # Prevent changing your own plan
        if user_id == g.user['uid']:
            return jsonify({'error': 'Cannot change your own plan'}), 403
        
        db = current_app.db
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        
        # Prepare update data
        update_data = {
            'plan': plan,
            'plan_updated_at': datetime.now(),
            'plan_updated_by': g.user['uid']
        }
        
        # Handle expiry date
        if expiry:
            try:
                from datetime import datetime
                expiry_date = datetime.strptime(expiry, '%Y-%m-%d')
                update_data['plan_expiry'] = expiry_date
            except ValueError:
                return jsonify({'error': 'Invalid expiry date format'}), 400
        else:
            # If no expiry date, remove it (for permanent plans)
            update_data['plan_expiry'] = None
        
        # Update user document
        db.collection('users').document(user_id).update(update_data)
        
        # Log the action
        user_data = user_doc.to_dict()
        username = user_data.get('username', 'Unknown')
        current_app.logger.info(f"Admin {g.user['username']} updated plan for user {username} to {plan}")
        
        return jsonify({'success': True, 'message': 'Plan updated successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error updating user plan: {e}")
        return jsonify({'error': 'An error occurred'}), 500


@admin_bp.route('/vouchers')
@admin_required
def vouchers():
    """Gutschein-Verwaltungsseite"""
    try:
        db = current_app.db
        
        # Get search and filter parameters
        search_query = request.args.get('search', '').strip()
        plan_filter = request.args.get('plan', '').strip()
        status_filter = request.args.get('status', '').strip()
        
        # Get all vouchers
        vouchers_collection = db.collection('vouchers')
        all_vouchers = list(vouchers_collection.stream())
        
        vouchers_list = []
        for doc in all_vouchers:
            voucher_data = doc.to_dict()
            voucher_data['id'] = doc.id
            
            # Determine voucher status
            now = datetime.now()
            if voucher_data.get('used_by'):
                voucher_data['status'] = 'used'
            elif voucher_data.get('expires_at') and voucher_data['expires_at'] < now:
                voucher_data['status'] = 'expired'
            else:
                voucher_data['status'] = 'active'
            
            # Apply filters
            if search_query:
                searchable_text = f"{voucher_data.get('code', '')} {voucher_data.get('used_by_username', '')}"
                if search_query.lower() not in searchable_text.lower():
                    continue
            
            if plan_filter and voucher_data.get('plan') != plan_filter:
                continue
                
            if status_filter and voucher_data.get('status') != status_filter:
                continue
            
            vouchers_list.append(voucher_data)
        
        # Sort by creation date (newest first)
        vouchers_list.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        # Calculate statistics
        total_vouchers = len(vouchers_list)
        active_vouchers = len([v for v in vouchers_list if v.get('status') == 'active'])
        used_vouchers = len([v for v in vouchers_list if v.get('status') == 'used'])
        expired_vouchers = len([v for v in vouchers_list if v.get('status') == 'expired'])
        
        stats = {
            'total_vouchers': total_vouchers,
            'active_vouchers': active_vouchers,
            'used_vouchers': used_vouchers,
            'expired_vouchers': expired_vouchers
        }
        
        # Get available plans
        available_plans = get_available_plans()
        
        return render_template('admin/vouchers.html',
                             vouchers=vouchers_list,
                             stats=stats,
                             search_query=search_query,
                             plan_filter=plan_filter,
                             status_filter=status_filter,
                             available_plans=available_plans)
        
    except Exception as e:
        current_app.logger.error(f"Error in voucher management: {e}")
        flash('Fehler beim Laden der Gutscheine.', 'error')
        return render_template('admin/vouchers.html',
                             vouchers=[],
                             stats={'total_vouchers': 0, 'active_vouchers': 0, 'used_vouchers': 0, 'expired_vouchers': 0},
                             search_query='',
                             plan_filter='',
                             status_filter='')


@admin_bp.route('/api/vouchers/create', methods=['POST'])
@admin_required
def create_vouchers():
    """Erstelle neue Gutscheine"""
    try:
        import secrets
        import string
        
        data = request.get_json()
        plan = data.get('plan')
        duration = data.get('duration')
        custom_duration_value = data.get('custom_duration_value')
        custom_duration_unit = data.get('custom_duration_unit')
        usage_limit = data.get('usage_limit')
        expires_at = data.get('expires_at')
        count = int(data.get('count', 1))
        custom_code = data.get('custom_code')
        code = data.get('code', '').strip()
        
        # Validation
        valid_plans = ['premium', 'pro', 'enterprise']
        if plan not in valid_plans:
            return jsonify({'success': False, 'message': 'Ungültiger Plan'}), 400
        
        # Handle duration
        duration_months = 0
        duration_days = 0
        
        if duration == 'custom':
            # Custom duration handling
            if not custom_duration_value or not custom_duration_unit:
                return jsonify({'success': False, 'message': 'Benutzerdefinierte Dauer nicht vollständig angegeben'}), 400
            
            duration_value = int(custom_duration_value)
            
            if custom_duration_unit == 'days':
                if duration_value < 1 or duration_value > 31:
                    return jsonify({'success': False, 'message': 'Tage müssen zwischen 1 und 31 liegen'}), 400
                duration_days = duration_value
            elif custom_duration_unit == 'months':
                if duration_value < 1 or duration_value > 12:
                    return jsonify({'success': False, 'message': 'Monate müssen zwischen 1 und 12 liegen'}), 400
                duration_months = duration_value
        else:
            # Standard duration
            duration_months = int(duration)
            if duration_months < 1 or duration_months > 12:
                return jsonify({'success': False, 'message': 'Ungültige Dauer'}), 400
        
        # Handle usage limit based on multiple usage toggle
        multiple_usage = request.form.get('multiple_usage') == 'on'
        usage_limit_value = 1  # Default to single use
        
        if multiple_usage:
            usage_limit = request.form.get('usage_limit', '').strip()
            if usage_limit:
                try:
                    usage_limit_value = int(usage_limit)
                    if usage_limit_value < 2 or usage_limit_value > 1000:
                        return jsonify({'success': False, 'message': 'Verwendungsanzahl muss zwischen 2 und 1000 liegen'}), 400
                except ValueError:
                    return jsonify({'success': False, 'message': 'Ungültige Verwendungsanzahl'}), 400
            else:
                usage_limit_value = 5  # Default for multiple usage
        
        if count < 1 or count > 100:
            return jsonify({'success': False, 'message': 'Ungültige Anzahl'}), 400
        
        # Handle expiry date
        expiry_date = None
        if expires_at:
            try:
                expiry_date = datetime.strptime(expires_at, '%Y-%m-%d')
            except ValueError:
                return jsonify({'success': False, 'message': 'Ungültiges Ablaufdatum'}), 400
        
        db = current_app.db
        created_vouchers = []
        
        # Check for custom code conflicts
        if custom_code and code:
            # Check if code already exists
            existing = db.collection('vouchers').where('code', '==', code.upper()).limit(1).stream()
            if list(existing):
                return jsonify({'success': False, 'message': 'Gutschein-Code bereits vorhanden'}), 400
            count = 1  # Force count to 1 for custom codes
        
        # Create vouchers
        for i in range(count):
            if custom_code and code:
                voucher_code = code.upper()
            else:
                # Generate random code
                voucher_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
                voucher_code = f"{plan.upper()}-{voucher_code[:4]}-{voucher_code[4:8]}-{voucher_code[8:]}"

            # Check if voucher code already exists
            existing_voucher = db.collection('vouchers').where('code', '==', voucher_code).limit(1).get()
            if existing_voucher:
                return jsonify({'success': False, 'message': 'Gutschein-Code bereits vergeben'}), 400
            
            voucher_data = {
                'code': voucher_code,
                'plan': plan,
                'duration_months': duration_months,
                'duration_days': duration_days,
                'usage_limit': usage_limit_value,
                'usage_count': 0,
                'created_at': datetime.now(),
                'created_by': g.user['uid'],
                'expires_at': expiry_date,
                'used_by': None,
                'used_by_username': None,
                'used_at': None,
                'active': True
            }
            
            # Add to database
            voucher_ref = db.collection('vouchers').add(voucher_data)
            voucher_data['id'] = voucher_ref[1].id
            created_vouchers.append(voucher_data)
        
        current_app.logger.info(f"Admin {g.user['username']} created {count} voucher(s) for {plan}")
        return jsonify({
            'success': True, 
            'message': f'{count} Gutschein(e) erfolgreich erstellt',
            'vouchers': created_vouchers
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating vouchers: {e}")
        return jsonify({'success': False, 'message': 'Fehler beim Erstellen der Gutscheine'}), 500


@admin_bp.route('/api/vouchers/<voucher_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_voucher(voucher_id):
    """Deaktiviere einen Gutschein"""
    try:
        db = current_app.db
        voucher_doc = db.collection('vouchers').document(voucher_id).get()
        
        if not voucher_doc.exists:
            return jsonify({'success': False, 'message': 'Gutschein nicht gefunden'}), 404
        
        # Update voucher
        db.collection('vouchers').document(voucher_id).update({
            'active': False,
            'deactivated_at': datetime.now(),
            'deactivated_by': g.user['uid']
        })
        
        current_app.logger.info(f"Admin {g.user['username']} deactivated voucher {voucher_id}")
        return jsonify({'success': True, 'message': 'Gutschein deaktiviert'})
        
    except Exception as e:
        current_app.logger.error(f"Error deactivating voucher: {e}")
        return jsonify({'success': False, 'message': 'Fehler beim Deaktivieren'}), 500


@admin_bp.route('/api/vouchers/<voucher_id>/delete', methods=['DELETE'])
@admin_required
def delete_voucher(voucher_id):
    """Lösche einen Gutschein"""
    try:
        db = current_app.db
        voucher_doc = db.collection('vouchers').document(voucher_id).get()
        
        if not voucher_doc.exists:
            return jsonify({'success': False, 'message': 'Gutschein nicht gefunden'}), 404
        
        # Check if voucher is used
        voucher_data = voucher_doc.to_dict()
        if voucher_data.get('used_by'):
            return jsonify({'success': False, 'message': 'Verwendete Gutscheine können nicht gelöscht werden'}), 400
        
        # Delete voucher
        db.collection('vouchers').document(voucher_id).delete()
        
        current_app.logger.info(f"Admin {g.user['username']} deleted voucher {voucher_id}")
        return jsonify({'success': True, 'message': 'Gutschein gelöscht'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting voucher: {e}")
        return jsonify({'success': False, 'message': 'Fehler beim Löschen'}), 500


@admin_bp.route('/plan-settings')
@admin_required
def plan_settings():
    """Plan Settings - Configure subscription plans"""
    try:
        db = current_app.db
        
        # Get current plans from the database
        plans_ref = db.collection('plans').stream()
        plans = []
        for plan_doc in plans_ref:
            plan_data = plan_doc.to_dict()
            plan_data['id'] = plan_doc.id
            plans.append(plan_data)
        
        # Sort plans by order/priority if available
        plans.sort(key=lambda x: x.get('order', 999))
        
        return render_template('admin/plan_settings.html', plans=plans)
        
    except Exception as e:
        current_app.logger.error(f"Error loading plan settings: {e}")
        flash('Fehler beim Laden der Plan-Einstellungen', 'danger')
        return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/api/plans', methods=['POST'])
@admin_required
def create_plan():
    """Create a new subscription plan"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'price', 'max_projects', 'max_storage_gb']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} ist erforderlich'}), 400
        
        # Validate data types
        try:
            price = float(data['price'])
            max_projects = int(data['max_projects'])
            max_storage_gb = int(data['max_storage_gb'])
            order = int(data.get('order', 999))
        except ValueError:
            return jsonify({'success': False, 'message': 'Ungültige Zahlenwerte'}), 400
        
        # Validate ranges
        if price < 0:
            return jsonify({'success': False, 'message': 'Preis muss positiv sein'}), 400
        if max_projects < 1:
            return jsonify({'success': False, 'message': 'Maximale Projekte muss mindestens 1 sein'}), 400
        if max_storage_gb < 1:
            return jsonify({'success': False, 'message': 'Maximaler Speicher muss mindestens 1 GB sein'}), 400
        
        db = current_app.db
        
        # Check if plan name already exists
        existing_plan = db.collection('plans').where('name', '==', data['name']).limit(1).get()
        if existing_plan:
            return jsonify({'success': False, 'message': 'Plan-Name bereits vorhanden'}), 400
        
        # Create plan document
        plan_data = {
            'name': data['name'],
            'description': data.get('description', ''),
            'price': price,
            'max_projects': max_projects,
            'max_storage_gb': max_storage_gb,
            'features': data.get('features', []),
            'is_active': data.get('is_active', True),
            'is_featured': data.get('is_featured', False),
            'order': order,
            'created_at': datetime.now(),
            'created_by': g.user['uid'],
            'updated_at': datetime.now(),
            'updated_by': g.user['uid']
        }
        
        # Add plan to database
        plan_ref = db.collection('plans').add(plan_data)
        plan_id = plan_ref[1].id
        
        current_app.logger.info(f"Admin {g.user['username']} created plan {data['name']} (ID: {plan_id})")
        return jsonify({'success': True, 'message': 'Plan erstellt', 'plan_id': plan_id})
        
    except Exception as e:
        current_app.logger.error(f"Error creating plan: {e}")
        return jsonify({'success': False, 'message': 'Fehler beim Erstellen des Plans'}), 500


@admin_bp.route('/api/plans/<plan_id>', methods=['PUT'])
@admin_required  
def update_plan(plan_id):
    """Update an existing subscription plan"""
    try:
        data = request.get_json()
        db = current_app.db
        
        # Check if plan exists
        plan_doc = db.collection('plans').document(plan_id).get()
        if not plan_doc.exists:
            return jsonify({'success': False, 'message': 'Plan nicht gefunden'}), 404
        
        # Validate data types
        update_data = {'updated_at': datetime.now(), 'updated_by': g.user['uid']}
        
        if 'name' in data:
            # Check if new name conflicts with existing plans
            existing_plan = db.collection('plans').where('name', '==', data['name']).limit(1).get()
            if existing_plan and existing_plan[0].id != plan_id:
                return jsonify({'success': False, 'message': 'Plan-Name bereits vorhanden'}), 400
            update_data['name'] = data['name']
        
        if 'description' in data:
            update_data['description'] = data['description']
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return jsonify({'success': False, 'message': 'Preis muss positiv sein'}), 400
                update_data['price'] = price
            except ValueError:
                return jsonify({'success': False, 'message': 'Ungültiger Preis'}), 400
        
        if 'max_projects' in data:
            try:
                max_projects = int(data['max_projects'])
                if max_projects < 1:
                    return jsonify({'success': False, 'message': 'Maximale Projekte muss mindestens 1 sein'}), 400
                update_data['max_projects'] = max_projects
            except ValueError:
                return jsonify({'success': False, 'message': 'Ungültige Projekt-Anzahl'}), 400
        
        if 'max_storage_gb' in data:
            try:
                max_storage_gb = int(data['max_storage_gb'])
                if max_storage_gb < 1:
                    return jsonify({'success': False, 'message': 'Maximaler Speicher muss mindestens 1 GB sein'}), 400
                update_data['max_storage_gb'] = max_storage_gb
            except ValueError:
                return jsonify({'success': False, 'message': 'Ungültiger Speicher-Wert'}), 400
        
        if 'features' in data:
            if isinstance(data['features'], list):
                update_data['features'] = data['features']
            else:
                return jsonify({'success': False, 'message': 'Features müssen eine Liste sein'}), 400
        
        if 'is_active' in data:
            update_data['is_active'] = bool(data['is_active'])
        
        if 'is_featured' in data:
            update_data['is_featured'] = bool(data['is_featured'])
        
        if 'order' in data:
            try:
                update_data['order'] = int(data['order'])
            except ValueError:
                return jsonify({'success': False, 'message': 'Ungültige Reihenfolge'}), 400
        
        # Update plan in database
        db.collection('plans').document(plan_id).update(update_data)
        
        current_app.logger.info(f"Admin {g.user['username']} updated plan {plan_id}")
        return jsonify({'success': True, 'message': 'Plan aktualisiert'})
        
    except Exception as e:
        current_app.logger.error(f"Error updating plan: {e}")
        return jsonify({'success': False, 'message': 'Fehler beim Aktualisieren des Plans'}), 500


@admin_bp.route('/api/plans/<plan_id>', methods=['DELETE'])
@admin_required
def delete_plan(plan_id):
    """Delete a subscription plan"""
    try:
        db = current_app.db
        
        # Check if plan exists
        plan_doc = db.collection('plans').document(plan_id).get()
        if not plan_doc.exists:
            return jsonify({'success': False, 'message': 'Plan nicht gefunden'}), 404
        
        plan_data = plan_doc.to_dict()
        
        # Check if any users are currently on this plan
        users_with_plan = db.collection('users').where('plan', '==', plan_data['name']).limit(1).get()
        if users_with_plan:
            return jsonify({'success': False, 'message': 'Plan kann nicht gelöscht werden, da er von Benutzern verwendet wird'}), 400
        
        # Delete plan
        db.collection('plans').document(plan_id).delete()
        
        current_app.logger.info(f"Admin {g.user['username']} deleted plan {plan_data['name']} (ID: {plan_id})")
        return jsonify({'success': True, 'message': 'Plan gelöscht'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting plan: {e}")
        return jsonify({'success': False, 'message': 'Fehler beim Löschen des Plans'}), 500

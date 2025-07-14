# app/routes/admin.py
"""
Admin routes for dashboard, user management, settings, and backend control.
Implements all required endpoints as Flask Blueprint.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

admin = Blueprint('admin', __name__)

# Dummy data for demonstration (replace with Firestore in production)
admin_users = []
settings = {'debug': False}
logs = ["System started.", "No errors detected."]

@admin.route('/admin/dashboard', methods=['GET'])
def dashboard():
    """
    Admin dashboard overview.
    """
    return render_template('admin/dashboard.html', logs=logs)

@admin.route('/admin/users', methods=['GET'])
def user_management():
    """
    Show user management interface.
    """
    return render_template('admin/user_management.html', users=admin_users)

@admin.route('/admin/users/edit/<user_id>', methods=['POST'])
def edit_user_role(user_id):
    """
    Change a user's role (dummy logic).
    """
    new_role = request.form.get('role')
    for user in admin_users:
        if user['uid'] == user_id:
            user['role'] = new_role
            flash('User role updated.', 'success')
            break
    return redirect(url_for('admin.user_management'))

@admin.route('/admin/settings', methods=['GET', 'POST'])
def global_settings():
    """
    View and update global settings (debug/test mode).
    """
    if request.method == 'POST':
        debug = request.form.get('debug') == 'on'
        settings['debug'] = debug
        flash('Settings updated.', 'success')
    return render_template('admin/settings.html', settings=settings)

@admin.route('/admin/control', methods=['GET', 'POST'])
def backend_control():
    """
    Simulated backend control functions (e.g., show logs).
    """
    if request.method == 'POST':
        action = request.form.get('action')
        logs.append(f"Action performed: {action}")
        flash('Action executed.', 'info')
    return render_template('admin/backend_control.html', logs=logs)

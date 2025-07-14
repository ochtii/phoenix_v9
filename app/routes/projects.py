# app/routes/projects.py
"""
Project-related routes for dashboard, project creation, details, and invitations.
Implements all required endpoints as Flask Blueprint.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Project
import uuid

projects = Blueprint('projects', __name__)

# In-memory project store for demonstration (replace with Firestore in production)
projects_db = {}

@projects.route('/projects', methods=['GET'])
def dashboard():
    """
    Show dashboard with user's own projects.
    """
    uid = session.get('user_id')
    user_projects = [p for p in projects_db.values() if p.owner_uid == uid or uid in p.members]
    return render_template('projects/project_view.html', projects=user_projects)

@projects.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    """
    Create a new project.
    """
    uid = session.get('user_id')
    if not uid:
        flash('Please log in to create a project.', 'danger')
        return redirect(url_for('user.login'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        is_public = bool(request.form.get('is_public'))
        if not title or not description:
            flash('All fields are required.', 'danger')
            return render_template('projects/project_settings.html')
        project_id = str(uuid.uuid4())
        project = Project(project_id, uid, title, description, members=[uid], is_public=is_public)
        projects_db[project_id] = project
        flash('Project created.', 'success')
        return redirect(url_for('projects.dashboard'))
    return render_template('projects/project_settings.html')

@projects.route('/projects/<project_id>', methods=['GET'])
def project_details(project_id):
    """
    Show details for a specific project.
    """
    project = projects_db.get(project_id)
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('projects.dashboard'))
    return render_template('projects/project_view.html', project=project)

@projects.route('/projects/<project_id>/invite', methods=['POST'])
def invite_to_project(project_id):
    """
    Invite friends to a project (dummy logic for demonstration).
    """
    # In a real app, you would send an invitation or add a user to the project
    flash('Invitation sent (simulated).', 'info')
    return redirect(url_for('projects.project_details', project_id=project_id))

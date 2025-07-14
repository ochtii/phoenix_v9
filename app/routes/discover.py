# app/routes/discover.py
"""
Routes for discovering and joining public projects.
Implements all required endpoints as Flask Blueprint.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Project

# Use the same in-memory projects_db as in projects.py for demonstration
from .projects import projects_db

discover = Blueprint('discover', __name__)

@discover.route('/discover', methods=['GET'])
def discover_projects():
    """
    Show all public projects.
    """
    public_projects = [p for p in projects_db.values() if p.is_public]
    return render_template('discover/explore.html', projects=public_projects)

@discover.route('/discover/join/<project_id>', methods=['POST'])
def join_public_project(project_id):
    """
    Join a public project (adds current user to members).
    """
    uid = session.get('user_id')
    project = projects_db.get(project_id)
    if not project or not project.is_public:
        flash('Project not found or not public.', 'danger')
        return redirect(url_for('discover.discover_projects'))
    if uid and uid not in project.members:
        project.members.append(uid)
        flash('You have joined the project.', 'success')
    else:
        flash('Already a member or not logged in.', 'info')
    return redirect(url_for('discover.discover_projects'))

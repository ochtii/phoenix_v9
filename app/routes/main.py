"""
Main routes for the Phoenix web application.
Handles the home page and general navigation.
"""

from flask import Blueprint, render_template, g, current_app, flash, redirect, url_for
from datetime import datetime
from app import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Home page route.
    Redirects logged-in users to start page, shows landing page for guests.
    """
    # If user is logged in, redirect to start page
    if g.user:
        return redirect(url_for('main.start'))
    
    # Get real statistics for landing page
    try:
        db = current_app.db
        
        # Count users
        users_collection = db.collection('users')
        users_count = len(list(users_collection.limit(10000).stream()))
        
        # Count projects  
        projects_collection = db.collection('projects')
        projects_count = len(list(projects_collection.limit(10000).stream()))
        
        # Count messages (placeholder for now)
        messages_count = 0
        try:
            messages_collection = db.collection('messages')
            messages_count = len(list(messages_collection.limit(10000).stream()))
        except:
            messages_count = 0
        
        # Count tasks from all projects
        tasks_count = 0
        completed_tasks_count = 0
        try:
            all_projects = list(projects_collection.stream())
            for project_doc in all_projects:
                project_data = project_doc.to_dict()
                tasks = project_data.get('tasks', [])
                if isinstance(tasks, list):
                    tasks_count += len(tasks)
                    # Count completed tasks
                    for task in tasks:
                        if isinstance(task, dict) and task.get('completed', False):
                            completed_tasks_count += 1
                elif isinstance(tasks, dict):
                    # Handle case where tasks is a dict instead of list
                    tasks_count += len(tasks)
                    for task_key, task_data in tasks.items():
                        if isinstance(task_data, dict) and task_data.get('completed', False):
                            completed_tasks_count += 1
        except Exception as e:
            current_app.logger.error(f"Error counting tasks: {e}")
            tasks_count = 0
            completed_tasks_count = 0
        
        stats = {
            'users': users_count,
            'projects': projects_count,
            'messages': messages_count,
            'tasks': tasks_count,
            'completed_tasks': completed_tasks_count
        }
        
    except Exception as e:
        current_app.logger.error(f"Error loading stats: {e}")
        # Fallback stats
        stats = {
            'users': 0,
            'projects': 0,
            'messages': 0,
            'tasks': 0,
            'completed_tasks': 0
        }
    
    # Show landing page for guests
    return render_template('index.html', stats=stats)


@main_bp.route('/start')
@login_required
def start():
    """
    Start page for logged-in users.
    Shows welcome message and random tips.
    """
    from datetime import datetime
    return render_template('start.html', datetime=datetime)


@main_bp.route('/dashboard')
@login_required 
def dashboard():
    """
    Main dashboard overview for logged-in users.
    """
    return render_template('main_dashboard.html')


@main_bp.route('/discover')
def discover():
    """
    Public project discovery page.
    Shows all public projects that users can join.
    """
    try:
        db = current_app.db
        
        # Get all public projects
        projects_query = db.collection('projects').where('is_public', '==', True).order_by('updated_at', direction='DESCENDING')
        public_projects = []
        
        for doc in projects_query.stream():
            project_data = doc.to_dict()
            
            # Get owner information
            owner_doc = db.collection('users').document(project_data['owner_uid']).get()
            if owner_doc.exists:
                project_data['owner'] = owner_doc.to_dict()
            
            # Get member count
            project_data['member_count'] = len(project_data.get('members', []))
            
            public_projects.append(project_data)
        
        return render_template('discover/explore.html', projects=public_projects)
    
    except Exception as e:
        current_app.logger.error(f"Discover error: {e}")
        return render_template('discover/explore.html', projects=[])


@main_bp.route('/discover/join/<project_id>', methods=['POST'])
@login_required
def join_project(project_id):
    """
    Join a public project.
    
    Args:
        project_id (str): ID of the project to join
    """
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get project document
        project_ref = db.collection('projects').document(project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            flash('Project not found.', 'error')
            return redirect(url_for('main.discover'))
        
        project_data = project_doc.to_dict()
        
        # Check if project is public
        if not project_data.get('is_public', False):
            flash('This project is not public.', 'error')
            return redirect(url_for('main.discover'))
        
        # Check if user is already a member
        if user_id in project_data.get('members', []):
            flash('You are already a member of this project.', 'info')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        # Add user to project members
        members = project_data.get('members', [])
        members.append(user_id)
        
        project_ref.update({
            'members': members,
            'updated_at': datetime.utcnow()
        })
        
        flash(f'Successfully joined project "{project_data["title"]}"!', 'success')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    except Exception as e:
        current_app.logger.error(f"Join project error: {e}")
        flash('An error occurred while joining the project.', 'error')
        return redirect(url_for('main.discover'))


@main_bp.route('/about')
def about():
    """About page with application information."""
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    """Contact page with support information."""
    return render_template('contact.html')


@main_bp.route('/faq')
def faq():
    """
    FAQ page with frequently asked questions.
    """
    return render_template('faq.html')
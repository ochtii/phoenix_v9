"""
Project management routes for the Phoenix web application.
Handles project creation, viewing, editing, and member management.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, g, current_app, jsonify
from datetime import datetime, timezone
import bleach
import uuid
from app import login_required
from app.models import Project, InviteCode

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/')
@login_required
def index():
    """
    Project dashboard showing user's projects.
    Displays both owned projects and projects where user is a member.
    """
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get projects where user is a member (without ordering to avoid index requirement)
        projects_query = db.collection('projects').where('members', 'array_contains', user_id)
        user_projects = []
        
        for doc in projects_query.stream():
            project_data = doc.to_dict()
            project_data['uid'] = doc.id
            
            # Get owner information
            if project_data.get('owner_uid'):
                owner_doc = db.collection('users').document(project_data['owner_uid']).get()
                if owner_doc.exists:
                    project_data['owner'] = owner_doc.to_dict()
            
            # Add member count
            project_data['member_count'] = len(project_data.get('members', []))
            
            # Check if current user is owner
            project_data['is_owner'] = project_data.get('owner_uid') == user_id
            
            user_projects.append(project_data)
        
        # Sort projects in Python instead of database (by updated_at descending)
        try:
            user_projects.sort(key=lambda x: x.get('updated_at', datetime.min), reverse=True)
        except Exception as sort_error:
            current_app.logger.warning(f"Could not sort projects: {sort_error}")
            # Continue without sorting if there's an issue
        
        return render_template('projects/index.html', projects=user_projects)
    
    except Exception as e:
        current_app.logger.error(f"Projects index error: {e}")
        flash('Error loading projects.', 'error')
        return render_template('projects/index.html', projects=[])
    
    except Exception as e:
        current_app.logger.error(f"Projects index error: {e}")
        return render_template('projects/index.html', projects=[])


@projects_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """
    Create a new project.
    GET: Display project creation form
    POST: Process new project data
    """
    if request.method == 'POST':
        title = bleach.clean(request.form.get('title', '').strip())
        description = bleach.clean(request.form.get('description', '').strip())
        is_public = request.form.get('is_public') == 'on'
        status = request.form.get('status', 'Planning')
        repository_url = bleach.clean(request.form.get('repository_url', '').strip())
        live_demo_url = bleach.clean(request.form.get('live_demo_url', '').strip())
        tech_stack = [tech.strip() for tech in request.form.get('tech_stack', '').split(',') if tech.strip()]
        tags = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        
        # Validation
        errors = []
        
        if not title:
            errors.append('Project title is required.')
        elif len(title) < 3:
            errors.append('Project title must be at least 3 characters long.')
        
        if not description:
            errors.append('Project description is required.')
        elif len(description) < 10:
            errors.append('Project description must be at least 10 characters long.')
        
        if status not in current_app.config['PROJECT_STATUSES']:
            errors.append('Invalid project status.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('projects/new.html')
        
        try:
            # Create new project
            new_project = Project(
                owner_uid=g.user['uid'],
                title=title,
                description=description,
                is_public=is_public,
                status=status
            )
            
            # Set additional fields
            new_project.repository_url = repository_url
            new_project.live_demo_url = live_demo_url
            new_project.tech_stack = tech_stack
            new_project.tags = tags
            
            # Save to Firestore
            db = current_app.db
            db.collection('projects').document(new_project.project_id).set(new_project.to_dict())
            
            flash(f'Project "{title}" created successfully!', 'success')
            return redirect(url_for('projects.view_project', project_id=new_project.project_id))
        
        except Exception as e:
            current_app.logger.error(f"Project creation error: {e}")
            flash('An error occurred while creating the project.', 'error')
    
    return render_template('projects/new.html', project_statuses=current_app.config['PROJECT_STATUSES'])


@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new project"""
    if request.method == 'POST':
        try:
            # Get form data
            project_name = request.form.get('project_name', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            template = request.form.get('template', '').strip()
            privacy = request.form.get('privacy', 'private')
            
            # Get team members from form
            team_members = []
            i = 0
            while True:
                member_email = request.form.get(f'team_members[{i}]')
                if member_email:
                    team_members.append(member_email.strip())
                    i += 1
                else:
                    break
            
            # Validation
            if not project_name or len(project_name) < 3:
                flash('Project name must be at least 3 characters long.', 'error')
                return render_template('projects/create.html')
            
            if not category:
                flash('Please select a project category.', 'error')
                return render_template('projects/create.html')
            
            # Create project
            db = current_app.db
            project_id = str(uuid.uuid4())
            user_id = g.user['uid']
            
            project_data = {
                'uid': project_id,
                'title': project_name,
                'description': description,
                'category': category,
                'template': template,
                'status': 'Planning',
                'is_public': privacy == 'public',
                'owner_uid': user_id,
                'members': [user_id],  # Owner is always a member
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'progress': 0,
                'invite_codes': []
            }
            
            # Save project
            db.collection('projects').document(project_id).set(project_data)
            
            # TODO: Send invitations to team members via email
            
            flash(f'Project "{project_name}" created successfully!', 'success')
            return redirect(url_for('projects.view', project_id=project_id))
            
        except Exception as e:
            current_app.logger.error(f"Error creating project: {e}")
            flash('An error occurred while creating the project.', 'error')
    
    return render_template('projects/create.html')


@projects_bp.route('/<project_id>')
@login_required
def view_project(project_id):
    """
    View project details.
    
    Args:
        project_id (str): ID of the project to view
    """
    try:
        db = current_app.db
        
        # Get project document
        project_doc = db.collection('projects').document(project_id).get()
        
        if not project_doc.exists:
            flash('Project not found.', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project_doc.to_dict()
        user_id = g.user['uid']
        
        # Check if user has access to this project
        if not project_data.get('is_public', False) and user_id not in project_data.get('members', []):
            flash('You do not have access to this project.', 'error')
            return redirect(url_for('projects.index'))
        
        # Get owner information
        owner_doc = db.collection('users').document(project_data['owner_uid']).get()
        if owner_doc.exists:
            project_data['owner'] = owner_doc.to_dict()
        
        # Get member information
        members = []
        for member_id in project_data.get('members', []):
            member_doc = db.collection('users').document(member_id).get()
            if member_doc.exists:
                member_data = member_doc.to_dict()
                members.append({
                    'uid': member_id,
                    'username': member_data.get('username'),
                    'profile_data': member_data.get('profile_data', {})
                })
        
        project_data['members_info'] = members
        project_data['is_owner'] = project_data['owner_uid'] == user_id
        project_data['is_member'] = user_id in project_data.get('members', [])
        
        return render_template('projects/project_view.html', project=project_data)
    
    except Exception as e:
        current_app.logger.error(f"Project view error: {e}")
        flash('An error occurred while loading the project.', 'error')
        return redirect(url_for('projects.index'))


@projects_bp.route('/<project_id>/view')
@login_required  
def view(project_id):
    """View detailed project information"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get project
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            flash('Project not found.', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project_doc.to_dict()
        project_data['uid'] = project_id
        
        # Check access
        if not project_data.get('is_public', False) and user_id not in project_data.get('members', []):
            flash('You do not have access to this project.', 'error')
            return redirect(url_for('projects.index'))
        
        # Add additional data
        project_data['is_owner'] = project_data.get('owner_uid') == user_id
        project_data['member_count'] = len(project_data.get('members', []))
        
        # Get owner info
        if project_data.get('owner_uid'):
            owner_doc = db.collection('users').document(project_data['owner_uid']).get()
            if owner_doc.exists:
                project_data['owner'] = owner_doc.to_dict()
        
        # Mock data for template (to be implemented)
        project_data['task_stats'] = {
            'total': 0,
            'completed': 0, 
            'in_progress': 0,
            'overdue': 0
        }
        project_data['recent_activity'] = []
        project_data['team_members'] = []
        project_data['tasks'] = []
        project_data['files'] = []
        project_data['activity'] = []
        
        return render_template('projects/view.html', project=project_data)
        
    except Exception as e:
        current_app.logger.error(f"Error viewing project: {e}")
        flash('Error loading project.', 'error')
        return redirect(url_for('projects.index'))


@projects_bp.route('/<project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """
    Edit project details (owner only).
    
    Args:
        project_id (str): ID of the project to edit
    """
    try:
        db = current_app.db
        
        # Get project document
        project_doc = db.collection('projects').document(project_id).get()
        
        if not project_doc.exists:
            flash('Project not found.', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project_doc.to_dict()
        user_id = g.user['uid']
        
        # Check if user is the owner
        if project_data['owner_uid'] != user_id:
            flash('Only the project owner can edit this project.', 'error')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        if request.method == 'POST':
            title = bleach.clean(request.form.get('title', '').strip())
            description = bleach.clean(request.form.get('description', '').strip())
            is_public = request.form.get('is_public') == 'on'
            status = request.form.get('status', 'Planning')
            repository_url = bleach.clean(request.form.get('repository_url', '').strip())
            live_demo_url = bleach.clean(request.form.get('live_demo_url', '').strip())
            tech_stack = [tech.strip() for tech in request.form.get('tech_stack', '').split(',') if tech.strip()]
            tags = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
            
            # Validation
            errors = []
            
            if not title:
                errors.append('Project title is required.')
            elif len(title) < 3:
                errors.append('Project title must be at least 3 characters long.')
            
            if not description:
                errors.append('Project description is required.')
            elif len(description) < 10:
                errors.append('Project description must be at least 10 characters long.')
            
            if status not in current_app.config['PROJECT_STATUSES']:
                errors.append('Invalid project status.')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('projects/project_settings.html', project=project_data, project_statuses=current_app.config['PROJECT_STATUSES'])
            
            # Update project
            update_data = {
                'title': title,
                'description': description,
                'is_public': is_public,
                'status': status,
                'repository_url': repository_url,
                'live_demo_url': live_demo_url,
                'tech_stack': tech_stack,
                'tags': tags,
                'updated_at': datetime.utcnow()
            }
            
            db.collection('projects').document(project_id).update(update_data)
            
            flash('Project updated successfully!', 'success')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        return render_template('projects/project_settings.html', project=project_data, project_statuses=current_app.config['PROJECT_STATUSES'])
    
    except Exception as e:
        current_app.logger.error(f"Project edit error: {e}")
        flash('An error occurred while editing the project.', 'error')
        return redirect(url_for('projects.index'))


@projects_bp.route('/<project_id>/invite', methods=['POST'])
@login_required
def invite_to_project(project_id):
    """
    Invite friends to a project (owner and members can invite).
    
    Args:
        project_id (str): ID of the project
    """
    try:
        db = current_app.db
        
        # Get project document
        project_doc = db.collection('projects').document(project_id).get()
        
        if not project_doc.exists:
            return jsonify({'success': False, 'message': 'Project not found.'})
        
        project_data = project_doc.to_dict()
        user_id = g.user['uid']
        
        # Check if user is a member of the project
        if user_id not in project_data.get('members', []):
            return jsonify({'success': False, 'message': 'You are not a member of this project.'})
        
        friend_id = request.json.get('friend_id')
        
        if not friend_id:
            return jsonify({'success': False, 'message': 'Friend ID is required.'})
        
        # Check if friend exists
        friend_doc = db.collection('users').document(friend_id).get()
        if not friend_doc.exists:
            return jsonify({'success': False, 'message': 'User not found.'})
        
        # Check if friend is already a member
        if friend_id in project_data.get('members', []):
            return jsonify({'success': False, 'message': 'User is already a member of this project.'})
        
        # Add friend to project members
        members = project_data.get('members', [])
        members.append(friend_id)
        
        db.collection('projects').document(project_id).update({
            'members': members,
            'updated_at': datetime.utcnow()
        })
        
        friend_data = friend_doc.to_dict()
        friend_username = friend_data.get('username', 'Unknown')
        
        return jsonify({
            'success': True,
            'message': f'{friend_username} has been added to the project!',
            'member': {
                'uid': friend_id,
                'username': friend_username,
                'profile_data': friend_data.get('profile_data', {})
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"Project invite error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while inviting the user.'})


@projects_bp.route('/<project_id>/remove_member', methods=['POST'])
@login_required
def remove_member(project_id):
    """
    Remove a member from a project (owner only).
    
    Args:
        project_id (str): ID of the project
    """
    try:
        db = current_app.db
        
        # Get project document
        project_doc = db.collection('projects').document(project_id).get()
        
        if not project_doc.exists:
            return jsonify({'success': False, 'message': 'Project not found.'})
        
        project_data = project_doc.to_dict()
        user_id = g.user['uid']
        
        # Check if user is the owner
        if project_data['owner_uid'] != user_id:
            return jsonify({'success': False, 'message': 'Only the project owner can remove members.'})
        
        member_id = request.json.get('member_id')
        
        if not member_id:
            return jsonify({'success': False, 'message': 'Member ID is required.'})
        
        # Cannot remove the owner
        if member_id == project_data['owner_uid']:
            return jsonify({'success': False, 'message': 'Cannot remove the project owner.'})
        
        # Remove member from project
        members = project_data.get('members', [])
        if member_id in members:
            members.remove(member_id)
            
            db.collection('projects').document(project_id).update({
                'members': members,
                'updated_at': datetime.utcnow()
            })
            
            return jsonify({'success': True, 'message': 'Member removed successfully.'})
        else:
            return jsonify({'success': False, 'message': 'User is not a member of this project.'})
    
    except Exception as e:
        current_app.logger.error(f"Remove member error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while removing the member.'})


@projects_bp.route('/<project_id>/leave', methods=['POST'])
@login_required
def leave_project(project_id):
    """
    Leave a project (members only, not owner).
    
    Args:
        project_id (str): ID of the project to leave
    """
    try:
        db = current_app.db
        
        # Get project document
        project_doc = db.collection('projects').document(project_id).get()
        
        if not project_doc.exists:
            flash('Project not found.', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project_doc.to_dict()
        user_id = g.user['uid']
        
        # Cannot leave if owner
        if project_data['owner_uid'] == user_id:
            flash('Project owners cannot leave their own projects. Transfer ownership or delete the project instead.', 'error')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        # Remove user from members
        members = project_data.get('members', [])
        if user_id in members:
            members.remove(user_id)
            
            db.collection('projects').document(project_id).update({
                'members': members,
                'updated_at': datetime.utcnow()
            })
            
            flash(f'You have left the project "{project_data["title"]}".', 'info')
        else:
            flash('You are not a member of this project.', 'error')
        
        return redirect(url_for('projects.index'))
    
    except Exception as e:
        current_app.logger.error(f"Leave project error: {e}")
        flash('An error occurred while leaving the project.', 'error')
        return redirect(url_for('projects.index'))


@projects_bp.route('/<project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """
    Delete a project (owner only).
    
    Args:
        project_id (str): ID of the project to delete
    """
    try:
        db = current_app.db
        
        # Get project document
        project_doc = db.collection('projects').document(project_id).get()
        
        if not project_doc.exists:
            flash('Project not found.', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project_doc.to_dict()
        user_id = g.user['uid']
        
        # Check if user is the owner
        if project_data['owner_uid'] != user_id:
            flash('Only the project owner can delete this project.', 'error')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        # Delete the project
        db.collection('projects').document(project_id).delete()
        
        flash(f'Project "{project_data["title"]}" has been deleted.', 'info')
        return redirect(url_for('projects.index'))
    
    except Exception as e:
        current_app.logger.error(f"Delete project error: {e}")
        flash('An error occurred while deleting the project.', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))


@projects_bp.route('/<project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    """Edit project details"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get project
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            flash('Project not found.', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project_doc.to_dict()
        
        # Check if user is the owner
        if project_data.get('owner_uid') != user_id:
            flash('Only the project owner can edit this project.', 'error')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            status = request.form.get('status', 'Planning')
            is_public = request.form.get('is_public') == 'true'
            
            # Validation
            if not name or len(name) < 3:
                flash('Project name must be at least 3 characters long.', 'error')
                return render_template('projects/edit.html', project=project_data)
            
            # Update project
            updates = {
                'name': name,
                'description': description,
                'category': category,
                'status': status,
                'is_public': is_public,
                'updated_at': datetime.now(timezone.utc)
            }
            
            db.collection('projects').document(project_id).update(updates)
            
            flash('Project updated successfully!', 'success')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        # GET request - show edit form
        project_data['uid'] = project_id
        return render_template('projects/edit.html', project=project_data)
        
    except Exception as e:
        current_app.logger.error(f"Error editing project: {e}")
        flash('An error occurred while editing the project.', 'error')
        return redirect(url_for('projects.index'))


@projects_bp.route('/join/<invite_code>')
@login_required
def join_with_code(invite_code):
    """Join a project using an invite code"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Find the invite code
        invite_doc = db.collection('invite_codes').document(invite_code.upper()).get()
        
        if not invite_doc.exists:
            flash('Invalid invite code. Please check the code and try again.', 'error')
            return redirect(url_for('projects.index'))
        
        invite_data = invite_doc.to_dict()
        
        # Check if code is active
        if not invite_data.get('is_active', True):
            flash('This invite code has been deactivated.', 'error')
            return redirect(url_for('projects.index'))
        
        # Get the project
        project_id = invite_data['project_id']
        project_doc = db.collection('projects').document(project_id).get()
        
        if not project_doc.exists:
            flash('The project associated with this invite code no longer exists.', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project_doc.to_dict()
        
        # Check if user is already a member
        if user_id in project_data.get('members', []):
            flash(f'You are already a member of "{project_data.get("title", "this project")}".', 'info')
            return redirect(url_for('projects.view', project_id=project_id))
        
        # Add user to project
        db.collection('projects').document(project_id).update({
            'members': project_data.get('members', []) + [user_id],
            'updated_at': datetime.now(timezone.utc)
        })
        
        # Update invite code usage
        invite_code_obj = InviteCode.from_dict(invite_data)
        invite_code_obj.use_code(user_id)
        
        db.collection('invite_codes').document(invite_code.upper()).update({
            'used_by': invite_code_obj.used_by,
            'used_count': invite_code_obj.used_count
        })
        
        flash(f'Successfully joined project "{project_data.get("title", "Unknown")}"!', 'success')
        return redirect(url_for('projects.view', project_id=project_id))
        
    except Exception as e:
        current_app.logger.error(f"Error joining project with invite code: {e}")
        flash('An error occurred while joining the project.', 'error')
        return redirect(url_for('projects.index'))


@projects_bp.route('/join', methods=['GET', 'POST'])
@login_required
def join():
    """Join a project with invite code form"""
    if request.method == 'POST':
        invite_code = request.form.get('invite_code', '').strip().upper()
        
        if not invite_code:
            flash('Please enter an invite code.', 'error')
            return render_template('projects/join.html')
        
        return redirect(url_for('projects.join_with_code', invite_code=invite_code))
    
    return render_template('projects/join.html')


@projects_bp.route('/<project_id>/settings')
@login_required
def project_settings(project_id):
    """Project settings including invite code management"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get project
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            flash('Project not found.', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project_doc.to_dict()
        project_data['uid'] = project_doc.id
        
        # Check if user is owner
        if project_data.get('owner_uid') != user_id:
            flash('You can only access settings for projects you own.', 'error')
            return redirect(url_for('projects.view', project_id=project_id))
        
        # Get invite codes for this project
        invite_codes_query = db.collection('invite_codes').where('project_id', '==', project_id).where('is_active', '==', True)
        invite_codes = []
        
        for doc in invite_codes_query.stream():
            code_data = doc.to_dict()
            code_data['code'] = doc.id
            invite_codes.append(code_data)
        
        # Sort by creation date
        invite_codes.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        return render_template('projects/project_settings.html', 
                             project=project_data, 
                             invite_codes=invite_codes)
        
    except Exception as e:
        current_app.logger.error(f"Error loading project settings: {e}")
        flash('An error occurred while loading project settings.', 'error')
        return redirect(url_for('projects.index'))


@projects_bp.route('/<project_id>/invite-codes/create', methods=['POST'])
@login_required
def create_invite_code(project_id):
    """Create a new invite code for a project"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get project
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            return jsonify({'error': 'Project not found'}), 404
        
        project_data = project_doc.to_dict()
        
        # Check if user is owner
        if project_data.get('owner_uid') != user_id:
            return jsonify({'error': 'Only project owners can create invite codes'}), 403
        
        # Check current invite code count (implement plan limits here)
        current_codes = len([code for code in project_data.get('invite_codes', []) if code])
        
        # Basic plan limit (can be extended based on user's actual plan)
        max_codes = 5  # This should come from user's subscription plan
        
        if current_codes >= max_codes:
            return jsonify({'error': f'Maximum of {max_codes} invite codes allowed'}), 400
        
        # Generate unique 6-character code
        import string
        import random
        
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            # Check if code already exists
            existing_code = db.collection('invite_codes').document(code).get()
            if not existing_code.exists:
                break
        
        # Create invite code
        invite_code_obj = InviteCode(
            code=code,
            project_id=project_id,
            created_by=user_id
        )
        
        # Save invite code
        db.collection('invite_codes').document(code).set(invite_code_obj.to_dict())
        
        # Update project's invite codes list
        current_invite_codes = project_data.get('invite_codes', [])
        current_invite_codes.append(code)
        
        db.collection('projects').document(project_id).update({
            'invite_codes': current_invite_codes,
            'updated_at': datetime.now(timezone.utc)
        })
        
        return jsonify({
            'success': True,
            'code': code,
            'created_at': invite_code_obj.created_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating invite code: {e}")
        return jsonify({'error': 'Failed to create invite code'}), 500


@projects_bp.route('/<project_id>/invite-codes/<code>/delete', methods=['POST'])
@login_required
def delete_invite_code(project_id, code):
    """Delete an invite code"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get project
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            return jsonify({'error': 'Project not found'}), 404
        
        project_data = project_doc.to_dict()
        
        # Check if user is owner
        if project_data.get('owner_uid') != user_id:
            return jsonify({'error': 'Only project owners can delete invite codes'}), 403
        
        # Deactivate invite code
        db.collection('invite_codes').document(code.upper()).update({
            'is_active': False
        })
        
        # Remove from project's invite codes list
        current_invite_codes = project_data.get('invite_codes', [])
        if code.upper() in current_invite_codes:
            current_invite_codes.remove(code.upper())
        
        db.collection('projects').document(project_id).update({
            'invite_codes': current_invite_codes,
            'updated_at': datetime.now(timezone.utc)
        })
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting invite code: {e}")
        return jsonify({'error': 'Failed to delete invite code'}), 500


@projects_bp.route('/<project_id>/update-settings', methods=['POST'])
@login_required
def update_project_settings(project_id):
    """Update project settings (privacy, image, etc.)"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get project
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            return jsonify({'error': 'Projekt nicht gefunden'}), 404
            
        project_data = project_doc.to_dict()
        
        # Check if user is owner
        if g.user['uid'] != project_data.get('owner_uid'):
            return jsonify({'error': 'Nur der Projektbesitzer kann Einstellungen ändern'}), 403
        
        data = request.get_json()
        
        # Prepare updates
        updates = {}
        
        # Privacy setting
        if 'is_private' in data:
            updates['is_private'] = bool(data['is_private'])
        
        # Project image
        if 'project_image' in data:
            updates['project_image'] = data['project_image']
        
        # Description
        if 'description' in data:
            updates['description'] = data['description']
        
        # Project name
        if 'name' in data:
            updates['name'] = data['name']
        
        # Update timestamp
        updates['updated_at'] = datetime.now(timezone.utc)
        
        # Apply updates
        db.collection('projects').document(project_id).update(updates)
        
        return jsonify({
            'success': True,
            'message': 'Projekteinstellungen erfolgreich aktualisiert'
        })
        
    except Exception as e:
        current_app.logger.error(f"Update project settings error: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren der Einstellungen'}), 500
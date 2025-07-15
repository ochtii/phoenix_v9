"""
Discovery/Explore routes for the Phoenix web application.
Handles public project browsing, search, and discovery features.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, g, current_app, jsonify
from datetime import datetime, timezone
import bleach
from app import login_required
import uuid

discover_bp = Blueprint('discover', __name__, url_prefix='/discover')


@discover_bp.route('/')
@discover_bp.route('/explore')
def explore():
    """Main explore page showing public projects"""
    try:
        db = current_app.db
        
        # Get search and filter parameters
        search_query = request.args.get('search', '').strip()
        category_filter = request.args.get('category', '').strip()
        status_filter = request.args.get('status', '').strip()
        sort_order = request.args.get('sort', 'newest')
        
        # Base query for public projects
        projects_query = db.collection('projects').where('is_public', '==', True)
        
        # Apply category filter
        if category_filter:
            projects_query = projects_query.where('category', '==', category_filter)
        
        # Apply status filter
        if status_filter:
            projects_query = projects_query.where('status', '==', status_filter.title())
        
        # Get all matching projects
        projects_docs = projects_query.get()
        projects = []
        
        for doc in projects_docs:
            project_data = doc.to_dict()
            project_data['uid'] = doc.id
            
            # Get owner information
            if project_data.get('owner_uid'):
                owner_doc = db.collection('users').document(project_data['owner_uid']).get()
                if owner_doc.exists:
                    project_data['owner'] = owner_doc.to_dict()
            
            # Add additional data
            project_data['member_count'] = len(project_data.get('members', []))
            project_data['views'] = project_data.get('views', 0)
            project_data['tags'] = project_data.get('tags', [])
            project_data['is_favorited'] = False  # TODO: Check if user has favorited
            
            # Apply search filter
            if search_query:
                searchable_text = f"{project_data.get('name', '')} {project_data.get('description', '')} {' '.join(project_data.get('tags', []))}"
                if search_query.lower() not in searchable_text.lower():
                    continue
            
            projects.append(project_data)
        
        # Sort projects
        if sort_order == 'newest':
            projects.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        elif sort_order == 'popular':
            projects.sort(key=lambda x: x.get('views', 0) + x.get('member_count', 0), reverse=True)
        elif sort_order == 'alphabetical':
            projects.sort(key=lambda x: x.get('name', '').lower())
        elif sort_order == 'updated':
            projects.sort(key=lambda x: x.get('updated_at', datetime.min), reverse=True)
        
        # Get available categories
        categories = [
            'Web Development', 'Mobile App', 'Desktop Software', 'Game Development',
            'Data Science', 'AI/ML', 'DevOps', 'Design', 'Marketing', 'Research'
        ]
        
        # Get statistics
        total_projects = len(projects)
        unique_creators = len(set(p.get('owner_uid') for p in projects if p.get('owner_uid')))
        
        return render_template('discover/explore.html',
                             projects=projects,
                             categories=categories,
                             total_projects=total_projects,
                             total_creators=unique_creators,
                             has_more=False)  # TODO: Implement pagination
        
    except Exception as e:
        current_app.logger.error(f"Error in explore: {e}")
        flash('Error loading projects.', 'error')
        return render_template('discover/explore.html', 
                             projects=[], 
                             categories=[], 
                             total_projects=0, 
                             total_creators=0,
                             has_more=False)


@discover_bp.route('/request-join/<project_id>', methods=['POST'])
@login_required
def request_join(project_id):
    """Send a join request to a project"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        skills = data.get('skills', '').strip()
        
        db = current_app.db
        user_id = g.user['uid']
        
        # Get project
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            return jsonify({'success': False, 'message': 'Project not found'})
        
        project_data = project_doc.to_dict()
        
        # Check if project is public
        if not project_data.get('is_public', False):
            return jsonify({'success': False, 'message': 'This project is not accepting join requests'})
        
        # Check if user is already a member
        if user_id in project_data.get('members', []):
            return jsonify({'success': False, 'message': 'You are already a member of this project'})
        
        # Check if user is the owner
        if project_data.get('owner_uid') == user_id:
            return jsonify({'success': False, 'message': 'You are the owner of this project'})
        
        # Check if request already exists
        existing_request = db.collection('join_requests')\
            .where('project_id', '==', project_id)\
            .where('user_id', '==', user_id)\
            .where('status', '==', 'pending')\
            .get()
        
        if existing_request:
            return jsonify({'success': False, 'message': 'You have already sent a join request for this project'})
        
        # Create join request
        request_data = {
            'project_id': project_id,
            'user_id': user_id,
            'message': bleach.clean(message) if message else '',
            'skills': bleach.clean(skills) if skills else '',
            'status': 'pending',
            'created_at': datetime.now(timezone.utc)
        }
        
        db.collection('join_requests').add(request_data)
        
        # TODO: Send notification to project owner
        
        return jsonify({'success': True, 'message': 'Join request sent successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error sending join request: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@discover_bp.route('/toggle-favorite/<project_id>', methods=['POST'])
@login_required
def toggle_favorite(project_id):
    """Toggle favorite status for a project"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Check if project exists
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            return jsonify({'success': False, 'message': 'Project not found'})
        
        # Check if already favorited
        favorite_doc = db.collection('favorites')\
            .where('user_id', '==', user_id)\
            .where('project_id', '==', project_id)\
            .get()
        
        if favorite_doc:
            # Remove from favorites
            for doc in favorite_doc:
                doc.reference.delete()
            favorited = False
        else:
            # Add to favorites
            favorite_data = {
                'user_id': user_id,
                'project_id': project_id,
                'created_at': datetime.now(timezone.utc)
            }
            db.collection('favorites').add(favorite_data)
            favorited = True
        
        return jsonify({'success': True, 'favorited': favorited})
        
    except Exception as e:
        current_app.logger.error(f"Error toggling favorite: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})
        
        # Get popular technologies for filter suggestions
        all_techs = []
        for project in public_projects:
            all_techs.extend(project.get('tech_stack', []))
        
        # Count technology usage
        tech_counts = {}
        for tech in all_techs:
            tech_lower = tech.lower()
            tech_counts[tech_lower] = tech_counts.get(tech_lower, 0) + 1
        
        # Get top 10 technologies
        popular_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        popular_techs = [tech[0].title() for tech in popular_techs]
        
        filter_options = {
            'statuses': current_app.config['PROJECT_STATUSES'],
            'technologies': popular_techs,
            'sort_options': [
                ('recent', 'Most Recent'),
                ('popular', 'Most Popular'),
                ('alphabetical', 'Alphabetical')
            ]
        }
        
        return render_template('discover/explore.html', 
                             projects=public_projects,
                             filter_options=filter_options,
                             current_filters={
                                 'tech': tech_filter,
                                 'status': status_filter,
                                 'sort': sort_by
                             })
    
    except Exception as e:
        current_app.logger.error(f"Discover error: {e}")
        return render_template('discover/explore.html', projects=[], filter_options={}, current_filters={})


@discover_bp.route('/join/<project_id>', methods=['POST'])
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
            return jsonify({'success': False, 'message': 'Project not found.'})
        
        project_data = project_doc.to_dict()
        
        # Check if project is public
        if not project_data.get('is_public', False):
            return jsonify({'success': False, 'message': 'This project is not public.'})
        
        # Check if user is already a member
        if user_id in project_data.get('members', []):
            return jsonify({'success': False, 'message': 'You are already a member of this project.'})
        
        # Add user to project members
        members = project_data.get('members', [])
        members.append(user_id)
        
        project_ref.update({
            'members': members,
            'updated_at': datetime.utcnow()
        })
        
        return jsonify({
            'success': True,
            'message': f'Successfully joined project "{project_data["title"]}"!',
            'project_url': url_for('projects.view_project', project_id=project_id)
        })
    
    except Exception as e:
        current_app.logger.error(f"Join project error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while joining the project.'})


@discover_bp.route('/featured')
def featured():
    """
    Featured projects page showing highlighted or trending projects.
    """
    try:
        db = current_app.db
        
        # Get featured projects (could be marked by admins or based on activity)
        # For now, we'll show projects with most members or recent activity
        projects_query = db.collection('projects').where('is_public', '==', True).order_by('updated_at', direction='DESCENDING').limit(12)
        
        featured_projects = []
        
        for doc in projects_query.stream():
            project_data = doc.to_dict()
            
            # Get owner information
            owner_doc = db.collection('users').document(project_data['owner_uid']).get()
            if owner_doc.exists:
                owner_data = owner_doc.to_dict()
                project_data['owner'] = {
                    'uid': project_data['owner_uid'],
                    'username': owner_data.get('username'),
                    'profile_data': owner_data.get('profile_data', {})
                }
            
            # Add member count
            project_data['member_count'] = len(project_data.get('members', []))
            
            # Check if current user is already a member
            if g.user:
                project_data['is_member'] = g.user['uid'] in project_data.get('members', [])
                project_data['is_owner'] = g.user['uid'] == project_data['owner_uid']
            else:
                project_data['is_member'] = False
                project_data['is_owner'] = False
            
            featured_projects.append(project_data)
        
        # Sort by member count for "popularity"
        featured_projects.sort(key=lambda x: x['member_count'], reverse=True)
        
        return render_template('discover/featured.html', projects=featured_projects)
    
    except Exception as e:
        current_app.logger.error(f"Featured projects error: {e}")
        return render_template('discover/featured.html', projects=[])


@discover_bp.route('/search')
def search():
    """
    Search projects by title, description, or technology.
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('discover.explore'))
    
    try:
        db = current_app.db
        
        # Get all public projects (Firestore doesn't support full-text search)
        projects_query = db.collection('projects').where('is_public', '==', True)
        search_results = []
        
        for doc in projects_query.stream():
            project_data = doc.to_dict()
            
            # Search in title, description, and tech stack
            title = project_data.get('title', '').lower()
            description = project_data.get('description', '').lower()
            tech_stack = ' '.join(project_data.get('tech_stack', [])).lower()
            tags = ' '.join(project_data.get('tags', [])).lower()
            
            search_text = f"{title} {description} {tech_stack} {tags}"
            
            if query.lower() in search_text:
                # Get owner information
                owner_doc = db.collection('users').document(project_data['owner_uid']).get()
                if owner_doc.exists:
                    owner_data = owner_doc.to_dict()
                    project_data['owner'] = {
                        'uid': project_data['owner_uid'],
                        'username': owner_data.get('username'),
                        'profile_data': owner_data.get('profile_data', {})
                    }
                
                # Add member count
                project_data['member_count'] = len(project_data.get('members', []))
                
                # Check if current user is already a member
                if g.user:
                    project_data['is_member'] = g.user['uid'] in project_data.get('members', [])
                    project_data['is_owner'] = g.user['uid'] == project_data['owner_uid']
                else:
                    project_data['is_member'] = False
                    project_data['is_owner'] = False
                
                search_results.append(project_data)
        
        # Sort by relevance (simple: exact title matches first, then others by update time)
        def relevance_score(project):
            title = project.get('title', '').lower()
            if query.lower() == title:
                return 3
            elif query.lower() in title:
                return 2
            else:
                return 1
        
        search_results.sort(key=lambda x: (relevance_score(x), x.get('updated_at', datetime.min)), reverse=True)
        
        return render_template('discover/search_results.html', 
                             projects=search_results,
                             query=query,
                             result_count=len(search_results))
    
    except Exception as e:
        current_app.logger.error(f"Search error: {e}")
        return render_template('discover/search_results.html', projects=[], query=query, result_count=0)

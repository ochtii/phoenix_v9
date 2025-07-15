"""
Task management routes for the Phoenix web application.
Handles task hierarchy: Project > Milestone > Task Package > Task
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, g, current_app
from datetime import datetime
from firebase_admin import firestore
from app import login_required
from app.models import Task, TaskComment, ProjectFinancials

tasks_bp = Blueprint('tasks', __name__)

# Get Firestore client
db = firestore.client()


@tasks_bp.route('/project/<project_id>/tasks')
@login_required
def project_tasks(project_id):
    """
    Display all tasks for a project in hierarchical view.
    """
    try:
        # Verify user has access to this project
        project_ref = db.collection('projects').document(project_id)
        project = project_ref.get()
        
        if not project.exists:
            flash('Project not found', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project.to_dict()
        
        # Check if user is member or owner
        user_id = g.user['uid']
        if not (project_data.get('owner_id') == user_id or user_id in project_data.get('members', [])):
            flash('Access denied', 'error')
            return redirect(url_for('projects.index'))
        
        # Get all tasks for this project
        tasks_query = db.collection('tasks').where('project_id', '==', project_id).order_by('order_index')
        tasks_docs = tasks_query.get()
        
        tasks = []
        for doc in tasks_docs:
            task_data = doc.to_dict()
            task_data['doc_id'] = doc.id
            tasks.append(task_data)
        
        # Organize tasks into hierarchy
        milestones = [t for t in tasks if t.get('task_type') == 'milestone']
        packages = [t for t in tasks if t.get('task_type') == 'package']
        regular_tasks = [t for t in tasks if t.get('task_type') == 'task']
        
        # Get project members for assignment dropdown
        members_query = db.collection('users').where('uid', 'in', [project_data.get('owner_id')] + project_data.get('members', []))
        members_docs = members_query.get()
        project_members = [{'uid': doc.to_dict().get('uid'), 'username': doc.to_dict().get('username')} for doc in members_docs]
        
        return render_template('projects/tasks.html',
                             project=project_data,
                             project_id=project_id,
                             milestones=milestones,
                             packages=packages,
                             tasks=regular_tasks,
                             all_tasks=tasks,
                             project_members=project_members)
    
    except Exception as e:
        current_app.logger.error(f"Error loading project tasks: {e}")
        flash('Error loading tasks', 'error')
        return redirect(url_for('projects.index'))


@tasks_bp.route('/project/<project_id>/tasks/create', methods=['POST'])
@login_required
def create_task(project_id):
    """
    Create a new task, milestone, or package.
    """
    try:
        # Verify project access
        project_ref = db.collection('projects').document(project_id)
        project = project_ref.get()
        
        if not project.exists:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        project_data = project.to_dict()
        user_id = g.user['uid']
        
        if not (project_data.get('owner_id') == user_id or user_id in project_data.get('members', [])):
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        # Get form data
        task_type = request.form.get('task_type', 'task')
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        parent_id = request.form.get('parent_id')
        priority = request.form.get('priority', 'medium')
        assigned_to = request.form.getlist('assigned_to')
        due_date_str = request.form.get('due_date')
        estimated_hours = float(request.form.get('estimated_hours', 0) or 0)
        cost_budget = float(request.form.get('cost_budget', 0) or 0)
        tags = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        
        if not title:
            return jsonify({'success': False, 'message': 'Title is required'}), 400
        
        # Parse due date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Create task object
        task = Task(
            project_id=project_id,
            parent_id=parent_id if parent_id else None,
            task_type=task_type,
            title=title,
            description=description,
            assigned_to=assigned_to,
            priority=priority,
            due_date=due_date,
            estimated_hours=estimated_hours,
            cost_budget=cost_budget,
            created_by=user_id,
            tags=tags
        )
        
        # Save to Firestore
        db.collection('tasks').add(task.to_dict())
        
        return jsonify({'success': True, 'message': f'{task_type.title()} created successfully'})
    
    except Exception as e:
        current_app.logger.error(f"Error creating task: {e}")
        return jsonify({'success': False, 'message': 'Error creating task'}), 500


@tasks_bp.route('/task/<task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    """
    Update an existing task.
    """
    try:
        # Find task document
        tasks_query = db.collection('tasks').where('task_id', '==', task_id)
        tasks_docs = list(tasks_query.get())
        
        if not tasks_docs:
            return jsonify({'success': False, 'message': 'Task not found'}), 404
        
        task_doc = tasks_docs[0]
        task_data = task_doc.to_dict()
        
        # Verify project access
        project_ref = db.collection('projects').document(task_data['project_id'])
        project = project_ref.get()
        
        if not project.exists:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        project_data = project.to_dict()
        user_id = g.user['uid']
        
        if not (project_data.get('owner_id') == user_id or user_id in project_data.get('members', [])):
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        # Update fields from form data
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        if 'title' in request.form:
            update_data['title'] = request.form.get('title').strip()
        if 'description' in request.form:
            update_data['description'] = request.form.get('description').strip()
        if 'status' in request.form:
            update_data['status'] = request.form.get('status')
        if 'priority' in request.form:
            update_data['priority'] = request.form.get('priority')
        if 'progress' in request.form:
            update_data['progress'] = int(request.form.get('progress', 0))
        if 'assigned_to' in request.form:
            update_data['assigned_to'] = request.form.getlist('assigned_to')
        if 'due_date' in request.form and request.form.get('due_date'):
            try:
                update_data['due_date'] = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
            except ValueError:
                pass
        if 'estimated_hours' in request.form:
            update_data['estimated_hours'] = float(request.form.get('estimated_hours', 0) or 0)
        if 'actual_hours' in request.form:
            update_data['actual_hours'] = float(request.form.get('actual_hours', 0) or 0)
        if 'cost_budget' in request.form:
            update_data['cost_budget'] = float(request.form.get('cost_budget', 0) or 0)
        if 'cost_actual' in request.form:
            update_data['cost_actual'] = float(request.form.get('cost_actual', 0) or 0)
        if 'tags' in request.form:
            update_data['tags'] = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        
        # Update in Firestore
        task_doc.reference.update(update_data)
        
        return jsonify({'success': True, 'message': 'Task updated successfully'})
    
    except Exception as e:
        current_app.logger.error(f"Error updating task: {e}")
        return jsonify({'success': False, 'message': 'Error updating task'}), 500


@tasks_bp.route('/task/<task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """
    Delete a task and all its subtasks.
    """
    try:
        # Find task document
        tasks_query = db.collection('tasks').where('task_id', '==', task_id)
        tasks_docs = list(tasks_query.get())
        
        if not tasks_docs:
            return jsonify({'success': False, 'message': 'Task not found'}), 404
        
        task_doc = tasks_docs[0]
        task_data = task_doc.to_dict()
        
        # Verify project access
        project_ref = db.collection('projects').document(task_data['project_id'])
        project = project_ref.get()
        
        if not project.exists:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        project_data = project.to_dict()
        user_id = g.user['uid']
        
        if not (project_data.get('owner_id') == user_id or user_id in project_data.get('members', [])):
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        # Delete subtasks first
        subtasks_query = db.collection('tasks').where('parent_id', '==', task_id)
        subtasks = subtasks_query.get()
        
        for subtask in subtasks:
            subtask.reference.delete()
        
        # Delete task comments
        comments_query = db.collection('task_comments').where('task_id', '==', task_id)
        comments = comments_query.get()
        
        for comment in comments:
            comment.reference.delete()
        
        # Delete the task
        task_doc.reference.delete()
        
        return jsonify({'success': True, 'message': 'Task deleted successfully'})
    
    except Exception as e:
        current_app.logger.error(f"Error deleting task: {e}")
        return jsonify({'success': False, 'message': 'Error deleting task'}), 500


@tasks_bp.route('/task/<task_id>/move', methods=['POST'])
@login_required
def move_task(task_id):
    """
    Move a task to a different parent or position.
    """
    try:
        new_parent_id = request.json.get('new_parent_id')
        new_order_index = request.json.get('new_order_index', 0)
        
        # Find task document
        tasks_query = db.collection('tasks').where('task_id', '==', task_id)
        tasks_docs = list(tasks_query.get())
        
        if not tasks_docs:
            return jsonify({'success': False, 'message': 'Task not found'}), 404
        
        task_doc = tasks_docs[0]
        task_data = task_doc.to_dict()
        
        # Verify project access
        project_ref = db.collection('projects').document(task_data['project_id'])
        project = project_ref.get()
        
        if not project.exists:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        project_data = project.to_dict()
        user_id = g.user['uid']
        
        if not (project_data.get('owner_id') == user_id or user_id in project_data.get('members', [])):
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        # Update task position
        update_data = {
            'parent_id': new_parent_id,
            'order_index': new_order_index,
            'updated_at': datetime.utcnow()
        }
        
        task_doc.reference.update(update_data)
        
        return jsonify({'success': True, 'message': 'Task moved successfully'})
    
    except Exception as e:
        current_app.logger.error(f"Error moving task: {e}")
        return jsonify({'success': False, 'message': 'Error moving task'}), 500


@tasks_bp.route('/task/<task_id>/comment', methods=['POST'])
@login_required
def add_task_comment(task_id):
    """
    Add a comment to a task.
    """
    try:
        content = request.form.get('content', '').strip()
        reply_to = request.form.get('reply_to')
        
        if not content:
            return jsonify({'success': False, 'message': 'Comment content is required'}), 400
        
        # Verify task exists and user has access
        tasks_query = db.collection('tasks').where('task_id', '==', task_id)
        tasks_docs = list(tasks_query.get())
        
        if not tasks_docs:
            return jsonify({'success': False, 'message': 'Task not found'}), 404
        
        task_data = tasks_docs[0].to_dict()
        
        # Verify project access
        project_ref = db.collection('projects').document(task_data['project_id'])
        project = project_ref.get()
        
        if not project.exists:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        project_data = project.to_dict()
        user_id = g.user['uid']
        
        if not (project_data.get('owner_id') == user_id or user_id in project_data.get('members', [])):
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        # Create comment
        comment = TaskComment(
            task_id=task_id,
            user_id=user_id,
            content=content,
            reply_to=reply_to if reply_to else None
        )
        
        # Save to Firestore
        db.collection('task_comments').add(comment.to_dict())
        
        return jsonify({'success': True, 'message': 'Comment added successfully'})
    
    except Exception as e:
        current_app.logger.error(f"Error adding task comment: {e}")
        return jsonify({'success': False, 'message': 'Error adding comment'}), 500


@tasks_bp.route('/project/<project_id>/timeline')
@login_required
def project_timeline(project_id):
    """
    Display project timeline/Gantt chart view.
    """
    try:
        # Verify project access
        project_ref = db.collection('projects').document(project_id)
        project = project_ref.get()
        
        if not project.exists:
            flash('Project not found', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project.to_dict()
        user_id = g.user['uid']
        
        if not (project_data.get('owner_id') == user_id or user_id in project_data.get('members', [])):
            flash('Access denied', 'error')
            return redirect(url_for('projects.index'))
        
        # Get all tasks with dates
        tasks_query = db.collection('tasks').where('project_id', '==', project_id).order_by('start_date')
        tasks_docs = tasks_query.get()
        
        tasks = []
        for doc in tasks_docs:
            task_data = doc.to_dict()
            if task_data.get('start_date') or task_data.get('due_date'):
                tasks.append(task_data)
        
        return render_template('projects/timeline.html',
                             project=project_data,
                             project_id=project_id,
                             tasks=tasks)
    
    except Exception as e:
        current_app.logger.error(f"Error loading project timeline: {e}")
        flash('Error loading timeline', 'error')
        return redirect(url_for('projects.index'))


@tasks_bp.route('/project/<project_id>/financials')
@login_required
def project_financials(project_id):
    """
    Display project financial tracking.
    """
    try:
        # Verify project access
        project_ref = db.collection('projects').document(project_id)
        project = project_ref.get()
        
        if not project.exists:
            flash('Project not found', 'error')
            return redirect(url_for('projects.index'))
        
        project_data = project.to_dict()
        user_id = g.user['uid']
        
        if not (project_data.get('owner_id') == user_id or user_id in project_data.get('members', [])):
            flash('Access denied', 'error')
            return redirect(url_for('projects.index'))
        
        # Check if financials are enabled for this project
        if not project_data.get('settings', {}).get('enable_financials', False):
            flash('Financial tracking is not enabled for this project', 'warning')
            return redirect(url_for('projects.view', project_id=project_id))
        
        # Get financial entries
        financials_query = db.collection('project_financials').where('project_id', '==', project_id).order_by('date', direction=firestore.Query.DESCENDING)
        financials_docs = financials_query.get()
        
        entries = []
        total_income = 0
        total_expenses = 0
        
        for doc in financials_docs:
            entry_data = doc.to_dict()
            entry_data['doc_id'] = doc.id
            entries.append(entry_data)
            
            if entry_data.get('entry_type') == 'income':
                total_income += entry_data.get('amount', 0)
            else:
                total_expenses += entry_data.get('amount', 0)
        
        return render_template('projects/financials.html',
                             project=project_data,
                             project_id=project_id,
                             entries=entries,
                             total_income=total_income,
                             total_expenses=total_expenses,
                             net_balance=total_income - total_expenses)
    
    except Exception as e:
        current_app.logger.error(f"Error loading project financials: {e}")
        flash('Error loading financials', 'error')
        return redirect(url_for('projects.index'))


@tasks_bp.route('/project/<project_id>/financials/add', methods=['POST'])
@login_required
def add_financial_entry(project_id):
    """
    Add a financial entry (income or expense).
    """
    try:
        # Verify project access
        project_ref = db.collection('projects').document(project_id)
        project = project_ref.get()
        
        if not project.exists:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        project_data = project.to_dict()
        user_id = g.user['uid']
        
        if not (project_data.get('owner_id') == user_id or user_id in project_data.get('members', [])):
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        # Get form data
        entry_type = request.form.get('entry_type')
        amount = float(request.form.get('amount', 0) or 0)
        currency = request.form.get('currency', 'EUR')
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date')
        
        if not entry_type or amount <= 0:
            return jsonify({'success': False, 'message': 'Valid entry type and amount are required'}), 400
        
        # Parse date
        entry_date = datetime.utcnow()
        if date_str:
            try:
                entry_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Create financial entry
        entry = ProjectFinancials(
            project_id=project_id,
            entry_type=entry_type,
            amount=amount,
            currency=currency,
            category=category,
            description=description,
            date=entry_date,
            created_by=user_id
        )
        
        # Save to Firestore
        db.collection('project_financials').add(entry.to_dict())
        
        return jsonify({'success': True, 'message': 'Financial entry added successfully'})
    
    except Exception as e:
        current_app.logger.error(f"Error adding financial entry: {e}")
        return jsonify({'success': False, 'message': 'Error adding financial entry'}), 500

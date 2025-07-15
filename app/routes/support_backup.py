"""
Support ticket routes for the Phoenix web application.
Handles user support requests and ticket management.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, g, current_app, jsonify, send_file
from datetime import datetime
import bleach
import uuid
import os
from werkzeug.utils import secure_filename
from app import login_required, role_required
from google.cloud import firestore

support_bp = Blueprint('support', __name__)


@support_bp.route('/tickets')
@login_required
def tickets():
    """
    Display user's support tickets.
    Shows all tickets created by the current user.
    """
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get user's tickets - ohne order_by für ersten Test
        tickets_query = db.collection('support_tickets').where('creator_uid', '==', user_id)
        tickets = []
        
        for doc in tickets_query.stream():
            ticket_data = doc.to_dict()
            ticket_data['id'] = doc.id  # Stelle sicher, dass ID gesetzt ist
            
            # Convert timestamp sicher
            if ticket_data.get('created_at'):
                try:
                    if hasattr(ticket_data['created_at'], 'replace'):
                        ticket_data['created_at'] = ticket_data['created_at'].replace(tzinfo=None)
                except:
                    # Fallback für timestamp handling
                    ticket_data['created_at'] = datetime.now()
            else:
                ticket_data['created_at'] = datetime.now()
                
            tickets.append(ticket_data)
        
        # Sortiere in Python statt in Firestore
        tickets.sort(key=lambda x: x.get('created_at', datetime.now()), reverse=True)
        
        return render_template('support/tickets.html', tickets=tickets)
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Laden der Tickets: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        flash('Fehler beim Laden der Tickets.', 'error')
        return render_template('support/tickets.html', tickets=[])


@support_bp.route('/new', methods=['GET'])
@login_required
def new_ticket():
    """Show new ticket form"""
    return render_template('support/new_ticket.html')


@support_bp.route('/tickets/create', methods=['POST'])
@login_required  
def create_ticket():
    """Create a new support ticket via AJAX"""
    try:
        db = current_app.db
        
        # Get form data
        category = request.form.get('category')
        priority = request.form.get('priority', 'medium')
        subject = bleach.clean(request.form.get('subject', '').strip())
        description = bleach.clean(request.form.get('description', '').strip())
        environment = bleach.clean(request.form.get('environment', '').strip())
        email_updates = request.form.get('email_updates') == 'on'
        
        # Validation
        if not all([category, subject, description]):
            return jsonify({'success': False, 'message': 'Bitte füllen Sie alle Pflichtfelder aus.'})
        
        # Handle file upload
        attachment_data = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                # Validate file
                allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    filename = secure_filename(file.filename)
                    # Store file content as base64 for Firestore
                    import base64
                    file_content = base64.b64encode(file.read()).decode('utf-8')
                    attachment_data = {
                        'filename': filename,
                        'content': file_content,
                        'content_type': file.content_type,
                        'size': len(file_content)
                    }
        
        # Generate ticket ID
        ticket_id = str(uuid.uuid4())[:8].upper()
        
        # Create ticket data
        ticket_data = {
            'id': ticket_id,
            'creator_uid': g.user['uid'],
            'creator_name': g.user.get('username', 'Unbekannt'),
            'creator_email': g.user.get('email', ''),
            'category': category,
            'priority': priority,
            'subject': subject,
            'description': description,
            'environment': environment if environment else None,
            'attachment': attachment_data,
            'email_updates': email_updates,
            'status': 'open',
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'replies': [],
            'status_updates': []
        }
        
        # Save to Firestore
        db.collection('support_tickets').document(ticket_id).set(ticket_data)
        
        return jsonify({
            'success': True, 
            'ticket_id': ticket_id,
            'message': 'Ticket erfolgreich erstellt!'
        })
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Erstellen des Tickets: {str(e)}")
        return jsonify({'success': False, 'message': 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.'})


@support_bp.route('/tickets/<ticket_id>')
@login_required
def view_ticket_new(ticket_id):
    """View a specific ticket"""
    try:
        db = current_app.db
        
        # Get ticket
        ticket_doc = db.collection('support_tickets').document(ticket_id).get()
        if not ticket_doc.exists:
            flash('Ticket nicht gefunden.', 'error')
            return redirect(url_for('support.new_ticket'))
        
        ticket_data = ticket_doc.to_dict()
        
        # Check if user has access
        user_id = g.user['uid']
        is_admin = g.user.get('role') == 'admin'
        
        if ticket_data['creator_uid'] != user_id and not is_admin:
            flash('Zugriff verweigert.', 'error')
            return redirect(url_for('support.new_ticket'))
        
        # Convert timestamps
        if ticket_data.get('created_at'):
            ticket_data['created_at'] = ticket_data['created_at'].replace(tzinfo=None)
        
        for reply in ticket_data.get('replies', []):
            if reply.get('created_at'):
                reply['created_at'] = reply['created_at'].replace(tzinfo=None)
        
        return render_template('support/view_ticket.html', ticket=ticket_data)
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Laden des Tickets: {str(e)}")
        flash('Fehler beim Laden des Tickets.', 'error')
        return redirect(url_for('support.new_ticket'))


@support_bp.route('/tickets/<ticket_id>/reply', methods=['POST'])
@login_required
def add_reply(ticket_id):
    """Add a reply to a ticket"""
    try:
        db = current_app.db
        
        # Get ticket
        ticket_ref = db.collection('support_tickets').document(ticket_id)
        ticket_doc = ticket_ref.get()
        
        if not ticket_doc.exists:
            return jsonify({'success': False, 'message': 'Ticket nicht gefunden.'})
        
        ticket_data = ticket_doc.to_dict()
        
        # Check access
        user_id = g.user['uid']
        is_admin = g.user.get('role') == 'admin'
        
        if ticket_data['creator_uid'] != user_id and not is_admin:
            return jsonify({'success': False, 'message': 'Zugriff verweigert.'})
        
        # Get reply data
        message = bleach.clean(request.form.get('message', '').strip())
        if not message:
            return jsonify({'success': False, 'message': 'Nachricht ist erforderlich.'})
        
        # Handle attachment
        attachment_data = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    filename = secure_filename(file.filename)
                    import base64
                    file_content = base64.b64encode(file.read()).decode('utf-8')
                    attachment_data = {
                        'filename': filename,
                        'content': file_content,
                        'content_type': file.content_type
                    }
        
        # Create reply
        reply_data = {
            'id': str(uuid.uuid4()),
            'message': message,
            'author_uid': user_id,
            'author_name': g.user.get('username', 'Unbekannt'),
            'is_admin': is_admin,
            'attachment': attachment_data,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        # Update ticket
        replies = ticket_data.get('replies', [])
        replies.append(reply_data)
        
        ticket_ref.update({
            'replies': replies,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'status': 'waiting' if not is_admin else 'in-progress'
        })
        
        return jsonify({'success': True, 'message': 'Antwort gesendet!'})
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Senden der Antwort: {str(e)}")
        return jsonify({'success': False, 'message': 'Fehler beim Senden der Antwort.'})


@support_bp.route('/tickets/<ticket_id>/status', methods=['POST'])
@login_required
@role_required('admin')
def update_status(ticket_id):
    """Update ticket status (admin only)"""
    try:
        db = current_app.db
        
        # Get new status
        new_status = request.json.get('status')
        if new_status not in ['open', 'in-progress', 'waiting', 'closed']:
            return jsonify({'success': False, 'message': 'Ungültiger Status.'})
        
        # Update ticket
        ticket_ref = db.collection('support_tickets').document(ticket_id)
        ticket_ref.update({
            'status': new_status,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({'success': True, 'message': 'Status aktualisiert!'})
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Aktualisieren des Status: {str(e)}")
        return jsonify({'success': False, 'message': 'Fehler beim Aktualisieren des Status.'})


@support_bp.route('/tickets/<ticket_id>')
@login_required
def view_ticket(ticket_id):
    """
    View a specific support ticket.
    
    Args:
        ticket_id (str): ID of the ticket to view
    """
    try:
        db = current_app.db
        
        # Get ticket document
        ticket_doc = db.collection('tickets').document(ticket_id).get()
        
        if not ticket_doc.exists:
            flash('Ticket not found.', 'error')
            return redirect(url_for('support.tickets'))
        
        ticket_data = ticket_doc.to_dict()
        user_id = g.user['uid']
        user_role = g.user.get('role', 'User')
        
        # Check if user has access to this ticket
        can_view = (
            ticket_data['creator_uid'] == user_id or  # Ticket creator
            user_role in ['Moderator', 'Admin', 'Webmaster']  # Staff members
        )
        
        if not can_view:
            flash('You do not have permission to view this ticket.', 'error')
            return redirect(url_for('support.tickets'))
        
        # Get creator information
        creator_doc = db.collection('users').document(ticket_data['creator_uid']).get()
        if creator_doc.exists:
            creator_data = creator_doc.to_dict()
            ticket_data['creator'] = {
                'uid': ticket_data['creator_uid'],
                'username': creator_data.get('username'),
                'role': creator_data.get('role')
            }
        
        # Get assigned moderator info if exists
        if ticket_data.get('assigned_moderator_uid'):
            moderator_doc = db.collection('users').document(ticket_data['assigned_moderator_uid']).get()
            if moderator_doc.exists:
                moderator_data = moderator_doc.to_dict()
                ticket_data['assigned_moderator'] = {
                    'uid': ticket_data['assigned_moderator_uid'],
                    'username': moderator_data.get('username'),
                    'role': moderator_data.get('role')
                }
        
        # Get responder information for responses
        for response in ticket_data.get('responses', []):
            if response.get('responder_uid'):
                responder_doc = db.collection('users').document(response['responder_uid']).get()
                if responder_doc.exists:
                    responder_data = responder_doc.to_dict()
                    response['responder'] = {
                        'uid': response['responder_uid'],
                        'username': responder_data.get('username'),
                        'role': responder_data.get('role')
                    }
        
        # Check if user can respond (creator or staff)
        can_respond = (
            ticket_data['creator_uid'] == user_id or
            user_role in ['Moderator', 'Admin', 'Webmaster']
        )
        
        # Check if user is staff (can see internal notes and manage ticket)
        is_staff = user_role in ['Moderator', 'Admin', 'Webmaster']
        
        return render_template('support/view_ticket.html', 
                             ticket=ticket_data,
                             can_respond=can_respond,
                             is_staff=is_staff)
    
    except Exception as e:
        current_app.logger.error(f"View ticket error: {e}")
        flash('An error occurred while loading the ticket.', 'error')
        return redirect(url_for('support.tickets'))


@support_bp.route('/tickets/<ticket_id>/respond', methods=['POST'])
@login_required
def respond_to_ticket(ticket_id):
    """
    Add a response to a support ticket.
    
    Args:
        ticket_id (str): ID of the ticket to respond to
    """
    try:
        db = current_app.db
        
        # Get ticket document
        ticket_doc = db.collection('tickets').document(ticket_id).get()
        
        if not ticket_doc.exists:
            return jsonify({'success': False, 'message': 'Ticket not found.'})
        
        ticket_data = ticket_doc.to_dict()
        user_id = g.user['uid']
        user_role = g.user.get('role', 'User')
        
        # Check if user can respond
        can_respond = (
            ticket_data['creator_uid'] == user_id or
            user_role in ['Moderator', 'Admin', 'Webmaster']
        )
        
        if not can_respond:
            return jsonify({'success': False, 'message': 'You do not have permission to respond to this ticket.'})
        
        content = bleach.clean(request.form.get('content', '').strip())
        is_internal = request.form.get('is_internal') == 'true' and user_role in ['Moderator', 'Admin', 'Webmaster']
        
        if not content:
            return jsonify({'success': False, 'message': 'Response content cannot be empty.'})
        
        if len(content) > 2000:
            return jsonify({'success': False, 'message': 'Response is too long. Maximum 2000 characters allowed.'})
        
        # Create response
        response_data = {
            'response_id': f"resp_{ticket_id}_{datetime.utcnow().timestamp()}",
            'responder_uid': user_id,
            'content': content,
            'timestamp': datetime.utcnow(),
            'is_internal': is_internal
        }
        
        # Add response to ticket
        responses = ticket_data.get('responses', [])
        responses.append(response_data)
        
        # Update ticket status if staff member responds
        update_data = {
            'responses': responses,
            'updated_at': datetime.utcnow()
        }
        
        if user_role in ['Moderator', 'Admin', 'Webmaster'] and ticket_data['status'] == 'Open':
            update_data['status'] = 'In Progress'
            if not ticket_data.get('assigned_moderator_uid'):
                update_data['assigned_moderator_uid'] = user_id
        
        db.collection('tickets').document(ticket_id).update(update_data)
        
        flash('Response added successfully!', 'success')
        return redirect(url_for('support.view_ticket', ticket_id=ticket_id))
    
    except Exception as e:
        current_app.logger.error(f"Ticket response error: {e}")
        flash('An error occurred while adding the response.', 'error')
        return redirect(url_for('support.view_ticket', ticket_id=ticket_id))


@support_bp.route('/tickets/<ticket_id>/close', methods=['POST'])
@role_required(['Moderator', 'Admin', 'Webmaster'])
def close_ticket(ticket_id):
    """
    Close a support ticket (staff only).
    
    Args:
        ticket_id (str): ID of the ticket to close
    """
    try:
        db = current_app.db
        
        # Get ticket document
        ticket_doc = db.collection('tickets').document(ticket_id).get()
        
        if not ticket_doc.exists:
            flash('Ticket not found.', 'error')
            return redirect(url_for('support.tickets'))
        
        # Update ticket status
        db.collection('tickets').document(ticket_id).update({
            'status': 'Closed',
            'closed_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        flash('Ticket closed successfully.', 'success')
        return redirect(url_for('support.view_ticket', ticket_id=ticket_id))
    
    except Exception as e:
        current_app.logger.error(f"Close ticket error: {e}")
        flash('An error occurred while closing the ticket.', 'error')
        return redirect(url_for('support.view_ticket', ticket_id=ticket_id))


@support_bp.route('/tickets/<ticket_id>/reopen', methods=['POST'])
@role_required(['Moderator', 'Admin', 'Webmaster'])
def reopen_ticket(ticket_id):
    """
    Reopen a closed support ticket (staff only).
    
    Args:
        ticket_id (str): ID of the ticket to reopen
    """
    try:
        db = current_app.db
        
        # Get ticket document
        ticket_doc = db.collection('tickets').document(ticket_id).get()
        
        if not ticket_doc.exists:
            flash('Ticket not found.', 'error')
            return redirect(url_for('support.tickets'))
        
        # Update ticket status
        db.collection('tickets').document(ticket_id).update({
            'status': 'In Progress',
            'closed_at': None,
            'updated_at': datetime.utcnow()
        })
        
        flash('Ticket reopened successfully.', 'success')
        return redirect(url_for('support.view_ticket', ticket_id=ticket_id))
    
    except Exception as e:
        current_app.logger.error(f"Reopen ticket error: {e}")
        flash('An error occurred while reopening the ticket.', 'error')
        return redirect(url_for('support.view_ticket', ticket_id=ticket_id))


@support_bp.route('/tickets/<ticket_id>/assign', methods=['POST'])
@role_required(['Moderator', 'Admin', 'Webmaster'])
def assign_ticket(ticket_id):
    """
    Assign a ticket to a moderator (staff only).
    
    Args:
        ticket_id (str): ID of the ticket to assign
    """
    try:
        db = current_app.db
        
        # Get ticket document
        ticket_doc = db.collection('tickets').document(ticket_id).get()
        
        if not ticket_doc.exists:
            return jsonify({'success': False, 'message': 'Ticket not found.'})
        
        moderator_uid = request.json.get('moderator_uid')
        
        if not moderator_uid:
            return jsonify({'success': False, 'message': 'Moderator ID is required.'})
        
        # Check if moderator exists and has appropriate role
        moderator_doc = db.collection('users').document(moderator_uid).get()
        if not moderator_doc.exists:
            return jsonify({'success': False, 'message': 'Moderator not found.'})
        
        moderator_data = moderator_doc.to_dict()
        if moderator_data.get('role') not in ['Moderator', 'Admin', 'Webmaster']:
            return jsonify({'success': False, 'message': 'User is not a moderator.'})
        
        # Assign ticket
        db.collection('tickets').document(ticket_id).update({
            'assigned_moderator_uid': moderator_uid,
            'status': 'In Progress',
            'updated_at': datetime.utcnow()
        })
        
        return jsonify({
            'success': True,
            'message': f'Ticket assigned to {moderator_data.get("username", "Unknown")}.'
        })
    
    except Exception as e:
        current_app.logger.error(f"Assign ticket error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while assigning the ticket.'})


@support_bp.route('/all_tickets')
@role_required(['Moderator', 'Admin', 'Webmaster'])
def all_tickets():
    """
    Display all support tickets (staff only).
    Shows tickets from all users with filtering options.
    """
    try:
        db = current_app.db
        
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        priority_filter = request.args.get('priority', 'all')
        category_filter = request.args.get('category', 'all')
        
        # Build query
        tickets_query = db.collection('tickets')
        
        if status_filter != 'all':
            tickets_query = tickets_query.where('status', '==', status_filter)
        
        if priority_filter != 'all':
            tickets_query = tickets_query.where('priority', '==', priority_filter)
        
        if category_filter != 'all':
            tickets_query = tickets_query.where('category', '==', category_filter)
        
        tickets_query = tickets_query.order_by('created_at', direction='DESCENDING')
        
        all_tickets = []
        for doc in tickets_query.stream():
            ticket_data = doc.to_dict()
            
            # Get creator info
            creator_doc = db.collection('users').document(ticket_data['creator_uid']).get()
            if creator_doc.exists:
                creator_data = creator_doc.to_dict()
                ticket_data['creator'] = {
                    'uid': ticket_data['creator_uid'],
                    'username': creator_data.get('username'),
                    'role': creator_data.get('role')
                }
            
            # Get assigned moderator info if exists
            if ticket_data.get('assigned_moderator_uid'):
                moderator_doc = db.collection('users').document(ticket_data['assigned_moderator_uid']).get()
                if moderator_doc.exists:
                    moderator_data = moderator_doc.to_dict()
                    ticket_data['assigned_moderator'] = {
                        'uid': ticket_data['assigned_moderator_uid'],
                        'username': moderator_data.get('username'),
                        'role': moderator_data.get('role')
                    }
            
            # Count responses
            ticket_data['response_count'] = len(ticket_data.get('responses', []))
            
            all_tickets.append(ticket_data)
        
        # Get moderators for assignment dropdown
        moderators_query = db.collection('users').where('role', 'in', ['Moderator', 'Admin', 'Webmaster'])
        moderators = []
        for doc in moderators_query.stream():
            moderator_data = doc.to_dict()
            moderators.append({
                'uid': moderator_data['uid'],
                'username': moderator_data.get('username'),
                'role': moderator_data.get('role')
            })
        
        filter_options = {
            'statuses': ['Open', 'In Progress', 'Closed'],
            'priorities': ['Low', 'Medium', 'High', 'Critical'],
            'categories': ['General', 'Technical', 'Account', 'Feature Request', 'Bug Report']
        }
        
        return render_template('support/all_tickets.html', 
                             tickets=all_tickets,
                             moderators=moderators,
                             filter_options=filter_options,
                             current_filters={
                                 'status': status_filter,
                                 'priority': priority_filter,
                                 'category': category_filter
                             })
    
    except Exception as e:
        current_app.logger.error(f"All tickets error: {e}")
        return render_template('support/all_tickets.html', tickets=[])
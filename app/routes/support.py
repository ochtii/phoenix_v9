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
    """Display user's support tickets"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get user's tickets from support_tickets collection
        tickets_query = db.collection('support_tickets').where('creator_uid', '==', user_id)
        tickets = []
        
        for doc in tickets_query.stream():
            ticket_data = doc.to_dict()
            ticket_data['id'] = doc.id
            
            # Handle timestamp conversion safely
            if ticket_data.get('created_at'):
                try:
                    if hasattr(ticket_data['created_at'], 'replace'):
                        ticket_data['created_at'] = ticket_data['created_at'].replace(tzinfo=None)
                except:
                    ticket_data['created_at'] = datetime.now()
            else:
                ticket_data['created_at'] = datetime.now()
                
            tickets.append(ticket_data)
        
        # Sort in Python
        tickets.sort(key=lambda x: x.get('created_at', datetime.now()), reverse=True)
        
        return render_template('support/tickets.html', tickets=tickets)
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Laden der Tickets: {str(e)}")
        flash('Fehler beim Laden der Tickets.', 'error')
        return render_template('support/tickets.html', tickets=[])


@support_bp.route('/new')
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
                allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    filename = secure_filename(file.filename)
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
        
        # Get ticket from support_tickets collection
        ticket_doc = db.collection('support_tickets').document(ticket_id).get()
        if not ticket_doc.exists:
            flash('Ticket nicht gefunden.', 'error')
            return redirect(url_for('support.new_ticket'))
        
        ticket_data = ticket_doc.to_dict()
        ticket_data['id'] = ticket_id
        
        # Check if user has access
        user_id = g.user['uid']
        is_admin = g.user.get('role') == 'admin'
        
        if ticket_data['creator_uid'] != user_id and not is_admin:
            flash('Zugriff verweigert.', 'error')
            return redirect(url_for('support.new_ticket'))
        
        # Convert timestamps safely
        if ticket_data.get('created_at'):
            try:
                if hasattr(ticket_data['created_at'], 'replace'):
                    ticket_data['created_at'] = ticket_data['created_at'].replace(tzinfo=None)
            except:
                ticket_data['created_at'] = datetime.now()
        
        for reply in ticket_data.get('replies', []):
            if reply.get('created_at'):
                try:
                    if hasattr(reply['created_at'], 'replace'):
                        reply['created_at'] = reply['created_at'].replace(tzinfo=None)
                except:
                    reply['created_at'] = datetime.now()
        
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
            'author_role': g.user.get('role', 'user'),
            'is_admin': is_admin or g.user.get('role') == 'moderator',
            'attachment': attachment_data,
            'attachment_name': attachment_data['filename'] if attachment_data else None,
            'attachment_size': f"{len(attachment_data['content']) * 3 // 4} bytes" if attachment_data else None,
            'created_at': datetime.now()
        }
        
        # Update ticket
        replies = ticket_data.get('replies', [])
        replies.append(reply_data)
        
        # Auto-set status to in-progress if admin/mod replies and ticket is open
        new_status = ticket_data.get('status', 'open')
        if (is_admin or g.user.get('role') == 'moderator') and ticket_data.get('status') == 'open':
            new_status = 'in-progress'
        elif not (is_admin or g.user.get('role') == 'moderator') and ticket_data.get('status') == 'in-progress':
            new_status = 'waiting'
        
        update_data = {
            'replies': replies,
            'updated_at': datetime.now(),
            'status': new_status
        }
        
        # Add status update if status changed
        if new_status != ticket_data.get('status'):
            status_updates = ticket_data.get('status_updates', [])
            status_updates.append({
                'status': new_status,
                'changed_by': user_id,
                'changed_by_name': g.user.get('username', 'Unbekannt'),
                'created_at': datetime.now(),
                'reason': 'Automatisch durch Antwort'
            })
            update_data['status_updates'] = status_updates
        
        ticket_ref.update(update_data)
        
        return jsonify({'success': True, 'message': 'Antwort gesendet!'})
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Senden der Antwort: {str(e)}")
        return jsonify({'success': False, 'message': 'Fehler beim Senden der Antwort.'})


@support_bp.route('/tickets/<ticket_id>/status', methods=['POST'])
@login_required
def update_status(ticket_id):
    """Update ticket status"""
    try:
        db = current_app.db
        
        # Get ticket first
        ticket_ref = db.collection('support_tickets').document(ticket_id)
        ticket_doc = ticket_ref.get()
        
        if not ticket_doc.exists:
            return jsonify({'success': False, 'message': 'Ticket nicht gefunden.'})
        
        ticket_data = ticket_doc.to_dict()
        
        # Check access - admin/mod can update any ticket, user can only update their own
        user_id = g.user['uid']
        is_admin_or_mod = g.user.get('role') in ['admin', 'moderator']
        
        if ticket_data['creator_uid'] != user_id and not is_admin_or_mod:
            return jsonify({'success': False, 'message': 'Zugriff verweigert.'})
        
        # Get new status
        new_status = request.json.get('status')
        if new_status not in ['open', 'in-progress', 'waiting', 'closed']:
            return jsonify({'success': False, 'message': 'Ungültiger Status.'})
        
        # Update ticket
        update_data = {
            'status': new_status,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        # Add status update to timeline
        status_updates = ticket_data.get('status_updates', [])
        status_updates.append({
            'status': new_status,
            'changed_by': user_id,
            'changed_by_name': g.user.get('username', 'Unbekannt'),
            'created_at': firestore.SERVER_TIMESTAMP
        })
        update_data['status_updates'] = status_updates
        
        ticket_ref.update(update_data)
        
        return jsonify({'success': True, 'message': 'Status aktualisiert!'})
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Aktualisieren des Status: {str(e)}")
        return jsonify({'success': False, 'message': 'Fehler beim Aktualisieren des Status.'})


@support_bp.route('/tickets/<ticket_id>/check-updates')
@login_required
def check_updates(ticket_id):
    """Check for new updates on a ticket"""
    try:
        db = current_app.db
        
        # Get ticket
        ticket_doc = db.collection('support_tickets').document(ticket_id).get()
        if not ticket_doc.exists:
            return jsonify({'has_updates': False})
        
        ticket_data = ticket_doc.to_dict()
        
        # Check access
        user_id = g.user['uid']
        is_admin_or_mod = g.user.get('role') in ['admin', 'moderator']
        
        if ticket_data['creator_uid'] != user_id and not is_admin_or_mod:
            return jsonify({'has_updates': False})
        
        # Simple check - in real implementation, you'd compare timestamps
        # For now, just return False to prevent constant reloading
        return jsonify({'has_updates': False})
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Prüfen auf Updates: {str(e)}")
        return jsonify({'has_updates': False})


@support_bp.route('/all-tickets')
@login_required
@role_required(['admin'])
def all_tickets():
    """Display all support tickets (admin only)"""
    try:
        db = current_app.db
        
        # Get all tickets from support_tickets collection
        tickets_query = db.collection('support_tickets')
        tickets = []
        
        for doc in tickets_query.stream():
            ticket_data = doc.to_dict()
            ticket_data['id'] = doc.id
            
            # Handle timestamp conversion safely
            if ticket_data.get('created_at'):
                try:
                    if hasattr(ticket_data['created_at'], 'replace'):
                        ticket_data['created_at'] = ticket_data['created_at'].replace(tzinfo=None)
                except:
                    ticket_data['created_at'] = datetime.now()
            else:
                ticket_data['created_at'] = datetime.now()
                
            tickets.append(ticket_data)
        
        # Sort in Python
        tickets.sort(key=lambda x: x.get('created_at', datetime.now()), reverse=True)
        
        return render_template('support/all_tickets.html', tickets=tickets)
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Laden aller Tickets: {str(e)}")
        flash('Fehler beim Laden der Tickets.', 'error')
        return render_template('support/all_tickets.html', tickets=[])


@support_bp.route('/tickets/<ticket_id>/download-attachment')
@login_required
def download_attachment(ticket_id):
    """Download ticket attachment"""
    try:
        db = current_app.db
        
        # Get ticket
        ticket_doc = db.collection('support_tickets').document(ticket_id).get()
        if not ticket_doc.exists:
            flash('Ticket nicht gefunden.', 'error')
            return redirect(url_for('support.tickets'))
        
        ticket_data = ticket_doc.to_dict()
        
        # Check access
        user_id = g.user['uid']
        is_admin_or_mod = g.user.get('role') in ['admin', 'moderator']
        
        if ticket_data['creator_uid'] != user_id and not is_admin_or_mod:
            flash('Zugriff verweigert.', 'error')
            return redirect(url_for('support.tickets'))
        
        # Get attachment
        attachment = ticket_data.get('attachment')
        if not attachment:
            flash('Anhang nicht gefunden.', 'error')
            return redirect(url_for('support.view_ticket_new', ticket_id=ticket_id))
        
        # Decode base64 content
        import base64
        import io
        
        file_content = base64.b64decode(attachment['content'])
        
        return send_file(
            io.BytesIO(file_content),
            as_attachment=True,
            download_name=attachment['filename'],
            mimetype=attachment.get('content_type', 'application/octet-stream')
        )
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Download: {str(e)}")
        flash('Fehler beim Download des Anhangs.', 'error')
        return redirect(url_for('support.tickets'))


@support_bp.route('/replies/<reply_id>/download-attachment')
@login_required
def download_reply_attachment(reply_id):
    """Download reply attachment"""
    try:
        db = current_app.db
        
        # Find the ticket containing this reply
        tickets_query = db.collection('support_tickets').where('replies', 'array_contains_any', [{'id': reply_id}])
        
        ticket_doc = None
        reply_data = None
        
        for doc in tickets_query.stream():
            ticket_data = doc.to_dict()
            for reply in ticket_data.get('replies', []):
                if reply.get('id') == reply_id:
                    ticket_doc = doc
                    reply_data = reply
                    break
            if reply_data:
                break
        
        if not ticket_doc or not reply_data:
            flash('Anhang nicht gefunden.', 'error')
            return redirect(url_for('support.tickets'))
        
        ticket_data = ticket_doc.to_dict()
        
        # Check access
        user_id = g.user['uid']
        is_admin_or_mod = g.user.get('role') in ['admin', 'moderator']
        
        if ticket_data['creator_uid'] != user_id and not is_admin_or_mod:
            flash('Zugriff verweigert.', 'error')
            return redirect(url_for('support.tickets'))
        
        # Get attachment
        attachment = reply_data.get('attachment')
        if not attachment:
            flash('Anhang nicht gefunden.', 'error')
            return redirect(url_for('support.view_ticket_new', ticket_id=ticket_doc.id))
        
        # Decode base64 content
        import base64
        import io
        
        file_content = base64.b64decode(attachment['content'])
        
        return send_file(
            io.BytesIO(file_content),
            as_attachment=True,
            download_name=attachment['filename'],
            mimetype=attachment.get('content_type', 'application/octet-stream')
        )
        
    except Exception as e:
        current_app.logger.error(f"Fehler beim Download: {str(e)}")
        flash('Fehler beim Download des Anhangs.', 'error')
        return redirect(url_for('support.tickets'))

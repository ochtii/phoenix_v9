"""
Messaging routes for the Phoenix web application.
Handles private messaging between users.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, g, current_app, jsonify, session
from datetime import datetime, timezone
import bleach
from app import login_required
from app.models import Message
import uuid

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')


@messages_bp.route('/')
@login_required
def inbox():
    """Display user's message inbox with conversations"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get conversations for this user
        conversations_ref = db.collection('conversations')\
            .where('participants', 'array_contains', user_id)\
            .order_by('updated_at', direction='DESCENDING')
        
        conversations = []
        for doc in conversations_ref.stream():
            conversation_data = doc.to_dict()
            conversation_data['uid'] = doc.id
            
            # Get other participant
            other_user_id = None
            for participant in conversation_data.get('participants', []):
                if participant != user_id:
                    other_user_id = participant
                    break
            
            if other_user_id:
                # Get other user info
                other_user_doc = db.collection('users').document(other_user_id).get()
                if other_user_doc.exists:
                    conversation_data['other_user'] = other_user_doc.to_dict()
                    conversation_data['other_user']['uid'] = other_user_id
                
                # Get last message
                last_message_ref = db.collection('conversations').document(doc.id)\
                    .collection('messages')\
                    .order_by('created_at', direction='DESCENDING')\
                    .limit(1)
                
                last_message_docs = list(last_message_ref.stream())
                if last_message_docs:
                    conversation_data['last_message'] = last_message_docs[0].to_dict()
                
                # Count unread messages
                unread_count = db.collection('conversations').document(doc.id)\
                    .collection('messages')\
                    .where('sender_id', '!=', user_id)\
                    .where('read', '==', False)\
                    .get()
                
                conversation_data['unread_count'] = len(unread_count)
                conversations.append(conversation_data)
        
        return render_template('messages/inbox.html', 
                             conversations=conversations,
                             active_conversation=None)
        
    except Exception as e:
        current_app.logger.error(f"Error loading inbox: {e}")
        flash('Error loading messages.', 'error')
        return render_template('messages/inbox.html', conversations=[])


@messages_bp.route('/conversation/<conversation_id>')
@login_required
def conversation(conversation_id):
    """View a specific conversation"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Get conversation
        conversation_doc = db.collection('conversations').document(conversation_id).get()
        if not conversation_doc.exists:
            flash('Conversation not found.', 'error')
            return redirect(url_for('messages.inbox'))
        
        conversation_data = conversation_doc.to_dict()
        
        # Check if user is participant
        if user_id not in conversation_data.get('participants', []):
            flash('You do not have access to this conversation.', 'error')
            return redirect(url_for('messages.inbox'))
        
        # Get other participant
        other_user_id = None
        for participant in conversation_data.get('participants', []):
            if participant != user_id:
                other_user_id = participant
                break
        
        if other_user_id:
            other_user_doc = db.collection('users').document(other_user_id).get()
            if other_user_doc.exists:
                conversation_data['other_user'] = other_user_doc.to_dict()
                conversation_data['other_user']['uid'] = other_user_id
        
        # Get messages
        messages_ref = db.collection('conversations').document(conversation_id)\
            .collection('messages')\
            .order_by('created_at', direction='ASCENDING')
        
        messages = []
        for msg_doc in messages_ref.stream():
            message_data = msg_doc.to_dict()
            message_data['uid'] = msg_doc.id
            
            # Get sender info
            if message_data.get('sender_id'):
                sender_doc = db.collection('users').document(message_data['sender_id']).get()
                if sender_doc.exists:
                    message_data['sender'] = sender_doc.to_dict()
            
            messages.append(message_data)
        
        conversation_data['messages'] = messages
        conversation_data['uid'] = conversation_id
        
        # Mark messages as read
        mark_messages_as_read(conversation_id, user_id)
        
        # Get all conversations for sidebar
        all_conversations = get_user_conversations(user_id)
        
        return render_template('messages/inbox.html',
                             conversations=all_conversations,
                             active_conversation=conversation_data,
                             active_conversation_id=conversation_id)
        
    except Exception as e:
        current_app.logger.error(f"Error loading conversation: {e}")
        flash('Error loading conversation.', 'error')
        return redirect(url_for('messages.inbox'))


@messages_bp.route('/<conversation_id>/send', methods=['POST'])
@login_required
def send_message(conversation_id):
    """Send a message in a conversation"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'message': 'Message content is required'})
        
        db = current_app.db
        user_id = g.user['uid']
        
        # Verify conversation access
        conversation_doc = db.collection('conversations').document(conversation_id).get()
        if not conversation_doc.exists:
            return jsonify({'success': False, 'message': 'Conversation not found'})
        
        conversation_data = conversation_doc.to_dict()
        if user_id not in conversation_data.get('participants', []):
            return jsonify({'success': False, 'message': 'Access denied'})
        
        # Create message
        message_data = {
            'sender_id': user_id,
            'content': bleach.clean(content),
            'created_at': datetime.now(timezone.utc),
            'read': False
        }
        
        # Add message to conversation
        db.collection('conversations').document(conversation_id)\
            .collection('messages').add(message_data)
        
        # Update conversation timestamp
        db.collection('conversations').document(conversation_id).update({
            'updated_at': datetime.now(timezone.utc)
        })
        
        return jsonify({'success': True, 'message': 'Message sent'})
        
    except Exception as e:
        current_app.logger.error(f"Error sending message: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@messages_bp.route('/create-conversation', methods=['POST'])
@login_required
def create_conversation():
    """Create a new conversation"""
    try:
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        initial_message = data.get('initial_message', '').strip()
        
        if not recipient_id:
            return jsonify({'success': False, 'message': 'Recipient is required'})
        
        db = current_app.db
        user_id = g.user['uid']
        
        # Check if conversation already exists
        existing_conversations = db.collection('conversations')\
            .where('participants', 'array_contains', user_id)\
            .get()
        
        for conv_doc in existing_conversations:
            conv_data = conv_doc.to_dict()
            participants = conv_data.get('participants', [])
            if len(participants) == 2 and recipient_id in participants:
                # Conversation already exists
                return jsonify({
                    'success': True, 
                    'conversation_id': conv_doc.id,
                    'message': 'Conversation already exists'
                })
        
        # Create new conversation
        conversation_data = {
            'participants': [user_id, recipient_id],
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        
        conversation_ref = db.collection('conversations').add(conversation_data)
        conversation_id = conversation_ref[1].id
        
        # Send initial message if provided
        if initial_message:
            message_data = {
                'sender_id': user_id,
                'content': bleach.clean(initial_message),
                'created_at': datetime.now(timezone.utc),
                'read': False
            }
            
            db.collection('conversations').document(conversation_id)\
                .collection('messages').add(message_data)
        
        return jsonify({
            'success': True, 
            'conversation_id': conversation_id,
            'message': 'Conversation created'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating conversation: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@messages_bp.route('/search-users')
@login_required
def search_users():
    """Search for users to start conversations"""
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify({'users': []})
        
        db = current_app.db
        user_id = g.user['uid']
        
        # Search users by username or email
        users_ref = db.collection('users')
        
        # Search by username
        username_results = users_ref.where('username', '>=', query)\
                                  .where('username', '<=', query + '\uf8ff')\
                                  .limit(10).get()
        
        # Search by email
        email_results = users_ref.where('email', '>=', query)\
                                .where('email', '<=', query + '\uf8ff')\
                                .limit(10).get()
        
        users = []
        seen_uids = set()
        
        for doc in list(username_results) + list(email_results):
            if doc.id != user_id and doc.id not in seen_uids:
                user_data = doc.to_dict()
                user_data['uid'] = doc.id
                users.append(user_data)
                seen_uids.add(doc.id)
        
        return jsonify({'users': users[:10]})
        
    except Exception as e:
        current_app.logger.error(f"Error searching users: {e}")
        return jsonify({'users': []})


@messages_bp.route('/<conversation_id>/mark-read', methods=['POST'])
@login_required
def mark_as_read(conversation_id):
    """Mark all messages in a conversation as read"""
    try:
        user_id = g.user['uid']
        mark_messages_as_read(conversation_id, user_id)
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"Error marking as read: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


@messages_bp.route('/<conversation_id>/delete', methods=['POST'])
@login_required
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        db = current_app.db
        user_id = g.user['uid']
        
        # Verify access
        conversation_doc = db.collection('conversations').document(conversation_id).get()
        if not conversation_doc.exists:
            return jsonify({'success': False, 'message': 'Conversation not found'})
        
        conversation_data = conversation_doc.to_dict()
        if user_id not in conversation_data.get('participants', []):
            return jsonify({'success': False, 'message': 'Access denied'})
        
        # Delete all messages in the conversation
        messages_ref = db.collection('conversations').document(conversation_id).collection('messages')
        for msg_doc in messages_ref.stream():
            msg_doc.reference.delete()
        
        # Delete the conversation
        db.collection('conversations').document(conversation_id).delete()
        
        return jsonify({'success': True, 'message': 'Conversation deleted'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting conversation: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})


def mark_messages_as_read(conversation_id, user_id):
    """Helper function to mark messages as read"""
    db = current_app.db
    
    # Get unread messages from other users
    messages_ref = db.collection('conversations').document(conversation_id)\
        .collection('messages')\
        .where('sender_id', '!=', user_id)\
        .where('read', '==', False)
    
    # Update each message
    for msg_doc in messages_ref.stream():
        msg_doc.reference.update({'read': True})


def get_user_conversations(user_id):
    """Helper function to get all user conversations"""
    db = current_app.db
    
    conversations_ref = db.collection('conversations')\
        .where('participants', 'array_contains', user_id)\
        .order_by('updated_at', direction='DESCENDING')
    
    conversations = []
    for doc in conversations_ref.stream():
        conversation_data = doc.to_dict()
        conversation_data['uid'] = doc.id
        
        # Get other participant
        other_user_id = None
        for participant in conversation_data.get('participants', []):
            if participant != user_id:
                other_user_id = participant
                break
        
        if other_user_id:
            other_user_doc = db.collection('users').document(other_user_id).get()
            if other_user_doc.exists:
                conversation_data['other_user'] = other_user_doc.to_dict()
                conversation_data['other_user']['uid'] = other_user_id
            
            # Get last message
            last_message_ref = db.collection('conversations').document(doc.id)\
                .collection('messages')\
                .order_by('created_at', direction='DESCENDING')\
                .limit(1)
            
            last_message_docs = list(last_message_ref.stream())
            if last_message_docs:
                conversation_data['last_message'] = last_message_docs[0].to_dict()
            
            # Count unread messages
            unread_count = db.collection('conversations').document(doc.id)\
                .collection('messages')\
                .where('sender_id', '!=', user_id)\
                .where('read', '==', False)\
                .get()
            
            conversation_data['unread_count'] = len(unread_count)
            conversations.append(conversation_data)
    
    return conversations
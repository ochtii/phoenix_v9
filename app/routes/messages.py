# app/routes/messages.py
"""
Message-related routes for inbox and user conversations.
Implements all required endpoints as Flask Blueprint.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Message
import uuid
import datetime

messages = Blueprint('messages', __name__)

# In-memory message store for demonstration (replace with Firestore in production)
messages_db = []

@messages.route('/messages', methods=['GET'])
def inbox():
    """
    Show inbox with all conversations for the current user.
    """
    uid = session.get('user_id')
    if not uid:
        flash('Please log in to view messages.', 'danger')
        return redirect(url_for('user.login'))
    # Group messages by user
    user_conversations = {}
    for msg in messages_db:
        if msg.sender_uid == uid:
            user_conversations.setdefault(msg.receiver_uid, []).append(msg)
        elif msg.receiver_uid == uid:
            user_conversations.setdefault(msg.sender_uid, []).append(msg)
    return render_template('messages/inbox.html', conversations=user_conversations)

@messages.route('/messages/<user_id>', methods=['GET', 'POST'])
def conversation(user_id):
    """
    Show and send messages in a conversation with a specific user.
    """
    uid = session.get('user_id')
    if not uid:
        flash('Please log in to view messages.', 'danger')
        return redirect(url_for('user.login'))
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            message_id = str(uuid.uuid4())
            msg = Message(message_id, uid, user_id, content, datetime.datetime.utcnow())
            messages_db.append(msg)
            flash('Message sent.', 'success')
    # Get conversation messages
    conv = [m for m in messages_db if (m.sender_uid == uid and m.receiver_uid == user_id) or (m.sender_uid == user_id and m.receiver_uid == uid)]
    conv.sort(key=lambda m: m.timestamp)
    return render_template('messages/conversation.html', messages=conv, user_id=user_id)

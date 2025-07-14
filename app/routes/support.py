# app/routes/support.py
"""
Support ticket routes for viewing, creating, and displaying tickets.
Implements all required endpoints as Flask Blueprint.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Ticket
import uuid

support = Blueprint('support', __name__)

# In-memory ticket store for demonstration (replace with Firestore in production)
tickets_db = {}

@support.route('/support/tickets', methods=['GET'])
def tickets():
    """
    Show all tickets created by the current user.
    """
    uid = session.get('user_id')
    user_tickets = [t for t in tickets_db.values() if t.creator_uid == uid]
    return render_template('support/view_ticket.html', tickets=user_tickets)

@support.route('/support/tickets/new', methods=['GET', 'POST'])
def new_ticket():
    """
    Create a new support ticket.
    """
    uid = session.get('user_id')
    if not uid:
        flash('Please log in to create a ticket.', 'danger')
        return redirect(url_for('user.login'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        if not title or not description:
            flash('All fields are required.', 'danger')
            return render_template('support/new_ticket.html')
        ticket_id = str(uuid.uuid4())
        ticket = Ticket(ticket_id, uid, title, description)
        tickets_db[ticket_id] = ticket
        flash('Ticket created.', 'success')
        return redirect(url_for('support.tickets'))
    return render_template('support/new_ticket.html')

@support.route('/support/tickets/<ticket_id>', methods=['GET'])
def ticket_details(ticket_id):
    """
    Show details for a specific ticket.
    """
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('support.tickets'))
    return render_template('support/view_ticket.html', ticket=ticket)

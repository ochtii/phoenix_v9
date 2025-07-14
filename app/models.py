# models.py
"""
Defines the data models for Firestore documents in the Phoenix application.
Each class represents a document structure for a collection.
"""
import datetime

class User:
    """
    User model for Firestore.
    Fields:
        - uid: Unique user ID
        - username: Display name
        - email: Email address
        - password_hash: Hashed password
        - role: User role (User, Moderator, Admin, Webmaster)
        - profile_data: Dict with avatar_url, about_me, location, website, social_links
    """
    def __init__(self, uid, username, email, password_hash, role='User', profile_data=None):
        self.uid = uid
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.profile_data = profile_data or {
            'avatar_url': '',
            'about_me': '',
            'location': '',
            'website': '',
            'social_links': {}
        }

    def to_dict(self):
        """Convert the user object to a dictionary for Firestore."""
        return self.__dict__

class Project:
    """
    Project model for Firestore.
    Fields:
        - project_id: Unique project ID
        - owner_uid: User ID of the project owner
        - title: Project title
        - description: Project description
        - members: List of user IDs
        - is_public: Boolean for public visibility
        - status: Project status
    """
    def __init__(self, project_id, owner_uid, title, description, members=None, is_public=False, status='active'):
        self.project_id = project_id
        self.owner_uid = owner_uid
        self.title = title
        self.description = description
        self.members = members or []
        self.is_public = is_public
        self.status = status

    def to_dict(self):
        """Convert the project object to a dictionary for Firestore."""
        return self.__dict__

class Message:
    """
    Message model for Firestore.
    Fields:
        - message_id: Unique message ID
        - sender_uid: Sender's user ID
        - receiver_uid: Receiver's user ID
        - content: Message content
        - timestamp: UTC datetime
    """
    def __init__(self, message_id, sender_uid, receiver_uid, content, timestamp=None):
        self.message_id = message_id
        self.sender_uid = sender_uid
        self.receiver_uid = receiver_uid
        self.content = content
        self.timestamp = timestamp or datetime.datetime.utcnow()

    def to_dict(self):
        """Convert the message object to a dictionary for Firestore."""
        return self.__dict__

class Ticket:
    """
    Ticket model for Firestore.
    Fields:
        - ticket_id: Unique ticket ID
        - creator_uid: User ID of the ticket creator
        - title: Ticket title
        - description: Ticket description
        - status: Ticket status (Open, In Progress, Closed)
        - assigned_moderator_uid: Moderator's user ID
    """
    def __init__(self, ticket_id, creator_uid, title, description, status='Open', assigned_moderator_uid=None):
        self.ticket_id = ticket_id
        self.creator_uid = creator_uid
        self.title = title
        self.description = description
        self.status = status
        self.assigned_moderator_uid = assigned_moderator_uid

    def to_dict(self):
        """Convert the ticket object to a dictionary for Firestore."""
        return self.__dict__

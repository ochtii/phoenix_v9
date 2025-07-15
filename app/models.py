"""
Data Models for the Phoenix Web Application
Defines the structure of Firestore documents as Python classes.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import bcrypt
import uuid


class User:
    """
    User model representing a user in the system.
    Maps to Firestore 'users' collection.
    """
    
    def __init__(self, uid: str = None, username: str = None, email: str = None, 
                 password: str = None, role: str = 'User', profile_data: Dict = None):
        """
        Initialize a User object.
        
        Args:
            uid (str): Unique user identifier
            username (str): User's chosen username
            email (str): User's email address
            password (str): Plain text password (will be hashed)
            role (str): User role (User, Moderator, Admin, Webmaster)
            profile_data (dict): Additional profile information
        """
        self.uid = uid or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password) if password else None
        self.role = role
        self.profile_data = profile_data or {
            'display_name': '',
            'avatar_url': '',
            'bio': '',
            'location': '',
            'website': '',
            'email_notifications': True,
            'social_links': {
                'twitter': '',
                'github': '',
                'linkedin': ''
            }
        }
        self.created_at = datetime.utcnow()
        self.last_login = None
        self.is_active = True
        self.friends = []  # List of user IDs
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        if not password:
            return None
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        if not self.password_hash or not password:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User object to dictionary for Firestore storage."""
        return {
            'uid': self.uid,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'profile_data': self.profile_data,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active,
            'friends': self.friends
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User object from Firestore document data."""
        user = cls()
        user.uid = data.get('uid')
        user.username = data.get('username')
        user.email = data.get('email')
        user.password_hash = data.get('password_hash')
        user.role = data.get('role', 'User')
        user.profile_data = data.get('profile_data', {})
        user.created_at = data.get('created_at')
        user.last_login = data.get('last_login')
        user.is_active = data.get('is_active', True)
        user.friends = data.get('friends', [])
        return user


class Project:
    """
    Project model representing a collaborative project.
    Maps to Firestore 'projects' collection.
    """
    
    def __init__(self, project_id: str = None, owner_uid: str = None, title: str = None,
                 description: str = None, is_public: bool = False, status: str = 'Planning',
                 category: str = None, template: str = None):
        """
        Initialize a Project object.
        
        Args:
            project_id (str): Unique project identifier
            owner_uid (str): User ID of the project owner
            title (str): Project title
            description (str): Project description
            is_public (bool): Whether the project is publicly visible
            status (str): Current project status
            category (str): Project category
            template (str): Project template used
        """
        self.project_id = project_id or str(uuid.uuid4())
        self.owner_uid = owner_uid
        self.title = title
        self.description = description
        self.category = category
        self.template = template
        self.members = [owner_uid] if owner_uid else []  # List of user IDs
        self.is_public = is_public
        self.status = status
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.tags = []  # List of project tags
        self.repository_url = ''
        self.live_demo_url = ''
        self.tech_stack = []  # List of technologies used
        self.invite_codes = []  # List of active invite codes for this project
    
    def add_member(self, user_uid: str) -> bool:
        """Add a member to the project."""
        if user_uid not in self.members:
            self.members.append(user_uid)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def remove_member(self, user_uid: str) -> bool:
        """Remove a member from the project."""
        if user_uid in self.members and user_uid != self.owner_uid:
            self.members.remove(user_uid)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def is_member(self, user_uid: str) -> bool:
        """Check if a user is a member of the project."""
        return user_uid in self.members
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Project object to dictionary for Firestore storage."""
        return {
            'project_id': self.project_id,
            'owner_uid': self.owner_uid,
            'title': self.title,
            'description': self.description,
            'members': self.members,
            'is_public': self.is_public,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags,
            'repository_url': self.repository_url,
            'live_demo_url': self.live_demo_url,
            'tech_stack': self.tech_stack,
            'category': self.category,
            'template': self.template,
            'invite_codes': self.invite_codes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create Project object from Firestore document data."""
        project = cls()
        project.project_id = data.get('project_id')
        project.owner_uid = data.get('owner_uid')
        project.title = data.get('title')
        project.description = data.get('description')
        project.members = data.get('members', [])
        project.is_public = data.get('is_public', False)
        project.status = data.get('status', 'Planning')
        project.created_at = data.get('created_at')
        project.updated_at = data.get('updated_at')
        project.tags = data.get('tags', [])
        project.repository_url = data.get('repository_url', '')
        project.live_demo_url = data.get('live_demo_url', '')
        project.tech_stack = data.get('tech_stack', [])
        project.category = data.get('category')
        project.template = data.get('template')
        project.invite_codes = data.get('invite_codes', [])
        return project


class Message:
    """
    Message model representing a private message between users.
    Maps to Firestore 'messages' collection.
    """
    
    def __init__(self, message_id: str = None, sender_uid: str = None, 
                 receiver_uid: str = None, content: str = None):
        """
        Initialize a Message object.
        
        Args:
            message_id (str): Unique message identifier
            sender_uid (str): User ID of the sender
            receiver_uid (str): User ID of the receiver
            content (str): Message content
        """
        self.message_id = message_id or str(uuid.uuid4())
        self.sender_uid = sender_uid
        self.receiver_uid = receiver_uid
        self.content = content
        self.timestamp = datetime.utcnow()
        self.is_read = False
        self.is_deleted_by_sender = False
        self.is_deleted_by_receiver = False
    
    def mark_as_read(self):
        """Mark the message as read."""
        self.is_read = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Message object to dictionary for Firestore storage."""
        return {
            'message_id': self.message_id,
            'sender_uid': self.sender_uid,
            'receiver_uid': self.receiver_uid,
            'content': self.content,
            'timestamp': self.timestamp,
            'is_read': self.is_read,
            'is_deleted_by_sender': self.is_deleted_by_sender,
            'is_deleted_by_receiver': self.is_deleted_by_receiver
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create Message object from Firestore document data."""
        message = cls()
        message.message_id = data.get('message_id')
        message.sender_uid = data.get('sender_uid')
        message.receiver_uid = data.get('receiver_uid')
        message.content = data.get('content')
        message.timestamp = data.get('timestamp')
        message.is_read = data.get('is_read', False)
        message.is_deleted_by_sender = data.get('is_deleted_by_sender', False)
        message.is_deleted_by_receiver = data.get('is_deleted_by_receiver', False)
        return message


class Ticket:
    """
    Support ticket model for user support requests.
    Maps to Firestore 'tickets' collection.
    """
    
    def __init__(self, ticket_id: str = None, creator_uid: str = None, 
                 title: str = None, description: str = None, status: str = 'Open'):
        """
        Initialize a Ticket object.
        
        Args:
            ticket_id (str): Unique ticket identifier
            creator_uid (str): User ID of the ticket creator
            title (str): Ticket title/subject
            description (str): Detailed description of the issue
            status (str): Current ticket status (Open, In Progress, Closed)
        """
        self.ticket_id = ticket_id or str(uuid.uuid4())
        self.creator_uid = creator_uid
        self.title = title
        self.description = description
        self.status = status
        self.priority = 'Medium'  # Low, Medium, High, Critical
        self.category = 'General'  # General, Technical, Account, Feature Request
        self.assigned_moderator_uid = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.closed_at = None
        self.responses = []  # List of ticket responses
    
    def add_response(self, responder_uid: str, content: str, is_internal: bool = False):
        """Add a response to the ticket."""
        response = {
            'response_id': str(uuid.uuid4()),
            'responder_uid': responder_uid,
            'content': content,
            'timestamp': datetime.utcnow(),
            'is_internal': is_internal  # Internal notes not visible to ticket creator
        }
        self.responses.append(response)
        self.updated_at = datetime.utcnow()
    
    def assign_moderator(self, moderator_uid: str):
        """Assign a moderator to the ticket."""
        self.assigned_moderator_uid = moderator_uid
        self.status = 'In Progress'
        self.updated_at = datetime.utcnow()
    
    def close_ticket(self):
        """Close the ticket."""
        self.status = 'Closed'
        self.closed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Ticket object to dictionary for Firestore storage."""
        return {
            'ticket_id': self.ticket_id,
            'creator_uid': self.creator_uid,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'category': self.category,
            'assigned_moderator_uid': self.assigned_moderator_uid,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'closed_at': self.closed_at,
            'responses': self.responses
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ticket':
        """Create Ticket object from Firestore document data."""
        ticket = cls()
        ticket.ticket_id = data.get('ticket_id')
        ticket.creator_uid = data.get('creator_uid')
        ticket.title = data.get('title')
        ticket.description = data.get('description')
        ticket.status = data.get('status', 'Open')
        ticket.priority = data.get('priority', 'Medium')
        ticket.category = data.get('category', 'General')
        ticket.assigned_moderator_uid = data.get('assigned_moderator_uid')
        ticket.created_at = data.get('created_at')
        ticket.updated_at = data.get('updated_at')
        ticket.closed_at = data.get('closed_at')
        ticket.responses = data.get('responses', [])
        return ticket


class InviteCode:
    """
    InviteCode model for project invitation codes.
    Maps to Firestore 'invite_codes' collection.
    """
    
    def __init__(self, code: str = None, project_id: str = None, created_by: str = None,
                 expires_at: datetime = None, is_active: bool = True):
        """
        Initialize an InviteCode object.
        
        Args:
            code (str): The invite code (e.g., "DN9N7T")
            project_id (str): ID of the project this code belongs to
            created_by (str): User ID who created this code
            expires_at (datetime): When this code expires (optional)
            is_active (bool): Whether this code is currently active
        """
        self.code = code
        self.project_id = project_id
        self.created_by = created_by
        self.created_at = datetime.utcnow()
        self.expires_at = expires_at
        self.is_active = is_active
        self.used_count = 0  # How many times this code has been used
        self.used_by = []  # List of user IDs who used this code
    
    def use_code(self, user_id: str) -> bool:
        """Mark this code as used by a user."""
        if self.is_active and user_id not in self.used_by:
            self.used_by.append(user_id)
            self.used_count += 1
            return True
        return False
    
    def deactivate(self):
        """Deactivate this invite code."""
        self.is_active = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the InviteCode object to a dictionary."""
        return {
            'code': self.code,
            'project_id': self.project_id,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'is_active': self.is_active,
            'used_count': self.used_count,
            'used_by': self.used_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InviteCode':
        """Create an InviteCode object from a dictionary."""
        invite_code = cls()
        invite_code.code = data.get('code')
        invite_code.project_id = data.get('project_id')
        invite_code.created_by = data.get('created_by')
        invite_code.created_at = data.get('created_at')
        invite_code.expires_at = data.get('expires_at')
        invite_code.is_active = data.get('is_active', True)
        invite_code.used_count = data.get('used_count', 0)
        invite_code.used_by = data.get('used_by', [])
        return invite_code


class Task:
    """
    Task model representing a task in the project hierarchy.
    Hierarchy: Project > Milestone > Task Package > Task
    """
    
    def __init__(self, task_id: str = None, project_id: str = None, parent_id: str = None,
                 task_type: str = 'task', title: str = '', description: str = '',
                 assigned_to: List[str] = None, status: str = 'todo', priority: str = 'medium',
                 start_date: datetime = None, due_date: datetime = None, 
                 estimated_hours: float = 0, actual_hours: float = 0,
                 cost_budget: float = 0, cost_actual: float = 0,
                 created_by: str = '', tags: List[str] = None, progress: int = 0):
        """
        Initialize a Task object.
        
        Args:
            task_id (str): Unique task identifier
            project_id (str): ID of the parent project
            parent_id (str): ID of parent task (for nested hierarchy)
            task_type (str): Type - 'milestone', 'package', 'task'
            title (str): Task title
            description (str): Task description
            assigned_to (List[str]): List of user IDs assigned to this task
            status (str): Task status - 'todo', 'in_progress', 'review', 'done', 'blocked'
            priority (str): Priority level - 'low', 'medium', 'high', 'critical'
            start_date (datetime): Planned start date
            due_date (datetime): Due date
            estimated_hours (float): Estimated work hours
            actual_hours (float): Actual work hours logged
            cost_budget (float): Budgeted cost
            cost_actual (float): Actual cost incurred
            created_by (str): User ID who created the task
            tags (List[str]): List of tags for categorization
            progress (int): Progress percentage (0-100)
        """
        self.task_id = task_id or str(uuid.uuid4())
        self.project_id = project_id
        self.parent_id = parent_id
        self.task_type = task_type  # 'milestone', 'package', 'task'
        self.title = title
        self.description = description
        self.assigned_to = assigned_to or []
        self.status = status
        self.priority = priority
        self.start_date = start_date
        self.due_date = due_date
        self.estimated_hours = estimated_hours
        self.actual_hours = actual_hours
        self.cost_budget = cost_budget
        self.cost_actual = cost_actual
        self.created_by = created_by
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.tags = tags or []
        self.progress = progress
        self.comments = []
        self.attachments = []
        self.dependencies = []  # List of task IDs this task depends on
        self.order_index = 0  # For custom ordering
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Task object to dictionary for Firestore storage."""
        return {
            'task_id': self.task_id,
            'project_id': self.project_id,
            'parent_id': self.parent_id,
            'task_type': self.task_type,
            'title': self.title,
            'description': self.description,
            'assigned_to': self.assigned_to,
            'status': self.status,
            'priority': self.priority,
            'start_date': self.start_date,
            'due_date': self.due_date,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'cost_budget': self.cost_budget,
            'cost_actual': self.cost_actual,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags,
            'progress': self.progress,
            'comments': self.comments,
            'attachments': self.attachments,
            'dependencies': self.dependencies,
            'order_index': self.order_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task object from dictionary (Firestore document)."""
        task = cls()
        for key, value in data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        return task


class TaskComment:
    """
    Comment model for task discussions.
    """
    
    def __init__(self, comment_id: str = None, task_id: str = '', user_id: str = '',
                 content: str = '', reply_to: str = None):
        """
        Initialize a TaskComment object.
        
        Args:
            comment_id (str): Unique comment identifier
            task_id (str): ID of the task this comment belongs to
            user_id (str): ID of the user who made the comment
            content (str): Comment content
            reply_to (str): ID of comment this is replying to
        """
        self.comment_id = comment_id or str(uuid.uuid4())
        self.task_id = task_id
        self.user_id = user_id
        self.content = content
        self.reply_to = reply_to
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_edited = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TaskComment object to dictionary for Firestore storage."""
        return {
            'comment_id': self.comment_id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'content': self.content,
            'reply_to': self.reply_to,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_edited': self.is_edited
        }


class ProjectFinancials:
    """
    Financial tracking model for projects.
    """
    
    def __init__(self, project_id: str = '', entry_id: str = None, entry_type: str = 'expense',
                 amount: float = 0, currency: str = 'EUR', category: str = '',
                 description: str = '', date: datetime = None, created_by: str = ''):
        """
        Initialize a ProjectFinancials object.
        
        Args:
            project_id (str): ID of the project
            entry_id (str): Unique entry identifier
            entry_type (str): 'income' or 'expense'
            amount (float): Amount in the specified currency
            currency (str): Currency code (EUR, USD, etc.)
            category (str): Category of income/expense
            description (str): Description of the entry
            date (datetime): Date of the transaction
            created_by (str): User ID who created the entry
        """
        self.entry_id = entry_id or str(uuid.uuid4())
        self.project_id = project_id
        self.entry_type = entry_type  # 'income' or 'expense'
        self.amount = amount
        self.currency = currency
        self.category = category
        self.description = description
        self.date = date or datetime.utcnow()
        self.created_by = created_by
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ProjectFinancials object to dictionary for Firestore storage."""
        return {
            'entry_id': self.entry_id,
            'project_id': self.project_id,
            'entry_type': self.entry_type,
            'amount': self.amount,
            'currency': self.currency,
            'category': self.category,
            'description': self.description,
            'date': self.date,
            'created_by': self.created_by,
            'created_at': self.created_at
        }
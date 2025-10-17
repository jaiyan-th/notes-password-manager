from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize db here to avoid circular imports
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    notes = db.relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')
    password_entries = db.relationship('PasswordEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.email}>'

class Note(db.Model):
    """Note model for storing user notes"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id
        # Validate content length
        if content and len(content) > 5000:
            raise ValueError("Note content cannot exceed 5000 characters")
    
    def update_content(self, title, content):
        """Update note content with validation"""
        if content and len(content) > 5000:
            raise ValueError("Note content cannot exceed 5000 characters")
        self.title = title
        self.content = content
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Note {self.title}>'

class PasswordEntry(db.Model):
    """Password entry model for storing encrypted passwords"""
    __tablename__ = 'password_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    encrypted_password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, service_name, username, encrypted_password, user_id):
        if not service_name or not username or not encrypted_password:
            raise ValueError("Service name, username, and password are required")
        self.service_name = service_name
        self.username = username
        self.encrypted_password = encrypted_password
        self.user_id = user_id
    
    def update_entry(self, service_name, username, encrypted_password):
        """Update password entry with validation"""
        if not service_name or not username or not encrypted_password:
            raise ValueError("Service name, username, and password are required")
        self.service_name = service_name
        self.username = username
        self.encrypted_password = encrypted_password
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<PasswordEntry {self.service_name}>'
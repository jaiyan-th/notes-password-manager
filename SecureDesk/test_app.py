#!/usr/bin/env python3
"""
Simple test script to verify the SecureWebApp functionality
"""

import pytest
from app import app, db
from models import User, Note, PasswordEntry
from utils.security import PasswordEncryption

@pytest.fixture(autouse=True)
def _db_cleaner():
    """Create and drop DB around each test to avoid data leakage between tests"""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_user_creation():
    """Test user model creation and password hashing"""
    with app.app_context():
        db.create_all()
        
        user = User(email='test@example.com')
        user.set_password('TestPassword123')
        
        assert user.email == 'test@example.com'
        assert user.check_password('TestPassword123')
        assert not user.check_password('WrongPassword')
        
        db.session.add(user)
        db.session.commit()
        
        # Verify user was saved
        saved_user = User.query.filter_by(email='test@example.com').first()
        assert saved_user is not None
        assert saved_user.check_password('TestPassword123')

def test_note_creation():
    """Test note model creation and validation"""
    with app.app_context():
        db.create_all()
        
        user = User(email='test@example.com')
        user.set_password('TestPassword123')
        db.session.add(user)
        db.session.commit()
        
        note = Note(
            title='Test Note',
            content='This is a test note content.',
            user_id=user.id
        )
        
        assert note.title == 'Test Note'
        assert note.content == 'This is a test note content.'
        assert note.user_id == user.id
        
        db.session.add(note)
        db.session.commit()
        
        # Verify note was saved
        saved_note = Note.query.filter_by(title='Test Note').first()
        assert saved_note is not None
        assert saved_note.user_id == user.id

def test_password_encryption():
    """Test password encryption and decryption"""
    with app.app_context():
        db.create_all()
        
        user = User(email='test@example.com')
        user.set_password('TestPassword123')
        db.session.add(user)
        db.session.commit()
        
        # Test password encryption
        original_password = 'MySecretPassword123!'
        encrypted = PasswordEncryption.encrypt_password(original_password, user.id)
        
        assert encrypted != original_password
        assert len(encrypted) > 0
        
        # Test password decryption
        decrypted = PasswordEncryption.decrypt_password(encrypted, user.id)
        assert decrypted == original_password
        
        # Test password entry creation
        password_entry = PasswordEntry(
            service_name='Gmail',
            username='test@gmail.com',
            encrypted_password=encrypted,
            user_id=user.id
        )
        
        db.session.add(password_entry)
        db.session.commit()
        
        # Verify password entry was saved
        saved_entry = PasswordEntry.query.filter_by(service_name='Gmail').first()
        assert saved_entry is not None
        assert saved_entry.user_id == user.id

def test_routes_require_auth(client):
    """Test that protected routes require authentication"""
    # Test dashboard requires auth
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirect to login
    
    # Test notes require auth
    response = client.get('/notes/')
    assert response.status_code == 302  # Redirect to login
    
    # Test passwords require auth
    response = client.get('/passwords/')
    assert response.status_code == 302  # Redirect to login

def test_registration_and_login(client):
    """Test user registration and login flow"""
    # Test registration
    response = client.post('/auth/register', data={
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'confirm_password': 'TestPassword123'
    })
    assert response.status_code == 302  # Redirect after successful registration
    
    # Test login
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'TestPassword123'
    })
    assert response.status_code == 302  # Redirect after successful login

if __name__ == '__main__':
    # Run basic tests
    print("Running SecureWebApp tests...")
    
    try:
        test_user_creation()
        print("✓ User creation test passed")
        
        test_note_creation()
        print("✓ Note creation test passed")
        
        test_password_encryption()
        print("✓ Password encryption test passed")
        
        print("\n✅ All basic tests passed!")
        print("\nTo run the full test suite, use: pytest test_app.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
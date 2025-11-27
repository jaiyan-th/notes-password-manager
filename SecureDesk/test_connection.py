#!/usr/bin/env python3
"""
Test script to verify frontend, backend, and database connectivity
"""

import os
import sys
from app import app, db
from models import User, Note, PasswordEntry
from utils.security import PasswordEncryption, PasswordGenerator

def test_database_connection():
    """Test database connectivity and operations"""
    print("🗄️  Testing Database Connection...")
    
    try:
        with app.app_context():
            # Test basic connection
            db.session.execute(db.text('SELECT 1'))
            print("  ✅ Database connection successful")
            
            # Create tables if they don't exist
            db.create_all()
            print("  ✅ Database tables verified")
            
            # Test user creation
            test_email = "test@example.com"
            existing_user = User.query.filter_by(email=test_email).first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
            user = User(email=test_email)
            user.set_password("TestPassword123")
            db.session.add(user)
            db.session.commit()
            print("  ✅ User creation successful")
            
            # Test note creation
            note = Note(title="Test Note", content="Test content", user_id=user.id)
            db.session.add(note)
            db.session.commit()
            print("  ✅ Note creation successful")
            
            # Test password encryption
            encrypted = PasswordEncryption.encrypt_password("TestPassword123", user.id)
            password_entry = PasswordEntry(
                service_name="Test Service",
                username="testuser",
                encrypted_password=encrypted,
                user_id=user.id
            )
            db.session.add(password_entry)
            db.session.commit()
            print("  ✅ Password entry creation successful")
            
            # Test decryption
            decrypted = PasswordEncryption.decrypt_password(encrypted, user.id)
            assert decrypted == "TestPassword123"
            print("  ✅ Password encryption/decryption successful")
            
            # Cleanup
            db.session.delete(password_entry)
            db.session.delete(note)
            db.session.delete(user)
            db.session.commit()
            print("  ✅ Cleanup successful")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def test_backend_routes():
    """Test backend route accessibility"""
    print("⚙️  Testing Backend Routes...")
    
    try:
        with app.test_client() as client:
            # Test public routes
            response = client.get('/')
            assert response.status_code in [200, 302]  # OK or redirect
            print("  ✅ Root route accessible")
            
            response = client.get('/auth/login')
            assert response.status_code == 200
            print("  ✅ Login route accessible")
            
            response = client.get('/auth/register')
            assert response.status_code == 200
            print("  ✅ Register route accessible")
            
            # Test protected routes (should redirect to login)
            response = client.get('/dashboard')
            assert response.status_code == 302  # Redirect to login
            print("  ✅ Protected routes properly secured")
            
            response = client.get('/notes/')
            assert response.status_code == 302  # Redirect to login
            print("  ✅ Notes routes properly secured")
            
            response = client.get('/passwords/')
            assert response.status_code == 302  # Redirect to login
            print("  ✅ Password routes properly secured")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Backend test failed: {e}")
        return False

def test_frontend_templates():
    """Test frontend template rendering"""
    print("🎨 Testing Frontend Templates...")
    
    try:
        with app.test_client() as client:
            # Test template rendering
            response = client.get('/auth/login')
            assert b'Sign in' in response.data
            print("  ✅ Login template renders correctly")
            
            response = client.get('/auth/register')
            assert b'Create account' in response.data
            print("  ✅ Register template renders correctly")
            
            # Test Amazon-style CSS is loaded
            response = client.get('/auth/login')
            assert b'--amazon-blue' in response.data or b'Amazon-style' in response.data
            print("  ✅ Amazon-style CSS loaded")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Frontend test failed: {e}")
        return False

def test_security_features():
    """Test security features"""
    print("🔐 Testing Security Features...")
    
    try:
        # Test password generation
        password = PasswordGenerator.generate_password(16, True)
        assert len(password) == 16
        print("  ✅ Password generation working")
        
        # Test password strength analysis
        analysis = PasswordGenerator.check_password_strength("TestPassword123!")
        assert analysis['score'] > 0
        print("  ✅ Password strength analysis working")
        
        # Test encryption with different user IDs
        with app.app_context():
            encrypted1 = PasswordEncryption.encrypt_password("test", 1)
            encrypted2 = PasswordEncryption.encrypt_password("test", 2)
            assert encrypted1 != encrypted2  # Different users should have different encryption
            print("  ✅ User-specific encryption working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Security test failed: {e}")
        return False

def main():
    """Run all connectivity tests"""
    print("🧪 SecureWebApp Connectivity Test Suite")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_backend_routes,
        test_frontend_templates,
        test_security_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Frontend, Backend, and Database are properly connected.")
        print("🚀 You can now run the application with: python run.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
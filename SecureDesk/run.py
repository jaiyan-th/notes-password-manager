#!/usr/bin/env python3
"""
Run script for SecureWebApp
"""

import os
import sys
from app import app, db
from models import User, Note, PasswordEntry

def setup_environment():
    """Set up environment variables"""
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production-' + os.urandom(24).hex()
    
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    if not os.environ.get('MASTER_KEY'):
        os.environ['MASTER_KEY'] = 'master-encryption-key-change-in-production'

def initialize_database():
    """Initialize the database with tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"✅ Database initialized successfully!")
            print(f"📊 Created tables: {', '.join(tables)}")
            
            # Check if we have any users
            user_count = User.query.count()
            note_count = Note.query.count()
            password_count = PasswordEntry.query.count()
            
            print(f"👥 Users: {user_count}")
            print(f"📝 Notes: {note_count}")
            print(f"🔐 Password entries: {password_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def run_tests():
    """Run basic connectivity tests"""
    try:
        with app.app_context():
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database connection: OK")
            
            # Test model imports
            from models import User, Note, PasswordEntry
            print("✅ Model imports: OK")
            
            # Test blueprint imports
            from auth import auth_bp
            from notes import notes_bp  
            from passwords import passwords_bp
            print("✅ Blueprint imports: OK")
            
            # Test form imports
            from utils.forms import RegistrationForm, LoginForm, NoteForm
            print("✅ Form imports: OK")
            
            # Test security utilities
            from utils.security import PasswordEncryption, PasswordGenerator
            print("✅ Security utilities: OK")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def create_app():
    """Create and configure the Flask application"""
    print("🚀 Starting SecureWebApp...")
    print("=" * 60)
    
    # Set up environment
    setup_environment()
    print("✅ Environment configured")
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database. Exiting.")
        sys.exit(1)
    
    # Run connectivity tests
    if not run_tests():
        print("❌ Connectivity tests failed. Exiting.")
        sys.exit(1)
    
    print("=" * 60)
    print("🎉 Application ready!")
    print("🌐 Frontend: Amazon-style blue and white UI")
    print("⚙️  Backend: Flask with SQLAlchemy")
    print("🗄️  Database: SQLite with encrypted password storage")
    print("=" * 60)
    print("📱 Open your browser and go to: http://localhost:5000")
    print("📋 Register a new account or login to get started")
    print("=" * 60)
    
    return app

if __name__ == '__main__':
    try:
        # Create the app and run
        flask_app = create_app()
        
        # Run the application
        flask_app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Prevent double initialization
        )
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Application failed to start: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Database initialization script for SecureWebApp
"""

from app import app, db
from models import User, Note, PasswordEntry

def init_database():
    """Initialize the database with tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Verify tables were created
        tables = db.engine.table_names()
        print(f"Created tables: {', '.join(tables)}")

def reset_database():
    """Reset the database by dropping and recreating all tables"""
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables dropped.")
        
        # Create all tables
        db.create_all()
        print("Database reset successfully!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset_database()
    else:
        init_database()
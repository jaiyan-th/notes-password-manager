from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
import os
from config import config
from markupsafe import Markup

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# If running under pytest or in a testing environment, prefer the testing configuration
# so tests use an in-memory SQLite database and CSRF is disabled.
import sys
if 'PYTEST_CURRENT_TEST' in os.environ or 'pytest' in sys.modules:
    app.config.from_object(config['testing'])

# Import models and initialize db
from models import db, User, Note, PasswordEntry

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Template filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to HTML line breaks"""
    if text is None:
        return ''
    return Markup(text.replace('\n', '<br>\n'))

# Main routes
@app.route('/')
def index():
    """Root route - redirect to dashboard if authenticated, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing overview of user's notes and password entries"""
    # Get recent notes and password entries for dashboard
    recent_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).limit(5).all()
    recent_passwords = PasswordEntry.query.filter_by(user_id=current_user.id).order_by(PasswordEntry.created_at.desc()).limit(5).all()
    
    # Get counts for statistics
    total_notes = Note.query.filter_by(user_id=current_user.id).count()
    total_passwords = PasswordEntry.query.filter_by(user_id=current_user.id).count()
    
    return render_template('dashboard.html', 
                         recent_notes=recent_notes,
                         recent_passwords=recent_passwords,
                         total_notes=total_notes,
                         total_passwords=total_passwords)

# Register blueprints
from auth import auth_bp
from notes import notes_bp
from passwords import passwords_bp

app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(passwords_bp)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    app.run(host='0.0.0.0', port=5000, debug=True)
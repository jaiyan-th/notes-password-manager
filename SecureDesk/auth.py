"""
Authentication routes and logic
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from utils.forms import RegistrationForm, LoginForm
from datetime import datetime

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    # Redirect if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                email=form.email.data.lower().strip(),
                created_at=datetime.utcnow()
            )
            user.set_password(form.password.data)
            
            # Add to database
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in with your new account.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register.html', form=form)
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    # Redirect if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        
        # Check credentials
        if user and user.check_password(form.password.data):
            # Update last login time
            user.update_last_login()
            
            # Log in user
            login_user(user, remember=False)
            
            flash(f'Welcome back, {user.email}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)
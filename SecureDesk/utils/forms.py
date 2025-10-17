"""
Form validation classes using WTForms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets import TextArea
from models import User
import re

class RegistrationForm(FlaskForm):
    """User registration form with validation"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different email.')
    
    def validate_password(self, password):
        """Validate password strength requirements"""
        pwd = password.data
        
        # Check for minimum requirements: 8 chars, mixed case, numbers
        if len(pwd) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        if not re.search(r'[a-z]', pwd):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        if not re.search(r'[A-Z]', pwd):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        if not re.search(r'\d', pwd):
            raise ValidationError('Password must contain at least one number.')

class LoginForm(FlaskForm):
    """User login form with validation"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    submit = SubmitField('Login')

class NoteForm(FlaskForm):
    """Note creation and editing form"""
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(max=200, message='Title must be less than 200 characters')
    ])
    
    content = TextAreaField('Content', validators=[
        Length(max=5000, message='Content must be less than 5000 characters')
    ], render_kw={'rows': 10, 'placeholder': 'Enter your note content here...'})
    
    submit = SubmitField('Save Note')

class PasswordEntryForm(FlaskForm):
    """Password entry creation and editing form"""
    service_name = StringField('Service Name', validators=[
        DataRequired(message='Service name is required'),
        Length(max=100, message='Service name must be less than 100 characters')
    ], render_kw={'placeholder': 'e.g., Gmail, Facebook, Bank'})
    
    username = StringField('Username/Email', validators=[
        DataRequired(message='Username is required'),
        Length(max=100, message='Username must be less than 100 characters')
    ], render_kw={'placeholder': 'Your username or email for this service'})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ], render_kw={'placeholder': 'Enter the password for this service'})
    
    submit = SubmitField('Save Password')

class EditPasswordEntryForm(FlaskForm):
    """Form for editing existing password entries"""
    service_name = StringField('Service Name', validators=[
        DataRequired(message='Service name is required'),
        Length(max=100, message='Service name must be less than 100 characters')
    ])
    
    username = StringField('Username/Email', validators=[
        DataRequired(message='Username is required'),
        Length(max=100, message='Username must be less than 100 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    submit = SubmitField('Update Password')

class DeleteConfirmationForm(FlaskForm):
    """Form for confirming deletions"""
    item_id = HiddenField('Item ID', validators=[DataRequired()])
    submit = SubmitField('Confirm Delete')

class SearchForm(FlaskForm):
    """Form for searching notes and passwords"""
    query = StringField('Search', validators=[
        Length(max=100, message='Search query must be less than 100 characters')
    ], render_kw={'placeholder': 'Search notes and passwords...'})
    
    submit = SubmitField('Search')

class PasswordGeneratorForm(FlaskForm):
    """Form for generating secure passwords"""
    length = StringField('Length', validators=[
        DataRequired(message='Length is required')
    ], default='16', render_kw={'type': 'number', 'min': '8', 'max': '128'})
    
    include_symbols = StringField('Include Symbols', render_kw={'type': 'checkbox', 'checked': True})
    
    submit = SubmitField('Generate Password')
    
    def validate_length(self, length):
        """Validate password length"""
        try:
            length_int = int(length.data)
            if length_int < 8:
                raise ValidationError('Password length must be at least 8 characters.')
            if length_int > 128:
                raise ValidationError('Password length cannot exceed 128 characters.')
        except ValueError:
            raise ValidationError('Please enter a valid number for length.')

# Custom widget for password reveal functionality
class PasswordRevealWidget:
    """Custom widget for password fields with reveal functionality"""
    
    def __call__(self, field, **kwargs):
        kwargs.setdefault('type', 'password')
        kwargs.setdefault('class', 'form-control password-field')
        
        # Build attributes string
        attrs = ' '.join(f'{k}="{v}"' for k, v in kwargs.items())
        
        html = '<div class="input-group">'
        html += f'<input {attrs} name="{field.name}" value="{field.data or ""}">'
        html += '<div class="input-group-append">'
        html += '<button class="btn btn-outline-secondary toggle-password" type="button">'
        html += '<i class="fas fa-eye"></i>'
        html += '</button>'
        html += '</div>'
        html += '</div>'
        
        return html
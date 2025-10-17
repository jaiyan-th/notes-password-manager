"""
Password management routes and logic
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, PasswordEntry
from utils.forms import PasswordEntryForm, EditPasswordEntryForm, DeleteConfirmationForm, SearchForm, PasswordGeneratorForm
from utils.security import PasswordEncryption, PasswordGenerator
from datetime import datetime

# Create passwords blueprint
passwords_bp = Blueprint('passwords', __name__, url_prefix='/passwords')

@passwords_bp.route('/')
@login_required
def list_passwords():
    """List all user password entries with search and pagination"""
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '', type=str)
    
    # Base query for user's password entries
    query = PasswordEntry.query.filter_by(user_id=current_user.id)
    
    # Apply search filter if provided
    if search_query:
        query = query.filter(
            (PasswordEntry.service_name.contains(search_query)) | 
            (PasswordEntry.username.contains(search_query))
        )
        search_form.query.data = search_query
    
    # Order by creation date (newest first) and paginate
    password_entries = query.order_by(PasswordEntry.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False, max_per_page=50
    )
    
    return render_template('passwords.html', 
                         password_entries=password_entries, 
                         search_form=search_form,
                         search_query=search_query)

@passwords_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_password():
    """Create a new password entry"""
    form = PasswordEntryForm()
    generator_form = PasswordGeneratorForm()
    
    if form.validate_on_submit():
        try:
            # Encrypt the password
            encrypted_password = PasswordEncryption.encrypt_password(
                form.password.data, 
                current_user.id
            )
            
            # Create new password entry
            password_entry = PasswordEntry(
                service_name=form.service_name.data.strip(),
                username=form.username.data.strip(),
                encrypted_password=encrypted_password,
                user_id=current_user.id
            )
            
            # Add to database
            db.session.add(password_entry)
            db.session.commit()
            
            flash('Password entry created successfully!', 'success')
            return redirect(url_for('passwords.list_passwords'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the password entry. Please try again.', 'error')
    
    return render_template('password_form.html', 
                         form=form, 
                         generator_form=generator_form,
                         title='Add New Password')

@passwords_bp.route('/<int:password_id>')
@login_required
def view_password(password_id):
    """View a specific password entry"""
    password_entry = PasswordEntry.query.filter_by(
        id=password_id, 
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('password_detail.html', password_entry=password_entry)

@passwords_bp.route('/<int:password_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_password(password_id):
    """Edit an existing password entry"""
    password_entry = PasswordEntry.query.filter_by(
        id=password_id, 
        user_id=current_user.id
    ).first_or_404()
    
    form = EditPasswordEntryForm()
    generator_form = PasswordGeneratorForm()
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.service_name.data = password_entry.service_name
        form.username.data = password_entry.username
        # Don't pre-populate password for security
    
    if form.validate_on_submit():
        try:
            # Encrypt the new password
            encrypted_password = PasswordEncryption.encrypt_password(
                form.password.data, 
                current_user.id
            )
            
            # Update password entry
            password_entry.update_entry(
                service_name=form.service_name.data.strip(),
                username=form.username.data.strip(),
                encrypted_password=encrypted_password
            )
            
            # Save changes
            db.session.commit()
            
            flash('Password entry updated successfully!', 'success')
            return redirect(url_for('passwords.view_password', password_id=password_entry.id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the password entry. Please try again.', 'error')
    
    return render_template('password_form.html', 
                         form=form, 
                         generator_form=generator_form,
                         password_entry=password_entry, 
                         title='Edit Password Entry')

@passwords_bp.route('/<int:password_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_password(password_id):
    """Delete a password entry with confirmation"""
    password_entry = PasswordEntry.query.filter_by(
        id=password_id, 
        user_id=current_user.id
    ).first_or_404()
    
    form = DeleteConfirmationForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Delete the password entry
                db.session.delete(password_entry)
                db.session.commit()
                
                flash('Password entry deleted successfully!', 'success')
                return redirect(url_for('passwords.list_passwords'))
                
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting the password entry. Please try again.', 'error')
    
    # Set the item_id for the form
    form.item_id.data = password_id
    
    return render_template('confirm_delete.html', 
                         form=form, 
                         item=password_entry, 
                         item_type='password entry',
                         cancel_url=url_for('passwords.view_password', password_id=password_entry.id))

@passwords_bp.route('/<int:password_id>/reveal', methods=['POST'])
@login_required
def reveal_password(password_id):
    """Reveal encrypted password via AJAX"""
    password_entry = PasswordEntry.query.filter_by(
        id=password_id, 
        user_id=current_user.id
    ).first_or_404()
    
    try:
        # Decrypt the password
        decrypted_password = PasswordEncryption.decrypt_password(
            password_entry.encrypted_password, 
            current_user.id
        )
        
        return jsonify({
            'status': 'success',
            'password': decrypted_password
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to decrypt password'
        }), 500

@passwords_bp.route('/generate', methods=['POST'])
@login_required
def generate_password():
    """Generate a secure password via AJAX"""
    form = PasswordGeneratorForm()
    
    if form.validate_on_submit():
        try:
            length = int(form.length.data)
            include_symbols = bool(form.include_symbols.data)
            
            # Generate password
            generated_password = PasswordGenerator.generate_password(
                length=length,
                include_symbols=include_symbols
            )
            
            # Get password strength analysis
            strength_analysis = PasswordGenerator.check_password_strength(generated_password)
            
            return jsonify({
                'status': 'success',
                'password': generated_password,
                'strength': strength_analysis
            })
            
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate password'
            }), 500
    
    return jsonify({
        'status': 'error',
        'message': 'Invalid form data'
    }), 400

@passwords_bp.route('/search')
@login_required
def search_passwords():
    """Search password entries (redirect to list with query)"""
    query = request.args.get('q', '')
    return redirect(url_for('passwords.list_passwords', q=query))

# API-like routes for AJAX operations
@passwords_bp.route('/api/<int:password_id>/quick-delete', methods=['POST'])
@login_required
def quick_delete_password(password_id):
    """Quick delete password entry via AJAX"""
    password_entry = PasswordEntry.query.filter_by(
        id=password_id, 
        user_id=current_user.id
    ).first_or_404()
    
    try:
        db.session.delete(password_entry)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Password entry deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to delete password entry'}), 500
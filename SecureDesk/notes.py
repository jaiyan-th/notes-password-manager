"""
Notes management routes and logic
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Note
from utils.forms import NoteForm, DeleteConfirmationForm, SearchForm
from datetime import datetime

# Create notes blueprint
notes_bp = Blueprint('notes', __name__, url_prefix='/notes')

@notes_bp.route('/')
@login_required
def list_notes():
    """List all user notes with search and pagination"""
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '', type=str)
    
    # Base query for user's notes
    query = Note.query.filter_by(user_id=current_user.id)
    
    # Apply search filter if provided
    if search_query:
        query = query.filter(
            (Note.title.contains(search_query)) | 
            (Note.content.contains(search_query))
        )
        search_form.query.data = search_query
    
    # Order by creation date (newest first) and paginate
    notes = query.order_by(Note.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False, max_per_page=50
    )
    
    return render_template('notes.html', 
                         notes=notes, 
                         search_form=search_form,
                         search_query=search_query)

@notes_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_note():
    """Create a new note"""
    form = NoteForm()
    
    if form.validate_on_submit():
        try:
            # Create new note
            note = Note(
                title=form.title.data.strip(),
                content=form.content.data.strip() if form.content.data else '',
                user_id=current_user.id
            )
            
            # Add to database
            db.session.add(note)
            db.session.commit()
            
            flash('Note created successfully!', 'success')
            return redirect(url_for('notes.list_notes'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the note. Please try again.', 'error')
    
    return render_template('note_form.html', form=form, title='Create New Note')

@notes_bp.route('/<int:note_id>')
@login_required
def view_note(note_id):
    """View a specific note"""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    return render_template('note_detail.html', note=note)

@notes_bp.route('/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    """Edit an existing note"""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    form = NoteForm(obj=note)
    
    if form.validate_on_submit():
        try:
            # Update note content
            note.update_content(
                title=form.title.data.strip(),
                content=form.content.data.strip() if form.content.data else ''
            )
            
            # Save changes
            db.session.commit()
            
            flash('Note updated successfully!', 'success')
            return redirect(url_for('notes.view_note', note_id=note.id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the note. Please try again.', 'error')
    
    return render_template('note_form.html', 
                         form=form, 
                         note=note, 
                         title='Edit Note')

@notes_bp.route('/<int:note_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_note(note_id):
    """Delete a note with confirmation"""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    form = DeleteConfirmationForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Delete the note
                db.session.delete(note)
                db.session.commit()
                
                flash('Note deleted successfully!', 'success')
                return redirect(url_for('notes.list_notes'))
                
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting the note. Please try again.', 'error')
    
    # Set the item_id for the form
    form.item_id.data = note_id
    
    return render_template('confirm_delete.html', 
                         form=form, 
                         item=note, 
                         item_type='note',
                         cancel_url=url_for('notes.view_note', note_id=note.id))

@notes_bp.route('/search')
@login_required
def search_notes():
    """Search notes (redirect to list with query)"""
    query = request.args.get('q', '')
    return redirect(url_for('notes.list_notes', q=query))

# API-like routes for AJAX operations
@notes_bp.route('/api/<int:note_id>/quick-delete', methods=['POST'])
@login_required
def quick_delete_note(note_id):
    """Quick delete note via AJAX"""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(note)
        db.session.commit()
        return {'status': 'success', 'message': 'Note deleted successfully'}
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': 'Failed to delete note'}, 500
import os
import uuid
from datetime import date
from dotenv import load_dotenv
load_dotenv()  # Load API key from .env file

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import Config
from database import db, JournalEntry
from ai_analyzer import analyze_wine_label

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

app = create_app()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    search = request.args.get('q', '')
    query = JournalEntry.query
    if search:
        query = query.filter(
            JournalEntry.wine_name.ilike(f'%{search}%') |
            JournalEntry.producer.ilike(f'%{search}%')
        )
    # Order by ID descending to always show newest first
    entries = query.order_by(JournalEntry.id.desc()).all()
    return render_template('index.html', entries=entries, search=search)

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['photo']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('index'))
        
    if file and allowed_file(file.filename):
        # Save image securely
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Path for saving on the server
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Path for database, making it easy to fetch via url_for('static', filename=...)
        db_path = f"uploads/{filename}"

        # Create empty entry with today's date
        entry = JournalEntry(date=date.today(), image_path=db_path)
        db.session.add(entry)
        db.session.commit()

        # AI analysis
        try:
            result = analyze_wine_label(filepath)
            entry.wine_name = result.get('wine_name', '')
            entry.producer = result.get('producer', '')
            entry.vintage = result.get('vintage', '')
            entry.region = result.get('region', '')
            entry.country = result.get('country', '')
            entry.grape_variety = result.get('grape_variety', '')
            entry.other_details = result.get('other_details', '')
            entry.confidence = result.get('confidence', 0.0)
            entry.raw_ai_response = result.get('raw_response', '')
            db.session.commit()
        except Exception as e:
            flash(f'AI analysis failed: {str(e)}. Please fill manually.', 'warning')

        return redirect(url_for('edit_entry', entry_id=entry.id))
    else:
        flash('Invalid file type. Allowed: jpg, jpeg, png, gif, webp', 'danger')
        return redirect(url_for('index'))

@app.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if request.method == 'POST':
        entry.wine_name = request.form.get('wine_name', '')
        entry.producer = request.form.get('producer', '')
        entry.vintage = request.form.get('vintage', '')
        entry.region = request.form.get('region', '')
        entry.country = request.form.get('country', '')
        entry.grape_variety = request.form.get('grape_variety', '')
        entry.other_details = request.form.get('other_details', '')
        db.session.commit()
        flash('Entry saved!', 'success')
        return redirect(url_for('view_entry', entry_id=entry.id))
    return render_template('edit_entry.html', entry=entry)

@app.route('/entry/<int:entry_id>')
def view_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    return render_template('view_entry.html', entry=entry)

@app.route('/entry/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted.', 'info')
    return redirect(url_for('index'))

@app.route('/entry/delete_multiple', methods=['POST'])
def delete_multiple_entries():
    entry_ids = request.form.getlist('entry_ids')
    if not entry_ids:
        flash('No entries selected.', 'warning')
        return redirect(url_for('index'))
    # Convert to int and delete
    ids_to_delete = [int(eid) for eid in entry_ids]
    JournalEntry.query.filter(JournalEntry.id.in_(ids_to_delete)).delete(synchronize_session='fetch')
    db.session.commit()
    flash(f'{len(ids_to_delete)} entry(ies) deleted.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
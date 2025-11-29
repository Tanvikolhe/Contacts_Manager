import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, flash

# Make sure 'database.py' is in the same folder
from database import init_db 

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = 'super_secret_key_for_contact_manager' 

DATABASE = 'contacts.db'

# --- Database Connection Helper ---

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name (e.g., contact['name'])
    return conn

# --- Contact Data Validation ---

def validate_contact(name, email, phone):
    """Performs basic validation on contact fields."""
    errors = {}
    
    # Name Validation
    if not name or len(name.strip()) == 0:
        errors['name'] = 'Name is required.'
    
    # Email Validation
    if not email or len(email.strip()) == 0:
        errors['email'] = 'Email is required.'
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors['email'] = 'Invalid email format.'

    # Phone Validation (Allows numbers, spaces, hyphens, plus sign)
    if phone and not re.match(r"^\+?[\d\s\-\(\)]{6,15}$", phone):
        errors['phone'] = 'Invalid phone number format.'

    return errors

# --- CRUD Operations (Routes) ---

@app.route('/', methods=('GET', 'POST'))
def index():
    """Handles the List (Read) and Add (Create) operations."""
    conn = get_db_connection()
    
    # Handle New Contact Submission (CREATE)
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        
        errors = validate_contact(name, email, phone)

        if errors:
            # Flash error messages if validation fails
            for field, msg in errors.items():
                flash(f'{field.capitalize()}: {msg}', 'error')
            
            # Re-render the page with existing contacts and user's form data
            contacts = conn.execute('SELECT * FROM contacts ORDER BY name').fetchall()
            conn.close()
            return render_template('index.html', contacts=contacts, form_data=request.form)
        
        else:
            # Insert valid data into the database
            conn.execute("INSERT INTO contacts (name, email, phone) VALUES (?, ?, ?)",
                         (name, email, phone))
            conn.commit()
            flash(f'Contact "{name}" added successfully!', 'success')
            conn.close()
            return redirect(url_for('index'))

    # Handle List Contacts (READ)
    contacts = conn.execute('SELECT * FROM contacts ORDER BY name').fetchall()
    conn.close()
    return render_template('index.html', contacts=contacts)


@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    """Handles the Edit (Update) operation."""
    conn = get_db_connection()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (id,)).fetchone()
    
    if contact is None:
        flash('Contact not found.', 'error')
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        
        errors = validate_contact(name, email, phone)

        if errors:
            for field, msg in errors.items():
                flash(f'{field.capitalize()}: {msg}', 'error')
            # If errors, re-render the edit page
            conn.close()
            return render_template('edit.html', contact=contact, form_data=request.form)
        
        else:
            # Update the record
            conn.execute('UPDATE contacts SET name = ?, email = ?, phone = ? WHERE id = ?',
                         (name, email, phone, id))
            conn.commit()
            flash(f'Contact "{name}" updated successfully!', 'success')
            conn.close()
            return redirect(url_for('index'))

    # GET request: show the edit form
    conn.close()
    return render_template('edit.html', contact=contact)


@app.route('/<int:id>/delete/', methods=('POST',))
def delete(id):
    """Handles the Delete operation."""
    conn = get_db_connection()
    
    # Get contact name before deleting for a confirmation message
    contact = conn.execute('SELECT name FROM contacts WHERE id = ?', (id,)).fetchone()
    
    if contact:
        conn.execute('DELETE FROM contacts WHERE id = ?', (id,))
        conn.commit()
        flash(f'Contact "{contact["name"]}" deleted successfully!', 'success')
    else:
        flash('Contact not found.', 'error')
        
    conn.close()
    return redirect(url_for('index'))

# --- Initialization and Execution ---

if __name__ == '__main__':
    # Initialize the database (creates table if it doesn't exist)
    init_db(DATABASE)
    print(f"Database initialized: {DATABASE}")
    
    # Run the Flask development server
    app.run(debug=True)
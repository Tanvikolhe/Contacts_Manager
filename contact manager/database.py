import sqlite3

def init_db(database_name):
    """
    Creates the 'contacts' table in the SQLite database if it doesn't already exist.
    """
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Table schema: id, name (required), email (required), phone (optional)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT
        );
    """)

    conn.commit()
    conn.close()
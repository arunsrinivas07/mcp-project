import sqlite3
import os

# Move DB outside of the project folder so Live Server ignores it
DB_PATH = r"C:\Users\Admin\.gemini\antigravity\mcp.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

def add_columns():
    # List of columns to add to 'topics'
    new_cols = [
        ("user_id", "INTEGER"),
        ("document_id", "INTEGER"),
        ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
    ]
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(topics)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    
    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            try:
                print(f"Adding column {col_name} to topics...")
                cursor.execute(f"ALTER TABLE topics ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
    conn.commit()

# 5. QUIZZES table
cursor.execute("""
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    document_id INTEGER,
    question TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_option TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (document_id) REFERENCES documents(id)
)
""")
conn.commit()

# Run the update
add_columns()

# 1. USERS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. DOCUMENTS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    filename TEXT,
    data BLOB,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# 3. TOPICS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    document_id INTEGER,
    content TEXT,
    used INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (document_id) REFERENCES documents(id)
)
""")

# 4. INTERACTIONS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    query TEXT,
    response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()
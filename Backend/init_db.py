# init_db.py

import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    # Drop the table if needed (optional for resets)
    cur.execute("DROP TABLE IF EXISTS users")

    # Create users table with role
    cur.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # Optional: add a default admin user
    admin_password = "admin123"  # You can hash it later using bcrypt
    cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", admin_password, "admin"))

    conn.commit()
    conn.close()
    print("✅ users.db created with admin user.")

if __name__ == "__main__":
    init_db()


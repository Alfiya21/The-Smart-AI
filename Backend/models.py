import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            rating REAL,
            url TEXT,
            pricing TEXT,
            tags TEXT,
            description TEXT,
            added_by INTEGER,
            FOREIGN KEY (added_by) REFERENCES users(id)
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER,
            tool_id INTEGER,
            PRIMARY KEY (user_id, tool_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (tool_id) REFERENCES tools(id)
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tool_id INTEGER,
            comment TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (tool_id) REFERENCES tools(id)
        );
    ''')
    

    conn.commit()
    conn.close()


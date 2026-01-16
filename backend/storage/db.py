import sqlite3

DB_NAME = "ddos.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS baseline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        request_count INTEGER
    )
    """)

    conn.commit()
    conn.close()

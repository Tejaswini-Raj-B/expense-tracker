import sqlite3
import os

DB_FILE = "expenses.db"

def get_conn():
    """Return a sqlite3 connection with Row factory."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create database file and tables if they don't exist."""
    # Only create once to avoid repeated work
    if not os.path.exists(DB_FILE):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE,
            monthly_budget REAL NOT NULL
        );
        """)
        conn.commit()
        conn.close()

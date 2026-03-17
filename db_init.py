# -----------------


"""db_init.py
Creates the SQLite database and tables for the hostel management system.
Run this once or let main.py create the DB on demand.
"""
import sqlite3
from pathlib import Path

DB_FILE = Path('hostel.db')

SCHEMA = '''
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block TEXT NOT NULL,
    room_number TEXT NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 1,
    occupants INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    phone TEXT,
    email TEXT,
    course TEXT,
    year INTEGER,
    room_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(room_id) REFERENCES rooms(id)
);

CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    due_date TEXT,
    paid_on TEXT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES students(id)
);
'''


def init_db(db_path='hostel.db'):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.executescript(SCHEMA)
        conn.commit()


if __name__ == '__main__':
    init_db(DB_FILE)
    print(f"Initialized database at {DB_FILE}")



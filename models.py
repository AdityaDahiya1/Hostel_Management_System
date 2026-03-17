"""models.py
Database access layer using sqlite3.
Keep statements simple and safe (parameters use placeholders).
"""
import sqlite3
from pathlib import Path

DB_PATH = Path('hostel.db')


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    from db_init import SCHEMA
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        conn.commit()


# Room functions

def add_room(block, room_number, capacity=1):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO rooms(block, room_number, capacity) VALUES(?,?,?)',
                    (block, room_number, capacity))
        conn.commit()
        return cur.lastrowid


def list_rooms():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM rooms ORDER BY block, room_number')
        return cur.fetchall()


def get_room(room_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM rooms WHERE id=?', (room_id,))
        return cur.fetchone()


def release_student_from_room(student_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT room_id FROM students WHERE id=?', (student_id,))
        r = cur.fetchone()
        if not r or r['room_id'] is None:
            return
        room_id = r['room_id']
        cur.execute('UPDATE rooms SET occupants = occupants - 1 WHERE id=? AND occupants>0', (room_id,))
        cur.execute('UPDATE students SET room_id=NULL WHERE id=?', (student_id,))
        conn.commit()


# Student functions

def add_student(name, roll_no, phone=None, email=None, course=None, year=None):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO students(name, roll_no, phone, email, course, year) VALUES(?,?,?,?,?,?)',
                    (name, roll_no, phone, email, course, year))
        conn.commit()
        return cur.lastrowid


def update_student(student_id, **fields):
    allowed = ['name', 'roll_no', 'phone', 'email', 'course', 'year']
    set_clause = ', '.join(f"{k}=?" for k in fields if k in allowed)
    vals = [fields[k] for k in fields if k in allowed]
    if not set_clause:
        return
    vals.append(student_id)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(f'UPDATE students SET {set_clause} WHERE id=?', vals)
        conn.commit()


def delete_student(student_id):
    # release room if allocated
    release_student_from_room(student_id)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM students WHERE id=?', (student_id,))
        conn.commit()


def get_student(student_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM students WHERE id=?', (student_id,))
        return cur.fetchone()


def search_students(term):
    like = f'%{term}%'
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT s.*, r.block as room_block, r.room_number as room_no
            FROM students s
            LEFT JOIN rooms r ON s.room_id = r.id
            WHERE s.name LIKE ? OR s.roll_no LIKE ? OR s.phone LIKE ? OR s.email LIKE ?
            ORDER BY s.name
        ''', (like, like, like, like))
        return cur.fetchall()


def list_students():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('''SELECT s.*, r.block as room_block, r.room_number as room_no
                       FROM students s LEFT JOIN rooms r ON s.room_id = r.id
                       ORDER BY s.name''')
        return cur.fetchall()

# Fee functions

def record_fee(student_id, amount, due_date=None, paid_on=None, remarks=None):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO fees(student_id, amount, due_date, paid_on, remarks) VALUES(?,?,?,?,?)',
                    (student_id, amount, due_date, paid_on, remarks))
        conn.commit()
        return cur.lastrowid


def get_fees_for_student(student_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM fees WHERE student_id=? ORDER BY created_at DESC', (student_id,))
        return cur.fetchall()


def get_all_fees():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('''SELECT f.*, s.name, s.roll_no FROM fees f JOIN students s ON f.student_id = s.id
                       ORDER BY f.created_at DESC''')
        return cur.fetchall()




import sqlite3
import os
from datetime import datetime

def init_db(db_path='loans.db'):
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT,
        nombre TEXT,
        items TEXT,
        doc_raw TEXT,
        person_photo TEXT,
        loan_time TEXT,
        returned INTEGER DEFAULT 0,
        return_time TEXT,
        return_photo TEXT
    )
    ''')
    conn.commit()
    conn.close()

def record_loan(cedula, nombre, items, doc_raw, person_photo, db_path='loans.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''INSERT INTO loans (cedula, nombre, items, doc_raw, person_photo, loan_time, returned)
                   VALUES (?, ?, ?, ?, ?, ?, 0)
                ''', (cedula, nombre, ','.join(items), doc_raw, person_photo, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def record_return(cedula, items_returned, return_photo, db_path='loans.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # we will mark all currently non-returned loans for this cedula as returned
    cur.execute('''SELECT id, items FROM loans WHERE cedula=? AND returned=0''', (cedula,))
    rows = cur.fetchall()
    for rid, items in rows:
        # This simple approach marks the loan returned fully
        cur.execute('''UPDATE loans SET returned=1, return_time=?, return_photo=? WHERE id=?''',
                    (datetime.utcnow().isoformat(), return_photo, rid))
    conn.commit()
    conn.close()

def get_active_loans(cedula, db_path='loans.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''SELECT id, items, loan_time FROM loans WHERE cedula=? AND returned=0''', (cedula,))
    rows = cur.fetchall()
    conn.close()
    return rows

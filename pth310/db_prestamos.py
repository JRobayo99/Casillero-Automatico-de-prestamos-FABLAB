import sqlite3
from pathlib import Path

def init_db(db_path="prestamos.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            apellido1 TEXT,
            apellido2 TEXT,
            cedula TEXT,
            fecha_nac TEXT,
            rh TEXT,
            sexo TEXT,
            foto_path TEXT,
            herramientas TEXT,
            fecha_prestamo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def guardar_prestamo(nombre, apellido1, apellido2, cedula, fecha_nac, rh, sexo, foto_path, herramientas, db_path="prestamos.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO prestamos (nombre, apellido1, apellido2, cedula, fecha_nac, rh, sexo, foto_path, herramientas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, apellido1, apellido2, cedula, fecha_nac, rh, sexo, foto_path, ','.join(herramientas)))
    conn.commit()
    conn.close()

def obtener_historial(db_path="prestamos.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM prestamos ORDER BY fecha_prestamo DESC')
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada.")

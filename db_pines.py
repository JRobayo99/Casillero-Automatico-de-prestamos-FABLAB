import sqlite3
import os
from datetime import datetime

class BaseDatoPines:
    """Gestiona la base de datos de PINes autorizados"""
    
    def __init__(self, nombre_db="pines.db"):
        self.nombre_db = nombre_db
        self.conexion = None
        self.inicializar_db()
    
    def inicializar_db(self):
        """Crea la base de datos y la tabla si no existen"""
        try:
            self.conexion = sqlite3.connect(self.nombre_db)
            cursor = self.conexion.cursor()
            
            # Crear tabla de PINes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pin TEXT UNIQUE NOT NULL,
                    usuario TEXT NOT NULL,
                    fecha_creacion TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    fecha_ultimo_uso TEXT
                )
            ''')
            
            # Crear tabla de intentos de acceso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS intentos_acceso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pin TEXT NOT NULL,
                    resultado TEXT NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    id_usuario INTEGER
                )
            ''')
            
            self.conexion.commit()
            print("Base de datos inicializada correctamente")
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
    
    def agregar_pin(self, pin, usuario):
        """Agrega un nuevo PIN a la base de datos"""
        try:
            cursor = self.conexion.cursor()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO pines (pin, usuario, fecha_creacion)
                VALUES (?, ?, ?)
            ''', (pin, usuario, fecha))
            
            self.conexion.commit()
            return True, f"PIN registrado exitosamente para {usuario}"
        except sqlite3.IntegrityError:
            return False, "El PIN ya existe en la base de datos"
        except sqlite3.Error as e:
            return False, f"Error al agregar PIN: {e}"
    
    def validar_pin(self, pin):
        """Valida si un PIN existe y está activo"""
        try:
            cursor = self.conexion.cursor()
            cursor.execute('''
                SELECT id, usuario, activo FROM pines 
                WHERE pin = ? AND activo = 1
            ''', (pin,))
            
            resultado = cursor.fetchone()
            
            # Registrar intento de acceso
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if resultado:
                cursor.execute('''
                    INSERT INTO intentos_acceso (pin, resultado, fecha_hora, id_usuario)
                    VALUES (?, ?, ?, ?)
                ''', (pin, 'ÉXITO', fecha, resultado[0]))
                
                # Actualizar fecha de último uso
                cursor.execute('''
                    UPDATE pines SET fecha_ultimo_uso = ? 
                    WHERE id = ?
                ''', (fecha, resultado[0]))
            else:
                cursor.execute('''
                    INSERT INTO intentos_acceso (pin, resultado, fecha_hora)
                    VALUES (?, ?, ?)
                ''', (pin, 'FALLÓ', fecha))
            
            self.conexion.commit()
            return resultado is not None, resultado
        except sqlite3.Error as e:
            print(f"Error al validar PIN: {e}")
            return False, None
    
    def obtener_todos_pines(self):
        """Obtiene todos los PINes registrados"""
        try:
            cursor = self.conexion.cursor()
            cursor.execute('''
                SELECT id, pin, usuario, fecha_creacion, activo, fecha_ultimo_uso
                FROM pines
                ORDER BY fecha_creacion DESC
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener PINes: {e}")
            return []
    
    def eliminar_pin(self, pin):
        """Desactiva un PIN (no lo elimina físicamente)"""
        try:
            cursor = self.conexion.cursor()
            cursor.execute('UPDATE pines SET activo = 0 WHERE pin = ?', (pin,))
            self.conexion.commit()
            return True, "PIN desactivado"
        except sqlite3.Error as e:
            return False, f"Error al desactivar PIN: {e}"
    
    def obtener_historial(self):
        """Obtiene el historial de intentos de acceso"""
        try:
            cursor = self.conexion.cursor()
            cursor.execute('''
                SELECT pin, resultado, fecha_hora FROM intentos_acceso
                ORDER BY fecha_hora DESC
                LIMIT 100
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener historial: {e}")
            return []
    
    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        if self.conexion:
            self.conexion.close()

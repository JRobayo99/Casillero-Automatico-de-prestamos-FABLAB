#!/usr/bin/env python3
"""
Módulo auxiliar para lectura de sensor RFID.
Puede ser llamado independientemente del flujo principal.
"""

import subprocess
import sys
import os

def leer_sensor_rfid():
    """
    Lee el PIN desde el sensor RFID usando PruebaRFID.py
    Retorna el PIN leído o None si hay error
    """
    try:
        print("🔍 Leyendo sensor RFID...")

        # Ejecutar el script de lectura RFID
        resultado = subprocess.run(
            ["sudo", "-E", "python3", "PruebaRFID.py"],
            capture_output=True,
            text=True,
            timeout=10  # Timeout de 10 segundos
        )

        # Procesar salida
        salida = resultado.stdout.strip()
        error = resultado.stderr.strip()

        print(f"Salida RFID: {salida}")
        if error:
            print(f"Error RFID: {error}")

        # Extraer PIN de la salida
        if "ID:" in salida:
            # Formato esperado: "ID: 123456789"
            partes = salida.split("ID: ")
            if len(partes) > 1:
                pin_raw = partes[1].split()[0].strip()
                print(f"✅ PIN detectado: {pin_raw}")
                return pin_raw

        print("❌ No se pudo detectar PIN en la salida")
        return None

    except subprocess.TimeoutExpired:
        print("⏰ Timeout en lectura RFID")
        return None
    except Exception as e:
        print(f"❌ Error al leer sensor RFID: {e}")
        return None

def leer_sensor_con_reintentos(max_reintentos=3, delay=2):
    """
    Intenta leer el sensor RFID con reintentos
    """
    for intento in range(max_reintentos):
        print(f"Intento {intento + 1}/{max_reintentos}")
        pin = leer_sensor_rfid()
        if pin:
            return pin
        if intento < max_reintentos - 1:
            print(f"Esperando {delay} segundos antes del siguiente intento...")
            import time
            time.sleep(delay)

    print("❌ No se pudo leer el PIN después de todos los intentos")
    return None

def validar_pin_leido(pin):
    """
    Valida un PIN leído contra la base de datos
    """
    try:
        from db_pines import BaseDatoPines
        db = BaseDatoPines("pines.db")
        valido, datos = db.validar_pin(pin)
        db.cerrar()

        if valido:
            usuario = datos[1]
            print(f"✅ PIN válido - Usuario: {usuario}")
            return True, usuario
        else:
            print("❌ PIN no válido o no registrado")
            return False, None

    except Exception as e:
        print(f"❌ Error al validar PIN: {e}")
        return False, None

if __name__ == "__main__":
    # Si se ejecuta directamente, leer sensor y mostrar resultado
    print("=== LECTOR RFID AUXILIAR ===")
    pin = leer_sensor_con_reintentos()
    if pin:
        print(f"PIN leído: {pin}")
        valido, usuario = validar_pin_leido(pin)
        if valido:
            print(f"Usuario autorizado: {usuario}")
        else:
            print("PIN no autorizado")
    else:
        print("No se pudo leer ningún PIN")
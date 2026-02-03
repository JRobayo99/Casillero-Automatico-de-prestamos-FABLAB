#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del lector RFID
Ejecutar con: sudo python3 test_rfid.py
"""
import sys
import os

def test_rfid():
    """Prueba básica del lector RFID"""
    try:
        print("🔍 Probando inicialización del lector RFID...")
        import RPi.GPIO as GPIO
        from mfrc522 import SimpleMFRC522

        print("✅ Librerías importadas correctamente")

        # Configurar GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        reader = SimpleMFRC522()
        print("✅ Lector RFID inicializado correctamente")

        print("\n📡 Acerque una tarjeta RFID al lector...")
        print("Presione Ctrl+C para salir")

        while True:
            try:
                id_rfid, texto = reader.read()
                pin_leido = str(id_rfid).strip()
                print(f"✅ PIN detectado: {pin_leido}")
                print(f"   Texto: {texto}")
                print("📡 Esperando siguiente lectura...\n")
            except KeyboardInterrupt:
                print("\n👋 Prueba finalizada")
                break
            except Exception as e:
                print(f"❌ Error durante lectura: {e}")

        GPIO.cleanup()

    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("   Instale con: pip install mfrc522")
        return False
    except PermissionError as e:
        print(f"❌ Error de permisos: {e}")
        print("   Ejecute con: sudo python3 test_rfid.py")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🧪 PRUEBA DEL LECTOR RFID")
    print("=" * 40)

    if os.geteuid() != 0:
        print("⚠ ADVERTENCIA: No ejecutando como root")
        print("   Para funcionalidad completa, use: sudo python3 test_rfid.py")
        print()

    success = test_rfid()

    if success:
        print("✅ Prueba completada exitosamente")
    else:
        print("❌ Prueba fallida")
        sys.exit(1)
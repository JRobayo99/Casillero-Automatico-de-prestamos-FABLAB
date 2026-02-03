import subprocess
import sys
import os

# Cambiar al directorio actual
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Ejecutar la interfaz completa del sistema
print("Iniciando Sistema Completo de Control de Acceso RFID...")
try:
    subprocess.run([sys.executable, "interfaz_completa.py"], check=True)
except KeyboardInterrupt:
    print("\nSistema cerrado por el usuario")
except Exception as e:
    print(f"Error: {e}")
    # Si falla, intentar con la interfaz de acceso básica
    print("Intentando ejecutar interfaz de acceso básica...")
    try:
        subprocess.run([sys.executable, "interfaz_acceso.py"], check=True)
    except Exception as e2:
        print(f"Error: {e2}")
        # Si falla todo, ejecutar PruebaRFID
        print("Intentando ejecutar PruebaRFID...")
        subprocess.run(["sudo", "-E", "python3", "PruebaRFID.py"], check=True)

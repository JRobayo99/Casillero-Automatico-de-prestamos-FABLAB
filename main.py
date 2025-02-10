import time
import subprocess
from mcp_control import leer_entrada

print("Sistema iniciado")

while True:

    estado= leer_entrada()

    if not (estado & 0b00000001):
        print("Boton presionado LED ROJO")
        subprocess.run(["sudo","python3","led_control.py","255","0","0"])
        time.sleep(0.5)

    time.sleep(0.1)
import subprocess
from mcp_control import activar_salida

print("Sistema listo (1–32, 0 para salir)")

while True:
    try:
        n = int(input("Número: "))
    except ValueError:
        continue

    if n == 0:
        break

    if 1 <= n <= 32:
        activar_salida(n)
        subprocess.run(
            ["sudo", "python3", "led_control.py", str(n)],
            check=False          
        )
    else:
        print("Número fuera de rango")
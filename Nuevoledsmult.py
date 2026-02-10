import tkinter as tk
import busio
import board
from adafruit_mcp230xx.mcp23017 import MCP23017
from rpi_ws281x import PixelStrip, Color

# =======================
# CONFIGURACIÓN LED
# =======================
LED_COUNT = 300
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 128
LED_INVERT = False
LED_CHANNEL = 0
SEGMENTS = 32

RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ,
    LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
)
strip.begin()

# =======================
# CONFIGURACIÓN I2C / MCP
# =======================
i2c = busio.I2C(board.SCL, board.SDA)

mcpA = MCP23017(i2c, address=0x23)  # 1–16
mcpB = MCP23017(i2c, address=0x27)  # 17–32

pinsA = [mcpA.get_pin(i) for i in range(16)]
pinsB = [mcpB.get_pin(i) for i in range(16)]

for p in pinsA + pinsB:
    p.switch_to_output(value=True)  # HIGH = apagado

# =======================
# FUNCIONES LED
# =======================
def set_segment(seg, color):
    base = LED_COUNT // SEGMENTS
    extra = LED_COUNT % SEGMENTS

    start = seg * base + min(seg, extra)
    length = base + (1 if seg < extra else 0)

    for i in range(start, start + length):
        strip.setPixelColor(i, color)

def leds_rojo():
    for s in range(SEGMENTS):
        set_segment(s, RED)
    strip.show()

# =======================
# FUNCIÓN PRINCIPAL
# =======================
def activar_casillero(numero):
    if numero < 1 or numero > 32:
        estado.config(text="Número fuera de rango (1–32)", fg="red")
        return

    # Apagar todos los pines
    for p in pinsA + pinsB:
        p.value = True

    # LEDs a rojo
    leds_rojo()

    # Activar pin correcto
    if numero <= 16:
        pinsA[numero - 1].value = False
    else:
        pinsB[numero - 17].value = False

    # LED a verde
    set_segment(numero - 1, GREEN)
    strip.show()

    estado.config(text=f"Casillero {numero} ACTIVADO", fg="green")

# =======================
# INTERFAZ
# =======================
root = tk.Tk()
root.title("Control Casilleros 1–32")
root.geometry("400x250")

tk.Label(root, text="Ingrese número de casillero (1–32)",
         font=("Arial", 14)).pack(pady=10)

entrada = tk.Entry(root, font=("Arial", 20), justify="center")
entrada.pack(pady=10)

def ejecutar():
    try:
        n = int(entrada.get())
        activar_casillero(n)
    except ValueError:
        estado.config(text="Entrada inválida", fg="red")

tk.Button(root, text="ACTIVAR",
          font=("Arial", 16),
          bg="#00adb5",
          command=ejecutar).pack(pady=10)

estado = tk.Label(root, text="", font=("Arial", 14))
estado.pack(pady=10)

leds_rojo()
root.mainloop()

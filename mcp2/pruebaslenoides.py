import time 
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017

i2c = busio.I2C(board.SCL, board.SDA)

mcp = MCP23017(i2c)

pins = [mcp.get_pin(i) for i in range(16)]

for pin in pins:
    pin.swicthh_to_output(value=False)

print("Probando los 16 pines del MCP23017")

while True:
    for i, pin in enumerate(pins):
        print(f"Encendiendo pin {i}")
        pin.value = True
        time.sleep(1)

        print(f"Apagando pin {i}")
        pin.value = False
        time.sleep(0.5)
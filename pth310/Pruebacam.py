import time
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017

i2c = busio.I2C(board.SCL, board.SDA)

mcp = MCP23017(i2c, address=0x27)

leds= []
for i in range(8):

    pin = mcp.get_pin(i)
    pin.switch_to_output(value=False)
    leds.append(pin)


def led_on(n):

    leds[n].value = True

def led_off(n):
    
    leds[n].value = False

def test_leds():

    for i in range(8):

        print(f"Encendiendo led {i}")
        led_on(i)
        time.sleep(0.5)

        print(f"Apagando led {i}")
        led_off(i)
        time.sleep(0.5)
        
if __name__ == "__main__":
    print("Iniciando prueba de leds")
    test_leds()
    print("Prueba finalizada")
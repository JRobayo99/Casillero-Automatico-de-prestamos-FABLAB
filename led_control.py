from rpi_ws281x import PixelStrip, Color
import time 
import sys


LED_CONT = 300
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 80
LED_INVERT = False
LED_CHANNEL = 0

strip = PixelStrip(LED_CONT,
                   LED_PIN,
                   LED_FREQ_HZ,
                   LED_DMA,
                   LED_INVERT,
                   LED_BRIGHTNESS,
                   LED_CHANNEL
                   )
strip.begin()

def set_color(r, g, b):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(r, g, b))
        strip.show()

def clear():
    set_color

if __name__== "__main__":
    if len (sys.argv) !=4:
        print("Uso: sudo python3 led_control.py R G B")
        sys.exit(1)

    r = int(sys.argv [1])
    g = int(sys.argv [2])
    b = int(sys.argv [3])

    set_color(r, g, b)

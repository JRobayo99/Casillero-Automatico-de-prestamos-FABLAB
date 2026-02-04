from rpi_ws281x import PixelStrip, Color
import time

SEGMENTS = 28
LED_COUNT = 300
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 128
LED_INVERT = False
LED_CHANNEL = 0

strip= PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def set_segment(seg_index, color):

    base = LED_COUNT // SEGMENTS
    extra = LED_COUNT % SEGMENTS

    start = seg_index * base + (seg_index if seg_index < extra else extra)
    length = base + (1 if seg_index < extra else 0)
    end = start + base + (1 if seg_index < extra else 0)

    for i in range(start, end):
        strip.setPixelColor(i, color)

def clear():

    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()


print("Prueba ws2812B iniciada")

colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255), Color(255, 255, 0), Color(0, 255, 255), Color(255, 0, 255)]

for s in range(SEGMENTS):
    clear()
    set_segment(s, colors[s % len(colors)])
    strip.show()
    time.sleep(0.5)

clear()

for s in range(SEGMENTS):
    set_segment(s, colors[s % len(colors)])
strip.show()

time.sleep(3)

clear()
print("Prueba finalizada") 

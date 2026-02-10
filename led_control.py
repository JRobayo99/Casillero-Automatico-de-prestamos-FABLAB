from rpi_ws281x import PixelStrip, Color

import sys


LED_COUNT = 300
SECTIONS = 32

LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 80
LED_INVERT = False
LED_CHANNEL = 0

strip = PixelStrip(LED_COUNT,
                   LED_PIN,
                   LED_FREQ_HZ,
                   LED_DMA,
                   LED_INVERT,
                   LED_BRIGHTNESS,
                   LED_CHANNEL
                   )
strip.begin()

def section_range(section):
    base = LED_COUNT // SECTIONS
    extra = LED_COUNT % SECTIONS

    start = section * base + min(section, extra)
    length = base + (1 if section < extra else 0)
    return start, start + length

def clear ():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))

def paint_all_green():
    for s in range(SECTIONS):
        start, end = section_range(s)
        for i in range(start, end):
            strip.setPixelColor(i, Color(0, 255, 0))
    strip.show()

def activate_section(section):
    paint_all_green()
    start, end = section_range(section)

    for i in range(start, end):
        strip.setPixelColor(i, Color(255, 0, 0))
    strip.show()
    

    if __name__ == "__main__":
        if len(sys.argv) != 2:
            print("Uso: python led_control.py <número de sección (0-31)>")
            sys.exit(1)

        num = int(sys.argv[1])
        
        if not 1 <= num <= 32:
            print(f"Error: el número de sección debe estar entre 0 y {SECTIONS-1}")
            sys.exit(1)
        
        activate_section(num - 1)
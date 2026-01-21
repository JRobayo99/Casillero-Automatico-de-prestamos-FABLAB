from mfrc522 import MFRC522
import lgpio
import time 

RST_PIN = 12
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, RST_PIN)

reader = MFRC522(spi_bus=0, spi_device=0, rst_pin=RST_PIN, gpio_handle=h)

print("Esperando tarjeta RFID...")

try:
    while True:
        status = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status == reader.MI_OK:
            status, uid = reader.MFRC522_Anticoll()

            if status == reader.MI_OK:
                print ("UID: ", uid)
                time.sleep(1)

except KeyboardInterrupt:
    pass
finally:
    lgpio.gpiochip_close(h)
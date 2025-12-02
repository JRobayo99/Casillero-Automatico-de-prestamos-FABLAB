import smbus2
import time

bus = smbus2.SMBus(1)
address= 0x27

while True:
    try:
        bus.write_byte(address, 0xFF)
        print ("Ok: Dispositivo 0x27 responde")
        time.sleep(1)
    
    except:
        print("Error")
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader =SimpleMFRC522()

try:
    print("Acerca el pin al lector")
    id, text = reader.read()
    print ("ID: %s\nText: Pin identicado %s" % (id, text))
finally:
    GPIO.cleanup
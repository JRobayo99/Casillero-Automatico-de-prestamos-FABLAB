from picamera2 import Picamera2
import time

picam=Picamera2()
picam.preview_configuration.main.size=(640,480)
picam.preview_configuration.main.format = "RGB888"
picam.configure ("preview")

picam.start()
print("Camara encendida. Vista previa activa....")
time.sleep(50)

picam.stop()
print("Prueba finalizada")
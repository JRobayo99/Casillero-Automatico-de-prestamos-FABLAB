import cv2
import numpy as np

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se puede abrir la cámara")
    exit()

ret, frame = cap.read()

if ret:

    cv2.imwrite('captura_prueba.jpg', frame)
    print("Imagen capturada y guardada como 'captura_prueba.jpg'")

else:
    print("Error al capturar la imagen")


cap.release()
cv2.destroyAllWindows()

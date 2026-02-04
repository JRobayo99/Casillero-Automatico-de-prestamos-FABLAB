import cv2
import pytesseract
import numpy as np

# SOLO EN WINDOWS (ajusta la ruta si es necesario)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocesamiento
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # OCR
    texto = pytesseract.image_to_string(thresh, lang='spa')

    # Mostrar texto en consola
    print("Texto detectado:")
    print(texto)

    # Mostrar imagen
    cv2.imshow("Camara", frame)
    cv2.imshow("Procesada", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

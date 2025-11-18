import cv2
import pytesseract
import os
import re

# --- CONFIGURACIONES --- #
cuadro = 100                 # Margen para recuadro
doc_detectado = False        # Estado de detección
carpeta = "capturas"
os.makedirs(carpeta, exist_ok=True)

# Si estás en Ubuntu NO necesitas modificar esto
# pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# --- INICIAR CÁMARA --- #
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# --------------------------- #
#  FUNCIÓN PARA PROCESAR OCR  #
# --------------------------- #
def detectar_documento(imagen):
    global doc_detectado

    # Convertir a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Quitar ruido conservando bordes
    gris = cv2.bilateralFilter(gris, 9, 75, 75)

    # Binarización adaptativa
    umbral = cv2.adaptiveThreshold(
        gris, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        41, 10
    )

    # OCR con modo lectura de bloques
    config = "--psm 6"
    texto = pytesseract.image_to_string(umbral, config=config)

    print("\n🔍 TEXTO DETECTADO:\n", texto)

    # Buscar palabras clave
    if re.search(r"COLOMBIA", texto, re.IGNORECASE) and \
       re.search(r"IDENTIFICACION", texto, re.IGNORECASE):

        print("\n🟢 DOCUMENTO IDENTIFICADO: CÉDULA COLOMBIANA\n")
        doc_detectado = True
    else:
        print("\n🔴 NO SE DETECTÓ CÉDULA\n")


# --------------------------- #
#     BUCLE PRINCIPAL         #
# --------------------------- #
while True:

    ret, frame = cap.read()
    if not ret:
        break

    # Dibujar zona de escaneo
    cv2.rectangle(frame, (cuadro, cuadro), (1280 - cuadro, 720 - cuadro), (0, 255, 0), 2)

    # Mensajes dinámicos
    if doc_detectado:
        cv2.putText(frame, "DOCUMENTO COLOMBIANO DETECTADO",
                    (370, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    else:
        cv2.putText(frame, "PRESIONE S PARA ESCANEAR",
                    (420, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("ID INTELIGENTE", frame)

    key = cv2.waitKey(5)

    # CAPTURA CON TECLA S/s
    if key in [83, 115]:

        # Recortar solo la zona del documento
        crop = frame[cuadro:720 - cuadro, cuadro:1280 - cuadro]

        ruta = os.path.join(carpeta, "captura_id.jpg")
        cv2.imwrite(ruta, crop)

        print("\n📸 Imagen guardada en:", ruta)

        detectar_documento(crop)

        if doc_detectado:
            break  # finaliza si se encontró

# LIBERAR RECURSOS
cap.release()
cv2.destroyAllWindows()
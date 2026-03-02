import cv2
import numpy as np
import zxingcpp # Asumiendo que usas esta
import pytesseract
import re

# Configuración de Tesseract (si no está en el PATH, pon la ruta)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_for_ocr(image):
    """Preprocesa la imagen para mejorar el OCR."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Aplicar un poco de desenfoque para reducir ruido
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    # Binarización: Otsu's method funciona bien para texto sobre fondo claro
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def decode_pdf417(image):
    """Intenta decodificar un código PDF417 en la imagen."""
    results = zxingcpp.read_barcodes(image)
    for result in results:
        # El formato PDF417 es el que nos interesa
        if result.format == zxingcpp.BarcodeFormat.PDF417:
            return result.text
    return None

def extract_new_id_text(image):
    """Intenta encontrar y extraer el texto OCR de la cédula nueva."""
    # --- Aquí iría la lógica para encontrar la región de las 3 líneas ---
    # Por simplicidad, asumimos que el ROI ya está centrado en esa zona.
    # En un caso real, buscarías contornos, líneas horizontales, etc.
    
    # Por ahora, tomamos la mitad inferior de la imagen de entrada como ROI
    h, w = image.shape[:2]
    roi = image[int(h*0.6):h, 0:w] # Ajusta este valor según tu ROI general

    if roi.size == 0:
        return None

    # Preprocesar el ROI
    processed_roi = preprocess_for_ocr(roi)

    # Configurar Tesseract
    custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<'
    
    text = pytesseract.image_to_string(processed_roi, config=custom_config)
    # Limpiar el texto (quitar espacios y saltos de línea extra)
    text = re.sub(r'\s+', '', text) 
    
    # Verificar si tiene la pinta de ser el texto de la cédula nueva (muchos '<' y longitud)
    if len(text) >= 80 and text.count('<') > 10:
        return text
    else:
        return None

def main():

    cap = cv2.VideoCapture(0) # Abre la cámara web
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    print("Resolución real:", cap.get(3), "x", cap.get(4))

    

    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Definir el ROI (por ejemplo, un rectángulo central)
        h, w = frame.shape[:2]
        roi_x1, roi_y1 = int(w*0.2), int(h*0.2)
        roi_x2, roi_y2 = int(w*0.8), int(h*0.8)
        
        # Dibujar el ROI en el frame
        cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
        cv2.putText(frame, "Coloque la cedula aqui", (roi_x1, roi_y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # Extraer la imagen del ROI
        roi_image = frame[roi_y1:roi_y2, roi_x1:roi_x2]

        # --- ESTRATEGIA DE IDENTIFICACION ---
        
        # 1. Intentar leer como cédula antigua (PDF417)
        pdf417_data = decode_pdf417(roi_image)
        
        if pdf417_data:
            # Mostrar resultado en el frame
            cv2.putText(frame, "CEDULA ANTIGUA DETECTADA", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            print(f"Datos PDF417: CEDULA ANTIGUA DETECTADA")
            # Aquí parseas los datos del PDF417
        else:
            # 2. Si no hay PDF417, intentar como cédula nueva (OCR)
            new_id_text = extract_new_id_text(roi_image)
            if new_id_text:
                cv2.putText(frame, "CEDULA NUEVA DETECTADA", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
                print(f"Texto OCR: CEDULA NUEVA DETECTADA")
                # Aquí parseas las 3 lineas del texto
            else:
                cv2.putText(frame, "No detectada", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        # Mostrar el frame
        cv2.imshow('Lector de Cedulas', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.namedWindow("Captura", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Captura", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)



    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
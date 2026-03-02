import cv2
import pytesseract
from pytesseract import Output

# Obtener dimensiones de la pantalla
screen_width = 1920  # Valor por defecto
screen_height = 1080  # Valor por defecto

# Intentar obtener dimensiones reales de la pantalla
try:
    import tkinter as tk
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
except:
    # Si tkinter no está disponible, usar dimensiones comunes
    print("No se pudo obtener dimensiones de pantalla, usando 1920x1080")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

<<<<<<< HEAD
# ============= DEFINICIÓN DEL ROI =============
# Coordenadas del área donde buscar el texto
# x1 = posición izquierda
# y1 = posición superior
# x2 = posición derecha
# y2 = posición inferior
x1, y1 = 500, 150    # Esquina superior izquierda
x2, y2 = 1700, 800   # Esquina inferior derecha

# crear ventana ajustable y colocarla en fullscreen
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    # ============= VISUALIZAR EL ROI =============
    # Dibujar rectángulo azul para mostrar el área de detección
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
    cv2.putText(frame, "ROI - Area de deteccion", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # ============= RECORTAR Y PROCESAR ROI =============
    # Extraer solo la región de interés
    roi = frame[y1:y2, x1:x2]
    
    # Aplicar OCR solo al ROI (ignora texto fuera de esta área)
    d = pytesseract.image_to_data(roi, lang='spa', output_type=Output.DICT)
    cant_cajas = len(d['text'])
    
    # ============= DIBUJAR RESULTADOS EN EL ROI =============
=======
# Crear ventana con tamaño ajustable
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
# Opción 1: Redimensionar la ventana al tamaño de la pantalla
cv2.resizeWindow('frame', screen_width, screen_height)
# Opción 2: Maximizar la ventana automáticamente (comentar la línea anterior y descomentar esta)
# cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    d = pytesseract.image_to_data(frame, lang='spa', output_type=Output.DICT)
    cant_cajas = len(d['text'])
    
    texto_detectado = []  # Lista para almacenar el texto detectado
    
>>>>>>> 6b471eb44943eaa488a88d7cd2bd62b1993e613c
    for i in range(cant_cajas):
        if int(d['conf'][i]) > 60:
            (text, x, y, w, h) = (d['text'][i], d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            if text and text.strip() != "":
<<<<<<< HEAD
                # Convertir coordenadas del ROI al frame original
                rect_x1 = x1 + x
                rect_y1 = y1 + y
                rect_x2 = x1 + x + w
                rect_y2 = y1 + y + h
                
                # Dibujar rectángulo verde alrededor del texto detectado
                cv2.rectangle(frame, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 255, 0), 2)
                # Escribir el texto detectado
                cv2.putText(frame, text, (rect_x1, rect_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Mostrar el frame con ROI y resultados
=======
                # Dibujar rectángulo y texto en el frame
                cuadro = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cuadro = cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Agregar texto detectado a la lista
                texto_detectado.append(text.strip())
    
    # Imprimir el texto detectado en la terminal
    if texto_detectado:
        print("Texto detectado:", " ".join(texto_detectado))
        
        # Buscar patrones típicos de cédula
        texto_completo = " ".join(texto_detectado)
        if "CEDULA" in texto_completo.upper() or any(char.isdigit() for char in texto_completo):
            print("\n--- POSIBLES DATOS DE CÉDULA ---")
            print(texto_completo)
            print("--------------------------------\n")
    
>>>>>>> 6b471eb44943eaa488a88d7cd2bd62b1993e613c
    cv2.imshow('frame', frame)
    
    # Presionar 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
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
    
    for i in range(cant_cajas):
        if int(d['conf'][i]) > 60:
            (text, x, y, w, h) = (d['text'][i], d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            if text and text.strip() != "":
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
    
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
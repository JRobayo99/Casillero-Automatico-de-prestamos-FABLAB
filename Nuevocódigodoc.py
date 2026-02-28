import cv2
import numpy as np

# Inicializar la cámara
cap = cv2.VideoCapture(0)

# --- VALORES HSV A AJUSTAR (USA EL CÓDIGO INTERACTIVO) ---
# Rangos para el AZUL de la nueva cédula (valores de ejemplo, ¡cámbialos!)
lower_azul = np.array([100, 100, 50])   # H_min, S_min, V_min
upper_azul = np.array([130, 255, 255]) # H_max, S_max, V_max

# Rangos para el AMARILLO de la cédula antigua (valores de ejemplo, ¡cámbialos!)
lower_amarillo = np.array([20, 100, 50])
upper_amarillo = np.array([35, 255, 255])
# --- FIN DE RANGOS ---

# Diccionario para almacenar colores y su representación en BGR
colores = {
    'azul': {'lower': lower_azul, 'upper': upper_azul, 'color_bgr': (255, 0, 0)},
    'amarillo': {'lower': lower_amarillo, 'upper': upper_amarillo, 'color_bgr': (0, 255, 255)}
}

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 1. Convertir a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 2. Detectar cada color
    for nombre, info in colores.items():
        # Crear la máscara base
        mask = cv2.inRange(hsv, info['lower'], info['upper'])
        
        # 3. Limpiar la máscara (Operaciones Morfológicas)
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  # Elimina ruido
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # Rellena huecos
        
        # 4. Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 5. Filtrar y dibujar por ÁREA
        for contour in contours:
            area = cv2.contourArea(contour)
            # Este valor (5000) es un ejemplo. AJÚSTALO según la distancia.
            if area > 5000:  
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), info['color_bgr'], 3)
                cv2.putText(frame, f'Cedula {nombre}', (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, info['color_bgr'], 2)
    
    cv2.imshow('Deteccion de Cedulas', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
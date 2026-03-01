import cv2
import numpy as np
import time

inicio = time.time()
TIEMPO_ESPERA = 10  # segundos


# ---------- CONFIGURACIÓN ----------
CAMARA_ID = 0
UMBRAL_COLOR = 0.4

ROI_WIDTH = 500
ROI_HEIGHT = 300

# Rangos HSV mejorados para mejor detección
# Amarillo (incluye tonos cálidos) - valores iniciales
amarillo_bajo = np.array([15, 40, 80])
amarillo_alto = np.array([35, 255, 255])

# Azul (tonos fríos)
azul_bajo = np.array([100, 50, 60])
azul_alto = np.array([130, 255, 255])

# Morado/Violeta (exclusivamente tonos púrpura)
morado_bajo = np.array([130, 30, 50])
morado_alto = np.array([160, 255, 255])

# Función auxiliar para crear trackbars de un color
def crear_trackbar_color(nombre):
    cv2.createTrackbar('Hmin', nombre, 0, 179, lambda v: None)
    cv2.createTrackbar('Hmax', nombre, 0, 179, lambda v: None)
    cv2.createTrackbar('Smin', nombre, 0, 255, lambda v: None)
    cv2.createTrackbar('Smax', nombre, 0, 255, lambda v: None)
    cv2.createTrackbar('Vmin', nombre, 0, 255, lambda v: None)
    cv2.createTrackbar('Vmax', nombre, 0, 255, lambda v: None)
    # inicializar con valores por defecto
    cv2.setTrackbarPos('Hmin', nombre, 0)
    cv2.setTrackbarPos('Hmax', nombre, 179)
    cv2.setTrackbarPos('Smin', nombre, 0)
    cv2.setTrackbarPos('Smax', nombre, 255)
    cv2.setTrackbarPos('Vmin', nombre, 0)
    cv2.setTrackbarPos('Vmax', nombre, 255)


kernel = np.ones((5, 5), np.uint8)

# ---------- CÁMARA ----------
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Crear ventanas UNA VEZ
cv2.namedWindow("Camara")
cv2.namedWindow("ROI")
cv2.namedWindow("Detectores de Color")
cv2.namedWindow("Mascara Amarillo")
cv2.namedWindow("Mascara Azul")
cv2.namedWindow("Mascara Morado")

# añadir trackbars de ajuste en las ventanas de máscaras
crear_trackbar_color("Mascara Amarillo")
crear_trackbar_color("Mascara Azul")
crear_trackbar_color("Mascara Morado")

# fijar los valores iniciales en los sliders según los rangos configurados arriba
def fijar_valores(nombre, bajo, alto):
    cv2.setTrackbarPos('Hmin', nombre, int(bajo[0]))
    cv2.setTrackbarPos('Smin', nombre, int(bajo[1]))
    cv2.setTrackbarPos('Vmin', nombre, int(bajo[2]))
    cv2.setTrackbarPos('Hmax', nombre, int(alto[0]))
    cv2.setTrackbarPos('Smax', nombre, int(alto[1]))
    cv2.setTrackbarPos('Vmax', nombre, int(alto[2]))

fijar_valores("Mascara Amarillo", amarillo_bajo, amarillo_alto)
fijar_valores("Mascara Azul", azul_bajo, azul_alto)
fijar_valores("Mascara Morado", morado_bajo, morado_alto)

print("📷 Coloca la cédula dentro del recuadro - presiona Q para salir")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (900, 550))

    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - inicio

    resultado_estable = None
    tiempo_inicio_estable = None
    TIEMPO_CONFIRMACION = 5 # segundos
    
    if tiempo_transcurrido < TIEMPO_ESPERA:
        # 🔹 SOLO MOSTRAR, NO DETECTAR
        segundos_restantes = int(TIEMPO_ESPERA - tiempo_transcurrido)
        cv2.putText(
            frame,
            f"Esperando... {segundos_restantes}s",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )

        cv2.imshow("Camara", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue   # ⬅️ SALTA detección

    h, w, _ = frame.shape

    # ---------- DEFINIR RECUADRO ----------
    x1 = (w - ROI_WIDTH) // 2
    y1 = (h - ROI_HEIGHT) // 2
    x2 = x1 + ROI_WIDTH
    y2 = y1 + ROI_HEIGHT

    # Dibujar recuadro
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Extraer ROI
    roi = frame[y1:y2, x1:x2]

    # ---------- DETECCIÓN DE COLOR ----------
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # si el usuario está ajustando los trackbars, leer valores
    def leer_rango(nombre):
        hmin = cv2.getTrackbarPos('Hmin', nombre)
        hmax = cv2.getTrackbarPos('Hmax', nombre)
        smin = cv2.getTrackbarPos('Smin', nombre)
        smax = cv2.getTrackbarPos('Smax', nombre)
        vmin = cv2.getTrackbarPos('Vmin', nombre)
        vmax = cv2.getTrackbarPos('Vmax', nombre)
        return np.array([hmin, smin, vmin]), np.array([hmax, smax, vmax])

    amarillo_bajo, amarillo_alto = leer_rango("Mascara Amarillo")
    azul_bajo, azul_alto = leer_rango("Mascara Azul")
    morado_bajo, morado_alto = leer_rango("Mascara Morado")

    # mostrar valores HSV en pantalla para ayuda de calibración
    cv2.putText(frame, f"Ama H[{amarillo_bajo[0]}-{amarillo_alto[0]}]", (20, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
    cv2.putText(frame, f"Azu H[{azul_bajo[0]}-{azul_alto[0]}]", (20, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
    cv2.putText(frame, f"Mor H[{morado_bajo[0]}-{morado_alto[0]}]", (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255), 1)

    mask_amarillo = cv2.inRange(hsv, amarillo_bajo, amarillo_alto)
    mask_azul = cv2.inRange(hsv, azul_bajo, azul_alto)
    mask_morado = cv2.inRange(hsv, morado_bajo, morado_alto)

    mask_amarillo = cv2.morphologyEx(mask_amarillo, cv2.MORPH_OPEN, kernel)
    mask_azul = cv2.morphologyEx(mask_azul, cv2.MORPH_OPEN, kernel)
    mask_morado = cv2.morphologyEx(mask_morado, cv2.MORPH_OPEN, kernel)

    total = roi.shape[0] * roi.shape[1]

    p_amarillo = cv2.countNonZero(mask_amarillo) / total * 100
    p_azul = cv2.countNonZero(mask_azul) / total * 100
    p_morado = cv2.countNonZero(mask_morado) / total * 100

    # ---------- CLASIFICACIÓN ----------
    # CÉDULA NUEVA: amarillo + morado/violeta fuerte
    if (p_amarillo > 8 and p_morado > 8):
        resultado_actual = "CEDULA ANTIGUA (Amarillo + Morado)"
    
    # CÉDULA ANTIGUA: azul + amarillo
    elif (p_azul > 10 and p_amarillo > 5):
        resultado_actual = "CEDULA NUEVA" \
        " (Azul + Amarillo)"
    
    else:
        resultado_actual = "NO RECONOCIDO"


    tiempo_actual = time.time()

    if "CEDULA" in resultado_actual:  # Válido si contiene CEDULA NUEVA o CEDULA ANTIGUA

        if resultado_actual == resultado_estable:
            # sigue siendo el mismo resultado
            if tiempo_inicio_estable is None:
                tiempo_inicio_estable = tiempo_actual

            tiempo_estable = tiempo_actual - tiempo_inicio_estable

            # mostrar progreso
            cv2.putText(
                frame,
                f"Confirmando: {resultado_actual} ({tiempo_estable:.1f}s)",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            if tiempo_estable >= TIEMPO_CONFIRMACION:
                print("\n===================================")
                print(f"RESULTADO FINAL: {resultado_actual}")
                print("===================================\n")

                cap.release()
                cv2.destroyAllWindows()
                
                break

        else:
            # resultado cambió → reiniciar conteo
            resultado_estable = resultado_actual
            tiempo_inicio_estable = tiempo_actual

    else:
        # no reconocido → resetear
        resultado_estable = None
        tiempo_inicio_estable = None


    # ---------- TEXTO ----------
    cv2.putText(frame, resultado_actual, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.putText(frame,
                f"Ama:{p_amarillo:.2f}%  Azu:{p_azul:.2f}%  Mor:{p_morado:.2f}%",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # ---------- MOSTRAR ----------
    cv2.imshow("Camara", frame)
    cv2.imshow("ROI", roi)
    cv2.imshow("Mascara Amarillo", mask_amarillo)
    cv2.imshow("Mascara Azul", mask_azul)
    cv2.imshow("Mascara Morado", mask_morado)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

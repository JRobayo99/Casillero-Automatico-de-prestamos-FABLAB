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

# Rangos HSV
amarillo_bajo = np.array([18, 20, 80])
amarillo_alto = np.array([45, 255, 255])

azul_bajo = np.array([90, 30, 50])
azul_alto = np.array([130, 255, 255])

morado_bajo = np.array([135, 25, 40])
morado_alto = np.array([165, 255, 255])

kernel = np.ones((5, 5), np.uint8)

# ---------- CÁMARA ----------
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Crear ventanas UNA VEZ
cv2.namedWindow("Camara")
cv2.namedWindow("ROI")

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
    if (p_amarillo > 5 and 15 <= p_azul <= 20):
        resultado_actual = "CEDULA NUEVA"

    elif (5 <= p_amarillo <= 10 and 5 <= p_azul <= 10):
        resultado_actual = "CEDULA ANTIGUA"
    else:
        resultado_actual = "NO RECONOCIDO"


    tiempo_actual = time.time()

    if resultado_actual in ["CEDULA NUEVA", "CEDULA ANTIGUA"]:

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

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

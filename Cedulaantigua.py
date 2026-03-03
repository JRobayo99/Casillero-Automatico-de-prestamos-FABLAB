import cv2
import zxingcpp
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import time
import re
from datetime import datetime

class cedula_amarilla:
    def __init__(self, parse_pdf417):
            self.parse_pdf417 = parse_pdf417
            

    def parse_pdf417(text):
        # Quitar caracteres no imprimibles
        clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)

        # Quitar palabras "NUL" que vienen del decodificador
        clean = clean.replace("NUL", " ")

        data = {}

        # ===============================
        # DETECCIÓN Y ELIMINACIÓN DE PREFIJO DE 8 DÍGITOS
        # ===============================
        # Buscar patrón: 8 dígitos + 10q
        # 
        #  dígitos + texto en mayúsculas
        patron_prefijo = r'(\d{8})(\d{10})([A-ZÑÁÉÍÓÚ]+)'
        match_prefijo = re.search(patron_prefijo, clean)
        
        if match_prefijo:
            # Si encontramos el patrón, extraemos solo los 10 dígitos (cédula) y el texto (apellido)
            cedula_encontrada = match_prefijo.group(2)
            texto_mayusculas = match_prefijo.group(3)
            
            # Reemplazar en el texto limpio: eliminamos los 8 dígitos del prefijo
            # pero mantenemos la cédula y el texto
            clean = clean.replace(match_prefijo.group(1), '', 1)
            
            # Guardar la cédula directamente
            data["Cédula"] = cedula_encontrada
            cedula = cedula_encontrada
        else:
            # Si no hay prefijo, buscar el patrón normal de 10 dígitos
            all_10_digits = re.findall(r'(?<!\d)\d{10}(?!\d)', clean)
            
            if len(all_10_digits) >= 2:
                cedula = all_10_digits[1]
                data["Cédula"] = cedula
            elif len(all_10_digits) == 1:
                cedula = all_10_digits[0]
                data["Cédula"] = cedula
            else:
                data["Cédula"] = None
                cedula = None

        
        

       
        # ===============================
        # 5. Apellidos y nombre
        # ===============================
        grupos = []
        if cedula:
            # Buscar después de la cédula
            pos = clean.find(cedula)
            if pos != -1:
                tail = clean[pos + len(cedula):]
                grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', tail)
                grupos = [g for g in grupos if g not in ["N", "NU", "NUL"]]

        # Si no encontramos grupos después de la cédula o no hay cédula,
        # buscar en todo el texto
        if not grupos:
            grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', clean)
            grupos = [g for g in grupos if g not in ["N", "NU", "NUL"]]

        # Asignar apellidos y nombre
        if len(grupos) >= 1:
            data["Primer apellido"] = grupos[0]
        if len(grupos) >= 2:
            data["Segundo apellido"] = grupos[1]
        if len(grupos) >= 3:
            data["Nombre"] = grupos[2]
            
        # Si tenemos exactamente 2 grupos, asumimos que el segundo es el nombre
        elif len(grupos) == 2:
            data["Nombre"] = grupos[1]
            data["Segundo apellido"] = ""

        return clean, data



    # ===============================
    # Configuración de cámara
    # ===============================
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    print("Resolución real:", cap.get(3), "x", cap.get(4))

    # Recuadro
    x1, y1 = 350, 50
    x2, y2 = 1650, 900




    # Ajustar la ventana de visualización al tamaño de la pantalla
    root = tk.Tk()
    root.withdraw()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.destroy()

    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Márgen para barras/elementos del sistema
    margin = 100
    max_w = max(100, screen_w - margin)
    max_h = max(100, screen_h - margin)

    scale = min(max_w / frame_w, max_h / frame_h, 1.0)
    display_w = max(100, int(frame_w * scale))
    display_h = max(100, int(frame_h * scale))

    cv2.namedWindow("Captura", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Captura", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Escaneo automático: intervalo y control de cooldown tras detección
    last_scan_time = 0.0
    scan_interval = 0.5  # segundos entre intentos de escaneo
    scan_cooldown_on_detect = 2.0  # segundos de espera tras detectar un código

    detected = False    
    # ===============================
    # Bucle principal
    # ===============================
    while True:
        ret, frame = cap.read()

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imshow("Captura", frame)

        key = cv2.waitKey(1) & 0xFF

        if not ret or frame is None:
            if key == 27:
                break
            continue

        # Escanear automáticamente cada `scan_interval` segundos
        now = time.time()
        if now - last_scan_time >= scan_interval and not detected:
            last_scan_time = now

            cropped = frame[y1:y2, x1:x2]
            if cropped is None or cropped.size == 0:
                pass
            else:
                try:
                    cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                    results = zxingcpp.read_barcodes(cropped_rgb)
                except Exception as e:
                    print("Error al leer códigos:", e)
                    results = []

                if len(results) == 0:
                    # No encontrado: nada que hacer
                    pass
                else:
                    print("\n===== CÓDIGOS DETECTADOS =====")
                    for r in results:
                        print(f"Formato: {r.format}")
                        clean, extracted = parse_pdf417(r.text)
                        print("\n--- Datos extraídos ---")
                        for k, val in extracted.items():
                            print(f"{k}: {val}")
                        print("\n")

                        if extracted.get("Cédula") and extracted.get("Primer apellido"):
                            detected = True
                            print("Cédula detectada con éxito. Cerrando escaner...")

                    # Aplicar cooldown mayor tras una detección para evitar repeticiones
                if not detected:
                    last_scan_time = time.time() + scan_cooldown_on_detect

        if detected:
            break

        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

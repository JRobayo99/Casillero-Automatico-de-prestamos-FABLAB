# camara_tk_pdf417.py
import cv2
import os
from datetime import datetime
import tkinter as tk
from tkinter import Label, Button, Text, END
from PIL import Image, ImageTk

# Intentar importar zxingcpp; si falla, el script avisará
try:
    import zxingcpp
    ZXING_AVAILABLE = True
except Exception as e:
    print("Aviso: zxingcpp no disponible:", e)
    ZXING_AVAILABLE = False

import re

# ===========================
# Tu función parse_pdf417 (idéntica a la que diste)
# ===========================
def parse_pdf417(text):
    clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)
    clean = re.sub(r'\s+', ' ', clean)
    data = {}
    all_10_digits = re.findall(r'(?<!\d)\d{10}(?!\d)', clean)
    if len(all_10_digits) >= 2:
        data["cedula"] = all_10_digits[1]
    else:
        data["cedula"] = None
    m = re.search(r'([MF])(\d{8})', clean)
    if m:
        data["sexo"] = m.group(1)
        data["fecha_nac"] = m.group(2)
    m = re.search(r'(A|B|O)[+-]', clean)
    if m:
        data["rh"] = m.group(0)
    # NOTA: tu regex de ejemplo para nombre/apellidos asume mayúsculas,
    # ajusta si tu PDF417 trae otros formatos.
    m = re.search(r'\d{10}\s+([A-ZÑÁÉÍÓÚ]+)\s+([A-ZÑÁÉÍÓÚ]+)\s+([A-ZÑÁÉÍÓÚ]+)', clean)
    if m:
        data["apellido1"] = m.group(2)
        data["apellido2"] = m.group(3)
        data["nombre"]   = m.group(4)
    return clean, data

# ----------------------
# Globals
# ----------------------
cap = None
running = False
os.makedirs("fotos", exist_ok=True)

# Define ROI (ajusta según tu resolución/cámara)
# Estos valores se usan para recortar la zona donde pones la cédula
ROI_X1, ROI_Y1 = 220, 90
ROI_X2, ROI_Y2 = 980, 580

# ----------------------
# Funciones cámara
# ----------------------
def encender_camara():
    global cap, running
    if running:
        return
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        txt_log.insert(END, "ERROR: no se pudo abrir la cámara\n")
        return
    running = True
    mostrar_frame()
    txt_log.insert(END, "Cámara encendida\n")

def apagar_camara():
    global cap, running
    running = False
    if cap is not None:
        cap.release()
    label_video.config(image='')
    txt_log.insert(END, "Cámara apagada\n")

def mostrar_frame():
    global cap, running
    if not running:
        return
    ret, frame = cap.read()
    if not ret:
        txt_log.insert(END, "Error leyendo frame\n")
        return
    # dibujar recuadro ROI
    cv2.rectangle(frame, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (0,255,0), 2)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)
    label_video.imgtk = imgtk
    label_video.configure(image=imgtk)
    label_video.after(10, mostrar_frame)

def capturar_foto():
    global cap, running
    if not running or cap is None:
        txt_log.insert(END, "La cámara no está encendida\n")
        return
    ret, frame = cap.read()
    if not ret:
        txt_log.insert(END, "Error al capturar imagen\n")
        return
    filename = datetime.now().strftime("fotos/captura_%Y%m%d_%H%M%S.jpg")
    cv2.imwrite(filename, frame)
    txt_log.insert(END, f"Foto guardada: {filename}\n")

# ----------------------
# Función para escanear PDF417 en el ROI
# ----------------------
def escanear_pdf417():
    global cap, running

    if not ZXING_AVAILABLE:
        txt_log.insert(END, "zxingcpp no está instalado. Instalar con: pip install zxing-cpp\n")
        return
    if not running or cap is None:
        txt_log.insert(END, "La cámara no está encendida\n")
        return

    ret, frame = cap.read()
    if not ret:
        txt_log.insert(END, "Error al leer frame\n")
        return

    # Recorte del ROI
    cropped = frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2]

    # --------------------------
    # 1) CONVERSIÓN A GRIS
    # --------------------------
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    # --------------------------
    # 2) AUMENTAR CONTRASTE (CLAHE)
    # --------------------------
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # --------------------------
    # 3) SUAVIZADO
    # --------------------------
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # Conjuntos de imágenes a probar
    variantes = [
        ("original", cropped),
        ("gray_enhanced", enhanced),
        ("scaled x2", cv2.resize(enhanced, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)),
        ("threshold", cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 21, 5
        ))
    ]

    angles = [
        ("0°", None),
        ("90°", cv2.ROTATE_90_CLOCKWISE),
        ("180°", cv2.ROTATE_180),
        ("270°", cv2.ROTATE_90_COUNTERCLOCKWISE)
    ]

    txt_log.insert(END, "Iniciando escaneo mejorado…\n")

    final_result = None
    final_variant = ""
    final_angle = ""

    # Recorremos todas las variantes + todas las rotaciones
    for var_label, var_img in variantes:

        # Convertir imagen a color para ZXing si hace falta
        if len(var_img.shape) == 2:  # imagen gris
            img_color = cv2.cvtColor(var_img, cv2.COLOR_GRAY2RGB)
        else:
            img_color = cv2.cvtColor(var_img, cv2.COLOR_BGR2RGB)

        for ang_label, ang in angles:
            txt_log.insert(END, f" → Probando {var_label} | Rotación {ang_label}\n")

            if ang is not None:
                rotated = cv2.rotate(img_color, ang)
            else:
                rotated = img_color

            results = zxingcpp.read_barcodes(rotated)

            if results:
                final_result = results[0]
                final_variant = var_label
                final_angle = ang_label
                break

        if final_result:
            break

    # ---------------------------------
    # RESULTADO FINAL
    # ---------------------------------
    if not final_result:
        txt_log.insert(END, "❌ No se pudo detectar PDF417 después de todas las mejoras.\n")
        return

    txt_log.insert(END, f"\n✔ PDF417 detectado usando variante '{final_variant}' con rotación {final_angle}\n")
    txt_log.insert(END, f"Formato: {final_result.format}\n")

    clean, extracted = parse_pdf417(final_result.text)

    txt_log.insert(END, "----- Texto limpio -----\n")
    txt_log.insert(END, clean + "\n")

    txt_log.insert(END, "----- Datos extraídos -----\n")
    for key, val in extracted.items():
        txt_log.insert(END, f"{key}: {val}\n")

    txt_log.insert(END, "\n")

# ----------------------
# GUI
# ----------------------
root = tk.Tk()
root.title("Cámara + Escaneo PDF417")
root.geometry("1000x700")

label_video = Label(root)
label_video.pack()

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=8)

Button(frame_buttons, text="Encender Cámara", command=encender_camara, width=18).grid(row=0, column=0, padx=4)
Button(frame_buttons, text="Apagar Cámara", command=apagar_camara, width=18).grid(row=0, column=1, padx=4)
Button(frame_buttons, text="Tomar Foto", command=capturar_foto, width=18).grid(row=0, column=2, padx=4)
Button(frame_buttons, text="Escanear PDF417", command=escanear_pdf417, width=18).grid(row=0, column=3, padx=4)

txt_log = Text(root, height=10)
txt_log.pack(fill="both", expand=False, padx=8, pady=8)

root.protocol("WM_DELETE_WINDOW", lambda: (apagar_camara(), root.destroy()))
root.mainloop()

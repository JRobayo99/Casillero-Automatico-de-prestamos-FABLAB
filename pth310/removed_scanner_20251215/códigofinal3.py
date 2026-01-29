# camara_tk_pdf417_mejorado.py

import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import Label, Button, Text, END
from PIL import Image, ImageTk
from datetime import datetime
import re
import zxingcpp
   

# ======================================================
# PARSEADOR PDF417 (Tu versión original mejorada)
# ======================================================
def parse_pdf417(text):
    clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)
    clean = clean.replace("NUL", " ")

    data = {}

    all_10_digits = re.findall(r'(?<!\d)\d{10}(?!\d)', clean)
    if len(all_10_digits) >= 2:
        cedula = all_10_digits[1]
        data["cedula"] = cedula
    else:
        data["cedula"] = None
        cedula = None

    m = re.search(r'([MF])(\d{8})', clean)
    if m:
        data["sexo"] = m.group(1)
        data["fecha_nac"] = m.group(2)

    m = re.search(r'(A|B|O)[+-]', clean)
    if m:
        data["rh"] = m.group(0)

    if cedula:
        pos = clean.find(cedula)
        tail = clean[pos + len(cedula):]

        grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', tail)
        grupos = [g for g in grupos if g not in ["N", "NU", "NUL"]]

        if len(grupos) >= 1:
            data["apellido1"] = grupos[0]
        if len(grupos) >= 2:
            data["apellido2"] = grupos[1]
        if len(grupos) >= 3:
            data["nombre"] = grupos[2]

    return clean, data



# ======================================================
# MEJORA AVANZADA DE LECTURA PDF417
# ======================================================
def mejorar_roi_pdf417(cropped):
    """
    Preprocesamiento completo:
    Upscale -> CLAHE -> Sharpen -> Morph-Close
    """

    # Aumentar resolución (critico)
    cropped_up = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Grises
    gray = cv2.cvtColor(cropped_up, cv2.COLOR_BGR2GRAY)

    # CLAHE (mejor contraste)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Sharpening
    kernel_sharp = np.array([[0, -1, 0],
                             [-1, 5, -1],
                             [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel_sharp)

    # Morph Close
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(sharpened, cv2.MORPH_CLOSE, kernel)

    return closed


def escanear_pdf417_mejorado(cropped):
    """
    Preprocesamiento + rotación automática
    """
    mejorado = mejorar_roi_pdf417(cropped)

    h, w = mejorado.shape
    mejorado_rgb = cv2.cvtColor(mejorado, cv2.COLOR_GRAY2RGB)

    # rotaciones a probar
    angles = [0, 10, -10, 20, -20, 30, -30]

    for ang in angles:
        if ang != 0:
            M = cv2.getRotationMatrix2D((w // 2, h // 2), ang, 1.0)
            rotado = cv2.warpAffine(mejorado_rgb, M, (w, h))
        else:
            rotado = mejorado_rgb

        results = zxingcpp.read_barcodes(rotado)

        if results:
            return results

    return []


# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================
cap = None
running = False
os.makedirs("fotos", exist_ok=True)

# ROI para la cédula
ROI_X1, ROI_Y1 = 220, 90
ROI_X2, ROI_Y2 = 980, 580


# ======================================================
# FUNCIONES DE CÁMARA
# ======================================================
def encender_camara():
    global cap, running
    if running:
        return

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        txt_log.insert(END, "ERROR: No se pudo abrir la cámara\n")
        return

    running = True
    txt_log.insert(END, "Cámara encendida\n")
    mostrar_frame()


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

    cv2.rectangle(frame, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (0, 255, 0), 2)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)

    label_video.imgtk = imgtk
    label_video.configure(image=imgtk)

    label_video.after(240, mostrar_frame)


def capturar_foto():
    global cap, running
    if not running:
        txt_log.insert(END, "La cámara no está encendida\n")
        return

    ret, frame = cap.read()
    if not ret:
        txt_log.insert(END, "Error capturando foto\n")
        return

    filename = datetime.now().strftime("fotos/captura_%Y%m%d_%H%M%S.jpg")
    cv2.imwrite(filename, frame)
    txt_log.insert(END, f"Foto guardada: {filename}\n")


# ======================================================
# ESCANEO PDF417 DESDE LA GUI
# ======================================================
def escanear_pdf417():
    global cap, running


    if not running:
        txt_log.insert(END, "La cámara no está encendida.\n")
        return

    ret, frame = cap.read()
    if not ret:
        txt_log.insert(END, "Error leyendo frame.\n")
        return

    cropped = frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2]

    results = escanear_pdf417_mejorado(cropped)

    if not results:
        txt_log.insert(END, "No se detectó ningún PDF417.\n")
        return

    for r in results:
        txt_log.insert(END, "\n===== CÓDIGO DETECTADO =====\n")
        txt_log.insert(END, f"Formato: {r.format}\n")

        clean, extracted = parse_pdf417(r.text)

        txt_log.insert(END, "Texto limpio:\n")
        txt_log.insert(END, clean + "\n")

        txt_log.insert(END, "Datos extraídos:\n")
        for k, v in extracted.items():
            txt_log.insert(END, f"  {k}: {v}\n")


# ======================================================
# INTERFAZ TKINTER
# ======================================================
root = tk.Tk()
root.title("Cámara + Escaneo PDF417 Mejorado")
root.geometry("800x800")

label_video = Label(root)
label_video.pack()

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=8)

Button(frame_buttons, text="Encender Cámara", width=18, command=encender_camara).grid(row=0, column=0, padx=4)
Button(frame_buttons, text="Apagar Cámara", width=18, command=apagar_camara).grid(row=0, column=1, padx=4)
Button(frame_buttons, text="Tomar Foto", width=18, command=capturar_foto).grid(row=0, column=2, padx=4)
Button(frame_buttons, text="Escanear PDF417", width=18, command=escanear_pdf417).grid(row=0, column=3, padx=4)

txt_log = Text(root, height=10)
txt_log.pack(fill="both", expand=False, padx=8, pady=8)

root.protocol("WM_DELETE_WINDOW", lambda: (apagar_camara(), root.destroy()))
root.mainloop()

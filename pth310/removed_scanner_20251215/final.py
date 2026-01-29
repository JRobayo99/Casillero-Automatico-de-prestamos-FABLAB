import cv2
import os
from datetime import datetime
import tkinter as tk
from tkinter import Label, Button, Text, END
import re
import zxingcpp
from PIL import Image, ImageTk

def parse_pdf417(text):

    clean = re.sub(r'[^A-Za-z0-9<]', '', text)
    clean = re.sub(r'<+', '<', clean)
    data = {}
    all_10_digits=re.find(r'(?<!\d)\d{10}(?!\d)', clean)
    if len(all_10_digits)>=2:
        
        data['Número de cédula'] = all_10_digits[1]

    else:
        data['Número de cédula'] = 'No encontrado'

    m = re.search(r'([MF])(\d{8})', clean)

    if m:
        data ['Genero'] = m.group(1)
        data ['Fecha de nacimiento'] = m.group(2)
    m = re.search(r'(A|B|O|AB)[+-]', clean)
    if m:
        data ['Tipo de sangre'] = m.group(0)

    m = re.search(r'\ d{10}\s+([A-ZÑÁÉÍÓÚ]+)\s+([A-ZÑÁÉÍÓÚ]+)\s+([A-ZÑÁÉÍÓÚ]+)', clean)

    if m:
        data ['Apellidos'] = m.group(2), m.group(3)
        data ['Nombres'] = m.group(4)

    return data,clean

cap = None
running = False

os.makedirs("fotos", exist_ok=True)

ROI_X1, ROI_Y1 = 220, 90
ROI_X2, ROI_Y2 = 980, 580

def encender_camara():
    global cap, running
    if running:
        return
    
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        txt_log.insert(END, "No se pudo abrir la cámara.\n")
        return
    
    running = True
    mostrar_frame()
    txt_log.insert(END, "Cámara encendida.\n")

def apagar_camara():
    global cap, running
    running = False
    if cap is not None:
        cap.release()
    label_video.config(image='')
    txt_log.insert(END, "Cámara apagada.\n")

def mostrar_frame():
    global cap, running, panel

    if not running:
        return
    
    ret, frame = cap.read()

    if not ret:
        txt_log.insert(END, "Error obteniendo frame\n")
        return
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)

    label_video.imgtk = imgtk
    label_video.config(image=imgtk)

    label_video.after(30, mostrar_frame)

def capturar_foto():
    global cap, running

    if not running or cap is None:
        print("La cámara no está encendida.")
        return
    
    ret, frame = cap.read()

    if not ret:
        print("Error capturando foto")
        return
    
    filename = datetime.now().strftime("fotos/foto_%Y%m%d_%H%M%S.jpg")
    cv2.imwrite(filename, frame)

    print(f"foto guardada como {filename}")

root = tk.Tk()
root.title("Control de Cámara")
root.geometry("800x600")

label_video = Label(root)
label_video.pack()

btn_encender = Button(root, text="Encender Cámara", command=encender_camara, width=20, height=2)
btn_encender.pack(pady= 5)

btn_apagar = Button(root, text="Apagar Cámara", command=apagar_camara, width=20, height=2)
btn_apagar.pack(pady= 5)

btn_foto = Button(root, text="Capturar Foto", command=capturar_foto, width=20, height=2)
btn_foto.pack(pady= 5)

root.mainloop()
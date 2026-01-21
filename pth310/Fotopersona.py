import cv2
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
import os

class CamaraApp:

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Aplicación de Cámara")
        self.ventana.resizable(False, False)

        self.video= cv2.VideoCapture(0)
        self.frame = None
        self.camara_activa =True
    
        self.lbl_video = tk.Label(self.ventana)
        self.lbl_video.pack()
    
        btn_frame = tk.Frame(ventana)
        btn_frame.pack(pady=10)
    
        
        tk.Button(btn_frame, text="Capturar Foto", command=self.tomar_foto).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Cerrar Cámara", command=self.cerrar_camara).grid(row=0, column=2, padx=5)

        self.actualizar_video()
    
    def abrir_camara(self):
        if not self.camara_activa:
            self.video = cv2.VideoCapture(2)
            self.camara_activa = True
            self.actualizar_video()

    def actualizar_video(self):
        if self.camara_activa:
            ret, frame = self.video.read()
            if ret:
                self.frame = frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.lbl_video.imgtk = imgtk
                self.lbl_video.configure(image=imgtk)
            self.lbl_video.after(10, self.actualizar_video)

    def tomar_foto(self):
        if self.frame is not None:
            os.makedirs("fotos", exist_ok=True)

            fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")

            nombre_foto = f"foto_{fecha_hora}.jpg"
            ruta_foto = os.path.join("fotos",nombre_foto)

            cv2.imwrite(ruta_foto, self.frame)
            print(f"Foto capturada y guardada como '{ruta_foto}'")

            self.cerrar_camara()

    def cerrar_camara(self):
        if self.camara_activa:
            self.camara_activa = False

        if self.video is not None:
            self.video.release()
        
        self.ventana.destroy()

root= tk.Tk()
app= CamaraApp(root)
root.mainloop()
root.geometry ("950x600")

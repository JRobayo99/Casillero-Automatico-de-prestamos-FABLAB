import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import time

class CameraApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Control de Cámara - Raspberry Pi")

        self.camera = None
        self.is_running = False

        self.label_video = Label(window)
        self.label_video.pack()

        Button(window, text="Encender Cámara", command=self.start_camera, width=20).pack(pady=5)
        Button(window, text="Apagar Cámara", command=self.stop_camera, width=20).pack(pady=5)
        Button(window, text="Tomar Foto", command=self.take_photo, width=20).pack(pady=5)

    def start_camera(self):
        if not self.is_running:
            self.camera = cv2.VideoCapture(0)  # /dev/video0
            self.is_running = True
            self.update_frame()

    def stop_camera(self):
        if self.is_running:
            self.is_running = False
            if self.camera:
                self.camera.release()
            self.label_video.config(image="")

    def update_frame(self):
        if self.is_running and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                self.label_video.imgtk = img
                self.label_video.configure(image=img)

            self.window.after(10, self.update_frame)

    def take_photo(self):
        if self.is_running and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                filename = f"foto_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Foto guardada: {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()


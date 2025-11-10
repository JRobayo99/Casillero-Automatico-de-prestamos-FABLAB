import RPi.GPIO as GPIO
import tkinter as tk
import time
from picamera2 import Picamera2
import os

GPIO.setmode(GPIO.BCM)
LED_PIN = 17 
GPIO.setup(LED_PIN,GPIO.OUT)

camera=Picamera2()
video_confing= camera.create_video_configuration()
camera.configure(video_config)

recording = False

def led_on():
    global recording
    GPIO.output(LED_PIN, GPIO.HIGH)
    status_label.config(text="LED encendido", fg="green")
    
    if not recording:
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        camera.start_recording (f"/home/pi/video_{timestamp}.h264")
        recording= True
    
def led_off():
    GPIO.output(LED_PIN, GPIO.LOW)
    status_label.config(text="LED apagado", fg="red")
    
    if recording:
        camera.stop_recording()
        recording= False
    
def on_closing():
    
    if recording:
        camera.stop_recording()
    
    GPIO.cleanup()
    root.destroy()
    
root = tk.Tk()
root.title("Interfaz de control por raspberry con LEDS")

btn_on= tk.Button(root, text="Encender LED", command= led_on, width=20, bg="lightgreen")
btn_on.pack(pady= 10)

btn_off= tk.Button(root, text="Apagar LED", command= led_off, width=20, bg="lightcoral")
btn_off.pack(pady= 10)

status_label = tk.Label(root, text="Led apagado", fg="red" , font=("Arial",14))
status_label.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()







import tkinter as tk
import emoji 
from tkinter import PhotoImage

def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

def show_dashboard():

    clear_content()
    label = tk.Label(content, text=("🔧🪛⚙️🛠️ Prestamo y devolución de herramientas"), font=("Arial", 30), bg="#eeeeee")
    label.pack(expand=True)

def show_profile():

    clear_content()
    label = tk.Label(content, text=("🪪✅ Ingreso de usuarios "), font=("Arial", 30), bg="#eeeeee")
    label.pack(expand=True)

    tk.Label(content, text="Nombre", bg="#eeeeee").pack(anchor="w", padx=20)
    tk.Entry(content).pack(padx=20, fill="x")

    tk.Label(content, text="Email", bg="#eeeeee").pack(anchor="w", padx=20, pady=(10, 0))
    tk.Entry(content).pack(padx=20, fill="x")

def show_picture():

    clear_content()
    label = tk.Label(content, text=("📅🛠️⚙️ Hisorial de prestamos"), font=("Arial", 30), bg="#eeeeee")
    label.pack(expand=True)

def show_info():

    clear_content()
    label = tk.Label(content, text="Información", font=("Arial", 30), bg="#eeeeee")
    label.pack(expand=True)

def show_settings():

    clear_content()
    label = tk.Label(content, text="Configuración", font=("Arial", 30), bg="#eeeeee")
    label.pack(expand=True)


def select_menu(option):
    label.config(text=f"Seleccionaste: {option}")

root = tk.Tk()
root.title("Casillero de prestamo automático")

root.geometry("2000x2000")

sidebar= tk.Frame(root, bg= "#222831", width=200)
sidebar.pack(side="left", fill="y")

menu_items =[
    ("🔧🪛⚙️🛠️","Prestamo y devolución de herramientas",show_dashboard),
    ("📅🛠️⚙️","Hisorial de prestamos",show_picture),
    ("🪪✅","Ingreso de usuarios ",show_profile),
    ("Info","tR", show_info),
    ("Settings","GT", show_settings)
]

for text, icon, command in menu_items:
    btn = tk.Button(sidebar, text= f"{icon} {text}", fg= "white", bg="#222831", relief="flat", anchor= "w", command= command)
    btn.pack(fill="x",padx=10, pady=5)


content= tk.Frame(root, bg="#eeeeee")
content.pack(side="right", fill="both", expand=True)

show_dashboard()

root.mainloop()
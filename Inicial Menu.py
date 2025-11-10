import tkinter as tk
from tkinter import PhotoImage


def select_menu(option):
    label.config(text=f"Seleccionaste: {option}")
    
root = tk.Tk()
root.title("Casillero de prestamo automático")

root.geometry("800x500")

sidebar= tk.Frame(root, bg= "#222831", width=200)
sidebar.pack(side="left", fill="y")



menu_items =[
    ("Dashboard","cdsa",),
    ("Porfile","Prt"),
    ("Picture","HGF"),
    ("Info","tR"),
    ("Settings","GT")
]

for text, icon in menu_items:
    btn = tk.Button(sidebar, text=f"{icon} {text}", bg = '#222831', fg="white",
                    relief="flat",anchor="w", command=lambda t=text: select_menu(t))
    
    btn.pack(fill="x", padx=10, pady=5)
    
content = tk.Frame(root, bg="#eeeeee")
content.pack(side= "right", fill="both", expand="True")

label = tk.Label(content, text="Casillero de prestamo automático")
label.pack(expand=True)

root.mainloop()
    
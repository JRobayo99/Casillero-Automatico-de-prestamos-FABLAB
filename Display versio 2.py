import tkinter as tk

def clear_content():
    
    for widget in content.winfo_children():
        widget.destroy()
        
        
def show_dashboard():
    
    clear_content()
    label = tk.Label(content, text="Dashboard", font=("Arial", 30), bg= "#eeeeee")
    label.pack(expand= True)
    
def show_profile():
    
    clear_content()
    label = tk.Label(content, text="Perfil de Usuario", font=("Arial", 30), bg= "#eeeeee")
    label.pack(expand= True)
    
    tk.Label(content, text="Nombre",bg= "#eeeeee").pack(anchor="w",padx=20)
    tk.Entry(content).pack(padx=20,fill="x")
    
    tk.Label(content, text="Email", bg= "#eeeeee").pack(anchor="w",padx=20, pady=(10,0))
    tk.Entry(content).pack(padx=20,fill="x")
    
def show_picture():
    
    clear_content()
    label = tk.Label(content, text="Sección Picture", font=("Arial", 30), bg= "#eeeeee")
    label.pack(expand= True)
    
def show_info():
    
    clear_content()
    label = tk.Label(content, text="Información", font=("Arial", 30), bg= "#eeeeee")
    label.pack(expand= True)
    
    
def show_settings():
    
    clear_content()
    label = tk.Label(content, text="Configuración", font=("Arial", 30), bg= "#eeeeee")
    label.pack(expand= True)
    
root = tk.Tk()
root.title("AUtoprestamo de herramientas")
root.geometry("800x500")

sidebar= tk.Frame(root, bg="#222831", width= 200)
sidebar.pack(side="left", fill="y")


prolife_label= tk.Label(sidebar, text="Usuario", fg="white", bg="#222831", font=("Arial",14,"bold"))
prolife_label.pack(pady=20)

menu_items = [
    ("Dashnoard","m", show_dashboard),
    ("Porfile","pp", show_profile),
    ("Picture", "cdr",show_picture),
    ("Info", "I", show_info),
    ("Settings","ERg", show_settings)
    ]

for text, icon, command in menu_items:
    btn = tk.Button(sidebar, text=f"{icon} {text}", bg="#222381", fg= "white", relief="flat", anchor="w", command=command)
    btn.pack(fill="x", padx=10, pady=5)
    
    
content= tk.Frame(root, bg="#eeeeee")
content.pack(side="right", fill="both", expand=True)

show_dashboard()

root.mainloop()
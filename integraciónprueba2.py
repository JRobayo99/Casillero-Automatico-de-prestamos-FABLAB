import threading
import tkinter as tk
import cv2
import zxingcpp
import re
from tkinter import messagebox


# Lista global donde se guardarán los préstamos seleccionados
herramientas_seleccionadas = []

def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

 #===============================
# Función de parsing PDF417 (igual a la tuya)
# ===============================
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


# ==========================================================
# FUNCIÓN PRINCIPAL DEL ESCÁNER (ejecutada en un hilo)
# ==========================================================
def iniciar_lector_pdf417(callback):
    def worker():
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        x1, y1 = 500, 150
        x2, y2 = 1700, 800

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow("Captura Cédula", frame)

            key = cv2.waitKey(1)

            if key == ord("s"):
                cropped = frame[y1:y2, x1:x2]
                cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                results = zxingcpp.read_barcodes(cropped_rgb)

                if len(results) > 0:
                    r = results[0]
                    clean, data = parse_pdf417(r.text)

                    # Cerrar cámara
                    cap.release()
                    cv2.destroyAllWindows()

                    # Enviar datos a Tkinter
                    callback(data)
                    return

                else:
                    messagebox.showwarning("Aviso", "No se detectó código PDF417.")

            if key == 27:  # ESC
                break

        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=worker).start()

def confirmar_prestamo():
    messagebox.showinfo("✅ Préstamo", "Préstamo confirmado.")
    show_dashboard()   

# -------------------- ESCANEO DE DOCUMENTO -------------------
def callback_datos_cedula(data):
    clear_content()

    tk.Label(content, text="Datos de la cédula", font=("Arial", 30), bg="#eeeeee").pack(pady=20)

    # Mostrar los datos leídos
    for k, v in data.items():
        tk.Label(content, text=f"{k}: {v}", font=("Arial", 18), bg="#eeeeee").pack()

    # Mostrar herramientas seleccionadas
    tk.Label(content, text="Herramientas prestadas:", font=("Arial", 22), bg="#eeeeee").pack(pady=20)

    for h in herramientas_seleccionadas:
        tk.Label(content, text=f"• {h}", font=("Arial", 18), bg="#eeeeee").pack()

    # Botón confirmar préstamo (AQUÍ SE AGREGA LO NUEVO)
    tk.Button(content,
              text="✔ Confirmar Préstamo",
              bg="#00adb5",
              font=("Arial", 20),
              command=confirmar_prestamo
    ).pack(pady=25)

    # Botón volver
    tk.Button(content, text="↩ Volver", command=show_dashboard).pack(pady=10)



def iniciar_scan():
    iniciar_lector_pdf417(callback_datos_cedula)

def btn_scandoc():
    clear_content()
    label = tk.Label(content, text="📄📷 Escaneo de documento para préstamo", font=("Arial", 30), bg="#eeeeee")
    label.pack(pady=20)

    # Mostrar herramientas seleccionadas
    resumen = "Herramientas a prestar:\n" + "\n".join(f"• {h}" for h in herramientas_seleccionadas)
    tk.Label(content, text=resumen, font=("Arial", 18), bg="#eeeeee").pack(pady=10)

    # Botón para iniciar escaneo
    tk.Button(content, text="📸 Escanear documento", font=("Arial", 20),
              bg="#00adb5", command=iniciar_scan).pack(pady=20)

    tk.Button(content, text=" ↩️ Volver", command=btn_presta).pack(pady=20)
# -------------------- PRÉSTAMO --------------------
def btn_presta():
    clear_content()
    label = tk.Label(content, text="🔧🪛⚙️🛠️ Préstamo de herramientas", font=("Arial", 30), bg="#eeeeee")
    label.pack(pady=20)

    # ---- Lista de herramientas disponibles ----
    herramientas = ["Multímetro", "Kit de estaño", "Pinzas", "Destornilladores", "Cautín", "Fuente de poder"]

    # Lista para guardar variables de checkboxes
    checks_vars = []

    # Crear checkboxes
    for herramienta in herramientas:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(content, text=herramienta, variable=var, font=("Arial", 18), bg="#eeeeee")
        chk.pack(anchor="w", padx=20)
        checks_vars.append((herramienta, var))

    # Función para guardar la selección antes de ir al escaneo
    def guardar_seleccion():
        herramientas_seleccionadas.clear()
        for herramienta, var in checks_vars:
            if var.get():
                herramientas_seleccionadas.append(herramienta)

        if not herramientas_seleccionadas:
            herramientas_seleccionadas.append("Ninguna herramienta seleccionada")

        btn_scandoc()   # Ir a escanear documento

    # Botón realizar préstamo
    btn_scanner_doc = tk.Button(content, text="Realizar Préstamo", font=("Arial", 20),
                                bg="#00adb5", command=guardar_seleccion)
    btn_scanner_doc.pack(pady=20, ipadx=10, ipady=10)

    tk.Button(content, text=" ↩️​ Volver", command=show_dashboard).pack(pady=20)

# -------------------- DEVOLUCIÓN --------------------
def btn_devolver():
    clear_content()
    label = tk.Label(content, text="🔧🪛⚙️🛠️ Devolución de herramientas", font=("Arial", 30), bg="#eeeeee")
    label.pack(pady=20)
    tk.Button(content, text=" ↩️​ Volver", command=show_dashboard).pack(pady=20)

# -------------------- DASHBOARD --------------------
def show_dashboard():
    clear_content()
    label = tk.Label(content, text="🔧🪛⚙️🛠️ Préstamo y devolución de herramientas", font=("Arial", 30), bg="#eeeeee")
    label.pack(pady=20)

    btn_prestamo = tk.Button(content, text="Realizar Préstamo", font=("Arial", 20), 
                             bg="#00adb5", command=btn_presta)
    btn_prestamo.pack(pady=20, ipadx=10, ipady=10)

    btn_devolucion = tk.Button(content, text="Devolver herramienta", font=("Arial", 20), 
                               bg="#00adb5", command=btn_devolver)
    btn_devolucion.pack(pady=20, ipadx=10, ipady=10)


        

def show_profile():

    clear_content()
    label = tk.Label(content, text=("🪪✅ Ingreso de usuarios "), font=("Arial", 30), bg="#eeeeee")
    label.pack(expand=True)

    tk.Label(content, text="Usuario", bg="#eeeeee").pack(anchor="w", padx=20)
    tk.Entry(content).pack(padx=20, fill="x")

    tk.Label(content, text="Contraseña", bg="#eeeeee").pack(anchor="w", padx=20, pady=(10, 0))
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
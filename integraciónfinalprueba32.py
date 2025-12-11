import threading
import tkinter as tk
import cv2
import zxingcpp
import re
import json
import os
from tkinter import messagebox

DB_FILE = "prestamos_db.json"
datos_cedula_global = {}
herramientas_seleccionadas = []
prestamos_activos = {}
ultimo_escaneo = {}


def cargar_prestamos():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)


def guardar_prestamos(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def clear_content():
    for widget in content.winfo_children():
        widget.destroy()


# ===============================
# Función de parsing PDF417
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


stop_scanner = False
tomar_foto = False   # variable global para facilitar manejo
scanner_thread = None  # guarda el hilo del scanner actual (si existe)


def cerrar_scanner():
    global stop_scanner, tomar_foto
    stop_scanner = True
    tomar_foto = False
    global scanner_thread
    # intentar esperar a que el hilo termine para liberar la cámara
    try:
        if scanner_thread is not None and scanner_thread.is_alive():
            scanner_thread.join(timeout=1.0)
    except Exception:
        pass
    scanner_thread = None
    try:
        cv2.destroyAllWindows()
    except:
        pass


# ==========================================================
# ESCÁNER PDF417
# ==========================================================
def iniciar_lector_pdf417(callback):

    cerrar_scanner()  # asegurar que no haya cámaras abiertas

    global stop_scanner, tomar_foto
    stop_scanner = False
    tomar_foto = False

    def worker():
        global stop_scanner, tomar_foto, scanner_thread
        try:
            cap = cv2.VideoCapture(0)
            # Validar que la cámara se abrió correctamente
            if not cap.isOpened():
                root.after(0, lambda: messagebox.showerror("Error", "No se pudo acceder a la cámara. Revisa que ninguna otra aplicación la esté usando o que el dispositivo esté conectado."))
                return

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

            x1, y1 = 500, 150
            x2, y2 = 1700, 800

            cv2.namedWindow("Captura Cédula", cv2.WINDOW_NORMAL)

            while not stop_scanner:
                ret, frame = cap.read()
                if not ret:
                    continue

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.imshow("Captura Cédula", frame)
                cv2.waitKey(1)

                if tomar_foto:
                    tomar_foto = False

                    cropped = frame[y1:y2, x1:x2]
                    cropped = cv2.resize(cropped, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
                    cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                    results = zxingcpp.read_barcodes(cropped_rgb)

                    if len(results) > 0:
                        cerrar_scanner()
                        r = results[0]
                        clean, data = parse_pdf417(r.text)
                        root.after(0, lambda: callback(data))
                        break
                    else:
                        root.after(0, lambda: messagebox.showwarning("Aviso", "No se detectó código PDF417."))
        finally:
            try:
                cap.release()
            except Exception:
                pass
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
            # limpiar referencia al hilo cuando termina
            try:
                scanner_thread = None
            except Exception:
                pass


    # ---------- BOTÓN TOMAR FOTO ----------
    def presionar_boton():
        global tomar_foto
        tomar_foto = True

    tk.Button(
        content,
        text="📸 Tomar Foto",
        font=("Arial", 20),
        bg="#00adb5",
        command=presionar_boton
    ).pack(pady=20)

    # ---------- BOTÓN VOLVER ----------
    tk.Button(
        content,
        text="↩ Volver",
        font=("Arial", 18),
        command=lambda: [cerrar_scanner(), show_dashboard()]
    ).pack(pady=10)

    # ---------- INICIO DEL HILO ----------
    global scanner_thread
    # si ya existe un hilo activo, no iniciar otro
    if scanner_thread is not None and scanner_thread.is_alive():
        root.after(0, lambda: messagebox.showinfo("Scanner", "El scanner ya está abierto."))
        return
    scanner_thread = threading.Thread(target=worker, daemon=True)
    scanner_thread.start()



    
# ==========================================================
# DEVOLUCIÓN
# ==========================================================
def callback_devolucion(data):

    cerrar_scanner()
    ced = data.get("cedula")

    if ced not in prestamos_activos:
        messagebox.showerror("Sin préstamos", "Esta cédula no tiene préstamos activos.")
        show_dashboard()
        return

    registro = prestamos_activos[ced]

    clear_content()
    tk.Label(content, text="Devolución de herramientas", font=("Arial", 30), bg="#eeeeee").pack(pady=20)

    usuario = f"{registro['apellido1']} {registro['apellido2']} {registro['nombre']}"
    tk.Label(content, text=f"Usuario: {usuario}", font=("Arial", 22), bg="#eeeeee").pack(pady=10)

    tk.Label(content, text="Seleccione las herramientas a devolver:",
             font=("Arial", 20), bg="#eeeeee").pack(pady=10)

    check_vars = []
    for h in registro["herramientas"]:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(content, text=h, variable=var, font=("Arial", 18), bg="#eeeeee")
        chk.pack(anchor="w", padx=20)
        check_vars.append((h, var))

    def devolver_seleccion():
        devolviendo = [h for h, var in check_vars if var.get()]

        if not devolviendo:
            messagebox.showwarning("Nada seleccionado", "Seleccione al menos una herramienta.")
            return

        for h in devolviendo:
            registro["herramientas"].remove(h)

        if not registro["herramientas"]:
            del prestamos_activos[ced]

        messagebox.showinfo("✔ Devolución", "Herramientas devueltas correctamente.")
        show_dashboard()

    tk.Button(content, text="✔ Devolver seleccionadas", bg="#00adb5",
              font=("Arial", 20), command=devolver_seleccion).pack(pady=20)

    def devolver_todo():
        
        del prestamos_activos[ced]
        messagebox.showinfo("✔ Devolución Completa", "Todas las herramientas fueron devueltas.")
        show_dashboard()

    tk.Button(content, text="✔ Devolver todas", bg="#00adb5",
              font=("Arial", 20), command=devolver_todo).pack(pady=10)

    tk.Button(content, text="↩ Volver", command=show_dashboard).pack(pady=20)

    global stop_scanner
    stop_scanner= True
    cv2.destroyAllWindows()

    

# ==========================================================
# CONFIRMAR PRÉSTAMO
# ==========================================================
def confirmar_prestamo():
    global ultimo_escaneo

    ced = ultimo_escaneo.get("cedula", None)
    if not ced:
        messagebox.showerror("Error", "No hay cédula detectada.")
        return

    prestamos_activos[ced] = {
        "nombre": ultimo_escaneo.get("nombre", ""),
        "apellido1": ultimo_escaneo.get("apellido1", ""),
        "apellido2": ultimo_escaneo.get("apellido2", ""),
        "herramientas": herramientas_seleccionadas.copy()
    }

    messagebox.showinfo("✅ Préstamo", "Préstamo confirmado.")
    show_dashboard()


def confirmar_devolucion(cedula):
    db = cargar_prestamos()
    db[cedula]["estado"] = "devuelto"
    guardar_prestamos(db)

    messagebox.showinfo("✔ Devolución", "Herramientas devueltas correctamente.")
    show_dashboard()

def iniciar_scan_prestamo():
    iniciar_lector_pdf417(confirmar_prestamo)


def iniciar_scan_devolucion():
    iniciar_lector_pdf417(callback_devolucion)


# -------------------- ESCANEO DE DOCUMENTO -------------------
def callback_datos_cedula(data):
    cerrar_scanner()

    global datos_cedula_global
    global ultimo_escaneo

    datos_cedula_global = data
    ultimo_escaneo = data

    clear_content()

    tk.Label(content, text="Datos de la cédula", font=("Arial", 30), bg="#eeeeee").pack(pady=20)

    for k, v in data.items():
        tk.Label(content, text=f"{k}: {v}", font=("Arial", 18), bg="#eeeeee").pack()

    tk.Label(content, text="Herramientas prestadas:", font=("Arial", 22), bg="#eeeeee").pack(pady=20)

    for h in herramientas_seleccionadas:
        tk.Label(content, text=f"• {h}", font=("Arial", 18), bg="#eeeeee").pack()

    tk.Button(
        content,
        text="✔ Confirmar Préstamo",
        bg="#00adb5",
        font=("Arial", 20),
        command=confirmar_prestamo
    ).pack(pady=25)

    tk.Button(content, text="↩ Volver", command=show_dashboard).pack(pady=10)


def iniciar_scan():
    iniciar_lector_pdf417(callback_datos_cedula)


def btn_scandoc():
    clear_content()
    cerrar_scanner()

    tk.Label(content, text="📄📷 Escaneo de documento para préstamo",
             font=("Arial", 30), bg="#eeeeee").pack(pady=20)

    resumen = "Herramientas a prestar:\n" + "\n".join(f"• {h}" for h in herramientas_seleccionadas)
    tk.Label(content, text=resumen, font=("Arial", 18), bg="#eeeeee").pack(pady=10)

    frame_botones = tk.Frame(content, bg="#eeeeee")
    frame_botones.pack(pady=40)

    # === BOTÓN 1 — ESCANEAR DOCUMENTO (equivalente a encender cámara) ===
    tk.Button(frame_botones,
              text="📄 Escanear Documento",
              font=("Arial", 20),
              bg="#00adb5",
              width=20,
              command=iniciar_scan_prestamo).grid(row=0, column=0, padx=20, pady=10)

    # === BOTÓN 2 — DEVOLVER (equivalente a apagar cámara) ===
    tk.Button(frame_botones,
              text="↩ Devolver",
              font=("Arial", 20),
              bg="#f05454",
              width=20,
              command=btn_devolver).grid(row=1, column=0, padx=20, pady=10)

    # === BOTÓN 3 — TOMAR FOTO (mantiene su función actual) ===
    tk.Button(frame_botones,
              text="📸 Tomar Foto",
              font=("Arial", 20),
              bg="#393e46",
              fg="white",
              width=20,
              command=lambda: iniciar_lector_pdf417(callback_datos_cedula)
             ).grid(row=2, column=0, padx=20, pady=10)

    tk.Button(content,
              text="↩ Volver",
              font=("Arial", 18),
              command=lambda: [cerrar_scanner(), btn_presta()]).pack(pady=20)


# -------------------- PRÉSTAMO --------------------
def btn_presta():
    clear_content()
    tk.Label(content, text="🔧🪛⚙️🛠️ Préstamo de herramientas",
             font=("Arial", 30), bg="#eeeeee").pack(pady=20)

    herramientas = ["Multímetro", "Kit de estaño", "Pinzas",
                    "Destornilladores", "Cautín", "Fuente de poder"]

    checks_vars = []

    for herramienta in herramientas:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(content, text=herramienta, variable=var,
                             font=("Arial", 18), bg="#eeeeee")
        chk.pack(anchor="w", padx=20)
        checks_vars.append((herramienta, var))

    def guardar_seleccion():
        herramientas_seleccionadas.clear()
        for herramienta, var in checks_vars:
            if var.get():
                herramientas_seleccionadas.append(herramienta)

        if not herramientas_seleccionadas:
            herramientas_seleccionadas.append("Ninguna herramienta seleccionada")

        btn_scandoc()

    tk.Button(content, text="Realizar Préstamo", font=("Arial", 20),
              bg="#00adb5", command=guardar_seleccion).pack(pady=20, ipadx=10, ipady=10)

    tk.Button(content, text=" ↩️​ Volver", command=show_dashboard).pack(pady=20)


# -------------------- DEVOLUCIÓN --------------------
def btn_devolver():
    clear_content()
    cerrar_scanner()

    tk.Label(content, text="🔄 Devolución de herramientas",
             font=("Arial", 30), bg="#eeeeee").pack(pady=20)

    tk.Label(content, text="Seleccione una opción",
             font=("Arial", 20), bg="#eeeeee").pack(pady=10)

    frame_botones = tk.Frame(content, bg="#eeeeee")
    frame_botones.pack(pady=40)

    # === BOTÓN 1 — ESCANEAR DOCUMENTO (equivale al encender cámara) ===
    tk.Button(frame_botones,
              text="📄 Escanear Documento",
              font=("Arial", 20),
              bg="#00adb5",
              width=20,
              command=iniciar_scan_devolucion).grid(row=0, column=0, padx=20, pady=10)

    # === BOTÓN 2 — DEVOLVER (equivale al apagar cámara) ===
    tk.Button(frame_botones,
              text="↩ Devolver",
              font=("Arial", 20),
              bg="#f05454",
              width=20,
              command=lambda: [cerrar_scanner(), show_dashboard()]).grid(row=1, column=0, padx=20, pady=10)

    # === BOTÓN 3 — TOMAR FOTO (idéntico al préstamo) ===
    tk.Button(frame_botones,
              text="📸 Tomar Foto",
              font=("Arial", 20),
              bg="#393e46",
              fg="white",
              width=20,
              command=lambda: iniciar_lector_pdf417(callback_devolucion)
             ).grid(row=2, column=0, padx=20, pady=10)

    tk.Button(content,
              text="↩ Volver",
              font=("Arial", 18),
              command=lambda: [cerrar_scanner(), show_dashboard()]).pack(pady=20)


# -------------------- DASHBOARD --------------------
def show_dashboard():
    clear_content()
    tk.Label(content, text="🔧🪛⚙️🛠️ Préstamo y devolución de herramientas",
             font=("Arial", 30), bg="#eeeeee").pack(pady=20)

    tk.Button(content, text="Realizar Préstamo", font=("Arial", 20),
              bg="#00adb5", command=btn_presta
              ).pack(pady=20, ipadx=10, ipady=10)

    tk.Button(content, text="Devolver herramienta", font=("Arial", 20),
              bg="#00adb5", command=btn_devolver
              ).pack(pady=20, ipadx=10, ipady=10)


# -------------------- MENÚS --------------------
def show_profile():
    clear_content()
    tk.Label(content, text="🪪✅ Ingreso de usuarios ",
             font=("Arial", 30), bg="#eeeeee").pack(expand=True)

    tk.Label(content, text="Usuario", bg="#eeeeee").pack(anchor="w", padx=20)
    tk.Entry(content).pack(padx=20, fill="x")

    tk.Label(content, text="Contraseña", bg="#eeeeee").pack(anchor="w", padx=20)
    tk.Entry(content).pack(padx=20, fill="x")


def show_picture():
    clear_content()
    tk.Label(content, text="📅🛠️⚙️ Historial de prestamos",
             font=("Arial", 30), bg="#eeeeee").pack(expand=True)


def show_info():
    clear_content()
    tk.Label(content, text="Información",
             font=("Arial", 30), bg="#eeeeee").pack(expand=True)


def show_settings():
    clear_content()
    tk.Label(content, text="Configuración",
             font=("Arial", 30), bg="#eeeeee").pack(expand=True)


def select_menu(option):
    label.config(text=f"Seleccionaste: {option}")


# -------------------- INTERFAZ PRINCIPAL --------------------
root = tk.Tk()
root.title("Casillero de prestamo automático")
root.geometry("2000x2000")

sidebar = tk.Frame(root, bg="#222831", width=200)
sidebar.pack(side="left", fill="y")

menu_items = [
    ("🔧🪛⚙️🛠️", "Prestamo y devolución de herramientas", show_dashboard),
    ("📅🛠️⚙️", "Historial de prestamos", show_picture),
    ("🪪✅", "Ingreso de usuarios ", show_profile),
    ("Info", "tR", show_info),
    ("Settings", "GT", show_settings)
]

for text, icon, command in menu_items:
    btn = tk.Button(
        sidebar,
        text=f"{icon} {text}",
        fg="white",
        bg="#222831",
        relief="flat",
        anchor="w",
        command=command
    )
    btn.pack(fill="x", padx=10, pady=5)

content = tk.Frame(root, bg="#eeeeee")
content.pack(side="right", fill="both", expand=True)

show_dashboard()

root.mainloop()

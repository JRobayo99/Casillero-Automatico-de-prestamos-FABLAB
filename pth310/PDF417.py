import cv2
import zxingcpp
import re

# ===============================
# Función para limpiar y extraer datos de la cédula
# ===============================
def parse_pdf417(text):
    # Quitar caracteres no imprimibles
    clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)

    # Quitar palabras "NUL" que vienen del decodificador
    clean = clean.replace("NUL", " ")

    data = {}

    # ===============================
    # 1. Encontrar las cadenas numéricas de 10 dígitos
    # ===============================
    all_10_digits = re.findall(r'(?<!\d)\d{10}(?!\d)', clean)

    if len(all_10_digits) >= 2:
        cedula = all_10_digits[1]
        data["Cédula"] = cedula
    else:
        data["Cédula"] = None
        cedula = None

   
    if cedula:
        pos = clean.find(cedula)
        tail = clean[pos + len(cedula):]

        # Grupos reales de letras (mínimo 2 letras)|
        grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', tail)

        # Evitar basura
        grupos = [g for g in grupos if g not in ["N", "NU", "NUL"]]

        if len(grupos) >= 1:
            data["Primer apellido"] = grupos[0]
        if len(grupos) >= 2:
            data["Segundo apellido"] = grupos[1]
        if len(grupos) >= 3:
            data["Nombres"] = grupos[2]
        
    
           

    return clean, data



# ===============================
# Configuración de cámara
# ===============================

# --- Callable scanner function ---
def scan_pdf417():
    import tkinter as tk
    from PIL import Image, ImageTk
    cap = cv2.VideoCapture(2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    x1, y1 = 500, 150
    x2, y2 = 1700, 800
    result_data = None
    running = True

    def close_scanner():
        nonlocal running
        running = False

    def scan_action():
        nonlocal result_data, running
        ret, frame = cap.read()
        if not ret or  frame is None :
            return
        
        h, w = frame.shape[:2]
        x1c = max(0, x1)
        y1c = max(0, y1)
        x2c = min(w, x2)
        y2c = min(h, y2)

        if x2c <= x1c or y2c <= y1c:
            return
        cropped = frame[y1c:y2c, x1c:x2c]

        if cropped.size == 0:
            return
        cropped = frame[y1:y2, x1:x2]
        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        results = zxingcpp.read_barcodes(cropped_rgb)
        if len(results) > 0:
            r = results[0]
            clean, extracted = parse_pdf417(r.text)
            result_data = extracted
            close_scanner()

    # Tkinter window for camera

    win = tk.Toplevel()
    win.title("Escáner de documento")
    win.geometry("950x530")  # Ventana más grande
    win.resizable(False, False)

    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)

    lmain = tk.Label(win)
    lmain.grid(row=0, column=0, sticky="nsew", pady=10)

    btn_frame = tk.Frame(win)
    btn_frame.grid(row=1, column=0, pady=20)
    btn_scan = tk.Button(
        btn_frame, text="Escanear documento", command=scan_action,
        font=("Helvetica", 16, "bold"), bg="#4CAF50", fg="white", width=20, height=2
    )
    btn_scan.pack(side="left", padx=20)
    btn_close = tk.Button(
        btn_frame, text="Cerrar escáner", command=close_scanner,
        font=("Helvetica", 16, "bold"), bg="#F44336", fg="white", width=20, height=2
    )
    btn_close.pack(side="left", padx=20)

    def show_frame():
        if not running:
            win.destroy()
            cap.release()
            cv2.destroyAllWindows()
            return
        ret, frame = cap.read()
        if ret:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            display_frame = cv2.resize(frame, (950, 500))
            rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
        win.after(20, show_frame)

    show_frame()
    win.grab_set()
    win.wait_window()
    return result_data

if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    data = scan_pdf417()
    print("Resultado escaneo:", data)
    root.destroy()

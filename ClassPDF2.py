import cv2
import zxingcpp
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import re
from datetime import datetime

# ===============================
# Función para limpiar y extraer datos de la cédula
# ===============================
<<<<<<< HEAD
class cedula_amarilla:

    def __init__(self, parse_pdf417, EscanerPDF417):
            self.parse_pdf417 = parse_pdf417
            self.EscanerPDF417 = EscanerPDF417
=======
class cedula_amarilla_datos:

    def __init__(self, parse_pdf417):
            
            self.parse_pdf417 = parse_pdf417
            
>>>>>>> pcdavid

    def parse_pdf417(self, text):
            # Quitar caracteres no imprimibles
        clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)

        # Quitar palabras "NUL" que vienen del decodificador
        clean = clean.replace("NUL", " ")

        data = {}

        # ===============================
        # 1. Intento principal: buscar cadenas numéricas de 10 dígitos
        # ===============================
        all_10_digits = re.findall(r'(?<!\d)\d{10}(?!\d)', clean)

        if len(all_10_digits) >= 2:
            cedula = all_10_digits[1]
            data["cedula"] = cedula
        else:
            data["cedula"] = None
            cedula = None

<<<<<<< HEAD
        # ===============================
        # 2. Sexo + fecha
        # ===============================
        

            
=======
>>>>>>> pcdavid

        # ===============================
        # 3. RH
        # ===============================
        m = re.search(r'(A|B|O)[+-]', clean)
        if m:
            data["rh"] = m.group(0)

        # ===============================
        # 4. Apellidos y nombre SIN “NUL”
        #    - Si no se encontró la cédula en el paso anterior, se
        #      intenta localizar el primer apellido en todo el texto
        #      y, según la regla solicitada, extraer 10 dígitos empezando
        #      desde la primera letra visible del apellido cuando el
        #      total de cifras en el texto supera 11.
        # ===============================
        # Si hay cédula, buscar apellidos en la cola después de la cédula
        grupos = []
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
        else:
            # Buscar posibles apellidos en todo el texto
            grupos_any = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', clean)
            grupos_any = [g for g in grupos_any if g not in ["N", "NU", "NUL"]]
            if len(grupos_any) >= 1:
                data["apellido1"] = grupos_any[0]
            if len(grupos_any) >= 2:
                data["apellido2"] = grupos_any[1]
            if len(grupos_any) >= 3:
                data["nombre"] = grupos_any[2]

            # Regla solicitada: si el total de cifras en el texto es > 11,
            # extraer 10 dígitos empezando desde la posición de la primera
            # letra del `apellido1`, acumulando dígitos hacia adelante.
            if data.get("apellido1"):
                total_digits = len(re.findall(r'\d', clean))
                if total_digits > 11:
                    pos_ap = clean.find(data["apellido1"])
                    if pos_ap != -1:
                        digits_collected = []
                        # Empezar desde el carácter anterior a la primera letra
                        i = pos_ap - 1
                        # Recorrer hacia atrás y acumular dígitos hasta 10
                        while i >= 0 and len(digits_collected) < 10:
                            if clean[i].isdigit():
                                digits_collected.insert(0, clean[i])
                            i -= 1

                        if len(digits_collected) == 10:
                            cedula = ''.join(digits_collected)
                            data["cedula"] = cedula

        return clean, data


<<<<<<< HEAD
    class EscanerPDF417:
=======
class EscanerPDF417:
        
>>>>>>> pcdavid
        """Interfaz de Tkinter para escanear códigos PDF417"""

        def __init__(self, root):
            self.root = root
            self.root.title("Escáner de Documentos PDF417")
            
            # Obtener dimensiones de la pantalla
            pantalla_ancho = self.root.winfo_screenwidth()
            pantalla_alto = self.root.winfo_screenheight()
            
            # Establecer tamaño de ventana (90% de la pantalla)
            ventana_ancho = int(pantalla_ancho * 0.9)
            ventana_alto = int(pantalla_alto * 0.9)
            
            self.root.geometry(f"{ventana_ancho}x{ventana_alto}")
            self.root.configure(bg="#2c3e50")
            
            # Centrar ventana
            pos_x = (pantalla_ancho - ventana_ancho) // 2
            pos_y = (pantalla_alto - ventana_alto) // 2
            self.root.geometry(f"{ventana_ancho}x{ventana_alto}+{pos_x}+{pos_y}")

            # Variables de control
            self.escaneando = False
            self.cap = None
            self.foto = None

            # Crear interfaz
            self.crear_interfaz()

        def crear_interfaz(self):
            """Crea la interfaz gráfica"""

            # Marco principal
            marco_principal = ttk.Frame(self.root)
            marco_principal.pack(fill="both", expand=True, padx=10, pady=10)

            # Título
            titulo = ttk.Label(marco_principal, text="ESCÁNER DE DOCUMENTOS PDF417 - AUTOMÁTICO",
                            font=("Helvetica", 24, "bold"))
            titulo.grid(row=0, column=0, columnspan=2, pady=(0, 10))

            # ============ PANEL IZQUIERDO: VIDEO ============
            marco_video = ttk.LabelFrame(marco_principal, text="Vista de Cámara", padding=10)
            marco_video.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=5)

            # Label para el video
            self.label_video = ttk.Label(marco_video, background="#000000")
            self.label_video.pack(fill="both", expand=True)

            # ============ PANEL DERECHO: INFORMACIÓN ============
            marco_info = ttk.LabelFrame(marco_principal, text="Información de Escaneo", padding=15)
            marco_info.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=5)

            # Información de estado
            ttk.Label(marco_info, text="DETECCIONES:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 5))

            self.text_info = scrolledtext.ScrolledText(marco_info, height=25, width=40,
                                                    font=("Courier", 10), wrap="word")
            self.text_info.pack(fill="both", expand=True, pady=10)

            # Configurar estilos de texto
            self.text_info.tag_configure("titulo", foreground="green", font=("Courier", 11, "bold"))
            self.text_info.tag_configure("error", foreground="red", font=("Courier", 10, "bold"))
            self.text_info.tag_configure("exito", foreground="lightgreen", font=("Courier", 10, "bold"))
            self.text_info.tag_configure("dato", foreground="cyan", font=("Courier", 10))
            self.text_info.tag_configure("separador", foreground="yellow")

            self.text_info.config(state="disabled", bg="#1e1e1e", fg="#00ff00")

            # Configurar pesos de grid
            marco_principal.columnconfigure(0, weight=2)
            marco_principal.columnconfigure(1, weight=1)
            marco_principal.rowconfigure(1, weight=1)

            # Botón para cerrar/volver (mantener siempre disponible)
            boton_cerrar = ttk.Button(marco_info, text="Volver / Cerrar Escáner", command=self.on_closing)
            boton_cerrar.pack(pady=(8, 0))

            # Iniciar captura de video
            self.iniciar_captura()

        def iniciar_captura(self):
            """Inicia la captura de video de la cámara"""
            try:
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                
                self.agregar_info("SISTEMA INICIALIZADO", "exito")
                self.agregar_info(f"Resolución: {int(self.cap.get(3))} x {int(self.cap.get(4))}", "dato")
                
                # Iniciar thread de video
                thread = threading.Thread(target=self._actualizar_video, daemon=True)
                thread.start()

            except Exception as e:
                self.agregar_info(f"Error al inicializar cámara: {e}", "error")
                messagebox.showerror("Error", f"No se pudo inicializar la cámara: {e}")

        def _actualizar_video(self):
            """Actualiza el video en la interfaz y escanea automáticamente"""
            # Recuadro
            x1, y1 = 500, 150
            x2, y2 = 1700, 800
            contador_frames = 0
            intervalo_escaneo = 5  # Escanear cada 5 frames

            while self.cap is not None:
                try:
                    if self.cap is None:
                        break

                    ret, frame = self.cap.read()
                    if not ret:
                        break

                    # Dibujar recuadro
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                    # Redimensionar para mostrar en tkinter
                    frame_resizado = cv2.resize(frame, (640, 360))
                    
                    # Convertir BGR a RGB
                    frame_rgb = cv2.cvtColor(frame_resizado, cv2.COLOR_BGR2RGB)

                    # Convertir a PhotoImage
                    img = Image.fromarray(frame_rgb)
                    photo = ImageTk.PhotoImage(img)

                    # Actualizar label
                    self.label_video.config(image=photo)
                    self.label_video.image = photo

                    self.root.update_idletasks()

                    # Realizar escaneo automático cada N frames
                    contador_frames += 1
                    if contador_frames >= intervalo_escaneo:
                        contador_frames = 0
                        self._escaneo_automatico(frame, x1, y1, x2, y2)
                    
                except Exception as e:
                    print(f"Error en actualización de video: {e}")
                    break

        def _escaneo_automatico(self, frame, x1, y1, x2, y2):
            """Realiza escaneo automático sin bloquear la interfaz"""
            try:
                # Recortar región
                cropped = frame[y1:y2, x1:x2]
                cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)

                # Decodificar
                results = zxingcpp.read_barcodes(cropped_rgb)

                if len(results) > 0:
                    self.root.after(0, self.agregar_info, "=" * 45, "separador")
                    self.root.after(0, self.agregar_info, f"DETECCIÓN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "titulo")
                    self.root.after(0, self.agregar_info, "=" * 45, "separador")
                    self.root.after(0, self.agregar_info, f"✓ {len(results)} código(s) detectado(s)", "exito")

                    for i, r in enumerate(results):
                        self.root.after(0, self.agregar_info, f"\n--- Código {i+1} ---", "titulo")
                        self.root.after(0, self.agregar_info, f"Formato: {r.format}", "dato")

                        # Limpieza y extracción
<<<<<<< HEAD
                        clean, extracted = parse_pdf417(r.text)
=======
                        clean, extracted = self.parse_pdf417(r.text)
>>>>>>> pcdavid

                        # Mostrar datos extraídos
                        self.root.after(0, self.agregar_info, "\nDATA EXTRAÍDA:", "titulo")

                        for key, val in extracted.items():
                            if val is not None:
                                self.root.after(0, self.agregar_info, f"  {key}: {val}", "dato")

            except Exception as e:
                pass  # Ignorar errores de escaneo para no saturar el log

        def agregar_info(self, texto, tag="dato"):
            """Agrega información al panel de texto"""
            self.text_info.config(state="normal")
            self.text_info.insert("end", texto + "\n", tag)
            self.text_info.see("end")
            self.text_info.config(state="disabled")

        def on_closing(self):
            """Maneja el cierre de la ventana"""
            if self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()
            self.root.destroy()


<<<<<<< HEAD
    def main():
        root = tk.Tk()
        app = EscanerPDF417(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()


    if __name__ == "__main__":
        main()
=======
def main():
    root = tk.Tk()
    app = EscanerPDF417(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
     main()
>>>>>>> pcdavid

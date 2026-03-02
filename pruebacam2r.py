import cv2
import zxingcpp
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import re
from datetime import datetime

def parse_pdf417(text):
    # Quitar caracteres no imprimibles
    clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)

    # Quitar palabras "NUL" que vienen del decodificador
    clean = clean.replace("NUL", " ")

    data = {}

    # ===============================
    # DETECCIÓN Y ELIMINACIÓN DE PREFIJO DE 8 DÍGITOS
    # ===============================
    # Buscar patrón: 8 dígitos + 10 dígitos + texto en mayúsculas
    patron_prefijo = r'(\d{8})(\d{10})([A-ZÑÁÉÍÓÚ]+)'
    match_prefijo = re.search(patron_prefijo, clean)
    
    if match_prefijo:
        # Si encontramos el patrón, extraemos solo los 10 dígitos (cédula) y el texto (apellido)
        cedula_encontrada = match_prefijo.group(2)
        texto_mayusculas = match_prefijo.group(3)
        
        # Reemplazar en el texto limpio: eliminamos los 8 dígitos del prefijo
        # pero mantenemos la cédula y el texto
        clean = clean.replace(match_prefijo.group(1), '', 1)
        
        # Guardar la cédula directamente
        data["Cédula"] = cedula_encontrada
        cedula = cedula_encontrada
    else:
        # Si no hay prefijo, buscar el patrón normal de 10 dígitos
        all_10_digits = re.findall(r'(?<!\d)\d{10}(?!\d)', clean)
        
        if len(all_10_digits) >= 2:
            cedula = all_10_digits[1]
            data["Cédula"] = cedula
        elif len(all_10_digits) == 1:
            cedula = all_10_digits[0]
            data["Cédula"] = cedula
        else:
            data["Cédula"] = None
            cedula = None

    # ===============================
    # 2. RH
    # ===============================
    m_rh = re.search(r'(A|B|O)[+-]', clean)
    if m_rh:
        data["rh"] = m_rh.group(0)

    # ===============================
    # 3. Fecha de nacimiento (formato DDMMYYYY)
    # ===============================
    m_fecha = re.search(r'\b(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])(19|20)\d{2}\b', clean)
    if m_fecha:
        dia = m_fecha.group(1)
        mes = m_fecha.group(2)
        anio = m_fecha.group(3) + m_fecha.group(4) if len(m_fecha.groups()) > 3 else m_fecha.group(3)
        data["fecha_nacimiento"] = f"{dia}/{mes}/{anio}"

    # ===============================
    # 4. Sexo
    # ===============================
    m_sexo = re.search(r'\b(MASCULINO|FEMENINO|M|F)\b', clean, re.IGNORECASE)
    if m_sexo:
        data["sexo"] = m_sexo.group(0).capitalize()

    # ===============================
    # 5. Apellidos y nombre
    # ===============================
    grupos = []
    if cedula:
        # Buscar después de la cédula
        pos = clean.find(cedula)
        if pos != -1:
            tail = clean[pos + len(cedula):]
            grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', tail)
            grupos = [g for g in grupos if g not in ["N", "NU", "NUL"]]

    # Si no encontramos grupos después de la cédula o no hay cédula,
    # buscar en todo el texto
    if not grupos:
        grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', clean)
        grupos = [g for g in grupos if g not in ["N", "NU", "NUL"]]

    # Asignar apellidos y nombre
    if len(grupos) >= 1:
        data["apellido1"] = grupos[0]
    if len(grupos) >= 2:
        data["apellido2"] = grupos[1]
    if len(grupos) >= 3:
        data["nombre"] = grupos[2]
        
    # Si tenemos exactamente 2 grupos, asumimos que el segundo es el nombre
    elif len(grupos) == 2:
        data["nombre"] = grupos[1]
        data["apellido2"] = ""

    return clean, data


class EscanerPDF417:
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
                    clean, extracted = parse_pdf417(r.text)

                    # Mostrar únicamente cédula, apellidos y nombre
                    ced = extracted.get("cedula")
                    ap1 = extracted.get("apellido1", "")
                    ap2 = extracted.get("apellido2", "")
                    nom = extracted.get("nombre", "")
                    self.root.after(0, self.agregar_info, "\nRESULTADO:", "titulo")
                    self.root.after(0, self.agregar_info, f"  cedula: {ced}", "dato")
                    self.root.after(0, self.agregar_info, f"  apellido1: {ap1}", "dato")
                    self.root.after(0, self.agregar_info, f"  apellido2: {ap2}", "dato")
                    self.root.after(0, self.agregar_info, f"  nombre: {nom}", "dato")

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


def main():
    root = tk.Tk()
    app = EscanerPDF417(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()


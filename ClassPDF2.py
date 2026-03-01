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
# basada en la versión que se usa en el notebook y otros ejemplos.
# Se mantiene la heurística de 10 dígitos y algunas reglas extra,
# pero ahora es un método independiente para que EscanerPDF417 pueda
# llamarlo directamente.

def parse_pdf417(text):
    # Quitar caracteres no imprimibles
    clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)

    # El decodificador a veces inyecta "NUL" entre campos
    clean = clean.replace('NUL', ' ')

    data = {}

    # 1. buscar todas las cadenas de 10 dígitos y elegir la segunda
    # algunos PDF417 traen signos o espacios entre números, eliminar aquí
    digits_only = re.sub(r'[^0-9]', '', clean)
    all_10_digits = re.findall(r'(?<!\d)\d{10}(?!\d)', clean)
    if not all_10_digits and len(digits_only) >= 10:
        # intentar usando la cadena compactada como respaldo
        all_10_digits = [digits_only[i:i+10] for i in range(len(digits_only)-9)]

    if len(all_10_digits) >= 2:
        data['cedula'] = all_10_digits[1]
        cedula = data['cedula']
    elif len(all_10_digits) == 1:
        data['cedula'] = all_10_digits[0]
        cedula = data['cedula']
    else:
        data['cedula'] = None
        cedula = None

    # 2. sexo + fecha
    m = re.search(r'([MF])(\d{8})', clean)
    if m:
        data['sexo'] = m.group(1)
        data['fecha_nac'] = m.group(2)

    # 3. RH
    m = re.search(r'(A|B|O)[+-]', clean)
    if m:
        data['rh'] = m.group(0)

    # 4. apellidos/nombre
    grupos = []
    if cedula:
        pos = clean.find(cedula)
        tail = clean[pos + len(cedula):]
        grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', tail)
        grupos = [g for g in grupos if g not in ('N', 'NU', 'NUL')]
        if len(grupos) >= 1:
            data['apellido1'] = grupos[0]
        if len(grupos) >= 2:
            data['apellido2'] = grupos[1]
        if len(grupos) >= 3:
            data['nombre'] = grupos[2]
    else:
        grupos_any = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', clean)
        grupos_any = [g for g in grupos_any if g not in ('N', 'NU', 'NUL')]
        if len(grupos_any) >= 1:
            data['apellido1'] = grupos_any[0]
        if len(grupos_any) >= 2:
            data['apellido2'] = grupos_any[1]
        if len(grupos_any) >= 3:
            data['nombre'] = grupos_any[2]
        # regla extra: si hay muchos dígitos totales, reconstruir cédula
        if data.get('apellido1'):
            total_digits = len(re.findall(r'\d', clean))
            if total_digits > 11:
                pos_ap = clean.find(data['apellido1'])
                if pos_ap != -1:
                    digits_collected = []
                    i = pos_ap - 1
                    while i >= 0 and len(digits_collected) < 10:
                        if clean[i].isdigit():
                            digits_collected.insert(0, clean[i])
                        i -= 1
                    if len(digits_collected) == 10:
                        cedula = ''.join(digits_collected)
                        data['cedula'] = cedula

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

                # botón adicional para escaneo manual
                boton_manual = ttk.Button(marco_info, text="Escanear ahora", command=lambda: self._escaneo_automatico(getattr(self, 'ultima_frame', None)))
                boton_manual.pack(pady=(4, 0))

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
                contador_frames = 0
                intervalo_escaneo = 5  # Escanear cada 5 frames

                while self.cap is not None:
                    try:
                        if self.cap is None:
                            break

                        ret, frame = self.cap.read()
                        if not ret:
                            break

                        # calcular región dinámicamente según resolución actual
                        h, w = frame.shape[:2]
                        # cuatro márgenes como proporción de ancho/alto
                        x1 = int(w * 0.25)
                        y1 = int(h * 0.15)
                        x2 = int(w * 0.85)
                        y2 = int(h * 0.75)

                        # Dibujar recuadro
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                        # guardar copia para posible escaneo manual
                        self.ultima_frame = frame.copy()

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
                            self._escaneo_automatico(frame)
                            
                    except Exception as e:
                        print(f"Error en actualización de video: {e}")
                        break

        def _escaneo_automatico(self, frame):
            """Realiza escaneo automático sin bloquear la interfaz"""
            try:
                # calcular la misma región que en el bucle de video
                h, w = frame.shape[:2]
                x1 = int(w * 0.25)
                y1 = int(h * 0.15)
                x2 = int(w * 0.85)
                y2 = int(h * 0.75)

                # Recortar región
                cropped = frame[y1:y2, x1:x2]
                # ampliar para ayudar al decodificador
                cropped = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
                # mostrar recorte en ventana temporal (útil para comprobar alineación)
                cv2.imshow("Recorte escaneo", cropped)
                cv2.waitKey(1)
                # Preprocesar: convertir a gris y ecualizar contraste
                gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                gray = clahe.apply(gray)
                prep = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

                # Función auxiliar para intentar varias orientaciones
                def try_orientations(img):
                    for angle, flag in [(0, None), (90, cv2.ROTATE_90_CLOCKWISE),
                                        (180, cv2.ROTATE_180),
                                        (270, cv2.ROTATE_90_COUNTERCLOCKWISE)]:
                        if flag is not None:
                            test = cv2.rotate(img, flag)
                        else:
                            test = img
                        res = zxingcpp.read_barcodes(test)
                        if res:
                            return res, angle
                    return [], 0

                results, used_angle = try_orientations(prep)
                if used_angle != 0:
                    self.root.after(0, self.agregar_info, f"Código detectado rotado {used_angle}°", "dato")

                if not results:
                    # intentar sin ecualización ni rotación como último recurso
                    fallback = zxingcpp.read_barcodes(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
                    if fallback:
                        results = fallback
                        self.root.after(0, self.agregar_info, "Código encontrado sin preprocesar", "dato")
                    else:
                        self.root.after(0, self.agregar_info, "Sin código en el recuadro", "error")
                        return

                self.root.after(0, self.agregar_info, "=" * 45, "separador")
                self.root.after(0, self.agregar_info, f"DETECCIÓN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "titulo")
                self.root.after(0, self.agregar_info, "=" * 45, "separador")
                self.root.after(0, self.agregar_info, f"✓ {len(results)} código(s) detectado(s)", "exito")

                for i, r in enumerate(results):
                    self.root.after(0, self.agregar_info, f"\n--- Código {i+1} ---", "titulo")
                    self.root.after(0, self.agregar_info, f"Formato: {r.format}", "dato")

                    # mostrar texto bruto para depuración
                    if not r.text or not r.text.strip():
                        self.root.after(0, self.agregar_info, "Código encontrado pero texto vacío", "error")
                        continue

                    self.root.after(0, self.agregar_info, f"Texto RAW: {r.text}", "dato")

                    # Limpieza y extracción usando función global
                    clean, extracted = parse_pdf417(r.text)
                    self.root.after(0, self.agregar_info, "Texto limpio:", "dato")
                    self.root.after(0, self.agregar_info, clean, "dato")
                    self.root.after(0, self.agregar_info, f"Diccionario extraído: {extracted}", "dato")

                    # Mostrar datos extraídos
                    self.root.after(0, self.agregar_info, "\nDATA EXTRAÍDA:", "titulo")
                    cedula_val = extracted.get('cedula')
                    if cedula_val is None:
                        self.root.after(0, self.agregar_info, "  <CÉDULA NO DETECTADA>", "error")
                    for key, val in extracted.items():
                        if val is not None:
                            self.root.after(0, self.agregar_info, f"  {key}: {val}", "dato")

            except Exception as e:
                # registrar error en log para no ocultarlo completamente
                self.root.after(0, self.agregar_info, f"Error escaneando: {e}", "error")

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

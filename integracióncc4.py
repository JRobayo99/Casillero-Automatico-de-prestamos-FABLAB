import cv2
import numpy as np
import zxingcpp
import pytesseract
from pytesseract import Output
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import re
from datetime import datetime
import sys

class IdentificadorCedulas:
    def __init__(self):
        # Configuración de la cámara
        self.cap = None
        self.tipo_cedula_detectado = None
        self.detection_complete = False
        
        # Configuración de ROIs para identificación
        self.roi_ident_x1, self.roi_ident_y1 = 350, 50
        self.roi_ident_x2, self.roi_ident_y2 = 1650, 900
        
        # Control de tiempo para escaneo automático
        self.last_scan_time = 0.0
        self.scan_interval = 0.3  # segundos entre intentos
        
        print("🔍 Sistema Integrado de Identificación de Cédulas Inicializado")
        
    def configurar_camara(self):
        """Configura la cámara con la resolución deseada"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Obtener resolución real
        self.frame_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📷 Resolución de cámara: {self.frame_w} x {self.frame_h}")
        return self.cap
    
    def configurar_ventana(self, titulo="Identificador de Cédulas"):
        """Configura la ventana de visualización"""
        cv2.namedWindow(titulo, cv2.WINDOW_NORMAL)
        
        # Obtener dimensiones de pantalla
        root = tk.Tk()
        root.withdraw()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()
        
        # Ajustar ventana a pantalla completa
        cv2.setWindowProperty(titulo, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        print(f"🖥️  Ventana configurada a: {screen_w}x{screen_h}")
        
        return titulo
    
    def preprocess_for_ocr(self, image):
        """Preprocesa la imagen para mejorar el OCR."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    def decode_pdf417(self, image):
        """Intenta decodificar un código PDF417 en la imagen."""
        try:
            results = zxingcpp.read_barcodes(image)
            for result in results:
                if result.format == zxingcpp.BarcodeFormat.PDF417:
                    return result.text
        except Exception as e:
            print(f"Error al leer PDF417: {e}")
        return None
    
    def extract_new_id_text(self, image):
        """Intenta encontrar y extraer el texto OCR de la cédula nueva."""
        h, w = image.shape[:2]
        # En cédula nueva, el texto está en la parte inferior
        roi = image[int(h*0.5):h, 0:w]
        
        if roi.size == 0:
            return None
        
        # Preprocesar
        processed_roi = self.preprocess_for_ocr(roi)
        
        # Configurar Tesseract para cédula nueva
        custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<'
        text = pytesseract.image_to_string(processed_roi, config=custom_config)
        text = re.sub(r'\s+', '', text)
        
        # Verificar si tiene características de cédula nueva
        if len(text) >= 70 and text.count('<') > 5:
            return text
        return None
    
    def identificar_tipo_cedula(self, frame):
        """
        Identifica si es cédula antigua (PDF417) o nueva (OCR)
        Retorna: 'antigua', 'nueva' o None
        """
        # Extraer ROI para identificación
        roi = frame[self.roi_ident_y1:self.roi_ident_y2, 
                   self.roi_ident_x1:self.roi_ident_x2]
        
        if roi.size == 0:
            return None
        
        # 1. Intentar detectar cédula antigua (PDF417)
        pdf417_data = self.decode_pdf417(roi)
        if pdf417_data:
            print("📄 ¡Cédula ANTIGUA detectada!")
            return 'antigua'
        
        # 2. Intentar detectar cédula nueva (OCR)
        new_id_text = self.extract_new_id_text(roi)
        if new_id_text:
            print("🆕 ¡Cédula NUEVA detectada!")
            return 'nueva'
        
        return None
    
    def mostrar_pantalla_carga(self, tipo_cedula):
        """Muestra una pantalla de carga antes de abrir el escáner específico"""
        print(f"⏳ Cargando escáner para cédula {tipo_cedula}...")
        
        # Crear ventana de carga con tkinter
        root = tk.Tk()
        root.title("Cargando Escáner")
        root.attributes('-fullscreen', True)

        root.configure(bg='#2E2E2E')

        main_frame= tk.Frame(root, bg='#2E2E2E')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        titulo = tk.Label(main_frame,
                          text=f"CÉDULA {tipo_cedula.upper()} DETECTADA",
                          font=('Arial', 14, 'bold'),
                          bg='#2E2E2E',
                          fg='white')
        titulo.grid(row=1, column=0,pady=20)

        subtitulo = tk.Label(main_frame,
                             text="Cargando escáner...",
                             font=('Arial', 48, 'bold'),
                             bg='#2E2E2E',
                             fg='#CCCCCC')
        subtitulo.grid(row=1, column=0,pady=20)

        cuenta_regresiva = tk.Label(main_frame,
                                    text ='La cámara se activará en 5 segundos',
                                    font=('Arial', 36, 'bold'),
                                    bg='#2E2E2E',
                                    fg='#FFD700')
        cuenta_regresiva.grid(row=3, column=0,pady=30)

        tiempo_label = tk.Label(main_frame,
                                text="5",
                                font=('Arial', 120, 'bold'),
                                bg='#2E2E2E',
                                fg='#FFD700')
        tiempo_label.grid(row=4, column=0,pady=50)

        instruccion = tk.Label(main_frame,
                                text="Por favor, espere mientras se carga el sistema",
                                font=('Arial', 28),
                                bg='#2E2E2E',
                                fg='#AAAAAA')
        instruccion.grid(row=5, column=0,pady=20)

        root.update()

        for i in range(5, 0, -1):
            tiempo_label.config(text=str(i))
            cuenta_regresiva.config(text=f"La cámara se activará en {i} segundos")
            root.update()
            time.sleep(1)

        tiempo_label.config(text='¡YA!', fg='#FF4500')
        cuenta_regresiva.config(text="Iniciando escáner...", fg='#FF4500')
        root.update()
        time.sleep(0.5)

        root.destroy()
        print("✅ Carga completa. Iniciando escáner...")

    def iniciar_identificacion(self):
        """Inicia el proceso de identificación"""
        
        # Configurar cámara
        self.configurar_camara()
        ventana = self.configurar_ventana("Identificador de Cédulas - Coloque la cédula en el recuadro")
        
        print("\n" + "="*60)
        print("🔍 MODO IDENTIFICACIÓN ACTIVADO")
        print("Coloque la cédula en el recuadro verde")
        print("Presione 'q' para salir")
        print("="*60 + "\n")
        
        while not self.detection_complete:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Dibujar ROI de identificación
            cv2.rectangle(frame, 
                         (self.roi_ident_x1, self.roi_ident_y1), 
                         (self.roi_ident_x2, self.roi_ident_y2), 
                         (0, 255, 0), 3)
            
            # Texto informativo
            cv2.putText(frame, "COLOQUE LA CEDULA AQUI", 
                       (self.roi_ident_x1, self.roi_ident_y1 - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.putText(frame, "IDENTIFICANDO TIPO DE CEDULA...", 
                       (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            # Escaneo automático
            now = time.time()
            if now - self.last_scan_time >= self.scan_interval:
                self.last_scan_time = now
                
                tipo = self.identificar_tipo_cedula(frame)
                
                if tipo:
                    # Mostrar detección en pantalla
                    color = (255, 0, 0) if tipo == 'nueva' else (0, 255, 0)
                    texto = f"CEDULA {tipo.upper()} DETECTADA!"
                    cv2.putText(frame, texto, 
                               (self.roi_ident_x1, self.roi_ident_y2 + 40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
                    
                    cv2.imshow(ventana, frame)
                    cv2.waitKey(500)  # Mostrar mensaje por medio segundo
                    
                    self.tipo_cedula_detectado = tipo
                    self.detection_complete = True
                    break
            
            # Mostrar frame
            cv2.imshow(ventana, frame)
            
            # Control de teclas
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        # Liberar recursos del identificador
        self.cap.release()
        cv2.destroyAllWindows()
        
        # Continuar según detección
        if self.detection_complete and self.tipo_cedula_detectado:
            self.mostrar_pantalla_carga(self.tipo_cedula_detectado)
            
            if self.tipo_cedula_detectado == 'antigua':
                print("\n📄 Iniciando escáner para CÉDULA ANTIGUA...")
                escaner = EscanerCedulaAntigua()
                escaner.iniciar_escaneo()
            else:
                print("\n🆕 Iniciando escáner para CÉDULA NUEVA...")
                escaner = EscanerCedulaNueva()
                escaner.iniciar_escaneo()



class EscanerCedulaAntigua:
    def __init__(self):
        self.cap = None
        self.detected = False
        
        # ROI específico para cédula antigua
        self.x1, self.y1 = 350, 50
        self.x2, self.y2 = 1650, 900
        
        self.last_scan_time = 0.0
        self.scan_interval = 0.5
        self.scan_cooldown = 2.0
        
    def configurar_camara(self):
        """Configura la cámara"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
    def configurar_ventana(self):
        """Configura ventana a pantalla completa"""
        cv2.namedWindow("Escáner Cédula Antigua", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Escáner Cédula Antigua", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
    def parse_pdf417(self, text):
        # Quitar caracteres no imprimibles
        clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)

        # Quitar palabras "NUL" que vienen del decodificador
        clean = clean.replace("NUL", " ")

        data = {}

        # ===============================
        # DETECCIÓN Y ELIMINACIÓN DE PREFIJO DE 8 DÍGITOS
        # ===============================
        # Buscar patrón: 8 dígitos + 10q
        # 
        #  dígitos + texto en mayúsculas
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
            data["Primer apellido"] = grupos[0]
        if len(grupos) >= 2:
            data["Segundo apellido"] = grupos[1]
        if len(grupos) >= 3:
            data["Nombre"] = grupos[2]
            
        # Si tenemos exactamente 2 grupos, asumimos que el segundo es el nombre
        elif len(grupos) == 2:
            data["Nombre"] = grupos[1]
            data["Segundo apellido"] = ""

        return clean, data
    
    def iniciar_escaneo(self):
        """Inicia el escaneo específico para cédula antigua"""
        self.configurar_camara()
        self.configurar_ventana()
        
        print("\n📄 ESCÁNER DE CÉDULA ANTIGUA INICIADO")
        print("Coloque el código de barras en el recuadro")
        print("Presione ESC para salir\n")
        
        while not self.detected:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Dibujar ROI específico
            cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0), 2)
            cv2.putText(frame, "COLOQUE EL CODIGO DE BARRAS AQUI", 
                       (self.x1, self.y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Escaneo automático
            now = time.time()
            if now - self.last_scan_time >= self.scan_interval:
                self.last_scan_time = now
                
                cropped = frame[self.y1:self.y2, self.x1:self.x2]
                if cropped.size > 0:
                    try:
                        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                        results = zxingcpp.read_barcodes(cropped_rgb)
                        
                        if results:
                            for r in results:
                                clean, extracted = self.parse_pdf417(r.text)
                                
                                if extracted.get("Cédula") and extracted.get("Primer apellido"):
                                    self.mostrar_resultados(extracted)
                                    self.detected = True
                                    break
                    except Exception as e:
                        print(f"Error: {e}")
            
            cv2.imshow("Escáner Cédula Antigua", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Escaneo de cédula antigua completado")
    
    def mostrar_resultados(self, data):
        """Muestra los resultados del escaneo"""
        print("\n" + "="*60)
        print("📄 DATOS DE CÉDULA ANTIGUA:")
        print("="*60)
        for key, value in data.items():
            print(f"   {key}: {value}")
        print("="*60 + "\n")


class EscanerCedulaNueva:
    def __init__(self):
        self.cap = None
        self.datos_detectados = False
        
        # ROI específico para cédula nueva
        self.x1, self.y1 = 350, 560
        self.x2, self.y2 = 1650, 900
        
        self.confianza_minima = 60
        
    def configurar_camara(self):
        """Configura la cámara"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
    def configurar_ventana(self):
        """Configura ventana a pantalla completa"""
        cv2.namedWindow("Escáner Cédula Nueva", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Escáner Cédula Nueva", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    def _limpiar_texto_ocr(self, texto):
        """Limpia y unifica el texto del OCR"""
        texto_limpio = ''.join(texto).replace(' ', '')
        texto_limpio = re.sub(r'[^A-Z0-9<]', '', texto_limpio.upper())
        return texto_limpio
    
    def _extraer_datos_cedula_nueva(self, texto_completo):
        """Extrae información de la cédula nueva"""
        if len(texto_completo) < 90:
            return None
        
        texto_90 = texto_completo[:90]
        
        numero_cedula = texto_90[48:58]
        texto_nombres = texto_90[60:90]
        
        partes = texto_nombres.split('<')
        partes = [p for p in partes if p]
        
        datos = {
            'texto_completo': texto_90,
            'numero_cedula': numero_cedula,
            'primer_apellido': partes[0] if len(partes) > 0 else '',
            'segundo_apellido': partes[1] if len(partes) > 1 else '',
            'nombres': ' '.join(partes[2:]) if len(partes) > 2 else ''
        }
        
        return datos
    
    def iniciar_escaneo(self):
        """Inicia el escaneo específico para cédula nueva"""
        self.configurar_camara()
        self.configurar_ventana()
        
        print("\n🆕 ESCÁNER DE CÉDULA NUEVA INICIADO")
        print("Coloque el texto de la cédula en el recuadro")
        print("Presione 'q' para salir\n")
        
        while not self.datos_detectados:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Dibujar ROI específico
            cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (255, 0, 0), 3)
            cv2.putText(frame, "COLOQUE EL TEXTO DE LA CEDULA AQUI", 
                       (self.x1, self.y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            
            # Procesar ROI con OCR
            roi = frame[self.y1:self.y2, self.x1:self.x2]
            
            if roi.size > 0:
                d = pytesseract.image_to_data(roi, lang='spa', output_type=Output.DICT)
                cant_cajas = len(d['text'])
                
                texto_detectado = []
                
                for i in range(cant_cajas):
                    if int(d['conf'][i]) > self.confianza_minima:
                        text = d['text'][i]
                        if text and text.strip():
                            texto_detectado.append(text.strip())
                
                if texto_detectado:
                    texto_limpio = self._limpiar_texto_ocr(texto_detectado)
                    info_texto = f"Caracteres: {len(texto_limpio)}/90"
                    cv2.putText(frame, info_texto, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    
                    if len(texto_limpio) >= 90:
                        datos = self._extraer_datos_cedula_nueva(texto_limpio)
                        if datos:
                            self.mostrar_resultados(datos)
                            self.datos_detectados = True
                            break
            
            cv2.imshow("Escáner Cédula Nueva", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Escaneo de cédula nueva completado")
    
    def mostrar_resultados(self, datos):
        """Muestra los resultados del escaneo"""
        print("\n" + "="*60)
        print("🆕 DATOS DE CÉDULA NUEVA:")
        print("="*60)
        print(f"   Número de Cédula: {datos['numero_cedula']}")
        print(f"   Primer Apellido: {datos['primer_apellido']}")
        print(f"   Segundo Apellido: {datos['segundo_apellido']}")
        print(f"   Nombres: {datos['nombres']}")
        print("="*60 + "\n")


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🎯 SISTEMA INTEGRADO DE IDENTIFICACIÓN DE CÉDULAS")
    print("="*60)
    print("\nEste sistema:")
    print("1️⃣  Identifica automáticamente si es cédula ANTIGUA o NUEVA")
    print("2️⃣  Muestra pantalla de carga")
    print("3️⃣  Abre el escáner específico según el tipo detectado")
    print("\n" + "="*60)
    
    identificador = IdentificadorCedulas()
    identificador.iniciar_identificacion()
    
    print("\n" + "="*60)
    print("🎉 Proceso completado exitosamente")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
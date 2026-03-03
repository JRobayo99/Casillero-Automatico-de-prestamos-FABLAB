import cv2
import numpy as np
import zxingcpp
import pytesseract
import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time
import threading
import os
import sys

# Configuración global
DEBUG = True

def debug_print(*args, **kwargs):
    """Imprime mensajes de debug si DEBUG está activado"""
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

class PantallaCarga:
    """Pantalla de carga con Tkinter para transiciones"""
    
    def __init__(self, titulo="Sistema de Lectura de Cédulas"):
        self.root = tk.Tk()
        self.root.title(titulo)
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#2c3e50')
        
        # Centrar contenido
        self.frame_principal = tk.Frame(self.root, bg='#2c3e50')
        self.frame_principal.pack(expand=True, fill='both')
        
        # Logo o título
        self.label_titulo = tk.Label(
            self.frame_principal, 
            text=titulo,
            font=('Arial', 32, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        self.label_titulo.pack(pady=50)
        
        # Mensaje de estado
        self.label_estado = tk.Label(
            self.frame_principal,
            text="Inicializando sistema...",
            font=('Arial', 24),
            bg='#2c3e50',
            fg='#3498db'
        )
        self.label_estado.pack(pady=30)
        
        # Subtipo de cédula detectada
        self.label_subtipo = tk.Label(
            self.frame_principal,
            text="",
            font=('Arial', 28, 'bold'),
            bg='#2c3e50',
            fg='#f1c40f'
        )
        self.label_subtipo.pack(pady=20)
        
        # Barra de progreso
        self.progreso = ttk.Progressbar(
            self.frame_principal,
            length=600,
            mode='determinate',
            style='blue.Horizontal.TProgressbar'
        )
        self.progreso.pack(pady=40)
        
        # Configurar estilo de la barra
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'blue.Horizontal.TProgressbar',
            troughcolor='#34495e',
            background='#3498db',
            thickness=30
        )
        
        # Instrucciones
        self.label_instrucciones = tk.Label(
            self.frame_principal,
            text="Preparando escáner específico...",
            font=('Arial', 16),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        self.label_instrucciones.pack(pady=20)
        
        # Botón de cancelar
        self.boton_cancelar = tk.Button(
            self.frame_principal,
            text="Cancelar",
            font=('Arial', 14),
            bg='#e74c3c',
            fg='white',
            padx=30,
            pady=10,
            command=self.cancelar
        )
        self.boton_cancelar.pack(pady=30)
        
        self.cancelado = False
        self.progreso_actual = 0
        
    def cancelar(self):
        """Cancela la operación"""
        self.cancelado = True
        self.mostrar_mensaje("Operación cancelada", "error")
        self.root.after(1500, self.cerrar)
    
    def actualizar_progreso(self, valor, maximo=100):
        """Actualiza la barra de progreso"""
        self.progreso['maximum'] = maximo
        self.progreso['value'] = valor
        self.root.update_idletasks()
    
    def actualizar_estado(self, mensaje, subtipo=""):
        """Actualiza el mensaje de estado"""
        self.label_estado.config(text=mensaje)
        if subtipo:
            self.label_subtipo.config(text=subtipo)
        self.root.update_idletasks()
    
    def mostrar_tipo_detectado(self, tipo):
        """Muestra qué tipo de cédula se detectó"""
        if tipo == 'antigua':
            self.label_subtipo.config(
                text="📄 CÉDULA ANTIGUA DETECTADA",
                fg='#3498db'
            )
        elif tipo == 'nueva':
            self.label_subtipo.config(
                text="🆔 CÉDULA NUEVA DETECTADA",
                fg='#2ecc71'
            )
        self.root.update_idletasks()
    
    def mostrar_mensaje(self, mensaje, tipo="info"):
        """Muestra un mensaje temporal"""
        colores = {
            'info': '#3498db',
            'success': '#2ecc71',
            'warning': '#f1c40f',
            'error': '#e74c3c'
        }
        self.label_instrucciones.config(
            text=mensaje,
            fg=colores.get(tipo, '#95a5a6')
        )
        self.root.update_idletasks()
    
    def iniciar(self):
        """Inicia el bucle de tkinter"""
        self.root.mainloop()
    
    def cerrar(self):
        """Cierra la ventana"""
        self.root.quit()
        self.root.destroy()


class IdentificadorCedulas:
    def __init__(self):
        # Configuración de cámara
        self.cap = None
        self.tipo_detectado = None
        self.datos_detectados = None
        
        # ROI para IDENTIFICACIÓN (zona general donde se coloca la cédula)
        self.roi_ident_x1, self.roi_ident_y1 = 350, 50
        self.roi_ident_x2, self.roi_ident_y2 = 1650, 900
        
        # Configuración de Tesseract - Intentar rutas comunes
        self.configurar_tesseract()
    
    def configurar_tesseract(self):
        """Configura la ruta de Tesseract según el sistema operativo"""
        posibles_rutas = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract'
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                pytesseract.pytesseract.tesseract_cmd = ruta
                debug_print(f"Tesseract encontrado en: {ruta}")
                return
        
        debug_print("Tesseract no encontrado. Asegúrate de que esté instalado.")
    
    def configurar_camara(self):
        """Configura la cámara con manejo de errores"""
        indices_probados = [0, 1, 2]
        
        for index in indices_probados:
            debug_print(f"Probando cámara índice {index}")
            self.cap = cv2.VideoCapture(index)
            
            if self.cap.isOpened():
                # Intentar configurar resolución
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Verificar que funciona
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.frame_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    self.frame_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    debug_print(f"Cámara {index} configurada: {self.frame_w}x{self.frame_h}")
                    return True
                else:
                    self.cap.release()
        
        debug_print("No se pudo configurar ninguna cámara")
        return False
    
    def preprocess_for_ocr(self, image):
        """Preprocesa la imagen para mejorar el OCR"""
        if image is None or image.size == 0:
            return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    def decode_pdf417(self, image):
        """Intenta decodificar un código PDF417"""
        try:
            if image is None or image.size == 0:
                return None
            
            results = zxingcpp.read_barcodes(image)
            for result in results:
                if result.format == zxingcpp.BarcodeFormat.PDF417:
                    return result.text
        except Exception as e:
            debug_print(f"Error en decode_pdf417: {e}")
        return None
    
    def extract_new_id_text(self, image):
        """Extrae texto OCR para cédula nueva"""
        if image is None or image.size == 0:
            return None
        
        h, w = image.shape[:2]
        roi = image[int(h*0.5):h, 0:w]
        
        if roi.size == 0:
            return None
        
        processed_roi = self.preprocess_for_ocr(roi)
        if processed_roi is None:
            return None
        
        custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<'
        
        try:
            text = pytesseract.image_to_string(processed_roi, config=custom_config)
            text = re.sub(r'\s+', '', text)
            
            if len(text) >= 80 and text.count('<') > 10:
                return text
        except Exception as e:
            debug_print(f"Error en OCR: {e}")
        
        return None
    
    def identificar_tipo_cedula(self, frame):
        """
        Identifica si la cédula es nueva o antigua
        Retorna: ('antigua', datos_pdf417) o ('nueva', texto_ocr) o (None, None)
        """
        h, w = frame.shape[:2]
        y2 = min(self.roi_ident_y2, h)
        x2 = min(self.roi_ident_x2, w)
        
        roi = frame[self.roi_ident_y1:y2, self.roi_ident_x1:x2]
        
        if roi.size == 0:
            return None, None
        
        # Intentar leer como cédula antigua (PDF417)
        pdf417_data = self.decode_pdf417(roi)
        
        if pdf417_data:
            clean, datos = CedulaAntigua.parse_pdf417(pdf417_data)
            if datos.get("Cédula") and datos.get("Primer apellido"):
                return 'antigua', pdf417_data
        
        # Intentar como cédula nueva (OCR)
        ocr_text = self.extract_new_id_text(roi)
        if ocr_text and len(ocr_text) >= 90:
            datos = CedulaNueva.extraer_datos(ocr_text)
            if datos and datos.get('numero_cedula'):
                return 'nueva', ocr_text
        
        return None, None
    
    def iniciar_identificacion(self, pantalla_carga=None):
        """Inicia el proceso de identificación de cédula"""
        if not self.configurar_camara():
            if pantalla_carga:
                pantalla_carga.mostrar_mensaje("Error al iniciar cámara", "error")
            return None, None
        
        if pantalla_carga:
            pantalla_carga.actualizar_estado("Buscando cédula...")
        
        cv2.namedWindow("Identificador de Cédulas", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Identificador de Cédulas", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        last_scan_time = 0
        scan_interval = 1.0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Dibujar ROI
            cv2.rectangle(frame, (self.roi_ident_x1, self.roi_ident_y1), 
                         (self.roi_ident_x2, self.roi_ident_y2), (0, 255, 0), 3)
            
            cv2.putText(frame, "COLOQUE LA CEDULA AQUI", 
                       (self.roi_ident_x1, self.roi_ident_y1 - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.putText(frame, "Presione 'q' para salir", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            now = time.time()
            if now - last_scan_time >= scan_interval:
                last_scan_time = now
                
                tipo, datos = self.identificar_tipo_cedula(frame)
                
                if tipo == 'antigua':
                    debug_print("CÉDULA ANTIGUA DETECTADA")
                    self.tipo_detectado = 'antigua'
                    self.datos_detectados = datos
                    break
                    
                elif tipo == 'nueva':
                    debug_print("CÉDULA NUEVA DETECTADA")
                    self.tipo_detectado = 'nueva'
                    self.datos_detectados = datos
                    break
            
            cv2.imshow('Identificador de Cédulas', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.tipo_detectado = None
                break
        
        cv2.destroyWindow('Identificador de Cédulas')
        return self.tipo_detectado, self.datos_detectados


class CedulaAntigua:
    # ROI específico para cédula antigua (del código original)
    ROI_X1 = 350
    ROI_Y1 = 50
    ROI_X2 = 1650
    ROI_Y2 = 900
    
    @staticmethod
    def parse_pdf417(text):
        """Parsea datos de cédula antigua (código original)"""
        clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)
        clean = clean.replace("NUL", " ")
        
        data = {}
        
        patron_prefijo = r'(\d{8})(\d{10})([A-ZÑÁÉÍÓÚ]+)'
        match_prefijo = re.search(patron_prefijo, clean)
        
        if match_prefijo:
            cedula_encontrada = match_prefijo.group(2)
            texto_mayusculas = match_prefijo.group(3)
            clean = clean.replace(match_prefijo.group(1), '', 1)
            data["Cédula"] = cedula_encontrada
            cedula = cedula_encontrada
        else:
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
        
        grupos = []
        if cedula:
            pos = clean.find(cedula)
            if pos != -1:
                tail = clean[pos + len(cedula):]
                grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', tail)
                grupos = [g for g in grupos if g not in ["N", "NU", "NUL"]]
        
        if not grupos:
            grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', clean)
            grupos = [g for g in grupos if g not in ["N", "NU", "NUL"]]
        
        if len(grupos) >= 1:
            data["Primer apellido"] = grupos[0]
        if len(grupos) >= 2:
            data["Segundo apellido"] = grupos[1]
        if len(grupos) >= 3:
            data["Nombre"] = grupos[2]
        elif len(grupos) == 2:
            data["Nombre"] = grupos[1]
            data["Segundo apellido"] = ""
        
        return clean, data
    
    @staticmethod
    def escanear(cap, pantalla_carga=None):
        """Escáner de cédula antigua con su ROI original"""
        debug_print("Iniciando escáner de cédula antigua")
        
        if pantalla_carga:
            pantalla_carga.actualizar_estado(
                "Iniciando escáner de cédula antigua...",
                "📄 CÉDULA ANTIGUA"
            )
            for i in range(0, 101, 10):
                pantalla_carga.actualizar_progreso(i)
                time.sleep(0.05)
        
        cv2.namedWindow("Escáner Cédula Antigua", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Escáner Cédula Antigua", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        last_scan_time = 0
        scan_interval = 0.5
        detected = False
        resultado = None
        
        while not detected:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Usar ROI original del código de cédula antigua
            h, w = frame.shape[:2]
            x1 = min(CedulaAntigua.ROI_X1, w-100)
            y1 = min(CedulaAntigua.ROI_Y1, h-100)
            x2 = min(CedulaAntigua.ROI_X2, w)
            y2 = min(CedulaAntigua.ROI_Y2, h)
            
            roi = frame[y1:y2, x1:x2]
            
            # Dibujar interfaz (estilo original)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Cedula Antigua", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            now = time.time()
            if now - last_scan_time >= scan_interval and not detected:
                last_scan_time = now
                
                if roi.size > 0:
                    try:
                        results = zxingcpp.read_barcodes(roi)
                        
                        for r in results:
                            if r.format == zxingcpp.BarcodeFormat.PDF417:
                                clean, datos = CedulaAntigua.parse_pdf417(r.text)
                                
                                if datos.get("Cédula") and datos.get("Primer apellido"):
                                    resultado = datos
                                    detected = True
                                    debug_print("Cédula antigua detectada exitosamente")
                                    break
                    except Exception as e:
                        debug_print(f"Error en escaneo: {e}")
            
            cv2.imshow('Escáner Cédula Antigua', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
        
        cv2.destroyWindow('Escáner Cédula Antigua')
        
        if resultado:
            print("\n" + "="*50)
            print("📄 CÉDULA ANTIGUA - DATOS EXTRAÍDOS")
            print("="*50)
            print(f"🆔 Cédula: {resultado.get('Cédula', 'N/A')}")
            print(f"👤 Primer apellido: {resultado.get('Primer apellido', 'N/A')}")
            print(f"👤 Segundo apellido: {resultado.get('Segundo apellido', 'N/A')}")
            print(f"👤 Nombre: {resultado.get('Nombre', 'N/A')}")
            print("="*50)
        
        return resultado


class CedulaNueva:
    # ROI específico para cédula nueva (del código original)
    ROI_X1 = 500
    ROI_Y1 = 550
    ROI_X2 = 1700
    ROI_Y2 = 800
    
    @staticmethod
    def limpiar_texto_ocr(texto):
        """Limpia texto OCR (código original)"""
        if isinstance(texto, list):
            texto = ''.join(texto)
        texto_limpio = texto.replace(' ', '')
        texto_limpio = re.sub(r'[^A-Z0-9<]', '', texto_limpio.upper())
        return texto_limpio
    
    @staticmethod
    def extraer_datos(texto_completo):
        """Extrae datos de cédula nueva (código original)"""
        texto_limpio = CedulaNueva.limpiar_texto_ocr(texto_completo)
        
        if len(texto_limpio) < 90:
            return None
        
        texto_90 = texto_limpio[:90]
        numero_cedula = texto_90[4:58]
        texto_nombres = texto_90[60:90]
        
        partes = texto_nombres.split('<')
        partes = [p for p in partes if p]
        
        datos = {
            'texto_completo_90': texto_90,
            'numero_cedula': numero_cedula,
            'primer_apellido': partes[0] if len(partes) >= 1 else '',
            'segundo_apellido': partes[1] if len(partes) >= 2 else '',
            'nombres': ' '.join(partes[2:]) if len(partes) >= 3 else ''
        }
        
        return datos
    
    @staticmethod
    def preprocess_for_ocr(image):
        """Preprocesa imagen para OCR (código original)"""
        if image is None or image.size == 0:
            return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    @staticmethod
    def escanear(cap, pantalla_carga=None):
        """Escáner de cédula nueva con su ROI original"""
        debug_print("Iniciando escáner de cédula nueva")
        
        if pantalla_carga:
            pantalla_carga.actualizar_estado(
                "Iniciando escáner de cédula nueva...",
                "🆔 CÉDULA NUEVA"
            )
            for i in range(0, 101, 10):
                pantalla_carga.actualizar_progreso(i)
                time.sleep(0.05)
        
        cv2.namedWindow("Escáner Cédula Nueva", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Escáner Cédula Nueva", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        last_scan_time = 0
        scan_interval = 1.0
        detected = False
        resultado = None
        
        while not detected:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Usar ROI original del código de cédula nueva
            h, w = frame.shape[:2]
            x1 = min(CedulaNueva.ROI_X1, w-100)
            y1 = min(CedulaNueva.ROI_Y1, h-100)
            x2 = min(CedulaNueva.ROI_X2, w)
            y2 = min(CedulaNueva.ROI_Y2, h)
            
            roi = frame[y1:y2, x1:x2]
            
            # Dibujar interfaz (estilo original)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
            cv2.putText(frame, "Cedula Nueva", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            now = time.time()
            if now - last_scan_time >= scan_interval and not detected:
                last_scan_time = now
                
                if roi.size > 0:
                    processed_roi = CedulaNueva.preprocess_for_ocr(roi)
                    
                    if processed_roi is not None:
                        custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<'
                        
                        try:
                            text = pytesseract.image_to_string(processed_roi, config=custom_config)
                            text_limpio = re.sub(r'\s+', '', text)
                            
                            # Mostrar contador
                            cv2.putText(frame, f"Caracteres: {len(text_limpio)}/90", 
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            if len(text_limpio) >= 90 and text_limpio.count('<') > 10:
                                datos = CedulaNueva.extraer_datos(text_limpio)
                                if datos and datos.get('numero_cedula'):
                                    resultado = datos
                                    detected = True
                                    debug_print("Cédula nueva detectada exitosamente")
                        except Exception as e:
                            debug_print(f"Error en OCR: {e}")
            
            cv2.imshow('Escáner Cédula Nueva', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
        
        cv2.destroyWindow('Escáner Cédula Nueva')
        
        if resultado:
            print("\n" + "="*50)
            print("🆔 CÉDULA NUEVA - DATOS EXTRAÍDOS")
            print("="*50)
            print(f"🆔 Número de Cédula: {resultado['numero_cedula']}")
            print(f"👤 Primer Apellido: {resultado['primer_apellido']}")
            print(f"👤 Segundo Apellido: {resultado['segundo_apellido']}")
            print(f"👤 Nombres: {resultado['nombres']}")
            print("="*50)
        
        return resultado


def main_con_pantalla_carga():
    """Función principal con pantalla de carga"""
    
    print("="*60)
    print("SISTEMA INTEGRADO DE LECTURA DE CÉDULAS")
    print("="*60)
    
    # Crear y mostrar pantalla de carga inicial
    pantalla = PantallaCarga("Sistema de Lectura de Cédulas Colombianas")
    pantalla.actualizar_estado("Inicializando sistema...")
    
    def ejecutar_proceso():
        try:
            # Actualizar progreso
            pantalla.actualizar_progreso(10)
            pantalla.actualizar_estado("Configurando cámara...")
            time.sleep(1)
            
            # Inicializar identificador
            pantalla.actualizar_progreso(30)
            pantalla.actualizar_estado("Iniciando identificador de cédulas...")
            identificador = IdentificadorCedulas()
            
            pantalla.actualizar_progreso(50)
            pantalla.actualizar_estado("Listo para identificar cédula")
            time.sleep(1)
            
            # Cerrar pantalla de carga para mostrar el identificador
            pantalla.root.after(0, pantalla.cerrar)
            time.sleep(1)
            
            # Identificar tipo de cédula
            tipo, datos = identificador.iniciar_identificacion()
            
            if tipo is None:
                print("\n🛑 Proceso cancelado por el usuario.")
                if identificador.cap:
                    identificador.cap.release()
                cv2.destroyAllWindows()
                return
            
            # Crear nueva pantalla de carga para la transición
            pantalla_transicion = PantallaCarga("Preparando escáner específico")
            pantalla_transicion.mostrar_tipo_detectado(tipo)
            
            # Actualizar según el tipo
            if tipo == 'antigua':
                pantalla_transicion.actualizar_estado(
                    "Cargando escáner de cédula antigua...",
                    "📄 CÉDULA ANTIGUA"
                )
                for i in range(0, 101, 20):
                    pantalla_transicion.actualizar_progreso(i)
                    time.sleep(0.3)
                
                pantalla_transicion.cerrar()
                time.sleep(1)
                
                # Ejecutar escáner de cédula antigua
                resultado = CedulaAntigua.escanear(identificador.cap)
                
            elif tipo == 'nueva':
                pantalla_transicion.actualizar_estado(
                    "Cargando escáner de cédula nueva...",
                    "🆔 CÉDULA NUEVA"
                )
                for i in range(0, 101, 20):
                    pantalla_transicion.actualizar_progreso(i)
                    time.sleep(0.3)
                
                pantalla_transicion.cerrar()
                time.sleep(1)
                
                # Ejecutar escáner de cédula nueva
                resultado = CedulaNueva.escanear(identificador.cap)
            
            # Liberar recursos
            if identificador.cap:
                identificador.cap.release()
            cv2.destroyAllWindows()
            
            print("\n🎉 Proceso completado exitosamente.")
            
        except Exception as e:
            debug_print(f"Error en el proceso: {e}")
            if 'pantalla' in locals():
                pantalla.mostrar_mensaje(f"Error: {str(e)}", "error")
            import traceback
            traceback.print_exc()
    
    # Ejecutar el proceso en un hilo separado
    threading.Thread(target=ejecutar_proceso, daemon=True).start()
    
    # Iniciar la pantalla de carga
    pantalla.iniciar()


if __name__ == "__main__":
    main_con_pantalla_carga()
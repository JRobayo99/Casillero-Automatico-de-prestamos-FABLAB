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
        self.roi_ident_x1, self.roi_ident_y1 = 500, 200
        self.roi_ident_x2, self.roi_ident_y2 = 1500, 900
        
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
        root.geometry("400x200")
        
        # Centrar ventana
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (400 // 2)
        y = (root.winfo_screenheight() // 2) - (200 // 2)
        root.geometry(f'400x200+{x}+{y}')
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, 
                          text=f"Preparando escáner para cédula {tipo_cedula.upper()}", 
                          font=('Arial', 14, 'bold'))
        titulo.pack(pady=20)
        
        # Barra de progreso
        progress = ttk.Progressbar(main_frame, mode='indeterminate', length=300)
        progress.pack(pady=20)
        progress.start(10)
        
        # Mensaje
        mensaje = ttk.Label(main_frame, 
                           text="Inicializando componentes...", 
                           font=('Arial', 10))
        mensaje.pack(pady=10)
        
        # Actualizar ventana
        root.update()
        
        # Simular carga
        for i in range(3):
            time.sleep(0.5)
            mensaje.config(text=f"Inicializando componentes{'.' * (i+1)}")
            root.update()
        
        root.destroy()
        
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
        """Parsea el texto del PDF417 de cédula antigua"""
        clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)
        clean = clean.replace("NUL", " ")
        
        data = {}
        
        # Buscar patrón de cédula
        patron_prefijo = r'(\d{8})(\d{10})([A-ZÑÁÉÍÓÚ]+)'
        match_prefijo = re.search(patron_prefijo, clean)
        
        if match_prefijo:
            cedula_encontrada = match_prefijo.group(2)
            data["Cédula"] = cedula_encontrada
            clean = clean.replace(match_prefijo.group(1), '', 1)
        else:
            all_10_digits = re.findall(r'(?<!\d)\d{10}(?!\d)', clean)
            if all_10_digits:
                data["Cédula"] = all_10_digits[0] if len(all_10_digits) == 1 else all_10_digits[1]
        
        # Extraer nombres y apellidos
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
        self.x1, self.y1 = 500, 550
        self.x2, self.y2 = 1700, 800
        
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
        
        numero_cedula = texto_90[4:58]
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
    print("\nPresione ENTER para comenzar...")
    input()
    
    identificador = IdentificadorCedulas()
    identificador.iniciar_identificacion()
    
    print("\n" + "="*60)
    print("🎉 Proceso completado exitosamente")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
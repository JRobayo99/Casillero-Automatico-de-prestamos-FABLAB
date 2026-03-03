import cv2
import numpy as np
import zxingcpp
import pytesseract
import re
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import time

class IdentificadorCedulas:
    def __init__(self):
        # Configuración de cámara
        self.cap = None
        self.tipo_detectado = None
        self.datos_detectados = None
        
        # ROI para IDENTIFICACIÓN (zona general donde se coloca la cédula)
        self.roi_ident_x1, self.roi_ident_y1 = 350, 50
        self.roi_ident_x2, self.roi_ident_y2 = 1650, 900
        
        # Configuración de Tesseract
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    def configurar_camara(self):
        """Configura la cámara con resolución 1920x1080"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Obtener resolución real
        self.frame_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Resolución de cámara: {self.frame_w} x {self.frame_h}")
        
    def configurar_ventana_pantalla_completa(self):
        """Configura la ventana en modo pantalla completa"""
        root = tk.Tk()
        root.withdraw()
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()
        root.destroy()
        
        cv2.namedWindow("Identificador de Cédulas", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Identificador de Cédulas", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
    def preprocess_for_ocr(self, image):
        """Preprocesa la imagen para mejorar el OCR"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    def decode_pdf417(self, image):
        """Intenta decodificar un código PDF417"""
        try:
            results = zxingcpp.read_barcodes(image)
            for result in results:
                if result.format == zxingcpp.BarcodeFormat.PDF417:
                    return result.text
        except Exception as e:
            print(f"Error en decode_pdf417: {e}")
        return None
    
    def extract_new_id_text(self, image):
        """Extrae texto OCR para cédula nueva"""
        h, w = image.shape[:2]
        # Enfocar en la parte inferior donde están los datos
        roi = image[int(h*0.5):h, 0:w]
        
        if roi.size == 0:
            return None
        
        processed_roi = self.preprocess_for_ocr(roi)
        custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<'
        
        try:
            text = pytesseract.image_to_string(processed_roi, config=custom_config)
            text = re.sub(r'\s+', '', text)
            
            if len(text) >= 80 and text.count('<') > 10:
                return text
        except Exception as e:
            print(f"Error en OCR: {e}")
        
        return None
    
    def identificar_tipo_cedula(self, frame):
        """
        Identifica si la cédula es nueva o antigua
        Retorna: ('antigua', datos_pdf417) o ('nueva', texto_ocr) o (None, None)
        """
        # Extraer ROI de identificación
        roi = frame[self.roi_ident_y1:self.roi_ident_y2, self.roi_ident_x1:self.roi_ident_x2]
        
        if roi.size == 0:
            return None, None
        
        # 1. Intentar leer como cédula antigua (PDF417)
        pdf417_data = self.decode_pdf417(roi)
        
        if pdf417_data:
            # Verificar que tenga datos válidos de cédula antigua
            clean, datos = CedulaAntigua.parse_pdf417(pdf417_data)
            if datos.get("Cédula") and datos.get("Primer apellido"):
                return 'antigua', pdf417_data
        
        # 2. Intentar como cédula nueva (OCR)
        ocr_text = self.extract_new_id_text(roi)
        if ocr_text and len(ocr_text) >= 90:
            datos = CedulaNueva.extraer_datos(ocr_text)
            if datos and datos.get('numero_cedula'):
                return 'nueva', ocr_text
        
        return None, None
    
    def dibujar_interfaz_identificacion(self, frame):
        """Dibuja la interfaz en el frame durante identificación"""
        # Dibujar ROI de identificación
        cv2.rectangle(frame, (self.roi_ident_x1, self.roi_ident_y1), 
                     (self.roi_ident_x2, self.roi_ident_y2), (0, 255, 0), 3)
        
        # Texto de instrucciones
        cv2.putText(frame, "COLOQUE LA CEDULA AQUI PARA IDENTIFICAR", 
                   (self.roi_ident_x1, self.roi_ident_y1 - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.putText(frame, "Presione 'q' para salir", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def iniciar_identificacion(self):
        """Inicia el proceso de identificación de cédula"""
        self.configurar_camara()
        self.configurar_ventana_pantalla_completa()
        
        print("\n=== IDENTIFICADOR DE CÉDULAS ===")
        print("Esperando detección de cédula...")
        print("Presione 'q' para salir\n")
        
        last_scan_time = 0
        scan_interval = 1.0  # Escanear cada segundo
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error al capturar frame")
                break
            
            # Dibujar interfaz de identificación
            frame = self.dibujar_interfaz_identificacion(frame)
            
            # Escanear periódicamente
            now = time.time()
            if now - last_scan_time >= scan_interval:
                last_scan_time = now
                
                tipo, datos = self.identificar_tipo_cedula(frame)
                
                if tipo == 'antigua':
                    print("\n✅ CÉDULA ANTIGUA DETECTADA")
                    self.tipo_detectado = 'antigua'
                    self.datos_detectados = datos
                    break
                    
                elif tipo == 'nueva':
                    print("\n✅ CÉDULA NUEVA DETECTADA")
                    self.tipo_detectado = 'nueva'
                    self.datos_detectados = datos
                    break
            
            # Mostrar frame
            cv2.imshow('Identificador de Cédulas', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.tipo_detectado = None
                break
        
        return self.tipo_detectado, self.datos_detectados


class CedulaAntigua:
    # ROI específico para cédula antigua (enfocado en el código PDF417)
    ROI_ANTIGUA_X1 = 500
    ROI_ANTIGUA_Y1 = 300
    ROI_ANTIGUA_X2 = 1500
    ROI_ANTIGUA_Y2 = 700
    
    @staticmethod
    def parse_pdf417(text):
        """Parsea datos de cédula antigua"""
        # Quitar caracteres no imprimibles
        clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)
        clean = clean.replace("NUL", " ")
        
        data = {}
        
        # Buscar patrón: 8 dígitos + 10q + texto
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
        
        # Extraer apellidos y nombre
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
    def dibujar_interfaz_antigua(frame, x1, y1, x2, y2):
        """Dibuja la interfaz específica para cédula antigua"""
        # Dibujar ROI específico para PDF417
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
        
        # Texto informativo
        cv2.putText(frame, "CÉDULA ANTIGUA - ENFOQUE EL CÓDIGO PDF417", 
                   (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        cv2.putText(frame, "Escaneando código de barras...", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Instrucciones adicionales
        cv2.putText(frame, "Presione ESC para cancelar", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    @staticmethod
    def escanear(cap, datos_pdf417=None):
        """
        Escáner de cédula antigua con su propio ROI
        Si recibe datos_pdf417, los procesa directamente
        Si no, inicia escaneo con cámara
        """
        # Si ya tenemos los datos, solo procesamos
        if datos_pdf417:
            print("\n" + "="*60)
            print("📋 PROCESANDO CÉDULA ANTIGUA")
            print("="*60)
            
            clean, datos = CedulaAntigua.parse_pdf417(datos_pdf417)
            
            print("\n--- DATOS EXTRAÍDOS ---")
            print(f"🆔 Cédula: {datos.get('Cédula', 'N/A')}")
            print(f"👤 Primer apellido: {datos.get('Primer apellido', 'N/A')}")
            print(f"👤 Segundo apellido: {datos.get('Segundo apellido', 'N/A')}")
            print(f"👤 Nombre: {datos.get('Nombre', 'N/A')}")
            print("="*60)
            
            return datos
        
        # Si no tenemos datos, iniciamos escaneo
        print("\n=== INICIANDO ESCÁNER DE CÉDULA ANTIGUA ===")
        
        # Configurar ventana en pantalla completa
        root = tk.Tk()
        root.withdraw()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()
        
        cv2.namedWindow("Escáner Cédula Antigua", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Escáner Cédula Antigua", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        last_scan_time = 0
        scan_interval = 0.5
        detected = False
        resultado = None
        
        while not detected:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Extraer ROI específico para cédula antigua
            roi = frame[CedulaAntigua.ROI_ANTIGUA_Y1:CedulaAntigua.ROI_ANTIGUA_Y2, 
                       CedulaAntigua.ROI_ANTIGUA_X1:CedulaAntigua.ROI_ANTIGUA_X2]
            
            # Dibujar interfaz
            frame = CedulaAntigua.dibujar_interfaz_antigua(
                frame, CedulaAntigua.ROI_ANTIGUA_X1, CedulaAntigua.ROI_ANTIGUA_Y1,
                CedulaAntigua.ROI_ANTIGUA_X2, CedulaAntigua.ROI_ANTIGUA_Y2
            )
            
            # Escanear periódicamente
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
                                    print("\n✅ CÉDULA ANTIGUA DETECTADA")
                                    break
                    except Exception as e:
                        print(f"Error en escaneo: {e}")
            
            cv2.imshow('Escáner Cédula Antigua', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
        
        cv2.destroyWindow('Escáner Cédula Antigua')
        
        if resultado:
            print("\n--- DATOS DE CÉDULA ANTIGUA ---")
            print(f"Cédula: {resultado.get('Cédula', 'N/A')}")
            print(f"Primer apellido: {resultado.get('Primer apellido', 'N/A')}")
            print(f"Segundo apellido: {resultado.get('Segundo apellido', 'N/A')}")
            print(f"Nombre: {resultado.get('Nombre', 'N/A')}")
            print("="*40)
        
        return resultado


class CedulaNueva:
    # ROI específico para cédula nueva (enfocado en el texto MRZ)
    ROI_NUEVA_X1 = 400
    ROI_NUEVA_Y1 = 500
    ROI_NUEVA_X2 = 1600
    ROI_NUEVA_Y2 = 900
    
    @staticmethod
    def limpiar_texto_ocr(texto):
        """Limpia texto OCR"""
        if isinstance(texto, list):
            texto = ''.join(texto)
        texto_limpio = texto.replace(' ', '')
        texto_limpio = re.sub(r'[^A-Z0-9<]', '', texto_limpio.upper())
        return texto_limpio
    
    @staticmethod
    def extraer_datos(texto_completo):
        """Extrae datos de cédula nueva"""
        texto_limpio = CedulaNueva.limpiar_texto_ocr(texto_completo)
        
        if len(texto_limpio) < 90:
            return None
        
        texto_90 = texto_limpio[:90]
        
        # Extraer número de cédula
        numero_cedula = texto_90[4:58]
        
        # Extraer texto de nombres (posiciones 60-89)
        texto_nombres = texto_90[60:90]
        
        # Dividir por <
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
        """Preprocesa la imagen para mejorar el OCR"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    @staticmethod
    def dibujar_interfaz_nueva(frame, x1, y1, x2, y2):
        """Dibuja la interfaz específica para cédula nueva"""
        # Dibujar ROI específico para MRZ
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        # Texto informativo
        cv2.putText(frame, "CÉDULA NUEVA - ENFOQUE LAS 3 LÍNEAS DE TEXTO", 
                   (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.putText(frame, "Leyendo texto MRZ...", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Instrucciones adicionales
        cv2.putText(frame, "Presione ESC para cancelar", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Mostrar contador de caracteres
        cv2.putText(frame, "Esperando 90 caracteres...", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    @staticmethod
    def escanear(cap, texto_ocr=None):
        """
        Escáner de cédula nueva con su propio ROI
        Si recibe texto_ocr, lo procesa directamente
        Si no, inicia escaneo con cámara
        """
        # Si ya tenemos los datos, solo procesamos
        if texto_ocr:
            print("\n" + "="*60)
            print("📋 PROCESANDO CÉDULA NUEVA")
            print("="*60)
            
            datos = CedulaNueva.extraer_datos(texto_ocr)
            
            if datos:
                print(f"🆔 Número de Cédula: {datos['numero_cedula']}")
                print(f"👤 Primer Apellido: {datos['primer_apellido']}")
                print(f"👤 Segundo Apellido: {datos['segundo_apellido']}")
                print(f"👤 Nombres: {datos['nombres']}")
            else:
                print("❌ Error al procesar los datos")
            
            print("="*60)
            return datos
        
        # Si no tenemos datos, iniciamos escaneo
        print("\n=== INICIANDO ESCÁNER DE CÉDULA NUEVA ===")
        
        # Configurar ventana en pantalla completa
        root = tk.Tk()
        root.withdraw()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()
        
        cv2.namedWindow("Escáner Cédula Nueva", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Escáner Cédula Nueva", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        last_scan_time = 0
        scan_interval = 1.0
        detected = False
        resultado = None
        
        while not detected:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Extraer ROI específico para cédula nueva
            roi = frame[CedulaNueva.ROI_NUEVA_Y1:CedulaNueva.ROI_NUEVA_Y2, 
                       CedulaNueva.ROI_NUEVA_X1:CedulaNueva.ROI_NUEVA_X2]
            
            # Dibujar interfaz
            frame = CedulaNueva.dibujar_interfaz_nueva(
                frame, CedulaNueva.ROI_NUEVA_X1, CedulaNueva.ROI_NUEVA_Y1,
                CedulaNueva.ROI_NUEVA_X2, CedulaNueva.ROI_NUEVA_Y2
            )
            
            # Escanear periódicamente
            now = time.time()
            if now - last_scan_time >= scan_interval and not detected:
                last_scan_time = now
                
                if roi.size > 0:
                    # Preprocesar ROI
                    processed_roi = CedulaNueva.preprocess_for_ocr(roi)
                    
                    # Configurar Tesseract
                    custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<'
                    
                    try:
                        text = pytesseract.image_to_string(processed_roi, config=custom_config)
                        text_limpio = re.sub(r'\s+', '', text)
                        
                        # Actualizar contador
                        cv2.putText(frame, f"Caracteres: {len(text_limpio)}/90", 
                                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        if len(text_limpio) >= 90 and text_limpio.count('<') > 10:
                            datos = CedulaNueva.extraer_datos(text_limpio)
                            if datos and datos.get('numero_cedula'):
                                resultado = datos
                                detected = True
                                print("\n✅ CÉDULA NUEVA DETECTADA")
                    except Exception as e:
                        print(f"Error en OCR: {e}")
            
            cv2.imshow('Escáner Cédula Nueva', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
        
        cv2.destroyWindow('Escáner Cédula Nueva')
        
        if resultado:
            print("\n--- DATOS DE CÉDULA NUEVA ---")
            print(f"Cédula: {resultado['numero_cedula']}")
            print(f"Primer apellido: {resultado['primer_apellido']}")
            print(f"Segundo apellido: {resultado['segundo_apellido']}")
            print(f"Nombres: {resultado['nombres']}")
            print("="*40)
        
        return resultado


def main():
    """Función principal que integra todo el flujo"""
    
    print("="*60)
    print("SISTEMA INTEGRADO DE LECTURA DE CÉDULAS")
    print("="*60)
    print("1. Identificando tipo de cédula...")
    
    # Inicializar cámara (una sola vez para todo el proceso)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Paso 1: Identificar tipo de cédula
    identificador = IdentificadorCedulas()
    identificador.cap = cap  # Usar la misma cámara
    tipo, datos = identificador.iniciar_identificacion()
    
    # Verificar si se canceló
    if tipo is None:
        print("\n🛑 Proceso cancelado por el usuario.")
        cap.release()
        cv2.destroyAllWindows()
        return
    
    # Paso 2: Procesar según el tipo detectado con sus ROIs específicos
    if tipo == 'antigua':
        print("\n📌 Cédula antigua detectada. Iniciando escáner específico...")
        resultado = CedulaAntigua.escanear(cap, datos)
        
    elif tipo == 'nueva':
        print("\n📌 Cédula nueva detectada. Iniciando escáner específico...")
        resultado = CedulaNueva.escanear(cap, datos)
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n🎉 Proceso completado exitosamente.")
    
    # Mantener ventana de resultado visible
    input("\nPresione Enter para salir...")


if __name__ == "__main__":
    main()
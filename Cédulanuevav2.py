import cv2
import pytesseract
from pytesseract import Output

class DetectorCedula:
    def __init__(self, fuente=0, idioma='spa', confianza_minima=60):
        """
        Inicializa el detector de cédulas
        
        Args:
            fuente: Fuente de video (0 para cámara web, o ruta de video)
            idioma: Idioma para OCR ('spa' para español)
            confianza_minima: Umbral de confianza para mostrar texto (0-100)
        """
        self.fuente = fuente
        self.idioma = idioma
        self.confianza_minima = confianza_minima
        self.cap = None
        self.screen_width = 1920  # Valores por defecto
        self.screen_height = 1080
        
        # Obtener dimensiones de la pantalla
        self._obtener_dimensiones_pantalla()
    
    def _obtener_dimensiones_pantalla(self):
        """Obtiene las dimensiones reales de la pantalla"""
        try:
            import tkinter as tk
            root = tk.Tk()
            self.screen_width = root.winfo_screenwidth()
            self.screen_height = root.winfo_screenheight()
            root.destroy()
            print(f"Dimensiones de pantalla detectadas: {self.screen_width}x{self.screen_height}")
        except:
            print("No se pudo obtener dimensiones de pantalla, usando 1920x1080")
    
    def _configurar_ventana(self, pantalla_completa=False):
        """
        Configura la ventana de visualización
        
        Args:
            pantalla_completa: Si True, pone la ventana en modo pantalla completa
        """
        cv2.namedWindow('Detector Cédula', cv2.WINDOW_NORMAL)
        
       
        cv2.setWindowProperty('Detector Cédula', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
    
    def _procesar_frame(self, frame):
        """
        Procesa un frame individual: aplica OCR y dibuja resultados
        
        Args:
            frame: Imagen a procesar
            
        Returns:
            tuple: (frame_procesado, texto_detectado)
        """
        d = pytesseract.image_to_data(frame, lang=self.idioma, output_type=Output.DICT)
        cant_cajas = len(d['text'])
        
        texto_detectado = []
        
        for i in range(cant_cajas):
            if int(d['conf'][i]) > self.confianza_minima:
                text = d['text'][i]
                x = d['left'][i]
                y = d['top'][i]
                w = d['width'][i]
                h = d['height'][i]
                
                if text and text.strip() != "":
                    # Dibujar rectángulo y texto en el frame
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    texto_detectado.append(text.strip())
        
        return frame, texto_detectado
    
    def _extraer_datos_cedula(self, texto_completo):
        """
        Intenta extraer información específica de cédula
        
        Args:
            texto_completo: Texto completo detectado
            
        Returns:
            dict: Diccionario con datos extraídos o None
        """
        datos_cedula = {}
        
        # Verificar si es una cédula (contiene "CEDULA" o números)
        if "CEDULA" in texto_completo.upper() or any(char.isdigit() for char in texto_completo):
            datos_cedula['texto_completo'] = texto_completo
            
            # Buscar patrones de números (cédula, identificación)
            palabras = texto_completo.split()
            numeros_encontrados = [p for p in palabras if p.isdigit()]
            if numeros_encontrados:
                datos_cedula['numeros'] = numeros_encontrados
            
            return datos_cedula
        
        return None
    
    def iniciar_deteccion(self, pantalla_completa=False, imprimir_tiempo_real=True):
        """
        Inicia el proceso de detección de cédulas
        
        Args:
            pantalla_completa: Si True, muestra en pantalla completa
            imprimir_tiempo_real: Si True, imprime texto detectado en tiempo real
        """
        # Inicializar cámara
        self.cap = cv2.VideoCapture(self.fuente)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Configurar ventana
        self._configurar_ventana(pantalla_completa)
        
        print("Detector de cédulas iniciado. Presiona 'q' para salir.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error al capturar frame")
                break
            
            # Procesar frame
            frame_procesado, texto_detectado = self._procesar_frame(frame)
            
            # Imprimir texto detectado en tiempo real
            if texto_detectado and imprimir_tiempo_real:
                print("Texto detectado:", " ".join(texto_detectado))
                
                # Intentar extraer datos de cédula
                texto_completo = " ".join(texto_detectado)
                datos_cedula = self._extraer_datos_cedula(texto_completo)
                
                if datos_cedula:
                    print("\n--- POSIBLES DATOS DE CÉDULA ---")
                    print(f"Texto: {datos_cedula.get('texto_completo', 'N/A')}")
                    if 'numeros' in datos_cedula:
                        print(f"Números encontrados: {', '.join(datos_cedula['numeros'])}")
                    print("--------------------------------\n")
            
            # Mostrar frame
            cv2.imshow('Detector Cédula', frame_procesado)
            
            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Limpiar recursos
        self.detener()
    
    def detener(self):
        """Detiene la captura y cierra ventanas"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Detector detenido.")
    
    def capturar_y_guardar(self, nombre_archivo="captura.jpg"):
        """
        Captura un frame y guarda la imagen
        
        Args:
            nombre_archivo: Nombre del archivo para guardar
        """
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                cv2.imwrite(nombre_archivo, frame)
                print(f"Captura guardada como {nombre_archivo}")
            else:
                print("Error al capturar frame")


# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del detector
    detector = DetectorCedula(
        fuente=0,           # 0 para cámara web, o ruta de video
        idioma='spa',       # Idioma español
        confianza_minima=60 # Confianza mínima del 60%
    )
    
    # Iniciar detección
    # Opciones:
    # - pantalla_completa=False: ventana redimensionada al tamaño de pantalla
    # - pantalla_completa=True:  pantalla completa
    detector.iniciar_deteccion(
        pantalla_completa=False,
        imprimir_tiempo_real=True
    )
    
    # También puedes usar:
    # detector.capturar_y_guardar("mi_cedula.jpg")  # Para capturar una imagen
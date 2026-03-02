 def _extraer_datos_cedula_nueva(self, texto_completo):
        """
        Extrae información de la cédula nueva colombiana basada en posiciones
        El formato esperado es de 90 caracteres con <, números y letras
        
        Args:
            texto_completo: Texto completo detectado y limpiado
            
        Returns:
            dict: Diccionario con los datos extraídos o None
        """
        if len(texto_completo) < 90:
            return None
        
        # Tomar solo los primeros 90 caracteres
        texto_90 = texto_completo[:90]
        
        print(f"\n🔍 Texto de 90 caracteres detectado: {texto_90}")
        
        # Extraer número de cédula (posiciones 47-57, 10 dígitos)
        # Nota: Python usa indexación 0-based, por lo que posición 47 es índice 47
        numero_cedula = texto_90[47:58]  # Hasta posición 57 inclusive (10 caracteres)
        
        # Extraer texto de posiciones 60-89 (30 caracteres)
        texto_nombres = texto_90[60:90]
        
        # Dividir en cadenas de texto (separadas por <)
        partes = texto_nombres.split('<')
        # Filtrar partes vacías
        partes = [p for p in partes if p]
        
        datos = {
            'texto_completo_90': texto_90,
            'numero_cedula': numero_cedula,
            'primer_apellido': '',
            'segundo_apellido': '',
            'nombres': ''
        }
        
        # Asignar según la cantidad de partes encontradas
        if len(partes) >= 1:
            datos['primer_apellido'] = partes[0]
        if len(partes) >= 2:
            datos['segundo_apellido'] = partes[1]
        if len(partes) >= 3:
            # Unir el resto como nombres
            datos['nombres'] = ' '.join(partes[2:])
        
        return datos
    
    def iniciar_deteccion(self, imprimir_tiempo_real=True):
        """
        Inicia el proceso de detección de cédulas
        
        Args:
            imprimir_tiempo_real: Si True, imprime texto detectado en tiempo real
        """
        # Configurar cámara
        self._configurar_camara()
        
        # Configurar ventana al tamaño de la pantalla
        self._configurar_ventana()
        
        print("\n=== DETECTOR DE CÉDULAS NUEVA COLOMBIANA INICIADO ===")
        print("Presiona 'q' para salir")
        print("Presiona 'c' para capturar y guardar imagen")
        print("=====================================================\n")
        
        while not self.datos_detectados:  # Continuar hasta detectar los 90 caracteres
            ret, frame = self.cap.read()
            if not ret:
                print("Error al capturar frame")
                break
            
            # Procesar frame
            frame_procesado, texto_detectado = self._procesar_frame(frame)
            
            # Mostrar información en el frame
            info_texto = f"Caracteres detectados: {len(''.join(texto_detectado)) if texto_detectado else 0}"
            cv2.putText(frame_procesado, info_texto, 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Procesar texto detectado
            if texto_detectado and imprimir_tiempo_real:
                texto_completo = " ".join(texto_detectado)
                texto_limpio = self._limpiar_texto_ocr(texto_detectado)
                
                print(f"\r📝 Caracteres válidos: {len(texto_limpio)}/90", end="", flush=True)
                
                # Verificar si tenemos 90 caracteres válidos
                if len(texto_limpio) >= 90:
                    print("\n" + "="*60)
                    print("✅ ¡90 CARACTERES DETECTADOS! Procesando información...")
                    
                    # Extraer datos de la cédula
                    datos_cedula = self._extraer_datos_cedula_nueva(texto_limpio)
                    
                    if datos_cedula:
                        print("\n" + "="*60)
                        print("📋 DATOS DE CÉDULA NUEVA COLOMBIANA:")
                        print("="*60)
                        print(f"🆔 Número de Cédula: {datos_cedula['numero_cedula']}")
                        print(f"👤 Primer Apellido: {datos_cedula['primer_apellido']}")
                        print(f"👤 Segundo Apellido: {datos_cedula['segundo_apellido']}")
                        print(f"👤 Nombres: {datos_cedula['nombres']}")
                        print("="*60 + "\n")
                        
                        # Marcar como detectado para salir del bucle
                        self.datos_detectados = True
                        
                        # Mostrar mensaje de cierre
                        print("🎉 Escáner cerrándose automáticamente...")
                        break
                    else:
                        print("❌ Error al procesar los datos")
            
            # Mostrar frame
            cv2.imshow('Detector Cédula', frame_procesado)
            
            # Control de teclas
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                self.capturar_y_guardar()
        
        # Limpiar recursos
        self.detener()
    
    def detener(self):
        """Detiene la captura y cierra ventanas"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("\n🛑 Detector detenido.")
    
    def capturar_y_guardar(self, nombre_archivo="captura_cedula.jpg"):
        """
        Captura un frame y guarda la imagen
        
        Args:
            nombre_archivo: Nombre del archivo para guardar
        """
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Guardar imagen completa
                cv2.imwrite(nombre_archivo, frame)
                print(f"📸 Captura guardada como {nombre_archivo}")
                
                # Guardar solo la región de interés
                roi = frame[self.y1:self.y2, self.x1:self.x2]
                nombre_roi = f"roi_{nombre_archivo}"
                cv2.imwrite(nombre_roi, roi)
                print(f"📸 Región de interés guardada como {nombre_roi}")
            else:
                print("❌ Error al capturar frame")
    
    def ajustar_recuadro(self, x1, y1, x2, y2):
        """
        Ajusta las coordenadas del recuadro de interés
        
        Args:
            x1, y1: Esquina superior izquierda
            x2, y2: Esquina inferior derecha
        """
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        print(f"Recuadro ajustado: ({x1}, {y1}) a ({x2}, {y2})")


# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del detector con la configuración solicitada
    detector = DetectorCedula(
        fuente=0,           # Cámara web
        idioma='spa',       # Español
        confianza_minima=60 # Confianza mínima 60%
    )
    
    # Iniciar detección
    detector.iniciar_deteccion(imprimir_tiempo_real=True)
    
    # Opcional: Si necesitas ajustar el recuadro en tiempo de ejecución
    # detector.ajustar_recuadro(400, 100, 1600, 700)
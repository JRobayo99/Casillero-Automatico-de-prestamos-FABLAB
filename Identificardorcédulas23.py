#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# scanner_pdf417_basico.py

import cv2
import numpy as np
import zxingcpp
import sys
import time


class ScannerPDF417Basico:
    """
    Escáner básico para detectar PDF417 (cédulas antiguas)
    usando zxingcpp y OpenCV
    """
    
    def __init__(self, camara_id=0):
        self.camara_id = camara_id
        self.cap = None
        self.ultimo_texto = ""
        self.ultimo_tiempo = 0
        
    def iniciar_camara(self):
        """Inicializa la cámara"""
        print(f"\n📷 Iniciando cámara {self.camara_id}...")
        
        self.cap = cv2.VideoCapture(self.camara_id)
        
        if not self.cap.isOpened():
            print("❌ Error: No se pudo abrir la cámara")
            return False
        
        # Configurar resolución
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("✅ Cámara iniciada correctamente")
        return True
    
    def detectar_pdf417(self, frame):
        """
        Detecta código PDF417 en el frame usando zxingcpp
        Retorna: (texto_decodificado, puntos_del_codigo)
        """
        try:
            # Convertir a escala de grises (zxingcpp trabaja mejor con grises)
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            # Leer códigos de barras con zxingcpp
            resultados = zxingcpp.read_barcodes(gray)
            
            for resultado in resultados:
                # Verificar si es PDF417 (formato de cédula antigua)
                if resultado.format == zxingcpp.BarcodeFormat.PDF417:
                    texto = resultado.text
                    puntos = resultado.position
                    
                    print(f"✅ PDF417 DETECTADO")
                    print(f"   Formato: {resultado.format}")
                    print(f"   Calidad: {resultado.quality}")
                    print(f"   Texto: {texto[:50]}..." if len(texto) > 50 else f"   Texto: {texto}")
                    
                    return texto, puntos
            
        except Exception as e:
            print(f"Error en detección: {e}")
        
        return None, None
    
    def dibujar_pdf417(self, frame, texto, puntos):
        """
        Dibuja el contorno del PDF417 y el texto decodificado
        """
        if puntos:
            # Convertir puntos a formato para OpenCV
            pts = np.array([[puntos[0].x, puntos[0].y],
                           [puntos[1].x, puntos[1].y],
                           [puntos[2].x, puntos[2].y],
                           [puntos[3].x, puntos[3].y]], np.int32)
            pts = pts.reshape((-1, 1, 2))
            
            # Dibujar rectángulo verde alrededor del código
            cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
            
            # Poner etiqueta
            cv2.putText(frame, "PDF417 DETECTADO", (puntos[0].x, puntos[0].y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Mostrar texto decodificado (primeros caracteres)
            if texto:
                texto_corto = texto[:30] + "..." if len(texto) > 30 else texto
                cv2.putText(frame, texto_corto, (puntos[0].x, puntos[0].y - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def ejecutar(self):
        """Ejecuta el escáner de PDF417"""
        
        # Iniciar cámara
        if not self.iniciar_camara():
            return
        
        print("\n🔍 BUSCANDO CÓDIGO PDF417")
        print("   Acerque el reverso de la cédula ANTIGUA")
        print("   Presione ESC para salir")
        print("   Presione ESPACIO para congelar/mostrar texto completo\n")
        
        frame_count = 0
        texto_completo = ""
        
        while True:
            # Capturar frame
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Error al capturar frame")
                break
            
            frame_count += 1
            
            # Crear una copia para dibujar
            frame_dibujado = frame.copy()
            
            # Detectar PDF417 (cada 2 frames para ahorrar CPU)
            if frame_count % 2 == 0:
                texto, puntos = self.detectar_pdf417(frame)
                
                if texto:
                    self.ultimo_texto = texto
                    self.ultimo_tiempo = time.time()
                    texto_completo = texto
                    
                    # Mostrar mensaje de cédula antigua
                    print("\n🎯 ¡CÉDULA ANTIGUA DETECTADA!")
            
            # Si tenemos un PDF417 detectado recientemente, dibujarlo
            if self.ultimo_texto and (time.time() - self.ultimo_tiempo) < 2:
                # Necesitamos los puntos, si no los tenemos, solo mostramos texto
                if 'puntos' in locals() and puntos:
                    frame_dibujado = self.dibujar_pdf417(frame_dibujado, self.ultimo_texto, puntos)
                else:
                    cv2.putText(frame_dibujado, "PDF417 DETECTADO", (50, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Información en pantalla
            cv2.putText(frame_dibujado, "BUSCANDO PDF417 - Cedula ANTIGUA", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.putText(frame_dibujado, "ESC: Salir | ESPACIO: Ver texto", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Mostrar frame
            cv2.imshow('Scanner PDF417 - Cedula Antigua', frame_dibujado)
            
            # Teclas de control
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                print("\n👋 Saliendo...")
                break
                
            elif key == ord(' ') and texto_completo:  # ESPACIO
                print("\n" + "="*50)
                print("📄 TEXTO COMPLETO DEL PDF417:")
                print("="*50)
                print(texto_completo)
                print("="*50)
        
        # Liberar recursos
        self.cap.release()
        cv2.destroyAllWindows()


def escanear_imagen(imagen_path):
    """
    Función para escanear una imagen guardada
    """
    print(f"\n📸 Escaneando imagen: {imagen_path}")
    
    # Cargar imagen
    frame = cv2.imread(imagen_path)
    if frame is None:
        print("❌ Error: No se pudo cargar la imagen")
        return
    
    # Convertir a grises
    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame
    
    # Buscar PDF417
    resultados = zxingcpp.read_barcodes(gray)
    
    encontrado = False
    for resultado in resultados:
        if resultado.format == zxingcpp.BarcodeFormat.PDF417:
            print("\n✅ PDF417 ENCONTRADO - CÉDULA ANTIGUA")
            print(f"   Formato: {resultado.format}")
            print(f"   Calidad: {resultado.quality}")
            print(f"   Texto completo:")
            print("-" * 40)
            print(resultado.text)
            print("-" * 40)
            
            # Dibujar en la imagen
            if resultado.position:
                pts = np.array([[resultado.position[0].x, resultado.position[0].y],
                               [resultado.position[1].x, resultado.position[1].y],
                               [resultado.position[2].x, resultado.position[2].y],
                               [resultado.position[3].x, resultado.position[3].y]], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
            
            encontrado = True
    
    if not encontrado:
        print("❌ No se encontró código PDF417 en la imagen")
    
    # Mostrar imagen con el código marcado
    if encontrado:
        cv2.imshow('PDF417 Detectado', frame)
        print("\nPresione cualquier tecla para cerrar la imagen...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Escáner básico de PDF417 para cédulas antiguas')
    parser.add_argument('--imagen', type=str, help='Ruta de imagen para escanear (opcional)')
    parser.add_argument('--camara', type=int, default=0, help='ID de cámara (default: 0)')
    
    args = parser.parse_args()
    
    print("="*50)
    print("📟 SCANNER PDF417 - CÉDULAS ANTIGUAS")
    print("="*50)
    
    if args.imagen:
        # Modo imagen
        escanear_imagen(args.imagen)
    else:
        # Modo cámara en vivo
        scanner = ScannerPDF417Basico(camara_id=args.camara)
        scanner.ejecutar()


if __name__ == "__main__":
    main()
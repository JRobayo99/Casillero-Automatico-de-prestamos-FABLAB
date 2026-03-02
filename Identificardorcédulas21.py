#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# identificador_tipo_cedula.py

import cv2
import sys
import zxingcpp  # Para detectar PDF417 (cédula antigua)
import pytesseract  # Para detectar MRZ (cédula nueva)


class IdentificadorTipoCedula:
    """
    Clase que solo identifica si una cédula es antigua o nueva
    basándose en la imagen del reverso
    """
    
    def __init__(self, debug=True):
        self.debug = debug
        self.tipo_detectado = None
        self.metodo_deteccion = None
    
    def preprocesar_imagen(self, image_path):
        """Carga y prepara la imagen para el análisis"""
        # Cargar imagen
        image = cv2.imread(image_path)
        if image is None:
            print(f"ERROR: No se pudo cargar la imagen: {image_path}")
            return None
        
        # Redimensionar si es muy grande para mejor rendimiento
        height, width = image.shape[:2]
        if width > 1200:
            scale = 1200 / width
            new_width = 1200
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
            if self.debug:
                print(f"Imagen redimensionada: {width}x{height} -> {new_width}x{new_height}")
        
        return image
    
    def detectar_pdf417(self, image):
        """
        Detecta si la imagen contiene un código PDF417 (cédula antigua)
        usando zxing-cpp
        """
        try:
            # Convertir a escala de grises para mejor detección
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Usar zxing-cpp para leer códigos de barras
            resultados = zxingcpp.read_barcodes(gray)
            
            for resultado in resultados:
                # Verificar si es PDF417
                if resultado.format == zxingcpp.BarcodeFormat.PDF417:
                    if self.debug:
                        print(f"  ✓ PDF417 detectado con calidad: {resultado.quality}")
                    return True
            
        except Exception as e:
            if self.debug:
                print(f"  Error en detección PDF417: {e}")
        
        return False
    
    def detectar_mrz(self, image):
        """
        Detecta si la imagen contiene una banda MRZ (cédula nueva)
        usando Tesseract OCR para buscar el patrón '<<'
        """
        try:
            # Configuración específica para MRZ
            config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'
            
            # Convertir a escala de grises
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Mejorar contraste
            gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
            
            # Realizar OCR
            ocr_result = pytesseract.image_to_string(gray, config=config, lang='spa')
            
            # Buscar el patrón característico de MRZ
            lines = ocr_result.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                # La MRZ tiene muchas '<' y longitud considerable
                if len(line) > 20 and line.count('<') > 5:
                    if self.debug:
                        print(f"  ✓ Patrón MRZ encontrado: {line[:30]}...")
                    return True
            
        except Exception as e:
            if self.debug:
                print(f"  Error en detección MRZ: {e}")
        
        return False
    
    def identificar(self, image_path):
        """
        Método principal: identifica el tipo de cédula
        Retorna: 'ANTIGUA', 'NUEVA' o None si no se pudo identificar
        """
        print(f"\n{'='*60}")
        print(f"🔍 IDENTIFICADOR DE TIPO DE CÉDULA BOLIVIANA")
        print(f"📸 Imagen: {image_path}")
        print('='*60)
        
        # Cargar imagen
        image = self.preprocesar_imagen(image_path)
        if image is None:
            return None
        
        # PASO 1: Buscar PDF417 (cédula antigua)
        print("\n📟 Buscando código PDF417 (zxing-cpp)...")
        if self.detectar_pdf417(image):
            self.tipo_detectado = 'ANTIGUA'
            self.metodo_deteccion = 'PDF417 detectado con zxing-cpp'
            print(f"\n✅ RESULTADO: CÉDULA {self.tipo_detectado}")
            print(f"   Método: {self.metodo_deteccion}")
            return self.tipo_detectado
        
        # PASO 2: Buscar MRZ (cédula nueva)
        print("\n📄 Buscando banda MRZ (Tesseract OCR)...")
        if self.detectar_mrz(image):
            self.tipo_detectado = 'NUEVA'
            self.metodo_deteccion = 'MRZ detectada con Tesseract OCR'
            print(f"\n✅ RESULTADO: CÉDULA {self.tipo_detectado}")
            print(f"   Método: {self.metodo_deteccion}")
            return self.tipo_detectado
        
        # No se pudo identificar
        print("\n❌ NO SE PUDO IDENTIFICAR EL TIPO DE CÉDULA")
        print("   Posibles causas:")
        print("   - La imagen no es del reverso de la cédula")
        print("   - La imagen tiene mala calidad o baja resolución")
        print("   - El código PDF417 o la banda MRZ no son visibles")
        
        self.tipo_detectado = None
        return None


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("\nUso: python3 identificador_tipo_cedula.py <ruta_imagen>")
        print("Ejemplo: python3 identificador_tipo_cedula.py reverso_cedula.jpg\n")
        print("Este script solo identifica si la cédula es ANTIGUA o NUEVA")
        print("basándose en la detección de PDF417 (zxing-cpp) o MRZ (Tesseract).\n")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Crear identificador
    identificador = IdentificadorTipoCedula(debug=True)
    
    # Identificar tipo de cédula
    tipo = identificador.identificar(image_path)
    
    # Mostrar resultado simple
    if tipo:
        print("\n" + "="*60)
        print(f"🎯 TIPO DE CÉDULA: {tipo}")
        print(f"   Método: {identificador.metodo_deteccion}")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("❌ NO SE PUDO DETERMINAR EL TIPO DE CÉDULA")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
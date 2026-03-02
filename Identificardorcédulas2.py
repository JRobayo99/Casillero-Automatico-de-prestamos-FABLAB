#!/usr/bin/env python3
# test_rapido.py - Versión mínima para probar la identificación

import cv2
import sys
import zxingcpp
import pytesseract

def es_cedula_antigua(image_path):
    """Retorna True si es cédula antigua (PDF417 detectado)"""
    image = cv2.imread(image_path)
    if image is None:
        return False
    
    # Convertir a grises
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Buscar PDF417
    resultados = zxingcpp.read_barcodes(gray)
    for r in resultados:
        if r.format == zxingcpp.BarcodeFormat.PDF417:
            return True
    return False

def es_cedula_nueva(image_path):
    """Retorna True si es cédula nueva (MRZ con << detectada)"""
    image = cv2.imread(image_path)
    if image is None:
        return False
    
    # Convertir a grises
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Configuración rápida para MRZ
    config = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'
    texto = pytesseract.image_to_string(gray, config=config)
    
    # Buscar patrón MRZ
    return '<<' in texto and texto.count('<') > 10

def identificar_tipo(image_path):
    """Identifica el tipo de cédula"""
    print(f"\nAnalizando: {image_path}")
    
    if es_cedula_antigua(image_path):
        print("✅ CÉDULA ANTIGUA (PDF417 detectado)")
        return "ANTIGUA"
    
    if es_cedula_nueva(image_path):
        print("✅ CÉDULA NUEVA (MRZ detectada)")
        return "NUEVA"
    
    print("❌ Tipo desconocido")
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 test_rapido.py <imagen>")
        sys.exit(1)
    
    tipo = identificar_tipo(sys.argv[1])
    sys.exit(0 if tipo else 1)
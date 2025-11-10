import cv2
import pytesseract
import re
import pandas as pd
import os
import numpy as np
from datetime import datetime

# -------------------------------
# Configuración de Tesseract
# -------------------------------
# Cambia la ruta según tu sistema:
# Windows example:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Linux example (normalmente ya está en PATH, si no, p.e.):
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
# Si está en PATH no hace falta asignarlo.
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

# -------------------------------
# Funciones de procesamiento
# -------------------------------
def preprocess_for_ocr(img):
    """Preprocesado para mejorar OCR: escala, gris, filtro, umbral adaptativo."""
    # redimensionar para mejorar la lectura (opcional)
    h, w = img.shape[:2]
    scale = 1.5
    img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_LINEAR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # eliminar ruido
    blur = cv2.bilateralFilter(gray, 9, 75, 75)
    # mejorar contraste (opcional)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    # gray = clahe.apply(blur)
    # umbral adaptativo
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 51, 9)
    return thresh

def ocr_image(img):
    """Ejecuta pytesseract sobre imagen preprocesada y retorna texto."""
    # Puedes probar distintos config: psm 6 (block), psm 1 (auto), oem 3
    config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZÑabcdefghijklmnopqrstuvwxyz.- '
    text = pytesseract.image_to_string(img, config=config, lang='spa')
    return text

def extract_fields(text):
    """Extrae número de documento y nombre del texto OCR usando heurísticas."""
    # Normalizar lineas
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    joined = " ".join(lines)

    # 1) Buscar número de documento (acepta con/ sin puntos, entre 6 y 11 dígitos total)
    # ejemplos: 1.234.567, 12.345.678, 1234567
    id_patterns = [
        r'\b\d{6,11}\b',                                # solo dígitos (6-11)
        r'\b\d{1,3}(?:\.\d{3}){1,3}\b'                  # con puntos: 1.234.567
    ]
    id_num = None
    for pat in id_patterns:
        m = re.search(pat, joined)
        if m:
            id_num = m.group(0)
            # limpiar puntos
            id_num = id_num.replace('.', '')
            break

    # 2) Buscar nombre: intenta etiquetas comunes primero
    name = None
    name_patterns = [
        r'(?:NOMBRE[S]?:?\s*([A-ZÁÉÍÓÚÑ\s]+))',   # NOMBRE(S): <NOMBRES>
        r'(?:NOMBRES Y APELLIDOS:?\s*([A-ZÁÉÍÓÚÑ\s]+))',
        r'(?:APELLIDOS:?\s*([A-ZÁÉÍÓÚÑ\s]+))',
    ]
    # Buscar en texto en mayúsculas para mayor robustez
    upper_text = "\n".join(lines).upper()
    for pat in name_patterns:
        m = re.search(pat, upper_text)
        if m:
            name = m.group(1).strip()
            # limpiar múltiples espacios
            name = re.sub(r'\s{2,}', ' ', name)
            break

    # fallback: si no hay etiqueta, tomar la línea en mayúsculas más larga (heurística)
    if not name:
        uppercase_lines = [ln for ln in lines if ln.upper() == ln and len(ln) > 4]
        if uppercase_lines:
            # elegir la línea más larga
            name = max(uppercase_lines, key=len)
            name = re.sub(r'[^A-ZÁÉÍÓÚÑ\s]', '', name).strip()

    # otra heurística: si aparece 'COLOMBIA' o 'IDENTIFICACION' podemos buscar lineas cercanas
    if (not name or not id_num) and 'COLOMBIA' in upper_text:
        # buscar ventana de líneas cerca de la palabra COLOMBIA
        for i, ln in enumerate(lines):
            if 'COLOMBIA' in ln.upper():
                # mirar las siguientes 4 líneas en búsqueda de nombre/id
                window = " ".join(lines[i:i+6]).upper()
                if not id_num:
                    m = re.search(r'\b\d{6,11}\b', window)
                    if m:
                        id_num = m.group(0).replace('.', '')
                if not name:
                    # intentar extraer usando mayúsculas
                    candidates = re.findall(r'[A-ZÁÉÍÓÚÑ\s]{6,}', window)
                    if candidates:
                        name = candidates[0].strip()
                break

    # limpieza final
    if name:
        name = re.sub(r'\s{2,}', ' ', name).strip()
    if id_num:
        id_num = id_num.strip()

    return {'name': name, 'id': id_num, 'raw': text}

def append_to_excel(row: dict, filename='identificaciones.xlsx'):
    """Añade fila al excel. Si no existe, lo crea."""
    df_row = pd.DataFrame([{
        'timestamp': datetime.now().isoformat(sep=' ', timespec='seconds'),
        'name': row.get('name', None),
        'id': row.get('id', None),
        'raw_text': row.get('raw', None)
    }])
    if os.path.exists(filename):
        # leer existente y concatenar
        try:
            existing = pd.read_excel(filename, engine='openpyxl')
            out = pd.concat([existing, df_row], ignore_index=True)
            out.to_excel(filename, index=False, engine='openpyxl')
        except Exception as e:
            # si hay error leyendo, sobreescribir con nuevo archivo
            print("Warning: no se pudo leer Excel existente, se creará uno nuevo. Error:", e)
            df_row.to_excel(filename, index=False, engine='openpyxl')
    else:
        df_row.to_excel(filename, index=False, engine='openpyxl')
    print(f"Guardado en {filename} -> nombre: {row.get('name')}, id: {row.get('id')}")

# -------------------------------
# Captura con cámara y flujo
# -------------------------------
def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    cuadro = 100  # margen del rectángulo

    doc_identificado = False

    print("Presiona 's' para capturar cuando el documento esté dentro del rectángulo.")
    print("Presiona ESC para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer cámara")
            break

        h, w = frame.shape[:2]
        cv2.rectangle(frame, (cuadro, cuadro), (w - cuadro, h - cuadro), (0, 255, 0), 2)
        if not doc_identificado:
            cv2.putText(frame, 'Ubique el documento en el recuadro - Presiona S para identificar',
                        (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        else:
            cv2.putText(frame, 'Documento detectado - Presiona S para capturar y extraer',
                        (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        cv2.imshow('ID INTELIGENTE', frame)
        key = cv2.waitKey(5) & 0xFF

        if key == 27:  # ESC
            break
        elif key == ord('s') or key == ord('S'):
            # recortar región del rectángulo para ahorrar trabajo al OCR
            roi = frame[cuadro:h-cuadro, cuadro:w-cuadro].copy()
            proc = preprocess_for_ocr(roi)
            text = ocr_image(proc)
            print("----- TEXTO OCR -----")
            print(text)
            fields = extract_fields(text)
            print("----- RESULTADOS -----")
            print(fields)
            # si quieres, muestra la ROI y el umbral
            cv2.imshow('ROI', roi)
            cv2.imshow('Preprocesado', proc)

            # guardar/añadir a excel
            append_to_excel({'name': fields['name'], 'id': fields['id'], 'raw': text})

            # Opcional: marcar doc identificado si en el texto aparece 'COLOMBIA' o 'IDENTIFICACION'
            if re.search(r'COLOMBIA', text, re.I) and re.search(r'IDENTIFIC', text, re.I):
                doc_identificado = True

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

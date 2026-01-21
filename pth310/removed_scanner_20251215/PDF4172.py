import cv2
import zxingcpp
import re

# ===============================
# Función para limpiar y extraer datos de la cédula
# ===============================
def parse_pdf417(text):
    # Quitar caracteres no imprimibles
    clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)

    # Quitar palabras "NUL" que vienen del decodificador
    clean = clean.replace("NUL", " ")

    data = {}

    # ===============================
    # 1. Encontrar las cadenas numéricas de 10 dígitos
    # ===============================
    all_10_digits = re.findall(r'(?<!\d)\d{10}(?!\d)', clean)

    if len(all_10_digits) >= 2:
        cedula = all_10_digits[1]
        data["cedula"] = cedula
    else:
        data["cedula"] = None
        cedula = None

    # ===============================
    # 2. Sexo + fecha
    # ===============================
    m = re.search(r'([MF])(\d{8})', clean)
    if m:
        data["sexo"] = m.group(1)
        data["fecha_nac"] = m.group(2)
        

        

    # ===============================
    # 3. RH
    # ===============================
    m = re.search(r'(A|B|O)[+-]', clean)
    if m:
        data["rh"] = m.group(0)

    # ===============================
    # 4. Apellidos y nombre SIN “NUL”
    # ===============================
    if cedula:
        pos = clean.find(cedula)
        tail = clean[pos + len(cedula):]

        # Grupos reales de letras (mínimo 2 letras)
        grupos = re.findall(r'\b[A-ZÑÁÉÍÓÚ]{2,}\b', tail)

        # Evitar basura
        grupos = [g for g in grupos if g not in ["N", "NU", "NUL"]]

        if len(grupos) >= 1:
            data["apellido1"] = grupos[0]
        if len(grupos) >= 2:
            data["apellido2"] = grupos[1]
        if len(grupos) >= 3:
            data["nombre"] = grupos[2]
        
    
           

    return clean, data



if __name__ == '__main__':
    # Demo / herramienta de prueba que abre la cámara y permite capturar
    # una región para decodificar PDF417. Esto ahora **no** se ejecuta
    # al importar el módulo, evitando que la cámara se abra en inicio del programa.
    try:
        cap = cv2.VideoCapture(2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        print("Resolución real:", cap.get(3), "x", cap.get(4))

        # Recuadro por defecto
        x1, y1 = 500, 150
        x2, y2 = 1700, 800

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow("Captura", frame)

            key = cv2.waitKey(1)

            if key == ord("s"):
                cropped = frame[y1:y2, x1:x2]
                cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)

                try:
                    results = zxingcpp.read_barcodes(cropped_rgb)
                except Exception as e:
                    print('zxingcpp error:', e)
                    results = []

                if len(results) == 0:
                    print("No se encontró ningún código PDF417 dentro del recuadro.")
                else:
                    print("\n===== CÓDIGOS DETECTADOS =====")
                    for r in results:
                        print(f"Formato: {r.format}")
                        clean, extracted = parse_pdf417(r.text)
                        print("\n--- Texto limpio ---")
                        print(clean)
                        print("\n--- Datos extraídos ---")
                        for key, val in extracted.items():
                            print(f"{key}: {val}")
                        print("\n")

            if key == 27:  # ESC
                break

    finally:
        try:
            cap.release()
        except Exception:
            pass
        cv2.destroyAllWindows()

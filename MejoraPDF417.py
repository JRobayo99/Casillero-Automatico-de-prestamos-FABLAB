def escanear_pdf417():
    global cap, running

    if not ZXING_AVAILABLE:
        txt_log.insert(END, "zxingcpp no está instalado. Instalar con: pip install zxing-cpp\n")
        return
    if not running or cap is None:
        txt_log.insert(END, "La cámara no está encendida\n")
        return

    ret, frame = cap.read()
    if not ret:
        txt_log.insert(END, "Error al leer frame\n")
        return

    # Recorte del ROI
    cropped = frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2]

    # --------------------------
    # 1) CONVERSIÓN A GRIS
    # --------------------------
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    # --------------------------
    # 2) AUMENTAR CONTRASTE (CLAHE)
    # --------------------------
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # --------------------------
    # 3) SUAVIZADO
    # --------------------------
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # Conjuntos de imágenes a probar
    variantes = [
        ("original", cropped),
        ("gray_enhanced", enhanced),
        ("scaled x2", cv2.resize(enhanced, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)),
        ("threshold", cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 21, 5
        ))
    ]

    angles = [
        ("0°", None),
        ("90°", cv2.ROTATE_90_CLOCKWISE),
        ("180°", cv2.ROTATE_180),
        ("270°", cv2.ROTATE_90_COUNTERCLOCKWISE)
    ]

    txt_log.insert(END, "Iniciando escaneo mejorado…\n")

    final_result = None
    final_variant = ""
    final_angle = ""

    # Recorremos todas las variantes + todas las rotaciones
    for var_label, var_img in variantes:

        # Convertir imagen a color para ZXing si hace falta
        if len(var_img.shape) == 2:  # imagen gris
            img_color = cv2.cvtColor(var_img, cv2.COLOR_GRAY2RGB)
        else:
            img_color = cv2.cvtColor(var_img, cv2.COLOR_BGR2RGB)

        for ang_label, ang in angles:
            txt_log.insert(END, f" → Probando {var_label} | Rotación {ang_label}\n")

            if ang is not None:
                rotated = cv2.rotate(img_color, ang)
            else:
                rotated = img_color

            results = zxingcpp.read_barcodes(rotated)

            if results:
                final_result = results[0]
                final_variant = var_label
                final_angle = ang_label
                break

        if final_result:
            break

    # ---------------------------------
    # RESULTADO FINAL
    # ---------------------------------
    if not final_result:
        txt_log.insert(END, "❌ No se pudo detectar PDF417 después de todas las mejoras.\n")
        return

    txt_log.insert(END, f"\n✔ PDF417 detectado usando variante '{final_variant}' con rotación {final_angle}\n")
    txt_log.insert(END, f"Formato: {final_result.format}\n")

    clean, extracted = parse_pdf417(final_result.text)

    txt_log.insert(END, "----- Texto limpio -----\n")
    txt_log.insert(END, clean + "\n")

    txt_log.insert(END, "----- Datos extraídos -----\n")
    for key, val in extracted.items():
        txt_log.insert(END, f"{key}: {val}\n")

    txt_log.insert(END, "\n")

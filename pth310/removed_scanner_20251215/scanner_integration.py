import threading
import time
import os
import cv2
import zxingcpp
import numpy as np
from zxing_utils import enhanced_read_barcodes
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# utils from PDF4172 adapted
import re

def limpiar(texto):
    texto = ''.join(c for c in texto if 32 <= ord(c) <= 126)
    return texto

def extraer_datos_pdf417(raw):
    txt = limpiar(raw)
    m = re.search(r"(\d{10})", txt)
    if not m:
        return None
    inicio = m.start()
    bloque = txt[inicio:]
    cedula = bloque[0:10]

    resto = bloque[10:]
    campos = [c for c in resto.split('<') if c.strip()]

    if len(campos) >= 3:
        ap1 = campos[0].strip()
        ap2 = campos[1].strip() if len(campos) > 1 else ''
        nom = campos[2].strip() if len(campos) > 2 else ''
        resto_tras = ''.join(campos[3:]) if len(campos) > 3 else ''
        sexo = resto_tras[0] if len(resto_tras) > 0 else ''
        fecha = resto_tras[1:9] if len(resto_tras) >= 9 else ''
        rh = resto_tras[9:12].replace('<', '').strip() if len(resto_tras) >= 12 else ''
    else:
        ap1 = resto[0:15].strip()
        ap2 = resto[15:30].strip() if len(resto) >= 30 else ''
        nom = resto[30:45].strip() if len(resto) >= 45 else ''
        sexo = resto[45] if len(resto) > 45 else ''
        fecha = resto[46:54] if len(resto) >= 54 else ''
        rh = resto[54:57].replace('<', '').strip() if len(resto) >= 57 else ''

    return {
        "cedula": cedula,
        "apellido1": ap1,
        "apellido2": ap2,
        "nombre": nom,
        "sexo": sexo,
        "fecha_nac": fecha,
        "rh": rh,
        "raw": txt
    }

class Scanner:
    def __init__(self, parent_frame, camera_index=2, roi=None):
        self.parent = parent_frame
        self.cam_index = camera_index
        # roi can be None to compute dynamically per-frame (recommended)
        self.roi = roi
        # detection confirmation parameters
        self._recent = {}  # text -> {'count': int, 'last': ts}
        self.confirm_count = 2
        self.confirm_window = 2.0  # seconds within which confirmations must occur
        self.debug = False
        self.running = False
        self.thread = None
        self.cap = None
        self.canvas = None
        self._frame_widget = None
        self._controls = None
        self.on_detect = None

    def start(self, on_detect=None, on_stop=None):
        if self.running:
            return
        self.on_detect = on_detect
        self.on_stop = on_stop
        # create UI
        self._frame_widget = tk.Frame(self.parent, bg='black')
        self._frame_widget.place(relwidth=1, relheight=1)
        self.canvas = tk.Canvas(self._frame_widget, bg='black')
        self.canvas.pack(fill='both', expand=True)
        ctrl = tk.Frame(self._frame_widget, bg='white')
        ctrl.place(relx=0.5, rely=0.9, anchor='s')
        tk.Button(ctrl, text='Capturar', command=self._capture).pack(side='left', padx=6)
        # status label
        self.status_label = tk.Label(ctrl, text='', bg='white')
        self.status_label.pack(side='left', padx=8)
        def _back():
            self.stop()
            if hasattr(self, 'on_stop') and self.on_stop:
                try:
                    self.on_stop()
                except Exception:
                    pass
        tk.Button(ctrl, text='Volver', command=_back).pack(side='left', padx=6)
        self._controls = ctrl
        # start camera thread
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        time.sleep(0.05)
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
        if self._frame_widget:
            self._frame_widget.destroy()
        self.cap = None
        self.thread = None

    def _run_loop(self):
        try:
            self.cap = cv2.VideoCapture(self.cam_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                h,w = frame.shape[:2]
                # compute dynamic ROI centered (85% width x 45% height)
                if self.roi is None:
                    box_w = int(w * 0.85)
                    box_h = int(h * 0.45)
                    x1c = (w - box_w) // 2
                    y1c = (h - box_h) // 2
                    x2c = x1c + box_w
                    y2c = y1c + box_h
                else:
                    x1,y1,x2,y2 = self.roi
                    # clamp roi to size
                    x1c = max(0, min(w, x1))
                    x2c = max(0, min(w, x2))
                    y1c = max(0, min(h, y1))
                    y2c = max(0, min(h, y2))
                # draw rect (más grueso para mejor visibilidad) y texto de instrucción
                thickness = max(2, int(min(w,h) * 0.006))
                cv2.rectangle(frame, (x1c,y1c), (x2c,y2c), (0,255,0), thickness)
                cv2.putText(frame, 'Coloca la cédula dentro del recuadro y pulsa Capturar', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)
                # convert BGR->RGB
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im_pil = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(im_pil)
                # avoid garbage collection
                self.canvas.imgtk = imgtk
                self.canvas.create_image(0,0, anchor='nw', image=imgtk)
                time.sleep(0.03)
        except Exception as e:
            print('Scanner loop error:', e)
        finally:
            if self.cap:
                try:
                    self.cap.release()
                except Exception:
                    pass

    def _capture(self):
        # grab one frame and run barcode detection
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showwarning('Cámara', 'No se pudo leer cámara')
            return
        h,w = frame.shape[:2]
        if self.roi is None:
            box_w = int(w * 0.85)
            box_h = int(h * 0.45)
            x1c = (w - box_w) // 2
            y1c = (h - box_h) // 2
            x2c = x1c + box_w
            y2c = y1c + box_h
        else:
            x1,y1,x2,y2 = self.roi
            x1c = max(0, min(w, x1))
            x2c = max(0, min(w, x2))
            y1c = max(0, min(h, y1))
            y2c = max(0, min(h, y2))
        cropped = frame[y1c:y2c, x1c:x2c]

        # Use enhanced zxing reader (scales, rotations, preprocessors)
        try:
            # Prefer PDF417 format and enable debug image logging when requested
            results_with_meta = enhanced_read_barcodes(cropped, debug=self.debug, formats=[zxingcpp.PDF417])
        except Exception as e:
            print('enhanced_read_barcodes error (ignored):', e)
            results_with_meta = []

        results = [r for (r, meta) in results_with_meta] if results_with_meta else []

        try:
            if self._controls and hasattr(self, 'status_label'):
                self.status_label.config(text='Detectando...')
                self._frame_widget.update_idletasks()
        except Exception:
            pass

        try:
            if self._controls and hasattr(self, 'status_label'):
                self.status_label.config(text='')
        except Exception:
            pass

        if len(results) == 0:
            # Save failed capture for debugging if debug mode is active
            if self.debug:
                try:
                    os.makedirs('/tmp/pdf417_debug', exist_ok=True)
                    fname = os.path.join('/tmp/pdf417_debug', f'failed_{int(time.time()*1000)}.jpg')
                    cv2.imwrite(fname, cropped)
                except Exception:
                    pass
            messagebox.showinfo('Escaneo', 'No se detectó código PDF417 en la captura')
            return

        r = results[0]
        payload = r.text if hasattr(r, 'text') else str(r)

        # Temporal confirmation: require same payload seen confirm_count times within window
        ts = time.time()
        rec = self._recent.get(payload)
        if rec:
            if ts - rec['last'] <= self.confirm_window:
                rec['count'] += 1
            else:
                rec['count'] = 1
            rec['last'] = ts
        else:
            self._recent[payload] = {'count': 1, 'last': ts}

        if self._recent[payload]['count'] < self.confirm_count:
            # notify user that a candidate was seen but needs confirmation
                # show short status instead of modal popup to avoid too many dialogs
                try:
                    self.status_label.config(text='Código detectado: necesita confirmación')
                    self._frame_widget.update_idletasks()
                except Exception:
                    pass
            return

        # confirmed
        data = extraer_datos_pdf417(payload) if extraer_datos_pdf417 else None
        if data is None:
            messagebox.showinfo('Escaneo', 'No se pudieron extraer datos desde el código')
            return

        # reset recent for this payload
        try:
            del self._recent[payload]
        except Exception:
            pass

        if self.on_detect:
            self.on_detect(data, cropped)

# helper for person photo capture
class PhotoCapture:
    def __init__(self, parent_frame, camera_index=0):
        self.parent = parent_frame
        self.cam_index = camera_index
        self.cap = None
        self.running = False
        self.thread = None
        self.frame_widget = None
        self.canvas = None
        self.captured_image = None

    def start(self, on_confirm=None):
        self.on_confirm = on_confirm
        self.frame_widget = tk.Frame(self.parent, bg='black')
        self.frame_widget.place(relwidth=1, relheight=1)
        self.canvas = tk.Canvas(self.frame_widget, bg='black')
        self.canvas.pack(fill='both', expand=True)
        ctrl = tk.Frame(self.frame_widget, bg='white')
        ctrl.place(relx=0.5, rely=0.9, anchor='s')
        tk.Button(ctrl, text='Capturar foto', command=self._capture).pack(side='left', padx=6)
        tk.Button(ctrl, text='Confirmar', command=self._confirm).pack(side='left', padx=6)
        tk.Button(ctrl, text='Volver', command=self.stop).pack(side='left', padx=6)
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        time.sleep(0.05)
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
        if self.frame_widget:
            self.frame_widget.destroy()
        self.cap = None
        self.captured_image = None

    def _loop(self):
        try:
            self.cap = cv2.VideoCapture(self.cam_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im_pil = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(im_pil)
                self.canvas.imgtk = imgtk
                self.canvas.create_image(0,0, anchor='nw', image=imgtk)
                time.sleep(0.03)
        except Exception as e:
            print('Photo loop error:', e)
        finally:
            if self.cap:
                try:
                    self.cap.release()
                except Exception:
                    pass

    def _capture(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showwarning('Cámara', 'No se pudo leer cámara')
            return
        self.captured_image = frame.copy()
        messagebox.showinfo('Foto', 'Foto capturada. Presiona Confirmar para guardar.')

    def _confirm(self):
        if self.captured_image is None:
            messagebox.showwarning('Foto', 'No hay foto capturada')
            return
        # save file
        os.makedirs('fotos', exist_ok=True)
        fname = os.path.join('fotos', f'person_{int(time.time())}.jpg')
        cv2.imwrite(fname, self.captured_image)
        if self.on_confirm:
            self.on_confirm(fname)
        self.stop()

# convenience functions
_scanner_instances = {}

def start_scanner(container, on_detect, camera_index=2, on_stop=None):
    s = Scanner(container, camera_index=camera_index)
    _scanner_instances[container] = s
    s.start(on_detect=on_detect, on_stop=on_stop)
    return s

def stop_scanner(container):
    s = _scanner_instances.get(container)
    if s:
        s.stop()
        del _scanner_instances[container]

def start_photo_capture(container, on_confirm, camera_index=0):
    p = PhotoCapture(container, camera_index=camera_index)
    p.start(on_confirm=on_confirm)
    return p


if __name__ == '__main__':
    print('Prueba scanner_integration')

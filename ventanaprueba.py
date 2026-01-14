import pandas as pd
import db_prestamos_csv
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, filedialog
import db
import PDF417


# Optional libraries for scanner and image preview


ventanai = tk.Tk()

ventanai.title("Casillero de pretamos")
ventanai.geometry("500x300")
ventanai.config(bg="royal blue")

# --- Marco verde (lado izquierdo) ---
# Left green panel
frame1 = tk.Frame(ventanai)
# Left panel: increase size and show clear border area for the ID
frame1.configure(bg="SpringGreen", width=350, height=1080, padx=0, pady=0, bd=2, relief='solid')
# position at top-left
frame1.place(x=0, y=0)

# --- Área de contenido (derecha) ---
content_frame = tk.Frame(ventanai, bg="#eeeeee")
content_frame.place(x=400, y=0, width=1420, height=1080)

# --- Base de datos local para préstamos ---


# (integración de escáner/PDF417 eliminada para volver al estado anterior)

# Helpers para modo escáner (fullscreen y expansión del área de contenido)



# --- Botón redondeado dentro de frame1 ---
# Configurables (modifica estos valores según quieras tamaño/estilo)
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 50
BUTTON_RADIUS = 18
BUTTON_X = 60
BUTTON_Y = 100
BUTTON_TEXT = "Préstamo"

frame_bg = frame1.cget('bg')
btn_fill = "#F58383"  # color interior del botón (ajústalo si quieres)
btn_outline = frame_bg  # contorno igual al color del marco para que no destaque

# Canvas para dibujar el botón (fondo del canvas igual al color del marco)
canvas_btn = tk.Canvas(frame1, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
				   bg=frame_bg, highlightthickness=0)
canvas_btn.place(x=BUTTON_X, y=BUTTON_Y)

def _rounded_rect(canvas, x1, y1, x2, y2, r=10, **kwargs):
	# Dibuja un rectángulo suavizado (aproximación a bordes redondeados)
	points = [x1+r, y1,
			  x2-r, y1,
			  x2, y1,
			  x2, y1+r,
			  x2, y2-r,
			  x2, y2,
			  x2-r, y2,
			  x1+r, y2,
			  x1, y2,
			  x1, y2-r,
			  x1, y1+r,
			  x1, y1]
	return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

# Dibujar el botón
_rounded_rect(canvas_btn, 0, 0, BUTTON_WIDTH, BUTTON_HEIGHT,
			  r=BUTTON_RADIUS, fill=btn_fill, outline=btn_outline)

# Fuente del texto del botón (ajustable)
font_btn = tkfont.Font(family='Helvetica2', size=12, weight='bold')
canvas_btn.create_text(BUTTON_WIDTH/2, BUTTON_HEIGHT/2, text=BUTTON_TEXT,
				   font=font_btn, fill='black')

# Simular comportamiento de botón (evento click)
canvas_btn.bind('<Button-1>', lambda e: open_prestamo(e))

def open_prestamo(event=None):
	# Si el selection_frame ya está visible, lo ocultamos (doble click cierra menú)
	if 'selection_frame' in globals():
		sel = globals()['selection_frame']
		if str(sel.place_info()) != '{}':
			sel.place_forget()
			ventanai.title('Casillero de pretamos')
			return
	# Mostrar la vista de selección DENTRO de la misma ventana (no abrir otra)
	ventanai.title("Selección de objetos (máx. 3)")
	# Limpiar el área de contenido antes de mostrar el selection_frame
	for w in content_frame.winfo_children():
		w.destroy()
	# Crear o limpiar el frame de selección que ocupará la parte derecha
	if 'selection_frame' not in globals():
		globals()['selection_frame'] = tk.Frame(ventanai, bg='white')

	sel = globals()['selection_frame']
	for w in sel.winfo_children():
		w.destroy()

	sel.place(x=400, y=50, width=400, height=400)

	tk.Label(sel, text="Selección de 5 objetos", font=('Helvetica', 12, 'bold'), bg='white').pack(pady=(10, 6))
	tk.Label(sel, text="Selecciona hasta 3 objetos:", font=('Helvetica', 10), bg='white').pack(pady=(0, 6))

	vars_cb = []
	def update_selection():
		sel_count = sum(v.get() for v in vars_cb)
		if sel_count > 3:
			messagebox.showwarning("Límite", "¡Puedes seleccionar como mínimo 1 objeto y máximo 3 objetos!")
			for v in reversed(vars_cb):
				if v.get() == 1:
					v.set(0)
					break

	objetos = [
		"Multímetro",
		"Cautín",
		"Fuente de poder",
		"Destornillador",
		"Taladro",
		"Multitool"
	]

	varbs_cb = []

	for nombre in objetos:
		v = tk.IntVar()
		cb = tk.Checkbutton(sel, text=nombre, variable=v, command=update_selection, bg='white')
		cb.pack(anchor='w', padx=20)
		vars_cb.append(v)

	btn_frame = tk.Frame(sel, bg='white')
	btn_frame.pack(pady=12)

	def escanear_documento():
		# Llama al escáner y obtiene los datos
		try:
			data = PDF417.scan_pdf417()
		except Exception as e:
			messagebox.showerror('Error', f'Error al escanear: {e}')
			return
		if not data or not data.get('Cédula'):
			messagebox.showwarning('Aviso', 'No se detectó un código PDF417 válido.')
			return
		# Validar que al menos un objeto esté seleccionado
		seleccion = []
		if 'vars_cb' in locals():
			seleccion = [f"Objeto {i+1}" for i, v in enumerate(vars_cb) if v.get() == 1]
		elif 'vars_cb' in globals():
			seleccion = [f"Objeto {i+1}" for i, v in enumerate(globals()['vars_cb']) if v.get() == 1]
		if not seleccion:
			messagebox.showwarning("Aviso", "Mínimo una herramienta")
			return
		# Cerrar la lista de selección de herramientas si está visible
		if 'selection_frame' in globals():
			sel = globals()['selection_frame']
			sel.place_forget()
		# Mostrar resumen en el content_frame
		for w in content_frame.winfo_children():
			w.destroy()
		tk.Label(content_frame, text='Datos detectados', font=('Helvetica', 12, 'bold'), bg='#eeeeee').pack(pady=(8,4))
		for k, v in data.items():
			tk.Label(content_frame, text=f'{k}: {v}', bg='#eeeeee').pack(pady=2, anchor='w', padx=8)
		btns = tk.Frame(content_frame, bg='#eeeeee')
		btns.place(x=8, y=20)


		def volver_selección():
			for w in content_frame.winfo_children():
				w.destroy()
			sel.place(x=400, y=50, width=400, height=400)
			ventanai.title("Selección de objetos (máx. 3)")

		def cancelar_prestamo():
			for w in content_frame.winfo_children():
				w.destroy()
			sel.place_forget()
			ventanai.title('Casillero de pretamos')
			
		tk.Button(btn_frame, text='Cancelar préstamo', command=cancelar_prestamo).pack(side='left', padx=6)
		tk.Button(btn_frame, text='Volver a selección', command=volver_selección).pack(side='left', padx=6)

	def volver_menu():
		sel.place_forget()
		ventanai.title('Casillero de pretamos')

	

	tk.Button(btn_frame, text='Escanear documento', command=escanear_documento).pack(side='left', padx=6)
	tk.Button(btn_frame, text='Volver', command=volver_menu).pack(side='left', padx=6)



BUTTON_WIDTH = 160
BUTTON_HEIGHT = 50
BUTTON_RADIUS = 18
BUTTON_X = 60
BUTTON_Y = 200
BUTTON_TEXT = "Devolución"

frame_bg = frame1.cget('bg')
btn_fill = "#F58383"  # color interior del botón (ajústalo si quieres)
btn_outline = frame_bg  # contorno igual al color del marco para que no destaque

# Canvas para dibujar el botón (fondo del canvas igual al color del marco)
canvas_btn = tk.Canvas(frame1, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
				   bg=frame_bg, highlightthickness=0)
canvas_btn.place(x=BUTTON_X, y=BUTTON_Y)

def _rounded_rect(canvas, x1, y1, x2, y2, r=10, **kwargs):
	# Dibuja un rectángulo suavizado (aproximación a bordes redondeados)
	points = [x1+r, y1,
			  x2-r, y1,
			  x2, y1,
			  x2, y1+r,
			  x2, y2-r,
			  x2, y2,
			  x2-r, y2,
			  x1+r, y2,
			  x1, y2,
			  x1, y2-r,
			  x1, y1+r,
			  x1, y1]
	return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

# Dibujar el botón
_rounded_rect(canvas_btn, 0, 0, BUTTON_WIDTH, BUTTON_HEIGHT,
			  r=BUTTON_RADIUS, fill=btn_fill, outline=btn_outline)

# Fuente del texto del botón (ajustable)
font_btn = tkfont.Font(family='Helvetica', size=12, weight='bold')
canvas_btn.create_text(BUTTON_WIDTH/2, BUTTON_HEIGHT/2, text=BUTTON_TEXT,
				   font=font_btn, fill='black')


# Simular comportamiento de botón (evento click) para devolución
def open_devolucion(event=None):
	# Ocultar selection_frame si está visible
	if 'selection_frame' in globals():
		sel = globals()['selection_frame']
		sel.place_forget()
	# Si el frame de devolución ya está visible, lo ocultamos (doble click cierra menú)
	if hasattr(open_devolucion, 'frame_dev'):
		try:
			if open_devolucion.frame_dev.winfo_exists() and open_devolucion.frame_dev.winfo_ismapped():
				open_devolucion.frame_dev.pack_forget()
				for w in content_frame.winfo_children():
					w.destroy()
				ventanai.title('Casillero de pretamos')
				del open_devolucion.frame_dev
				return
		except tk.TclError:
			del open_devolucion.frame_dev
	# Limpiar el área de contenido y mostrar los botones requeridos
	for w in content_frame.winfo_children():
		w.destroy()
	frame_dev = tk.Frame(content_frame, bg='#eeeeee')
	frame_dev.pack(expand=True, fill='both')
	open_devolucion.frame_dev = frame_dev
	label_info = tk.Label(frame_dev, text="Para devolver debes escanear el documento", font=('Helvetica', 14, 'bold'), fg='red', bg='#eeeeee')
	label_info.place(x=80, y=100)
	btns = tk.Frame(frame_dev, bg='#eeeeee')
	btns.place(x=80, y=300)
	def escanear_documento_devolucion():
		try:
			data = PDF417.scan_pdf417()
		except Exception as e:
			messagebox.showerror('Error', f'Error al escanear: {e}')
			return
		if not data or not data.get('cedula'):
			messagebox.showwarning('Aviso', 'No se detectó un código PDF417 válido.')
			return
		for w in content_frame.winfo_children():
			w.destroy()
		tk.Label(content_frame, text='Datos detectados', font=('Helvetica', 12, 'bold'), bg='#eeeeee').pack(pady=(8,4))
		for k, v in data.items():
			tk.Label(content_frame, text=f'{k}: {v}', bg='#eeeeee').pack(pady=2, anchor='w', padx=8)
		btns = tk.Frame(content_frame, bg='#eeeeee')
		btns.pack(pady=8)
		def on_confirm():
			# Aquí puedes llamar a la función de devolución en la base de datos
			messagebox.showinfo('Devolución', f'Devolución registrada para {data.get("nombre", "")} ({data.get("cedula", "")})')
			for w in content_frame.winfo_children():
				w.destroy()
			ventanai.title('Casillero de pretamos')
		tk.Button(btns, text='Confirmar devolución', command=on_confirm).pack(side='left', padx=6)
		tk.Button(btns, text='Cancelar', command=lambda: [c.destroy() for c in content_frame.winfo_children()]).pack(side='left', padx=6)

	tk.Button(btns, text='Escanear documento', font=('Helvetica', 12, 'bold'), command=escanear_documento_devolucion).pack(side='left', padx=10)
	def volver_menu():
		for w in content_frame.winfo_children():
			w.destroy()
		ventanai.title('Casillero de pretamos')
	tk.Button(btns, text='Volver', font=('Helvetica', 12), command=volver_menu).pack(side='left', padx=10)

canvas_btn.bind('<Button-1>', open_devolucion)
canvas_btn.config(cursor='hand2')

# --- Botón redondeado dentro de frame1 ---
# Configurables (modifica estos valores según quieras tamaño/estilo)
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 50
BUTTON_RADIUS = 18
BUTTON_X = 60
BUTTON_Y = 300
BUTTON_TEXT = "Acceso por PIN"

frame_bg = frame1.cget('bg')
btn_fill = "#F58383"  # color interior del botón (ajústalo si quieres)
btn_outline = frame_bg  # contorno igual al color del marco para que no destaque

# Canvas para dibujar el botón (fondo del canvas igual al color del marco)
canvas_btn = tk.Canvas(frame1, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
				   bg=frame_bg, highlightthickness=0)
canvas_btn.place(x=BUTTON_X, y=BUTTON_Y)

def _rounded_rect(canvas, x1, y1, x2, y2, r=10, **kwargs):
	# Dibuja un rectángulo suavizado (aproximación a bordes redondeados)
	points = [x1+r, y1,
			  x2-r, y1,
			  x2, y1,
			  x2, y1+r,
			  x2, y2-r,
			  x2, y2,
			  x2-r, y2,
			  x1+r, y2,
			  x1, y2,
			  x1, y2-r,
			  x1, y1+r,
			  x1, y1]
	return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

# Dibujar el botón
_rounded_rect(canvas_btn, 0, 0, BUTTON_WIDTH, BUTTON_HEIGHT,
			  r=BUTTON_RADIUS, fill=btn_fill, outline=btn_outline)

# Fuente del texto del botón (ajustable)
font_btn = tkfont.Font(family='Helvetica', size=12, weight='bold')
canvas_btn.create_text(BUTTON_WIDTH/2, BUTTON_HEIGHT/2, text=BUTTON_TEXT,
				   font=font_btn, fill='black')

# Simular comportamiento de botón (evento click)
def on_button_click(event=None):
	print('Botón redondeado pulsado')

canvas_btn.bind('<Button-1>', lambda e: print('Acceso por PIN pulsado'))
canvas_btn.config(cursor='hand2')

# --- Botón redondeado dentro de frame1 ---
# Configurables (modifica estos valores según quieras tamaño/estilo)
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 55
BUTTON_RADIUS = 18
BUTTON_X = 40
BUTTON_Y = 400
BUTTON_TEXT = "Historial de préstamos"

frame_bg = frame1.cget('bg')
btn_fill = "#F58383"  # color interior del botón (ajústalo si quieres)
btn_outline = frame_bg  # contorno igual al color del marco para que no destaque

# Canvas para dibujar el botón (fondo del canvas igual al color del marco)
canvas_btn = tk.Canvas(frame1, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
				   bg=frame_bg, highlightthickness=0)
canvas_btn.place(x=BUTTON_X, y=BUTTON_Y)

def _rounded_rect(canvas, x1, y1, x2, y2, r=10, **kwargs):
	# Dibuja un rectángulo suavizado (aproximación a bordes redondeados)
	points = [x1+r, y1,
			  x2-r, y1,
			  x2, y1,
			  x2, y1+r,
			  x2, y2-r,
			  x2, y2,
			  x2-r, y2,
			  x1+r, y2,
			  x1, y2,
			  x1, y2-r,
			  x1, y1+r,
			  x1, y1]
	return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

# Dibujar el botón
_rounded_rect(canvas_btn, 0, 0, BUTTON_WIDTH, BUTTON_HEIGHT,
			  r=BUTTON_RADIUS, fill=btn_fill, outline=btn_outline)

# Fuente del texto del botón (ajustable)
font_btn = tkfont.Font(family='Helvetica', size=12, weight='bold')
canvas_btn.create_text(BUTTON_WIDTH/2, BUTTON_HEIGHT/2, text=BUTTON_TEXT,
				   font=font_btn, fill='black')

# Simular comportamiento de botón (evento click)
def on_button_click(event=None):
	print('Botón redondeado pulsado')

canvas_btn.bind('<Button-1>', lambda e: print('Historial pulsado'))
canvas_btn.config(cursor='hand2')


# Inicializar base de datos
db.init_db()

# Ajustes de ventana: mantenemos un tamaño mínimo razonable
ventanai.minsize(950,600)
ventanai.resizable(False, False)

ventanai.mainloop()

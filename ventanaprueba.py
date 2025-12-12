import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

ventanai = tk.Tk()

ventanai.title("Casillero de pretamos")
ventanai.geometry("600x400")
ventanai.config(bg="royal blue")

# --- Marco verde (lado izquierdo) ---
# Left green panel
frame1 = tk.Frame(ventanai)
# Keep paddings small so the frame size is controlled by width/height
frame1.configure(bg="SpringGreen", width=300, height=400, padx=0, pady=0)
# position at top-left
frame1.place(x=0, y=0)

# --- Botón redondeado dentro de frame1 ---
# Configurables (modifica estos valores según quieras tamaño/estilo)
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 50
BUTTON_RADIUS = 18
BUTTON_X = 60
BUTTON_Y = 20
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
font_btn = tkfont.Font(family='Helvetica', size=12, weight='bold')
canvas_btn.create_text(BUTTON_WIDTH/2, BUTTON_HEIGHT/2, text=BUTTON_TEXT,
					   font=font_btn, fill='black')

# Simular comportamiento de botón (evento click)
def open_prestamo(event=None):
	# Mostrar la vista de selección DENTRO de la misma ventana (no abrir otra)
	ventanai.title("Selección de 5 objetos")
	# Crear o limpiar el frame de selección que ocupará la parte derecha
	try:
		selection_frame
	except NameError:
		# frame creado por primera vez
		globals()['selection_frame'] = tk.Frame(ventanai, bg='white')

	self = globals()['selection_frame']
	# limpiar contenido anterior
	for w in self.winfo_children():
		w.destroy()

	# colocar en la parte derecha de la ventana
	self.place(x=300, y=0, width=300, height=400)

	tk.Label(self, text="Selección de 5 objetos", font=('Helvetica', 12, 'bold'), bg='white').pack(pady=(10, 6))

	tk.Label(self, text="Selecciona hasta 5 objetos:", font=('Helvetica', 10), bg='white').pack(pady=(0, 6))

	# Checkbuttons para 5 objetos
	vars_cb = []
	def update_selection():
		sel = sum(v.get() for v in vars_cb)
		if sel > 5:
			messagebox.showwarning("Límite", "Sólo puedes seleccionar hasta 5 objetos")
			# deshacer la última selección marcada
			for v in reversed(vars_cb):
				if v.get() == 1:
					v.set(0)
					break

	for i in range(5):
		v = tk.IntVar()
		cb = tk.Checkbutton(self, text=f"Objeto {i+1}", variable=v, command=update_selection, bg='white')
		cb.pack(anchor='w', padx=20)
		vars_cb.append(v)

	btn_frame = tk.Frame(self, bg='white')
	btn_frame.pack(pady=12)

	def aceptar():
		seleccion = [f"Objeto {i+1}" for i, v in enumerate(vars_cb) if v.get() == 1]
		messagebox.showinfo("Seleccionados", f"Has seleccionado: {', '.join(seleccion) if seleccion else 'Nada'}")

	def volver_menu():
		# ocultar la vista de selección y restaurar título
		self.place_forget()
		ventanai.title("Casillero de pretamos")

	tk.Button(btn_frame, text="Aceptar", command=aceptar).pack(side='left', padx=6)
	tk.Button(btn_frame, text="Volver", command=volver_menu).pack(side='left', padx=6)

canvas_btn.bind('<Button-1>', lambda e: open_prestamo(e))
canvas_btn.config(cursor='hand2')

def open_devolucion(event=None):
	# Mostrar la vista de selección DENTRO de la misma ventana (no abrir otra)
	ventanai.title("Selección de 5 objetos")
	# Crear o limpiar el frame de selección que ocupará la parte derecha
	try:
		selection_frame
	except NameError:
		# frame creado por primera vez
		globals()['selection_frame'] = tk.Frame(ventanai, bg='white')

	self2 = globals()['selection_frame']
	# limpiar contenido anterior
	for w in self2.winfo_children():
		w.destroy()

	# colocar en la parte derecha de la ventana
	self2.place(x=300, y=0, width=300, height=400)

	tk.Label(self2, text="Selección de 5 objetos", font=('Helvetica', 12, 'bold'), bg='white').pack(pady=(10, 6))

	tk.Label(self2, text="Selecciona hasta 5 objetos:", font=('Helvetica', 10), bg='white').pack(pady=(0, 6))

	# Checkbuttons para 5 objetos
	vars_cb2 = []
	def update_selection():
		sel2 = sum(v.get() for v2 in vars_cb2)
		if sel2 > 5:
			messagebox.showwarning("Límite", "Sólo puedes seleccionar hasta 5 objetos")
			# deshacer la última selección marcada
			for v2 in reversed(vars_cb2):
				if v2.get() == 1:
					v2.set(0)
					break

	for i in range(5):
		v2 = tk.IntVar()
		cb2 = tk.Checkbutton(self2, text=f"Objeto {i+1}", variable=v, command=update_selection, bg='white')
		cb2.pack(anchor='w', padx=20)
		vars_cb2.append(v2)

	btn_frame2 = tk.Frame(self2, bg='white')
	btn_frame2.pack(pady=12)

	def aceptar():
		seleccion2 = [f"Objeto {i+1}" for i, v in enumerate(vars_cb2) if v.get() == 1]
		messagebox.showinfo("Seleccionados", f"Has seleccionado: {', '.join(seleccion2) if seleccion2 else 'Nada'}")

	def volver_menu():
		# ocultar la vista de selección y restaurar título
		self2.place_forget()
		ventanai.title("Casillero de pretamos")

	tk.Button(btn_frame2, text="Aceptar", command=aceptar).pack(side='left', padx=6)
	tk.Button(btn_frame2, text="Volver", command=volver_menu).pack(side='left', padx=6)

canvas_btn.bind('<Button-2>', lambda e: open_devolucion(e))
canvas_btn.config(cursor='hand2')
# --- Botón redondeado dentro de frame1 ---
# Configurables (modifica estos valores según quieras tamaño/estilo)
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 50
BUTTON_RADIUS = 18
BUTTON_X = 60
BUTTON_Y = 90
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

# Simular comportamiento de botón (evento click)
def on_button_click(event=None):
	print('Botón redondeado pulsado')

def open_devolucion(event=None):
	ventanai.title("Devolución")
	try:
		devol_frame
	except NameError:
		globals()['devol_frame'] = tk.Frame(ventanai, bg='white')

	f = globals()['devol_frame']
	for w in f.winfo_children():
		w.destroy()

	f.place(x=300, y=0, width=300, height=400)

	tk.Label(f, text="Devolución", font=('Helvetica', 12, 'bold'), bg='white').pack(pady=(10, 6))
	tk.Label(f, text="Para devolver: escanea el documento", font=('Helvetica', 10), bg='white').pack(pady=(0, 6))

	# Entrada para texto (editable por el usuario) con texto por defecto
	entry_dev = tk.Entry(f, width=36)
	entry_dev.insert(0, "Para devolver: escanea el documento")
	entry_dev.pack(pady=(0, 8), padx=10)

	def iniciar_escaner():
		# Simula el escaneo (rellena la entrada con texto de ejemplo)
		entry_dev.delete(0, tk.END)
		entry_dev.insert(0, "Documento escaneado: ID123456")
		messagebox.showinfo("Escáner", "Escaneo simulado completado")

	def devolver():
		documento = entry_dev.get().strip()
		if not documento:
			messagebox.showwarning("Aviso", "No hay documento escaneado o texto en la entrada")
			return
		messagebox.showinfo("Devolución", f"Documento devuelto: {documento}")
		entry_dev.delete(0, tk.END)

	btnf = tk.Frame(f, bg='white')
	btnf.pack(pady=10)
	tk.Button(btnf, text="Iniciar escáner", command=iniciar_escaner).pack(side='left', padx=6)
	tk.Button(btnf, text="Devolver", command=devolver).pack(side='left', padx=6)
	tk.Button(btnf, text="Volver", command=lambda: [f.place_forget(), ventanai.title("Casillero de pretamos")]).pack(side='left', padx=6)

canvas_btn.bind('<Button-1>', lambda e: open_devolucion(e))
canvas_btn.config(cursor='hand2')

# --- Botón redondeado dentro de frame1 ---
# Configurables (modifica estos valores según quieras tamaño/estilo)
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 50
BUTTON_RADIUS = 18
BUTTON_X = 60
BUTTON_Y = 160
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
BUTTON_Y = 230
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


# Ajustes de ventana: mantenemos un tamaño mínimo razonable
ventanai.minsize(1850, 1080)
ventanai.resizable(False, False)

ventanai.mainloop()
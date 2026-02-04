import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkinter.simpledialog as simpledialog
from db_pines import BaseDatoPines
from datetime import datetime
import threading
import time

class InterfazPINRFID:
    """Interfaz gráfica para gestionar PINes con lector RFID integrado"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Acceso por PIN RFID")
        self.root.geometry("1000x750")
        self.root.configure(bg="#2c3e50")
        
        # Inicializar base de datos
        self.db = BaseDatoPines("pines.db")
        
        # Variable para el PIN ingresado
        self.pin_ingresado = tk.StringVar()
        
        # Control de lectura RFID
        self.leyendo_rfid = False
        self.reader = None
        self.inicializar_rfid()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar PINes en la lista
        self.actualizar_lista_pines()
        
        # Iniciar thread de lectura RFID
        self.iniciar_lectura_rfid()
    
    def inicializar_rfid(self):
        """Inicializa el lector RFID"""
        try:
            import RPi.GPIO as GPIO
            from mfrc522 import SimpleMFRC522
            
            self.reader = SimpleMFRC522()
            self.rfid_disponible = True
            print("Lector RFID inicializado correctamente")
        except ImportError:
            self.rfid_disponible = False
            print("Librerías RFID no disponibles (modo simulación)")
        except Exception as e:
            self.rfid_disponible = False
            print(f"Error al inicializar RFID: {e}")
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica"""
        
        # Estilo
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('TButton', font=('Helvetica', 10))
        estilo.configure('TLabel', font=('Helvetica', 10), background="#2c3e50", foreground="white")
        estilo.configure('Title.TLabel', font=('Helvetica', 14, 'bold'), background="#2c3e50", foreground="white")
        
        # ============= MARCO DE LECTURA RFID =============
        marco_rfid = ttk.LabelFrame(self.root, text="LECTURA RFID", padding=15)
        marco_rfid.pack(fill="x", padx=10, pady=10)
        
        # Estado del lector
        self.etiqueta_rfid_estado = ttk.Label(marco_rfid, text="🟢 Esperando lectura RFID...", 
                                              foreground="yellow", font=('Helvetica', 12, 'bold'))
        self.etiqueta_rfid_estado.pack(pady=10)
        
        # Info del lector
        info_rfid = "Lector RFID: " + ("✓ Conectado" if self.rfid_disponible else "✗ No disponible (Modo Simulación)")
        ttk.Label(marco_rfid, text=info_rfid, foreground="orange").pack(anchor="w", pady=5)
        
        # Botones de control
        marco_botones_rfid = ttk.Frame(marco_rfid)
        marco_botones_rfid.pack(fill="x", pady=10)
        
        ttk.Button(marco_botones_rfid, text="Detener Lectura", 
                   command=self.detener_lectura_rfid).pack(side="left", padx=5)
        ttk.Button(marco_botones_rfid, text="Reiniciar", 
                   command=self.reiniciar_lectura_rfid).pack(side="left", padx=5)
        
        # ============= MARCO DE VALIDACIÓN MANUAL =============
        marco_validacion = ttk.LabelFrame(self.root, text="VALIDACIÓN MANUAL DE PIN", padding=15)
        marco_validacion.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(marco_validacion, text="Ingresa PIN manualmente:").pack(anchor="w", pady=5)
        
        # Campo de entrada para PIN
        entrada_pin = ttk.Entry(marco_validacion, textvariable=self.pin_ingresado, 
                                show="*", font=('Helvetica', 14), width=30)
        entrada_pin.pack(pady=5)
        entrada_pin.bind('<Return>', lambda e: self.validar_pin_entrada())
        
        # Botones para validación
        marco_botones_validacion = ttk.Frame(marco_validacion)
        marco_botones_validacion.pack(fill="x", pady=10)
        
        ttk.Button(marco_botones_validacion, text="VALIDAR PIN", 
                   command=self.validar_pin_entrada).pack(side="left", padx=5)
        ttk.Button(marco_botones_validacion, text="Limpiar", 
                   command=lambda: self.pin_ingresado.set("")).pack(side="left", padx=5)
        
        # Etiqueta de estado
        self.etiqueta_estado = ttk.Label(marco_validacion, text="Esperando PIN...", 
                                         foreground="yellow")
        self.etiqueta_estado.pack(pady=10)
        
        # ============= MARCO DE REGISTRO DE PIN =============
        marco_registro = ttk.LabelFrame(self.root, text="REGISTRAR NUEVO PIN", padding=15)
        marco_registro.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(marco_registro, text="PIN:").grid(row=0, column=0, sticky="w", pady=5)
        self.entrada_nuevo_pin = ttk.Entry(marco_registro, show="*", width=30)
        self.entrada_nuevo_pin.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(marco_registro, text="Nombre Usuario:").grid(row=1, column=0, sticky="w", pady=5)
        self.entrada_usuario = ttk.Entry(marco_registro, width=30)
        self.entrada_usuario.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Button(marco_registro, text="Registrar PIN", 
                   command=self.registrar_pin).grid(row=2, column=0, columnspan=2, pady=10)
        
        # ============= MARCO DE LISTADO DE PINES =============
        marco_listado = ttk.LabelFrame(self.root, text="PINES REGISTRADOS", padding=10)
        marco_listado.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear tabla con Treeview
        columnas = ("ID", "PIN", "Usuario", "Fecha Creación", "Estado", "Último Uso")
        self.tabla_pines = ttk.Treeview(marco_listado, columns=columnas, height=8)
        self.tabla_pines.column("#0", width=0, stretch="no")
        
        for col in columnas:
            self.tabla_pines.column(col, anchor="center", width=150)
            self.tabla_pines.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(marco_listado, orient="vertical", command=self.tabla_pines.yview)
        self.tabla_pines.configure(yscroll=scrollbar.set)
        
        self.tabla_pines.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones de gestión
        marco_botones_tabla = ttk.Frame(self.root)
        marco_botones_tabla.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(marco_botones_tabla, text="Actualizar Lista", 
                   command=self.actualizar_lista_pines).pack(side="left", padx=5)
        ttk.Button(marco_botones_tabla, text="Eliminar PIN Seleccionado", 
                   command=self.eliminar_pin_seleccionado).pack(side="left", padx=5)
        ttk.Button(marco_botones_tabla, text="Ver Historial", 
                   command=self.mostrar_historial).pack(side="left", padx=5)
    
    def iniciar_lectura_rfid(self):
        """Inicia el thread de lectura RFID"""
        self.leyendo_rfid = True
        thread = threading.Thread(target=self._leer_rfid_continuo, daemon=True)
        thread.start()
    
    def _leer_rfid_continuo(self):
        """Lee continuamente del lector RFID en un thread separado"""
        while self.leyendo_rfid:
            try:
                if self.rfid_disponible and self.reader:
                    # Leer del RFID
                    print("Esperando lectura RFID...")
                    id_rfid, texto = self.reader.read()
                    
                    # Procesar el PIN leído
                    pin_leido = str(id_rfid).strip()
                    print(f"PIN leído del RFID: {pin_leido}")
                    
                    # Actualizar la interfaz con el PIN leído
                    self.root.after(0, self.procesar_pin_rfid, pin_leido)
                else:
                    # Modo simulación: simular lectura cada 5 segundos
                    time.sleep(1)
            except Exception as e:
                print(f"Error al leer RFID: {e}")
                self.root.after(0, self.actualizar_estado_rfid, "Error de lectura", "red")
                time.sleep(2)
    
    def procesar_pin_rfid(self, pin):
        """Procesa el PIN leído del RFID"""
        self.pin_ingresado.set(pin)
        self.actualizar_estado_rfid(f"PIN leído: {pin}", "cyan")
        
        # Validar automáticamente
        self.root.after(500, self.validar_pin_entrada)
    
    def actualizar_estado_rfid(self, mensaje, color):
        """Actualiza el estado visual del lector RFID"""
        self.etiqueta_rfid_estado.config(text=f"🔹 {mensaje}", foreground=color)
    
    def detener_lectura_rfid(self):
        """Detiene la lectura RFID"""
        self.leyendo_rfid = False
        self.actualizar_estado_rfid("Lectura detenida", "orange")
    
    def reiniciar_lectura_rfid(self):
        """Reinicia la lectura RFID"""
        self.leyendo_rfid = False
        time.sleep(1)
        self.iniciar_lectura_rfid()
        self.actualizar_estado_rfid("Esperando lectura RFID...", "yellow")
    
    def validar_pin_entrada(self):
        """Valida el PIN ingresado"""
        pin = self.pin_ingresado.get()
        
        if not pin:
            messagebox.showwarning("Advertencia", "Por favor ingresa un PIN")
            return
        
        valido, datos = self.db.validar_pin(pin)
        
        if valido:
            usuario = datos[1]
            self.etiqueta_estado.config(text=f"✓ PIN VÁLIDO - Usuario: {usuario}", foreground="green")
            messagebox.showinfo("✓ ACCESO CONCEDIDO", f"Bienvenido {usuario}\nAcceso permitido")
            self.pin_ingresado.set("")
            self.actualizar_lista_pines()
        else:
            self.etiqueta_estado.config(text="✗ PIN INVÁLIDO - Acceso denegado", foreground="red")
            messagebox.showerror("✗ ACCESO DENEGADO", "PIN no válido o no registrado.\nAcceso DENEGADO")
            self.pin_ingresado.set("")
    
    def registrar_pin(self):
        """Registra un nuevo PIN"""
        pin = self.entrada_nuevo_pin.get()
        usuario = self.entrada_usuario.get()
        
        if not pin or not usuario:
            messagebox.showwarning("Advertencia", "Por favor completa todos los campos")
            return
        
        if len(pin) < 4:
            messagebox.showwarning("Advertencia", "El PIN debe tener al menos 4 caracteres")
            return
        
        exito, mensaje = self.db.agregar_pin(pin, usuario)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.entrada_nuevo_pin.delete(0, "end")
            self.entrada_usuario.delete(0, "end")
            self.actualizar_lista_pines()
        else:
            messagebox.showerror("Error", mensaje)
    
    def actualizar_lista_pines(self):
        """Actualiza la lista de PINes en la tabla"""
        # Limpiar tabla
        for item in self.tabla_pines.get_children():
            self.tabla_pines.delete(item)
        
        # Obtener datos
        pines = self.db.obtener_todos_pines()
        
        # Insertar datos
        for pin_data in pines:
            id_pin, pin, usuario, fecha_creacion, activo, fecha_ultimo_uso = pin_data
            estado = "✓ Activo" if activo else "✗ Inactivo"
            fecha_uso = fecha_ultimo_uso if fecha_ultimo_uso else "Nunca"
            
            self.tabla_pines.insert("", "end", values=(
                id_pin, "****", usuario, fecha_creacion, estado, fecha_uso
            ))
    
    def eliminar_pin_seleccionado(self):
        """Elimina (desactiva) el PIN seleccionado"""
        seleccion = self.tabla_pines.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un PIN")
            return
        
        item = seleccion[0]
        valores = self.tabla_pines.item(item, "values")
        usuario = valores[2]
        
        confirmar = messagebox.askyesno("Confirmación", 
                                        f"¿Desactivas el PIN de {usuario}?")
        
        if confirmar:
            # Obtener el PIN real de la base de datos
            pines = self.db.obtener_todos_pines()
            id_pin = int(valores[0])
            
            for pin_data in pines:
                if pin_data[0] == id_pin:
                    self.db.eliminar_pin(pin_data[1])
                    messagebox.showinfo("Éxito", "PIN desactivado")
                    self.actualizar_lista_pines()
                    break
    
    def mostrar_historial(self):
        """Muestra el historial de intentos de acceso"""
        historial = self.db.obtener_historial()
        
        # Crear ventana de historial
        ventana_historial = tk.Toplevel(self.root)
        ventana_historial.title("Historial de Acceso")
        ventana_historial.geometry("700x400")
        
        # Crear tabla de historial
        columnas = ("PIN", "Resultado", "Fecha/Hora")
        tabla_historial = ttk.Treeview(ventana_historial, columns=columnas, height=20)
        tabla_historial.column("#0", width=0, stretch="no")
        
        for col in columnas:
            tabla_historial.column(col, anchor="center", width=220)
            tabla_historial.heading(col, text=col)
        
        for registro in historial:
            pin_parcial = registro[0][:2] + "**" if registro[0] else "****"
            # Color según resultado
            resultado_color = "✓ ÉXITO" if registro[1] == "ÉXITO" else "✗ FALLÓ"
            tabla_historial.insert("", "end", values=(
                pin_parcial, resultado_color, registro[2]
            ))
        
        scrollbar = ttk.Scrollbar(ventana_historial, orient="vertical", 
                                 command=tabla_historial.yview)
        tabla_historial.configure(yscroll=scrollbar.set)
        
        tabla_historial.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def cerrar(self):
        """Cierra la aplicación"""
        self.leyendo_rfid = False
        self.db.cerrar()
        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        except:
            pass
        self.root.destroy()

def main():
    root = tk.Tk()
    interfaz = InterfazPINRFID(root)
    root.protocol("WM_DELETE_WINDOW", interfaz.cerrar)
    root.mainloop()

if __name__ == "__main__":
    main()

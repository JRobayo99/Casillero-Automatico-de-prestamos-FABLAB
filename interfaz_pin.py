import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkinter.simpledialog as simpledialog
from db_pines import BaseDatoPines
from datetime import datetime

class InterfazPIN:
    """Interfaz gráfica para gestionar PINes y acceso"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Acceso por PIN")
        self.root.geometry("900x700")
        self.root.configure(bg="#2c3e50")
        
        # Inicializar base de datos
        self.db = BaseDatoPines("pines.db")
        
        # Variable para el PIN ingresado
        self.pin_ingresado = tk.StringVar()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar PINes en la lista
        self.actualizar_lista_pines()
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica"""
        
        # Estilo
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('TButton', font=('Helvetica', 10))
        estilo.configure('TLabel', font=('Helvetica', 10), background="#2c3e50", foreground="white")
        
        # ============= MARCO DE VALIDACIÓN DE PIN =============
        marco_validacion = ttk.LabelFrame(self.root, text="VALIDACIÓN DE PIN", padding=15)
        marco_validacion.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(marco_validacion, text="Ingresa PIN:").pack(anchor="w", pady=5)
        
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
        self.tabla_pines = ttk.Treeview(marco_listado, columns=columnas, height=10)
        self.tabla_pines.column("#0", width=0, stretch="no")
        
        for col in columnas:
            self.tabla_pines.column(col, anchor="center", width=130)
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
            messagebox.showinfo("Éxito", f"Acceso concedido a {usuario}")
            self.pin_ingresado.set("")
        else:
            self.etiqueta_estado.config(text="✗ PIN INVÁLIDO - Acceso denegado", foreground="red")
            messagebox.showerror("Error", "PIN no válido o no registrado. Acceso denegado.")
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
            estado = "Activo" if activo else "Inactivo"
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
        ventana_historial.geometry("600x400")
        
        # Crear tabla de historial
        columnas = ("PIN", "Resultado", "Fecha/Hora")
        tabla_historial = ttk.Treeview(ventana_historial, columns=columnas, height=20)
        tabla_historial.column("#0", width=0, stretch="no")
        
        for col in columnas:
            tabla_historial.column(col, anchor="center", width=180)
            tabla_historial.heading(col, text=col)
        
        for registro in historial:
            pin_parcial = registro[0][:2] + "**" if registro[0] else "****"
            tabla_historial.insert("", "end", values=(
                pin_parcial, registro[1], registro[2]
            ))
        
        scrollbar = ttk.Scrollbar(ventana_historial, orient="vertical", 
                                 command=tabla_historial.yview)
        tabla_historial.configure(yscroll=scrollbar.set)
        
        tabla_historial.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def cerrar(self):
        """Cierra la aplicación"""
        self.db.cerrar()
        self.root.destroy()

def main():
    root = tk.Tk()
    interfaz = InterfazPIN(root)
    root.protocol("WM_DELETE_WINDOW", interfaz.cerrar)
    root.mainloop()

if __name__ == "__main__":
    main()

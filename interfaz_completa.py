import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import subprocess
import sys
import os
from datetime import datetime

class InterfazSistemaCompleto:
    """Interfaz completa del sistema con RFID integrado"""

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Acceso RFID - FABLAB")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(True, True)

        # Variables de control
        self.leyendo_rfid = True
        self.pin_leido = None
        self.db = None

        # Inicializar base de datos
        self.inicializar_db()

        # Crear interfaz
        self.crear_interfaz()

        # Iniciar lectura RFID
        self.iniciar_lectura_rfid()

    def inicializar_db(self):
        """Inicializa la conexión a la base de datos"""
        try:
            from db_pines import BaseDatoPines
            self.db = BaseDatoPines("pines.db")
            print("Base de datos inicializada correctamente")
        except Exception as e:
            print(f"Error al inicializar BD: {e}")
            messagebox.showerror("Error", f"Error al inicializar base de datos: {e}")

    def crear_interfaz(self):
        """Crea la interfaz gráfica completa"""

        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Pestaña 1: Acceso RFID
        self.crear_pestana_acceso()

        # Pestaña 2: Gestión de PINes
        self.crear_pestana_gestion()

        # Pestaña 3: Historial
        self.crear_pestana_historial()

        # Pestaña 4: Configuración
        self.crear_pestana_configuracion()

    def crear_pestana_acceso(self):
        """Crea la pestaña de acceso RFID"""
        pestana_acceso = ttk.Frame(self.notebook)
        self.notebook.add(pestana_acceso, text="🔐 Acceso RFID")

        # Marco principal
        marco_principal = tk.Frame(pestana_acceso, bg="#34495e")
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(marco_principal, text="CONTROL DE ACCESO",
                         font=("Helvetica", 28, "bold"), fg="#ecf0f1", bg="#34495e")
        titulo.pack(pady=(20, 10))

        # Marco de lectura RFID
        marco_rfid = tk.Frame(marco_principal, bg="#2c3e50", relief="raised", bd=2)
        marco_rfid.pack(fill="x", padx=40, pady=20)

        # Icono RFID
        self.icono_rfid = tk.Label(marco_rfid, text="📡", font=("Helvetica", 64),
                                  fg="#f39c12", bg="#2c3e50")
        self.icono_rfid.pack(pady=20)

        # Mensaje de instrucción
        mensaje = tk.Label(marco_rfid, text="ACERQUE EL PIN AL LECTOR RFID",
                          font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#2c3e50")
        mensaje.pack(pady=(0, 10))

        # Estado de lectura
        self.etiqueta_estado_acceso = tk.Label(marco_rfid, text="Esperando lectura...",
                                             font=("Helvetica", 14), fg="#bdc3c7", bg="#2c3e50")
        self.etiqueta_estado_acceso.pack(pady=(0, 20))

        # PIN leído
        self.etiqueta_pin_acceso = tk.Label(marco_rfid, text="",
                                          font=("Helvetica", 18, "bold"), fg="#27ae60", bg="#2c3e50")
        self.etiqueta_pin_acceso.pack(pady=10)

        # Información adicional
        info_frame = tk.Frame(marco_rfid, bg="#2c3e50")
        info_frame.pack(fill="x", padx=20, pady=10)

        info_texto = tk.Label(info_frame,
                             text="• Si el PIN no está registrado, use la pestaña 'Gestión'\n"
                                  "• Los intentos de acceso quedan registrados",
                             font=("Helvetica", 10), fg="#bdc3c7", bg="#2c3e50",
                             justify="left")
        info_texto.pack(anchor="w")

        # Marco de botones
        marco_botones = tk.Frame(marco_principal, bg="#34495e")
        marco_botones.pack(fill="x", padx=40, pady=(20, 0))

        # Botón Detener/Reiniciar lectura
        self.boton_control_lectura = tk.Button(marco_botones, text="DETENER LECTURA",
                                             command=self.controlar_lectura,
                                             font=("Helvetica", 12, "bold"),
                                             bg="#f39c12", fg="white", padx=20, pady=12,
                                             relief="raised", bd=3)
        self.boton_control_lectura.pack(side="left", padx=(0, 10))

        # Botón Salir
        boton_salir = tk.Button(marco_botones, text="SALIR DEL SISTEMA",
                               command=self.salir_sistema,
                               font=("Helvetica", 12, "bold"),
                               bg="#e74c3c", fg="white", padx=20, pady=12,
                               relief="raised", bd=3)
        boton_salir.pack(side="right", padx=(10, 0))

    def crear_pestana_gestion(self):
        """Crea la pestaña de gestión de PINes"""
        pestana_gestion = ttk.Frame(self.notebook)
        self.notebook.add(pestana_gestion, text="⚙️ Gestión de PINes")

        # Marco principal
        marco_principal = tk.Frame(pestana_gestion, bg="#34495e")
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(marco_principal, text="GESTIÓN DE PINES",
                         font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#34495e")
        titulo.pack(pady=(20, 10))

        # Marco de registro
        marco_registro = tk.Frame(marco_principal, bg="#2c3e50", relief="raised", bd=2)
        marco_registro.pack(fill="x", padx=20, pady=20)

        # Título registro
        titulo_reg = tk.Label(marco_registro, text="REGISTRAR NUEVO PIN",
                             font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#2c3e50")
        titulo_reg.pack(pady=15)

        # Formulario
        form_frame = tk.Frame(marco_registro, bg="#2c3e50")
        form_frame.pack(fill="x", padx=20, pady=10)

        # PIN
        tk.Label(form_frame, text="PIN:", font=("Helvetica", 12), fg="#ecf0f1", bg="#2c3e50").grid(row=0, column=0, sticky="w", pady=5)
        self.entrada_pin_gestion = tk.Entry(form_frame, font=("Helvetica", 12), width=30)
        self.entrada_pin_gestion.grid(row=0, column=1, padx=10, pady=5)

        # Usuario
        tk.Label(form_frame, text="Usuario:", font=("Helvetica", 12), fg="#ecf0f1", bg="#2c3e50").grid(row=1, column=0, sticky="w", pady=5)
        self.entrada_usuario_gestion = tk.Entry(form_frame, font=("Helvetica", 12), width=30)
        self.entrada_usuario_gestion.grid(row=1, column=1, padx=10, pady=5)

        # Botones
        botones_frame = tk.Frame(marco_registro, bg="#2c3e50")
        botones_frame.pack(fill="x", padx=20, pady=15)

        tk.Button(botones_frame, text="REGISTRAR PIN", command=self.registrar_pin_gestion,
                 font=("Helvetica", 12, "bold"), bg="#27ae60", fg="white", padx=20, pady=8).pack(side="left", padx=(0, 10))

        tk.Button(botones_frame, text="LEER PIN RFID", command=self.leer_pin_para_registro,
                 font=("Helvetica", 12, "bold"), bg="#3498db", fg="white", padx=20, pady=8).pack(side="left", padx=(0, 10))

        tk.Button(botones_frame, text="LIMPIAR", command=self.limpiar_formulario_gestion,
                 font=("Helvetica", 12, "bold"), bg="#95a5a6", fg="white", padx=20, pady=8).pack(side="left")

        # Marco de lista de PINes
        marco_lista = tk.Frame(marco_principal, bg="#2c3e50", relief="raised", bd=2)
        marco_lista.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Título lista
        titulo_lista = tk.Label(marco_lista, text="PINES REGISTRADOS",
                               font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#2c3e50")
        titulo_lista.pack(pady=15)

        # Tabla
        columnas = ("ID", "PIN", "Usuario", "Fecha Creación", "Estado")
        self.tabla_pines = ttk.Treeview(marco_lista, columns=columnas, height=8)
        self.tabla_pines.column("#0", width=0, stretch="no")

        for col in columnas:
            self.tabla_pines.column(col, anchor="center", width=150)
            self.tabla_pines.heading(col, text=col)

        scrollbar = ttk.Scrollbar(marco_lista, orient="vertical", command=self.tabla_pines.yview)
        self.tabla_pines.configure(yscroll=scrollbar.set)

        self.tabla_pines.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 15))
        scrollbar.pack(side="right", fill="y", pady=(0, 15))

        # Botones de gestión
        botones_gestion_frame = tk.Frame(marco_lista, bg="#2c3e50")
        botones_gestion_frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Button(botones_gestion_frame, text="ACTUALIZAR LISTA", command=self.actualizar_lista_pines,
                 font=("Helvetica", 10, "bold"), bg="#f39c12", fg="white", padx=15, pady=6).pack(side="left", padx=(0, 5))

        tk.Button(botones_gestion_frame, text="ELIMINAR PIN", command=self.eliminar_pin_seleccionado,
                 font=("Helvetica", 10, "bold"), bg="#e74c3c", fg="white", padx=15, pady=6).pack(side="left")

    def crear_pestana_historial(self):
        """Crea la pestaña de historial"""
        pestana_historial = ttk.Frame(self.notebook)
        self.notebook.add(pestana_historial, text="📊 Historial")

        # Marco principal
        marco_principal = tk.Frame(pestana_historial, bg="#34495e")
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(marco_principal, text="HISTORIAL DE ACCESOS",
                         font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#34495e")
        titulo.pack(pady=(20, 10))

        # Área de texto para historial
        marco_historial = tk.Frame(marco_principal, bg="#2c3e50", relief="raised", bd=2)
        marco_historial.pack(fill="both", expand=True, padx=20, pady=20)

        # Título historial
        titulo_hist = tk.Label(marco_historial, text="REGISTRO DE INTENTOS DE ACCESO",
                              font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#2c3e50")
        titulo_hist.pack(pady=15)

        # Tabla de historial
        columnas_hist = ("PIN", "Resultado", "Fecha/Hora")
        self.tabla_historial = ttk.Treeview(marco_historial, columns=columnas_hist, height=15)
        self.tabla_historial.column("#0", width=0, stretch="no")

        for col in columnas_hist:
            self.tabla_historial.column(col, anchor="center", width=200)
            self.tabla_historial.heading(col, text=col)

        scrollbar_hist = ttk.Scrollbar(marco_historial, orient="vertical", command=self.tabla_historial.yview)
        self.tabla_historial.configure(yscroll=scrollbar_hist.set)

        self.tabla_historial.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 15))
        scrollbar_hist.pack(side="right", fill="y", pady=(0, 15))

        # Botones
        botones_hist_frame = tk.Frame(marco_historial, bg="#2c3e50")
        botones_hist_frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Button(botones_hist_frame, text="ACTUALIZAR HISTORIAL", command=self.actualizar_historial,
                 font=("Helvetica", 10, "bold"), bg="#3498db", fg="white", padx=15, pady=6).pack(side="left")

        tk.Button(botones_hist_frame, text="LIMPIAR HISTORIAL", command=self.limpiar_historial,
                 font=("Helvetica", 10, "bold"), bg="#e74c3c", fg="white", padx=15, pady=6).pack(side="right")

    def crear_pestana_configuracion(self):
        """Crea la pestaña de configuración"""
        pestana_config = ttk.Frame(self.notebook)
        self.notebook.add(pestana_config, text="🔧 Configuración")

        # Marco principal
        marco_principal = tk.Frame(pestana_config, bg="#34495e")
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(marco_principal, text="CONFIGURACIÓN DEL SISTEMA",
                         font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#34495e")
        titulo.pack(pady=(20, 10))

        # Marco de configuración
        marco_config = tk.Frame(marco_principal, bg="#2c3e50", relief="raised", bd=2)
        marco_config.pack(fill="both", expand=True, padx=20, pady=20)

        # Información del sistema
        info_sistema = tk.Label(marco_config, text="INFORMACIÓN DEL SISTEMA",
                               font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#2c3e50")
        info_sistema.pack(pady=15)

        # Área de información
        info_frame = tk.Frame(marco_config, bg="#34495e")
        info_frame.pack(fill="x", padx=20, pady=10)

        # Información básica
        info_texto = tk.Text(info_frame, height=10, width=60, font=("Helvetica", 11),
                           bg="#34495e", fg="#ecf0f1", relief="flat")
        info_texto.pack()

        # Insertar información
        info_texto.insert(tk.END, "SISTEMA DE CONTROL DE ACCESO RFID\n")
        info_texto.insert(tk.END, "=" * 40 + "\n\n")
        info_texto.insert(tk.END, f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        info_texto.insert(tk.END, f"Versión: 1.0.0\n")
        info_texto.insert(tk.END, f"Base de datos: pines.db\n")
        info_texto.insert(tk.END, f"Python: {sys.version.split()[0]}\n\n")

        # Estadísticas
        try:
            if self.db:
                pines_total = len(self.db.obtener_todos_pines())
                historial_total = len(self.db.obtener_historial())
                info_texto.insert(tk.END, f"Pines registrados: {pines_total}\n")
                info_texto.insert(tk.END, f"Intentos de acceso: {historial_total}\n")
        except:
            info_texto.insert(tk.END, "Estadísticas no disponibles\n")

        info_texto.config(state="disabled")

        # Botones de configuración
        botones_config_frame = tk.Frame(marco_config, bg="#2c3e50")
        botones_config_frame.pack(fill="x", padx=20, pady=15)

        tk.Button(botones_config_frame, text="PROBAR RFID", command=self.probar_rfid,
                 font=("Helvetica", 10, "bold"), bg="#27ae60", fg="white", padx=15, pady=6).pack(side="left", padx=(0, 5))

        tk.Button(botones_config_frame, text="REINICIAR BD", command=self.reiniciar_bd,
                 font=("Helvetica", 10, "bold"), bg="#e74c3c", fg="white", padx=15, pady=6).pack(side="left", padx=(0, 5))

        tk.Button(botones_config_frame, text="ACERCA DE", command=self.acerca_de,
                 font=("Helvetica", 10, "bold"), bg="#9b59b6", fg="white", padx=15, pady=6).pack(side="left")

    # Métodos de funcionalidad
    def iniciar_lectura_rfid(self):
        """Inicia la lectura RFID en un thread separado"""
        thread = threading.Thread(target=self._leer_rfid_continuo, daemon=True)
        thread.start()

    def _leer_rfid_continuo(self):
        """Lee continuamente del lector RFID"""
        while self.leyendo_rfid:
            try:
                print("Intentando leer PIN RFID...")

                # Usar subprocess para leer RFID
                pin_leido = self.leer_pin_rfid_subprocess()

                if pin_leido:
                    print(f"PIN leído exitosamente: {pin_leido}")
                    # Actualizar interfaz en el hilo principal
                    self.root.after(0, self.procesar_pin_leido, pin_leido)
                    # Pausar lectura por 3 segundos después de lectura exitosa
                    time.sleep(3)
                else:
                    # Reintentar cada 2 segundos
                    time.sleep(2)

            except Exception as e:
                print(f"Error en lectura RFID: {e}")
                self.root.after(0, self.actualizar_estado_acceso, f"Error: {str(e)}", "#e74c3c")
                time.sleep(2)

    def leer_pin_rfid_subprocess(self):
        """Lee PIN usando subprocess"""
        try:
            resultado = subprocess.run(
                ["sudo", "-E", "python3", "PruebaRFID.py"],
                capture_output=True,
                text=True,
                timeout=5
            )

            salida = resultado.stdout
            print(f"Salida RFID: {salida}")

            if "ID:" in salida:
                partes = salida.split("ID: ")
                if len(partes) > 1:
                    pin_leido = partes[1].split()[0].strip()
                    return pin_leido

            return None

        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            print(f"Error en subprocess RFID: {e}")
            return None

    def procesar_pin_leido(self, pin):
        """Procesa el PIN leído del RFID"""
        self.pin_leido = pin
        self.etiqueta_pin_acceso.config(text=f"PIN LEÍDO: {pin}")
        self.actualizar_estado_acceso("PIN leído exitosamente", "#27ae60")

        # Validar PIN
        self.validar_pin_acceso(pin)

    def validar_pin_acceso(self, pin):
        """Valida el PIN en la base de datos"""
        try:
            valido, datos = self.db.validar_pin(pin)

            if valido:
                usuario = datos[1]
                self.actualizar_estado_acceso(f"✓ ACCESO CONCEDIDO - {usuario}", "#27ae60")
                messagebox.showinfo("Acceso Concedido", f"Bienvenido {usuario}")
                # Cambiar a pestaña de gestión automáticamente
                self.notebook.select(1)
            else:
                self.actualizar_estado_acceso("✗ PIN NO REGISTRADO", "#e74c3c")
                messagebox.showwarning("Acceso Denegado", "PIN no registrado en el sistema")
                # Cambiar a pestaña de gestión para registro
                self.notebook.select(1)

        except Exception as e:
            print(f"Error al validar PIN: {e}")
            self.actualizar_estado_acceso("Error en validación", "#e74c3c")

    def actualizar_estado_acceso(self, mensaje, color="#bdc3c7"):
        """Actualiza el estado en la pestaña de acceso"""
        self.etiqueta_estado_acceso.config(text=mensaje, fg=color)

    def controlar_lectura(self):
        """Controla la lectura RFID (detener/reiniciar)"""
        if self.leyendo_rfid:
            self.leyendo_rfid = False
            self.boton_control_lectura.config(text="REINICIAR LECTURA", bg="#27ae60")
            self.actualizar_estado_acceso("Lectura detenida", "#f39c12")
        else:
            self.leyendo_rfid = True
            self.boton_control_lectura.config(text="DETENER LECTURA", bg="#f39c12")
            self.actualizar_estado_acceso("Lectura reiniciada", "#27ae60")
            self.iniciar_lectura_rfid()

    def salir_sistema(self):
        """Sale del sistema"""
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea salir del sistema?"):
            self.leyendo_rfid = False
            if self.db:
                self.db.cerrar()
            self.root.destroy()

    # Métodos de gestión de PINes
    def registrar_pin_gestion(self):
        """Registra un nuevo PIN desde la pestaña de gestión"""
        pin = self.entrada_pin_gestion.get().strip()
        usuario = self.entrada_usuario_gestion.get().strip()

        if not pin or not usuario:
            messagebox.showwarning("Advertencia", "Por favor complete todos los campos")
            return

        try:
            exito, mensaje = self.db.agregar_pin(pin, usuario)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.limpiar_formulario_gestion()
                self.actualizar_lista_pines()
            else:
                messagebox.showerror("Error", mensaje)
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar PIN: {e}")

    def leer_pin_para_registro(self):
        """Lee un PIN RFID para registrarlo"""
        self.actualizar_estado_acceso("Leyendo PIN para registro...", "#f39c12")

        # Leer PIN
        pin_leido = self.leer_pin_rfid_subprocess()

        if pin_leido:
            self.entrada_pin_gestion.delete(0, tk.END)
            self.entrada_pin_gestion.insert(0, pin_leido)
            self.actualizar_estado_acceso(f"PIN leído: {pin_leido}", "#27ae60")
            messagebox.showinfo("PIN Leído", f"PIN {pin_leido} listo para registro")
        else:
            self.actualizar_estado_acceso("No se pudo leer PIN", "#e74c3c")
            messagebox.showwarning("Error", "No se pudo leer el PIN RFID")

    def limpiar_formulario_gestion(self):
        """Limpia el formulario de gestión"""
        self.entrada_pin_gestion.delete(0, tk.END)
        self.entrada_usuario_gestion.delete(0, tk.END)

    def actualizar_lista_pines(self):
        """Actualiza la lista de PINes en la tabla"""
        # Limpiar tabla
        for item in self.tabla_pines.get_children():
            self.tabla_pines.delete(item)

        try:
            pines = self.db.obtener_todos_pines()

            for pin_data in pines:
                id_pin, pin, usuario, fecha_creacion, activo, fecha_ultimo_uso = pin_data
                estado = "✓ Activo" if activo else "✗ Inactivo"
                fecha_uso = fecha_ultimo_uso if fecha_ultimo_uso else "Nunca"

                self.tabla_pines.insert("", "end", values=(
                    id_pin, "****", usuario, fecha_creacion, estado
                ))
        except Exception as e:
            print(f"Error al actualizar lista: {e}")

    def eliminar_pin_seleccionado(self):
        """Elimina el PIN seleccionado"""
        seleccion = self.tabla_pines.selection()

        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona un PIN")
            return

        item = seleccion[0]
        valores = self.tabla_pines.item(item, "values")
        usuario = valores[2]

        if messagebox.askyesno("Confirmar", f"¿Desactivar PIN de {usuario}?"):
            try:
                pines = self.db.obtener_todos_pines()
                id_pin = int(valores[0])

                for pin_data in pines:
                    if pin_data[0] == id_pin:
                        self.db.eliminar_pin(pin_data[1])
                        messagebox.showinfo("Éxito", "PIN desactivado")
                        self.actualizar_lista_pines()
                        break
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar PIN: {e}")

    # Métodos de historial
    def actualizar_historial(self):
        """Actualiza el historial de accesos"""
        # Limpiar tabla
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)

        try:
            historial = self.db.obtener_historial()

            for registro in historial:
                pin_parcial = registro[0][:2] + "**" if registro[0] else "****"
                resultado_color = "✓ ÉXITO" if registro[1] == "ÉXITO" else "✗ FALLÓ"

                self.tabla_historial.insert("", "end", values=(
                    pin_parcial, resultado_color, registro[2]
                ))
        except Exception as e:
            print(f"Error al actualizar historial: {e}")

    def limpiar_historial(self):
        """Limpia el historial (solo visualmente)"""
        if messagebox.askyesno("Confirmar", "¿Limpiar vista del historial?"):
            for item in self.tabla_historial.get_children():
                self.tabla_historial.delete(item)

    # Métodos de configuración
    def probar_rfid(self):
        """Prueba la conexión RFID"""
        self.actualizar_estado_acceso("Probando RFID...", "#f39c12")

        pin_test = self.leer_pin_rfid_subprocess()

        if pin_test:
            self.actualizar_estado_acceso(f"RFID OK - PIN: {pin_test}", "#27ae60")
            messagebox.showinfo("Prueba Exitosa", f"Lector RFID funcionando correctamente\nPIN detectado: {pin_test}")
        else:
            self.actualizar_estado_acceso("RFID Error", "#e74c3c")
            messagebox.showerror("Prueba Fallida", "No se pudo leer PIN RFID")

    def reiniciar_bd(self):
        """Reinicia la base de datos"""
        if messagebox.askyesno("Confirmar", "¿Reiniciar base de datos? Se perderán todos los datos."):
            try:
                import os
                if os.path.exists("pines.db"):
                    os.remove("pines.db")

                # Reinicializar BD
                from db_pines import BaseDatoPines
                self.db = BaseDatoPines("pines.db")

                messagebox.showinfo("Éxito", "Base de datos reiniciada")
                self.actualizar_lista_pines()
                self.actualizar_historial()

            except Exception as e:
                messagebox.showerror("Error", f"Error al reiniciar BD: {e}")

    def acerca_de(self):
        """Muestra información del sistema"""
        info = """SISTEMA DE CONTROL DE ACCESO RFID

Versión: 1.0.0
Desarrollado para: FABLAB
Fecha: 2026

Características:
• Lectura automática RFID
• Base de datos SQLite
• Interfaz gráfica completa
• Historial de accesos
• Gestión de PINes

Tecnologías:
• Python 3
• Tkinter
• SQLite
• RPi.GPIO
• mfrc522"""

        messagebox.showinfo("Acerca de", info)

def main():
    root = tk.Tk()
    app = InterfazSistemaCompleto(root)
    root.protocol("WM_DELETE_WINDOW", app.salir_sistema)
    root.mainloop()

if __name__ == "__main__":
    main()
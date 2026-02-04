import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from db_pines import BaseDatoPines

class PantallaBienvenida:
    """Pantalla inicial de bienvenida con lectura RFID"""

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Acceso - Bienvenida")
        self.root.geometry("800x600")
        self.root.configure(bg="#34495e")
        self.root.resizable(False, False)

        # Centrar ventana
        self.root.eval('tk::PlaceWindow . center')

        # Inicializar base de datos
        self.db = BaseDatoPines("pines.db")

        # Variables de control
        self.leyendo_rfid = True
        self.reader = None
        self.pin_admin = "admin123"  # Contraseña de administrador

        # Inicializar RFID
        self.inicializar_rfid()

        # Crear interfaz
        self.crear_interfaz()

        # Iniciar lectura RFID
        self.iniciar_lectura_rfid()

    def inicializar_rfid(self):
        """Inicializa el lector RFID"""
        try:
            import RPi.GPIO as GPIO
            from mfrc522 import SimpleMFRC522

            # Configurar GPIO
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)

            self.reader = SimpleMFRC522()
            self.rfid_disponible = True
            print("✅ Lector RFID inicializado correctamente")
        except ImportError as e:
            self.rfid_disponible = False
            print(f"❌ Librerías RFID no disponibles: {e}")
            print("   Instale con: pip install mfrc522")
        except PermissionError as e:
            self.rfid_disponible = False
            print(f"❌ Permisos insuficientes para GPIO: {e}")
            print("   Ejecute con: sudo python3 pantalla_bienvenida.py")
        except Exception as e:
            self.rfid_disponible = False
            print(f"❌ Error al inicializar RFID: {e}")
            print("   Modo simulación activado")

    def crear_interfaz(self):
        """Crea la interfaz de bienvenida"""

        # Marco principal
        marco_principal = tk.Frame(self.root, bg="#34495e")
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(marco_principal, text="FABLAB",
                         font=("Helvetica", 36, "bold"), fg="#ecf0f1", bg="#34495e")
        titulo.pack(pady=(20, 10))

        subtitulo = tk.Label(marco_principal, text="Sistema de Control de Acceso",
                           font=("Helvetica", 18), fg="#bdc3c7", bg="#34495e")
        subtitulo.pack(pady=(0, 40))

        # Marco de lectura RFID
        marco_rfid = tk.Frame(marco_principal, bg="#2c3e50", relief="raised", bd=2)
        marco_rfid.pack(fill="x", padx=40, pady=20)

        # Icono RFID
        icono_rfid = tk.Label(marco_rfid, text="📡", font=("Helvetica", 48),
                             fg="#f39c12", bg="#2c3e50")
        icono_rfid.pack(pady=20)

        # Mensaje principal
        self.mensaje_principal = tk.Label(marco_rfid,
                                        text="ACERQUE EL PIN AL LECTOR",
                                        font=("Helvetica", 16, "bold"),
                                        fg="#ecf0f1", bg="#2c3e50")
        self.mensaje_principal.pack(pady=(0, 10))

        # Estado del lector
        estado_lector = "Lector RFID: " + ("✅ CONECTADO" if self.rfid_disponible else "⚠ MODO SIMULACIÓN")
        color_estado = "#27ae60" if self.rfid_disponible else "#e67e22"

        self.etiqueta_estado = tk.Label(marco_rfid, text=estado_lector,
                                       font=("Helvetica", 12), fg=color_estado, bg="#2c3e50")
        self.etiqueta_estado.pack(pady=(0, 20))

        # Marco de mensajes dinámicos
        self.marco_mensajes = tk.Frame(marco_rfid, bg="#2c3e50")
        self.marco_mensajes.pack(fill="x", padx=20, pady=10)

        # Mensaje de estado (inicialmente oculto)
        self.mensaje_estado = tk.Label(self.marco_mensajes, text="",
                                      font=("Helvetica", 14), fg="#f1c40f", bg="#2c3e50",
                                      wraplength=600, justify="center")
        self.mensaje_estado.pack(pady=10)

        # Marco de botones
        marco_botones = tk.Frame(marco_principal, bg="#34495e")
        marco_botones.pack(fill="x", padx=40, pady=20)

        # Botón Registrar PIN (inicialmente oculto)
        self.boton_registrar = tk.Button(marco_botones, text="REGISTRAR PIN",
                                        command=self.mostrar_registro,
                                        font=("Helvetica", 12, "bold"),
                                        bg="#e74c3c", fg="white", padx=20, pady=10,
                                        relief="raised", bd=3)
        # Inicialmente oculto
        self.boton_registrar.pack_forget()

        # Espacio
        tk.Label(marco_botones, text="", bg="#34495e").pack(pady=5)

        # Botón Volver
        boton_volver = tk.Button(marco_botones, text="VOLVER",
                                command=self.cerrar_programa,
                                font=("Helvetica", 12, "bold"),
                                bg="#95a5a6", fg="white", padx=20, pady=10,
                                relief="raised", bd=3)
        boton_volver.pack()

        # Información del sistema
        info_frame = tk.Frame(marco_principal, bg="#34495e")
        info_frame.pack(fill="x", padx=40, pady=(20, 0))

        info_texto = tk.Label(info_frame,
                             text="Para acceder al sistema, acerque su PIN al lector RFID.\n"
                                  "Si es su primera vez, solicite registro al administrador.",
                             font=("Helvetica", 10), fg="#bdc3c7", bg="#34495e",
                             justify="center")
        info_texto.pack()

    def iniciar_lectura_rfid(self):
        """Inicia el thread de lectura RFID"""
        thread = threading.Thread(target=self._leer_rfid_continuo, daemon=True)
        thread.start()

    def _leer_rfid_continuo(self):
        """Lee continuamente del lector RFID"""
        simulacion_contador = 0
        pines_simulacion = ["1234567890", "9876543210", "1111111111"]

        while self.leyendo_rfid:
            try:
                if self.rfid_disponible and self.reader:
                    # Leer del RFID real
                    print("📡 Esperando lectura RFID...")
                    id_rfid, texto = self.reader.read()

                    # Procesar el PIN leído
                    pin_leido = str(id_rfid).strip()
                    print(f"✅ PIN leído del RFID: {pin_leido}")

                    # Procesar en el hilo principal
                    self.root.after(0, self.procesar_pin_rfid, pin_leido)
                else:
                    # Modo simulación
                    simulacion_contador += 1
                    if simulacion_contador % 10 == 0:  # Cada 10 segundos
                        pin_simulado = pines_simulacion[(simulacion_contador // 10) % len(pines_simulacion)]
                        print(f"🔄 MODO SIMULACIÓN - Probando PIN: {pin_simulado}")
                        self.root.after(0, self.procesar_pin_rfid, pin_simulado)

                    time.sleep(1)  # Verificar cada segundo

            except Exception as e:
                print(f"❌ Error al leer RFID: {e}")
                self.root.after(0, self.actualizar_estado_lector, f"Error: {str(e)[:50]}...", "red")
                time.sleep(2)

    def intentar_lectura_auxiliar(self):
        """Intenta leer usando el módulo auxiliar si el principal falla"""
        try:
            print("🔄 Intentando lectura auxiliar del sensor RFID...")
            from lector_rfid_aux import leer_sensor_rfid

            pin_aux = leer_sensor_rfid()
            if pin_aux:
                print(f"✅ PIN leído por método auxiliar: {pin_aux}")
                self.procesar_pin_rfid(pin_aux)
            else:
                print("❌ Método auxiliar tampoco pudo leer el PIN")
                self.actualizar_estado_lector("No se pudo leer PIN", "red")
        except Exception as e:
            print(f"❌ Error en lectura auxiliar: {e}")
            self.actualizar_estado_lector("Error en sensor auxiliar", "red")

    def actualizar_estado_lector(self, mensaje, color):
        """Actualiza el estado visual del lector"""
        self.etiqueta_estado.config(text=f"Estado: {mensaje}", fg=color)

    def procesar_pin_rfid(self, pin):
        """Procesa el PIN leído del RFID"""
        print(f"🔍 Procesando PIN: {pin}")

        # Actualizar estado
        self.actualizar_estado_lector("Procesando PIN...", "blue")

        # Validar PIN
        valido, datos = self.db.validar_pin(pin)

        if valido:
            usuario = datos[1]
            self.mostrar_mensaje_exito(f"✅ PIN VÁLIDO\nBienvenido {usuario}")
            self.actualizar_estado_lector("Acceso concedido", "green")
            self.root.after(2000, self.abrir_menu_principal, pin, usuario)
        else:
            self.mostrar_mensaje_error(f"❌ PIN NO REGISTRADO\nPIN: {pin}\n\nRegistre este PIN para continuar")
            self.actualizar_estado_lector("PIN no registrado", "orange")
            self.mostrar_boton_registro(pin)

    def mostrar_mensaje_exito(self, mensaje):
        """Muestra mensaje de éxito"""
        self.mensaje_estado.config(text=mensaje, fg="#27ae60")
        self.mensaje_estado.pack(pady=10)

    def mostrar_mensaje_error(self, mensaje):
        """Muestra mensaje de error"""
        self.mensaje_estado.config(text=mensaje, fg="#e74c3c")
        self.mensaje_estado.pack(pady=10)

    def mostrar_boton_registro(self, pin):
        """Muestra el botón de registro con el PIN leído"""
        self.pin_a_registrar = pin
        self.boton_registrar.pack(pady=10)

    def mostrar_registro(self):
        """Muestra el diálogo de registro con contraseña admin"""
        # Pedir contraseña de administrador
        password = simpledialog.askstring("Contraseña Administrador",
                                        "Ingrese contraseña de administrador:",
                                        show="*")

        if password == self.pin_admin:
            # Contraseña correcta, mostrar formulario de registro
            self.abrir_registro_pin(self.pin_a_registrar)
        else:
            messagebox.showerror("Error", "Contraseña de administrador incorrecta")

    def abrir_registro_pin(self, pin):
        """Abre la ventana de registro de PIN"""
        self.leyendo_rfid = False  # Detener lectura RFID

        # Crear ventana de registro
        ventana_registro = tk.Toplevel(self.root)
        ventana_registro.title("Registro de Nuevo PIN")
        ventana_registro.geometry("500x400")
        ventana_registro.configure(bg="#34495e")
        ventana_registro.resizable(False, False)
        ventana_registro.transient(self.root)
        ventana_registro.grab_set()

        # Centrar ventana
        ventana_registro.eval('tk::PlaceWindow . center')

        # Marco principal
        marco = tk.Frame(ventana_registro, bg="#34495e")
        marco.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(marco, text="REGISTRO DE PIN",
                         font=("Helvetica", 18, "bold"), fg="#ecf0f1", bg="#34495e")
        titulo.pack(pady=(10, 20))

        # PIN leído
        tk.Label(marco, text=f"PIN detectado: {pin}",
                font=("Helvetica", 12), fg="#f39c12", bg="#34495e").pack(pady=10)

        # Formulario
        tk.Label(marco, text="Nombre del Usuario:",
                font=("Helvetica", 12), fg="#ecf0f1", bg="#34495e").pack(pady=(20, 5))

        entrada_usuario = tk.Entry(marco, font=("Helvetica", 12), width=30)
        entrada_usuario.pack(pady=5)
        entrada_usuario.focus()

        def registrar():
            usuario = entrada_usuario.get().strip()
            if not usuario:
                messagebox.showwarning("Advertencia", "Por favor ingrese el nombre del usuario")
                return

            # Registrar PIN
            exito, mensaje = self.db.agregar_pin(pin, usuario)

            if exito:
                messagebox.showinfo("Éxito", f"PIN registrado exitosamente para {usuario}")
                ventana_registro.destroy()
                self.reiniciar_bienvenida()
            else:
                messagebox.showerror("Error", mensaje)

        def cancelar():
            ventana_registro.destroy()
            self.reiniciar_bienvenida()

        # Botones
        marco_botones = tk.Frame(marco, bg="#34495e")
        marco_botones.pack(pady=30)

        tk.Button(marco_botones, text="REGISTRAR", command=registrar,
                 font=("Helvetica", 12, "bold"), bg="#27ae60", fg="white",
                 padx=20, pady=10).pack(side="left", padx=10)

        tk.Button(marco_botones, text="CANCELAR", command=cancelar,
                 font=("Helvetica", 12, "bold"), bg="#95a5a6", fg="white",
                 padx=20, pady=10).pack(side="left", padx=10)

        # Bind Enter key
        ventana_registro.bind('<Return>', lambda e: registrar())
        ventana_registro.bind('<Escape>', lambda e: cancelar())

    def abrir_menu_principal(self, pin, usuario):
        """Abre el menú principal con el PIN validado"""
        self.leyendo_rfid = False

        # Importar aquí para evitar importaciones circulares
        from interfaz_pin_rfid import InterfazPINRFID

        # Cerrar ventana actual
        self.root.destroy()

        # Abrir menú principal
        root_principal = tk.Tk()
        interfaz = InterfazPINRFID(root_principal)
        root_principal.protocol("WM_DELETE_WINDOW", interfaz.cerrar)
        root_principal.mainloop()

    def reiniciar_bienvenida(self):
        """Reinicia la pantalla de bienvenida"""
        self.mensaje_estado.config(text="")
        self.boton_registrar.pack_forget()
        self.leyendo_rfid = True
        self.iniciar_lectura_rfid()

    def cerrar_programa(self):
        """Cierra el programa"""
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea salir?"):
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
    bienvenida = PantallaBienvenida(root)
    root.protocol("WM_DELETE_WINDOW", bienvenida.cerrar_programa)
    root.mainloop()

if __name__ == "__main__":
    main()

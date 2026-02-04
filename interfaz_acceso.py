import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import subprocess
import sys
import os

class InterfazAcceso:
    """Interfaz simple de acceso con lectura RFID y botones"""

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Acceso RFID")
        self.root.geometry("600x400")
        self.root.configure(bg="#34495e")
        self.root.resizable(False, False)

        # Centrar ventana
        self.root.eval('tk::PlaceWindow . center')

        # Variables de control
        self.leyendo_rfid = True
        self.pin_leido = None

        # Crear interfaz
        self.crear_interfaz()

        # Iniciar lectura RFID en thread separado
        self.iniciar_lectura_rfid()

    def crear_interfaz(self):
        """Crea la interfaz gráfica"""

        # Marco principal
        marco_principal = tk.Frame(self.root, bg="#34495e")
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(marco_principal, text="ACCESO AL SISTEMA",
                         font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#34495e")
        titulo.pack(pady=(20, 10))

        # Marco de lectura RFID
        marco_rfid = tk.Frame(marco_principal, bg="#2c3e50", relief="raised", bd=2)
        marco_rfid.pack(fill="x", padx=20, pady=20)

        # Icono RFID
        icono_rfid = tk.Label(marco_rfid, text="📡", font=("Helvetica", 48),
                             fg="#f39c12", bg="#2c3e50")
        icono_rfid.pack(pady=20)

        # Mensaje de instrucción
        mensaje = tk.Label(marco_rfid, text="ACERQUE EL PIN AL LECTOR RFID",
                          font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#2c3e50")
        mensaje.pack(pady=(0, 10))

        # Estado de lectura
        self.etiqueta_estado = tk.Label(marco_rfid, text="Esperando lectura...",
                                       font=("Helvetica", 12), fg="#bdc3c7", bg="#2c3e50")
        self.etiqueta_estado.pack(pady=(0, 20))

        # PIN leído (inicialmente vacío)
        self.etiqueta_pin = tk.Label(marco_rfid, text="",
                                    font=("Helvetica", 16, "bold"), fg="#27ae60", bg="#2c3e50")
        self.etiqueta_pin.pack(pady=10)

        # Marco de botones
        marco_botones = tk.Frame(marco_principal, bg="#34495e")
        marco_botones.pack(fill="x", padx=20, pady=(20, 0))

        # Botón Registro de nuevo PIN
        boton_registro = tk.Button(marco_botones, text="REGISTRO DE NUEVO PIN",
                                  command=self.registro_nuevo_pin,
                                  font=("Helvetica", 12, "bold"),
                                  bg="#27ae60", fg="white", padx=20, pady=12,
                                  relief="raised", bd=3)
        boton_registro.pack(side="left", padx=(0, 10))

        # Botón Volver
        boton_volver = tk.Button(marco_botones, text="VOLVER",
                                command=self.volver,
                                font=("Helvetica", 12, "bold"),
                                bg="#e74c3c", fg="white", padx=20, pady=12,
                                relief="raised", bd=3)
        boton_volver.pack(side="right", padx=(10, 0))

    def iniciar_lectura_rfid(self):
        """Inicia la lectura RFID en un thread separado"""
        thread = threading.Thread(target=self._leer_rfid_continuo, daemon=True)
        thread.start()

    def _leer_rfid_continuo(self):
        """Lee continuamente del lector RFID"""
        while self.leyendo_rfid:
            try:
                print("Intentando leer PIN RFID...")

                # Usar la función auxiliar del Rsgisandvrift.py
                pin_leido = self.leer_pin_rfid_aux()

                if pin_leido:
                    print(f"PIN leído exitosamente: {pin_leido}")
                    # Actualizar interfaz en el hilo principal
                    self.root.after(0, self.mostrar_pin_leido, pin_leido)
                    # Pausar lectura por 3 segundos después de lectura exitosa
                    time.sleep(3)
                else:
                    # Reintentar cada 2 segundos
                    time.sleep(2)

            except Exception as e:
                print(f"Error en lectura RFID: {e}")
                self.root.after(0, self.actualizar_estado, f"Error: {str(e)}", "#e74c3c")
                time.sleep(2)

    def leer_pin_rfid_aux(self):
        """Función auxiliar para leer PIN desde RFID usando subprocess"""
        try:
            # Ejecutar PruebaRFID.py y capturar salida
            resultado = subprocess.run(
                ["sudo", "-E", "python3", "PruebaRFID.py"],
                capture_output=True,
                text=True,
                timeout=5  # Timeout de 5 segundos
            )

            # Procesar la salida para extraer el PIN
            salida = resultado.stdout
            print(f"Salida del lector RFID: {salida}")

            # Buscar el ID en la salida (formato típico: "ID: 123456789")
            if "ID:" in salida:
                # Extraer el ID después de "ID: "
                partes = salida.split("ID: ")
                if len(partes) > 1:
                    pin_leido = partes[1].split()[0].strip()
                    return pin_leido

            return None

        except subprocess.TimeoutExpired:
            print("Timeout en lectura RFID")
            return None
        except Exception as e:
            print(f"Error al leer PIN RFID: {e}")
            return None

    def mostrar_pin_leido(self, pin):
        """Muestra el PIN leído en la interfaz"""
        self.pin_leido = pin
        self.etiqueta_pin.config(text=f"PIN LEÍDO: {pin}")
        self.actualizar_estado("PIN leído exitosamente", "#27ae60")

        # Validar PIN automáticamente
        self.validar_pin(pin)

    def actualizar_estado(self, mensaje, color="#bdc3c7"):
        """Actualiza el mensaje de estado"""
        self.etiqueta_estado.config(text=mensaje, fg=color)

    def validar_pin(self, pin):
        """Valida el PIN en la base de datos"""
        try:
            from db_pines import BaseDatoPines
            db = BaseDatoPines("pines.db")
            valido, datos = db.validar_pin(pin)
            db.cerrar()

            if valido:
                usuario = datos[1]
                self.actualizar_estado(f"✓ ACCESO CONCEDIDO - {usuario}", "#27ae60")
                messagebox.showinfo("Acceso Concedido", f"Bienvenido {usuario}")
                # Aquí podrías abrir el menú principal
                # self.root.after(2000, self.abrir_menu_principal)
            else:
                self.actualizar_estado("✗ PIN NO REGISTRADO", "#e74c3c")
                messagebox.showwarning("Acceso Denegado", "PIN no registrado en el sistema")

        except Exception as e:
            print(f"Error al validar PIN: {e}")
            self.actualizar_estado("Error en validación", "#e74c3c")

    def registro_nuevo_pin(self):
        """Abre la funcionalidad de registro de nuevo PIN"""
        # Detener lectura RFID temporalmente
        self.leyendo_rfid = False

        # Pedir contraseña de administrador
        from tkinter.simpledialog import askstring
        password = askstring("Contraseña Administrador",
                           "Ingrese contraseña de administrador:",
                           show="*")

        if password == "admin123":  # Contraseña por defecto
            # Abrir interfaz de registro
            self.abrir_registro_pin()
        else:
            messagebox.showerror("Error", "Contraseña de administrador incorrecta")
            self.leyendo_rfid = True  # Reanudar lectura

    def abrir_registro_pin(self):
        """Abre la ventana de registro de PIN"""
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

        # PIN (si se leyó uno)
        pin_texto = self.pin_leido if self.pin_leido else "Ningún PIN leído"
        tk.Label(marco, text=f"PIN detectado: {pin_texto}",
                font=("Helvetica", 12), fg="#f39c12", bg="#34495e").pack(pady=10)

        # Formulario
        tk.Label(marco, text="Nombre del Usuario:",
                font=("Helvetica", 12), fg="#ecf0f1", bg="#34495e").pack(pady=(20, 5))

        entrada_usuario = tk.Entry(marco, font=("Helvetica", 12), width=30)
        entrada_usuario.pack(pady=5)
        entrada_usuario.focus()

        def registrar():
            usuario = entrada_usuario.get().strip()
            pin_a_registrar = self.pin_leido

            if not usuario:
                messagebox.showwarning("Advertencia", "Por favor ingrese el nombre del usuario")
                return

            if not pin_a_registrar:
                messagebox.showwarning("Advertencia", "No hay PIN leído. Acerque una tarjeta RFID primero")
                return

            # Registrar PIN
            try:
                from db_pines import BaseDatoPines
                db = BaseDatoPines("pines.db")
                exito, mensaje = db.agregar_pin(pin_a_registrar, usuario)
                db.cerrar()

                if exito:
                    messagebox.showinfo("Éxito", f"PIN registrado exitosamente para {usuario}")
                    ventana_registro.destroy()
                    self.reiniciar_interfaz()
                else:
                    messagebox.showerror("Error", mensaje)
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar PIN: {e}")

        def cancelar():
            ventana_registro.destroy()
            self.reiniciar_interfaz()

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

    def reiniciar_interfaz(self):
        """Reinicia la interfaz después del registro"""
        self.pin_leido = None
        self.etiqueta_pin.config(text="")
        self.actualizar_estado("Esperando lectura...", "#bdc3c7")
        self.leyendo_rfid = True
        self.iniciar_lectura_rfid()

    def volver(self):
        """Cierra el programa"""
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea salir del sistema?"):
            self.leyendo_rfid = False
            self.root.destroy()

def main():
    root = tk.Tk()
    interfaz = InterfazAcceso(root)
    root.protocol("WM_DELETE_WINDOW", interfaz.volver)
    root.mainloop()

if __name__ == "__main__":
    main()

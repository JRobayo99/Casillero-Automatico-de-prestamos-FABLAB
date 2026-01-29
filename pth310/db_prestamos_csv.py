import pandas as pd
from pathlib import Path
from datetime import datetime
import PDF417

def init_csv(csv_path="prestamos.csv"):
    if not Path(csv_path).exists():
        df = pd.DataFrame(columns=[
            'Nombre', 'apellido1', 'apellido2', 'cedula', 'fecha_nac', 'rh', 'sexo', 'foto_path', 'herramientas', 'fecha_prestamo'
        ])
        df.to_csv(csv_path, index=False)

def guardar_prestamo_csv(nombre, apellido1, apellido2, cedula, fecha_nac, rh, sexo, foto_path, herramientas, csv_path="prestamos.csv"):
    init_csv(csv_path)
    df = pd.read_csv(csv_path)
    nueva_fila = {
        'nombre': nombre,
        'apellido1': apellido1,
        'apellido2': apellido2,
        'cedula': cedula,
        'fecha_nac': fecha_nac,
        'rh': rh,
        'sexo': sexo,
        'foto_path': foto_path,
        'herramientas': ','.join(herramientas),
        'fecha_prestamo': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_csv(csv_path, index=False)

def obtener_historial_csv(csv_path="prestamos.csv"):
    init_csv(csv_path)
    return pd.read_csv(csv_path)

def escanear_y_guardar_prestamo(foto_path, herramientas, csv_path="prestamos.csv"):
    data = PDF417.scan_pdf417()
    if not data:
        print("No se detectó ningún dato válido.")
        return
    nombre = data.get('nombre', '')
    apellido1 = data.get('apellido1', '')
    apellido2 = data.get('apellido2', '')
    cedula = data.get('cedula', '')
    fecha_nac = data.get('fecha_nac', '')
    rh = data.get('rh', '')
    sexo = data.get('sexo', '')
    from db_prestamos_csv import guardar_prestamo_csv
    guardar_prestamo_csv(nombre, apellido1, apellido2, cedula, fecha_nac, rh, sexo, foto_path, herramientas, csv_path)
    print(f"Préstamo guardado para {nombre} {apellido1} {apellido2} con herramientas: {herramientas}")

if __name__ == "__main__":
    init_csv()
    guardar_prestamo_csv('Juan','Pérez','Gómez','1234567890','1990-01-01','O+','M','/ruta/foto.jpg',['Martillo','Destornillador'])
    print(obtener_historial_csv())

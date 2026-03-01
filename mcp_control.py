import smbus

bus = smbus.SMBus(1)

MCP1 = 0x27
MCP2 = 0x23

# multiplexores de entrada (sólo lectura)
MUX1 = 0x25
MUX2 = 0x26

IODIRA = 0x00
IODIRB = 0x01
GPIOA = 0x12
GPIOB = 0x13

# Configurar todos los MCP como salidas
for addr in (MCP1, MCP2):
    bus.write_byte_data(addr, IODIRA, 0x00)
    bus.write_byte_data(addr, IODIRB, 0x00)

# Configurar multiplexores como entradas
for addr in (MUX1, MUX2):
    bus.write_byte_data(addr, IODIRA, 0xFF)  # todos los pines A como entrada
    bus.write_byte_data(addr, IODIRB, 0xFF)  # todos los pines B como entrada

def activar_salida(num):
    """Activa una de las 32 salidas de los MCP23017 existentes.

    **Modo histórico**: este método sigue operativo para controlar los
    expander de salida (0x27 y 0x23). Conserva el comportamiento original
    de encender un solo bit entre 1 y 32.
    """
    if not 1 <= num <= 32:
        return

    # Apagar todo antes de seleccionar
    for addr in (MCP1, MCP2):
        bus.write_byte_data(addr, GPIOA, 0x00)
        bus.write_byte_data(addr, GPIOB, 0x00)

    if num <= 16:
        bus.write_byte_data(MCP1, GPIOA, 1 << (num - 1))
    else:
        bus.write_byte_data(MCP2, GPIOA, 1 << (num - 17))


def seleccionar_canal(num):
    """Escribe el número de canal (1–31) en los multiplexores de entrada.

    Esta es la "nueva" forma de selección: el valor se envía en bruto al
    registro GPIOA de los dispositivos 0x25 y 0x26, que están
    configurados como entradas/enrutadores. Sólo se aceptan valores
    entre 1 y 31.
    """
    if not 1 <= num <= 31:
        return

    bus.write_byte_data(MUX1, GPIOA, num)
    bus.write_byte_data(MUX2, GPIOA, num)


def leer_multiplexores():
    """Lee el estado actual de los multiplexores de entrada.

    Devuelve un diccionario con tuplas (GPIOA, GPIOB) para cada chip.
    """
    estado = {}
    for idx, addr in enumerate((MUX1, MUX2), start=1):
        a = bus.read_byte_data(addr, GPIOA)
        b = bus.read_byte_data(addr, GPIOB)
        estado[f"mux{idx}"] = (a, b)
    return estado
